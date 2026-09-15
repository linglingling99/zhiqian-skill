"""Real executable tests, not LLM behavior tests. Synthetic fixtures only."""
import copy
import contextlib
import importlib.util
import io
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / 'skills/human-ai-collab/scripts/check_workspace.py'
sys.dont_write_bytecode = True
MODULE = None
if SCRIPT.exists():
    spec = importlib.util.spec_from_file_location('hac_workspace_checker', SCRIPT)
    MODULE = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(MODULE)

class WorkspaceCheckTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.root=Path(self.tmp.name)/'task'; self.root.mkdir()
        (self.root/'checks').mkdir(); (self.root/'outputs').mkdir()
        texts={'TASK.md':'TASK_ID: demo\nREVISION: 2\n# 当前任务\nR-001: 清晰方案\n',
               'outputs/方案.md':'手机网页；本地使用，不自动外发。',
               'checks/review.txt':'检查当前方案包含本地保存和不外发；人工/模型内容审查仍需单独进行。'}
        for p,t in texts.items(): (self.root/p).write_text(t,encoding='utf-8')
        self.receipt={'schema_version':'0.3','task_id':'demo','revision':2,'scope_enforcement':'SOFT','context_status':'CLEAN',
          'files':[], 'checks':[{'id':'V-001','requirement':'R-001','status':'PASS','evidence':['A-003'],'applies_to':['A-002']}],
          'changes':[{'id':'C-001','affected':['A-001','A-002'],'reviewed':['A-001','A-002']}]}
        for i,(p,role) in enumerate([('TASK.md','current'),('outputs/方案.md','deliverable'),('checks/review.txt','evidence')],1):
            self.receipt['files'].append({'id':f'A-{i:03d}','path':p,'role':role,'status':'ACTIVE',
                'sha256':hashlib.sha256((self.root/p).read_bytes()).hexdigest(), 'reviewed_revision':2,
                'depends_on':[] if i==1 else ['A-001'] if i==2 else ['A-002']})
    def tearDown(self): self.tmp.cleanup()
    def run_check(self, delivery=True):
        self.assertTrue(SCRIPT.is_file(), 'workspace checker must exist')
        p=self.root/'checks/receipt.json'; p.write_text(json.dumps(self.receipt,ensure_ascii=False),encoding='utf-8')
        argv=['--root',str(self.root),'--receipt','checks/receipt.json']
        if delivery: argv+=['--delivery']
        # Exercise the real entry point in-process; subprocess startup is slow in some hosts.
        out=io.StringIO()
        with contextlib.redirect_stdout(out): rc=MODULE.main(argv)
        self.assertIn(rc,(0,1,2))
        return rc,json.loads(out.getvalue())
    def reject(self,code):
        rc,d=self.run_check(); self.assertNotEqual(rc,0); self.assertIn(code,[e['code'] for e in d['issues']],d)
    def test_unhashable_enum_fields(self):
        original=copy.deepcopy(self.receipt)
        for parent,key in [('root','scope_enforcement'),('root','context_status'),('file','role'),('file','status'),('check','status')]:
            with self.subTest(parent=parent,key=key):
                self.receipt=copy.deepcopy(original)
                target=self.receipt if parent=='root' else self.receipt['files'][1] if parent=='file' else self.receipt['checks'][0]
                target[key]=[]
                self.reject('SCHEMA')
    def test_valid_receipt(self): self.assertEqual(self.run_check()[0],0)
    def test_cli_valid(self):
        self.run_check()
        proc=subprocess.run([sys.executable,str(SCRIPT),'--root',str(self.root),'--delivery'],capture_output=True,text=True,timeout=10)
        self.assertEqual(proc.returncode,0,proc.stdout+proc.stderr)
    def test_read_only(self):
        before={str(p.relative_to(self.root)):p.read_bytes() for p in self.root.rglob('*') if p.is_file()}
        self.run_check()
        for p,b in before.items(): self.assertEqual((self.root/p).read_bytes(),b)
    def test_missing_file(self): (self.root/'outputs/方案.md').unlink(); self.reject('MISSING_FILE')
    def test_hash_mismatch(self): (self.root/'outputs/方案.md').write_text('被改动',encoding='utf-8'); self.reject('HASH_MISMATCH')
    def test_old_revision(self): self.receipt['files'][1]['reviewed_revision']=1; self.reject('STALE_REVISION')
    def test_revision_bool(self): self.receipt['revision']=True; self.reject('SCHEMA')
    def test_path_escape(self): self.receipt['files'][1]['path']='../other.txt'; self.reject('UNSAFE_PATH')
    def test_absolute_path(self): self.receipt['files'][1]['path']=str(self.root/'outputs/方案.md'); self.reject('UNSAFE_PATH')
    def test_windows_path(self): self.receipt['files'][1]['path']='C:\\outside\\file.md'; self.reject('UNSAFE_PATH')
    def test_backslash_path(self): self.receipt['files'][1]['path']='outputs\\方案.md'; self.reject('UNSAFE_PATH')
    def test_symlink_file(self):
        p=self.root/'outputs/方案.md'; p.unlink()
        outside=Path(self.tmp.name)/'foreign.txt'; outside.write_text('should never read',encoding='utf-8')
        try:p.symlink_to(outside)
        except OSError:self.skipTest('symlink privilege not available')
        self.reject('UNSAFE_PATH')
    def test_symlink_directory(self):
        self.receipt['files'][1]['path']='link/foreign.md'
        outside=Path(self.tmp.name)/'foreign'; outside.mkdir(); (outside/'foreign.md').write_text('foreign',encoding='utf-8')
        try:(self.root/'link').symlink_to(outside,target_is_directory=True)
        except OSError:self.skipTest('symlink privilege not available')
        self.reject('UNSAFE_PATH')
    def test_duplicate_id(self): self.receipt['files'][1]['id']='A-001'; self.reject('DUPLICATE_ID')
    def test_duplicate_path(self): self.receipt['files'][1]['path']='TASK.md'; self.reject('DUPLICATE_PATH')
    def test_unknown_dependency(self): self.receipt['files'][1]['depends_on']=['A-999']; self.reject('UNKNOWN_DEPENDENCY')
    def test_cycle(self): self.receipt['files'][0]['depends_on']=['A-002']; self.reject('DEPENDENCY_CYCLE')
    def test_superseded_evidence(self): self.receipt['files'][2]['status']='SUPERSEDED'; self.reject('INACTIVE_EVIDENCE')
    def test_incomplete_change(self): self.receipt['changes'][0]['reviewed']=['A-001']; self.reject('UNRECONCILED_CHANGE')
    def test_contaminated(self): self.receipt['context_status']='CONTAMINATED'; self.reject('CONTEXT_NOT_CLEAN')
    def test_unknown_context(self): self.receipt['context_status']='UNKNOWN'; self.reject('CONTEXT_NOT_CLEAN')
    def test_no_checks(self): self.receipt['checks']=[]; self.reject('NO_ACCEPTANCE_CHECK')
    def test_unverified_not_pass(self): self.receipt['checks'][0]['status']='UNVERIFIED'; self.reject('UNVERIFIED_ACCEPTANCE')
    def test_check_needs_evidence(self): self.receipt['checks'][0]['evidence']=[]; self.reject('MISSING_EVIDENCE')
    def test_wrong_task(self): self.receipt['task_id']='other'; self.reject('TASK_BINDING_MISMATCH')
    def test_task_revision_mismatch(self): self.receipt['revision']=3; self.reject('TASK_BINDING_MISMATCH')
    def test_no_current_state(self): self.receipt['files'][0]['role']='log'; self.reject('CURRENT_STATE_COUNT')
    def test_empty_files(self): self.receipt['files']=[]; self.reject('CURRENT_STATE_COUNT')
    def test_invalid_hash(self): self.receipt['files'][1]['sha256']='notahash'; self.reject('SCHEMA')
    def test_receipt_self_reference(self): self.receipt['files'][1]['path']='checks/receipt.json'; self.reject('SELF_REFERENCE')
    def test_foreign_target(self): self.receipt['checks'][0]['applies_to']=['A-999']; self.reject('UNKNOWN_TARGET')
    def test_required_status(self): del self.receipt['files'][1]['status']; self.reject('SCHEMA')
    def test_no_hard_claim(self):
        self.receipt['scope_enforcement']='HARD'; rc,d=self.run_check(); self.assertEqual(rc,0)
        self.assertFalse(d['host_isolation_verified']); self.assertFalse(d['semantic_correctness_verified'])
    def test_no_research_required(self): self.assertEqual(self.run_check()[0],0)
    def test_preview_can_be_incomplete(self):
        self.receipt['checks'][0]['status']='UNVERIFIED'; self.assertEqual(self.run_check(delivery=False)[0],0)
    def test_wrong_case_path(self): self.receipt['files'][0]['path']='task.md'; self.reject('MISSING_FILE')
    def test_unknown_requirement(self):
        self.receipt['checks'][0]['requirement']='R-999'; self.reject('UNKNOWN_REQUIREMENT')
    def test_uncovered_requirement(self):
        path=self.root/'TASK.md'; path.write_text(path.read_text()+'R-002: 数据导出\n',encoding='utf-8')
        self.receipt['files'][0]['sha256']=hashlib.sha256(path.read_bytes()).hexdigest()
        self.reject('UNCOVERED_REQUIREMENT')
    def test_evidence_not_bound(self):
        self.receipt['files'][2]['depends_on']=[]; self.reject('EVIDENCE_NOT_BOUND')
    def test_rehashed_semantic_error_is_not_verified(self):
        path=self.root/'outputs/方案.md'; path.write_text('自动发送资料到云端（与需求矛盾）',encoding='utf-8')
        self.receipt['files'][1]['sha256']=hashlib.sha256(path.read_bytes()).hexdigest()
        rc,result=self.run_check()
        self.assertEqual(rc,0) # Deliberately documents the mechanical checker's limit.
        self.assertFalse(result['semantic_correctness_verified'])
    def test_bad_json(self):
        self.assertTrue(SCRIPT.is_file()); (self.root/'checks/receipt.json').write_text('{',encoding='utf-8')
        p=subprocess.run([sys.executable,str(SCRIPT),'--root',str(self.root),'--receipt','checks/receipt.json'],capture_output=True,text=True)
        self.assertEqual(p.returncode,2); self.assertIn('INPUT_ERROR',p.stdout)

if __name__=='__main__': unittest.main()
