#!/usr/bin/env python3
"""Read-only receipt validation. No network, command execution or workspace writes.

This checks declared files in a quiescent workspace. It is NOT a sandbox,
a semantic evaluator, a comprehensive inventory or an independent AI test.
"""
import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath
import re
import stat
import sys

MAX_FILE = 25 * 1024 * 1024
ROLES = {'current', 'deliverable', 'evidence', 'research', 'log', 'experience', 'index'}
STATES = {'ACTIVE', 'SUPERSEDED', 'INVALID'}


def safe_file(root, relative):
    """Reject absolute, ambiguous, traversal and symlink paths before reading."""
    if (not isinstance(relative, str) or not relative or '\\' in relative
            or ':' in relative or '\x00' in relative or any(c in relative for c in '*?')):
        raise ValueError('UNSAFE_PATH')
    parts = relative.split('/')
    if PurePosixPath(relative).is_absolute() or any(p in ('', '.', '..', '.git') for p in parts):
        raise ValueError('UNSAFE_PATH')
    target = root
    for part in parts:
        target = target / part
        if target.is_symlink():
            raise ValueError('UNSAFE_PATH')
        if not target.exists():
            raise ValueError('MISSING_FILE')
        # Exact spelling matters on case-insensitive filesystems too.
        if part not in {p.name for p in target.parent.iterdir()}:
            raise ValueError('MISSING_FILE')
    if not target.is_relative_to(root) or not stat.S_ISREG(target.stat().st_mode):
        raise ValueError('UNSAFE_PATH')
    return target


def read_stable(path, limit=MAX_FILE):
    before = path.stat()
    if before.st_size > limit:
        raise ValueError('FILE_TOO_LARGE')
    with path.open('rb') as stream:
        raw = stream.read(limit + 1)
    after = path.stat()
    if len(raw) > limit:
        raise ValueError('FILE_TOO_LARGE')
    if (before.st_ino, before.st_size, before.st_mtime_ns) != (after.st_ino, after.st_size, after.st_mtime_ns):
        raise ValueError('SNAPSHOT_CHANGED')
    return raw


def no_duplicate_keys(pairs):
    out = {}
    for key, value in pairs:
        if key in out:
            raise ValueError('duplicate JSON key')
        out[key] = value
    return out


def validate(root, data, receipt_path, delivery=False):
    issues = []
    def issue(code, target, detail):
        issues.append({'code': code, 'target': target, 'detail': detail})
    def strings(value):
        return isinstance(value, list) and all(isinstance(v, str) and v for v in value)
    def member(value, allowed):
        return isinstance(value, str) and value in allowed
    def positive_int(value):
        return type(value) is int and value > 0
    def rows(key):
        value = data.get(key, [])
        if not isinstance(value, list) or len(value) > 256 or any(not isinstance(r, dict) for r in value):
            issue('SCHEMA', key, 'Expected a list of at most 256 objects')
            return []
        return value
    if not isinstance(data, dict):
        data = {}
        issue('SCHEMA', 'receipt', 'Expected JSON object')
    revision = data.get('revision')
    if (data.get('schema_version') != '0.3' or not positive_int(revision)
            or not isinstance(data.get('task_id'), str) or not data.get('task_id')
            or not member(data.get('scope_enforcement'), {'HARD', 'SOFT'})
            or not member(data.get('context_status'), {'CLEAN', 'CONTAMINATED', 'UNKNOWN'})):
        issue('SCHEMA', 'receipt', 'Invalid schema version, task, revision or scope/context status')
    files = rows('files')
    checks = rows('checks')
    changes = rows('changes')
    objects, paths, raw_files = {}, set(), {}
    for f in files:
        ident, path = f.get('id'), f.get('path')
        if (not isinstance(ident, str) or not ident or not member(f.get('role'), ROLES)
                or not member(f.get('status'), STATES) or not positive_int(f.get('reviewed_revision'))
                or not re.fullmatch(r'[0-9a-f]{64}', str(f.get('sha256', '')))
                or not strings(f.get('depends_on', []))):
            issue('SCHEMA', str(ident), 'Invalid file record')
            continue
        if ident in objects:
            issue('DUPLICATE_ID', ident, 'File IDs must be unique')
        objects[ident] = f
        if isinstance(path, str):
            if path in paths:
                issue('DUPLICATE_PATH', path, 'List a file only once')
            paths.add(path)
        if path == receipt_path:
            issue('SELF_REFERENCE', ident, 'The receipt cannot hash itself')
            continue
        try:
            raw = read_stable(safe_file(root, path))
            raw_files[ident] = raw
            if hashlib.sha256(raw).hexdigest() != f['sha256']:
                issue('HASH_MISMATCH', ident, 'File differs from the recorded snapshot')
        except (OSError, ValueError) as exc:
            code = str(exc) if isinstance(exc, ValueError) else 'READ_ERROR'
            issue(code, str(ident), 'File cannot be safely checked')
        if f['status'] == 'ACTIVE' and f['role'] in {'current', 'deliverable'} and f['reviewed_revision'] != revision:
            issue('STALE_REVISION', ident, 'Active state/output was not reviewed at the current revision')
    requirement_ids = set()
    current = [f for f in objects.values() if f['role'] == 'current' and f['status'] == 'ACTIVE']
    if len(current) != 1:
        issue('CURRENT_STATE_COUNT', 'files', 'Exactly one active Current Truth is required')
    elif current[0]['id'] in raw_files:
        try:
            text = raw_files[current[0]['id']].decode('utf-8')
            requirement_ids = set(re.findall(r'\bR-\d+\b', text))
            task = re.search(r'^TASK_ID:\s*(\S+)\s*$', text, re.M)
            rev = re.search(r'^REVISION:\s*(\d+)\s*$', text, re.M)
            if not task or not rev or task.group(1) != data.get('task_id') or int(rev.group(1)) != revision:
                issue('TASK_BINDING_MISMATCH', current[0]['id'], 'TASK_ID / REVISION differs from the receipt')
        except UnicodeDecodeError:
            issue('SCHEMA', current[0]['id'], 'Current Truth must be UTF-8 Markdown')
    edges = {key: set() for key in objects}
    for ident, f in objects.items():
        for dep in f.get('depends_on', []):
            if dep not in objects:
                issue('UNKNOWN_DEPENDENCY', ident, dep)
            else:
                edges[ident].add(dep)
                if f['status'] == 'ACTIVE' and objects[dep]['status'] != 'ACTIVE':
                    issue('INACTIVE_DEPENDENCY', ident, dep)
    # Kahn-style elimination avoids recursion limits with adversarial inputs.
    remaining = {k: set(v) for k, v in edges.items()}
    while remaining:
        roots = {k for k, v in remaining.items() if not v}
        if not roots:
            issue('DEPENDENCY_CYCLE', 'files', 'File dependencies contain a cycle')
            break
        remaining = {k: v - roots for k, v in remaining.items() if k not in roots}
    seen_checks = set()
    covered_requirements = set()
    for c in checks:
        ident = c.get('id')
        if (not isinstance(ident, str) or not ident or ident in seen_checks
                or not isinstance(c.get('requirement'), str) or not c.get('requirement')
                or not member(c.get('status'), {'PASS', 'FAIL', 'UNVERIFIED'})
                or not strings(c.get('evidence', [])) or not strings(c.get('applies_to', []))):
            issue('SCHEMA', str(ident), 'Invalid acceptance check')
            continue
        seen_checks.add(ident)
        covered_requirements.add(c['requirement'])
        if c['requirement'] not in requirement_ids:
            issue('UNKNOWN_REQUIREMENT', ident, c['requirement'])
        if delivery and c['status'] != 'PASS':
            issue('UNVERIFIED_ACCEPTANCE', ident, 'A declared acceptance check has not passed')
        if c['status'] == 'PASS' and not c.get('evidence'):
            issue('MISSING_EVIDENCE', ident, 'PASS requires a recorded evidence file')
        if c['status'] == 'PASS' and not c.get('applies_to'):
            issue('UNKNOWN_TARGET', ident, 'PASS must name an output it checks')
        for eid in c.get('evidence', []):
            e = objects.get(eid)
            if not e or e['role'] != 'evidence' or e['status'] != 'ACTIVE':
                issue('INACTIVE_EVIDENCE', ident, eid)
            elif c['status'] == 'PASS' and not set(c.get('applies_to', [])).issubset(set(e.get('depends_on', []))):
                issue('EVIDENCE_NOT_BOUND', ident, 'Evidence must depend on the checked output versions')
        for target in c.get('applies_to', []):
            t = objects.get(target)
            if not t or t['status'] != 'ACTIVE' or t['role'] != 'deliverable':
                issue('UNKNOWN_TARGET', ident, target)
    seen_changes = set()
    for c in changes:
        ident = c.get('id')
        if (not isinstance(ident, str) or not ident or ident in seen_changes
                or not strings(c.get('affected')) or not strings(c.get('reviewed'))):
            issue('SCHEMA', str(ident), 'Invalid change record')
            continue
        seen_changes.add(ident)
        if set(c['affected']) - set(c['reviewed']):
            issue('UNRECONCILED_CHANGE', ident, 'Not all declared affected artifacts have been reviewed')
        if (set(c['affected']) | set(c['reviewed'])) - objects.keys():
            issue('UNKNOWN_TARGET', ident, 'Change references an unregistered artifact')
    if delivery:
        if data.get('context_status') != 'CLEAN':
            issue('CONTEXT_NOT_CLEAN', 'receipt', 'Cannot treat unknown/contaminated context as independent')
        for requirement in sorted(requirement_ids - covered_requirements):
            issue('UNCOVERED_REQUIREMENT', requirement, 'Current requirement has no declared acceptance check')
        if not checks:
            issue('NO_ACCEPTANCE_CHECK', 'checks', 'Delivery needs at least one acceptance check')
        if not any(f['role'] == 'deliverable' and f['status'] == 'ACTIVE' for f in objects.values()):
            issue('NO_DELIVERABLE', 'files', 'Delivery needs a real output')
    return {'status': 'PASS' if not issues else 'FAIL', 'issues': issues,
            'files_checked': len(raw_files), 'checks_declared': len(checks),
            'host_isolation_verified': False, 'semantic_correctness_verified': False,
            'agent_behavior_verified': False,
            'limits': 'Declared files only; metadata claims are not independently verified. No sandbox or semantic guarantee.'}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', required=True)
    parser.add_argument('--receipt', default='checks/receipt.json')
    parser.add_argument('--delivery', action='store_true')
    args = parser.parse_args(argv)
    try:
        requested = Path(args.root).expanduser()
        if requested.is_symlink():
            raise ValueError('symlink root not accepted')
        root = requested.resolve(strict=True)
        if not root.is_dir():
            raise ValueError('root must be a directory')
        path = safe_file(root, args.receipt)
        data = json.loads(read_stable(path, 2*1024*1024).decode('utf-8'), object_pairs_hook=no_duplicate_keys)
        result = validate(root, data, args.receipt, args.delivery)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0 if result['status'] == 'PASS' else 1
    except (OSError, ValueError, UnicodeError) as exc:
        print(json.dumps({'status':'ERROR', 'issues':[{'code':'INPUT_ERROR','detail':str(exc)}]},ensure_ascii=False))
        return 2

if __name__ == '__main__':
    sys.exit(main())
