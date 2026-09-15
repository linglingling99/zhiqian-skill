#!/usr/bin/env python3
"""Validate constructed fixtures. This does not run or grade independent LLMs."""
from pathlib import Path, PurePosixPath
import importlib.util
import json
import shutil
import sys
import tempfile
import zipfile

sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('checker',ROOT/'skills/human-ai-collab/scripts/check_workspace.py')
checker=importlib.util.module_from_spec(spec);spec.loader.exec_module(checker)
checks=[]
def check(ok,label):
    checks.append((bool(ok),label))
    print(('PASS ' if ok else 'FAIL ')+label)
with tempfile.TemporaryDirectory() as tmp:
    target=Path(tmp)
    with zipfile.ZipFile(ROOT/'evals/fixtures/v0.3-hypothetical.zip') as z:
        for info in z.infolist():
            name=PurePosixPath(info.filename)
            if name.is_absolute() or '..' in name.parts or info.file_size>2*1024*1024:
                raise ValueError('Unsafe synthetic fixture archive')
            if info.is_dir():continue
            p=target/name; p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(z.read(info))
    common=json.loads((target/'COMMON_INPUT.json').read_text(encoding='utf-8'))
    check(common['kind']=='AUTHOR_CONSTRUCTED_HYPOTHETICAL_CASE','fixture provenance is explicitly hypothetical')
    for arm in ['A_baseline','B_skill']:
        rule=json.loads((target/arm/'业务规则.json').read_text(encoding='utf-8'))
        for label,ok in [('single operator',rule['operators']==1),('local',rule['storage']=='local'),
                         ('no accounts',rule['accounts'] is False),('no sending',rule['auto_send'] is False),
                         ('partial returns',rule['partial_return'] is True),('backup',rule['backup_required'] is True),
                         ('duplicate checkout denied',rule['duplicate_checkout']=='reject'),
                         ('duplicate return denied',rule['duplicate_return']=='reject')]:
            check(ok,arm+': '+label)
        data=json.loads((target/'data'/arm/'result.json').read_text(encoding='utf-8'))
        check(data['A']['known_total']==5 and data['A']['incomplete'] is True,arm+': incomplete total is not exact')
        check(data['B']['known_total'] is None,arm+': missing value is not zero')
        check(len(list((target/'simple'/arm).iterdir()))==1,arm+': simple task does not acquire paperwork')
    b=target/'B_skill'; receipt=json.loads((b/'checks/receipt.json').read_text(encoding='utf-8'))
    result=checker.validate(b,receipt,'checks/receipt.json',True)
    check(result['status']=='PASS','constructed Skill workspace is mechanically coherent')
    check(result['semantic_correctness_verified'] is False,'mechanical pass is not semantic verification')
    check(result['agent_behavior_verified'] is False,'no independent AI behavior claim')
    (b/'业务规则.json').write_text('{"changed":true}',encoding='utf-8')
    bad=checker.validate(b,receipt,'checks/receipt.json',True)
    check(any(i['code']=='HASH_MISMATCH' for i in bad['issues']),'real mutation is detected without changing the archived fixture')
print(f'FIXTURE_CHECKS_ONLY: {sum(ok for ok,_ in checks)}/{len(checks)}')
sys.exit(0 if all(ok for ok,_ in checks) else 1)
