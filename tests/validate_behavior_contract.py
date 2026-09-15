#!/usr/bin/env python3
"""V0.2 行为契约静态检查。

只验证关键规则和模板是否存在，不代表真实宿主一定遵守；真实行为需 WorkBuddy A/B 与 Handoff 测试。
"""
from pathlib import Path
import json
import sys

ROOT = Path(__file__).resolve().parent.parent
SKILL = ROOT / "skills" / "human-ai-collab"

files = {
    "skill": (SKILL / "SKILL.md").read_text(encoding="utf-8"),
    "dialogue": (SKILL / "references/dialogue.md").read_text(encoding="utf-8"),
    "memory": (SKILL / "references/memory.md").read_text(encoding="utf-8"),
    "research": (SKILL / "references/research.md").read_text(encoding="utf-8"),
    "delivery": (SKILL / "references/delivery.md").read_text(encoding="utf-8"),
    "task": (SKILL / "assets/templates/task.md").read_text(encoding="utf-8"),
    "index": (SKILL / "assets/templates/index.md").read_text(encoding="utf-8"),
    "research_tpl": (SKILL / "assets/templates/research.md").read_text(encoding="utf-8"),
    "profile": (SKILL / "assets/templates/profile.md").read_text(encoding="utf-8"),
    "log": (SKILL / "assets/templates/log.md").read_text(encoding="utf-8"),
}

results = []
def check(ok, msg): results.append((bool(ok), msg))

lines = files["skill"].splitlines()
end = next(i for i in range(1, len(lines)) if lines[i].strip() == "---")
desc = next((l.split(":",1)[1].strip() for l in lines[1:end] if l.startswith("description:")), "")
check(desc.startswith("Use when"), "description 以 Use when 开头")
check(len(desc) <= 1024, f"description <= 1024（{len(desc)}）")

for token in ["WORK_ROOT", "ALLOWED_READ_ROOTS", "ALLOWED_WRITE_ROOTS", "EXPLICIT_EXCEPTIONS"]:
    check(token in files["skill"] and token in files["task"], f"Scope 字段: {token}")

check("数据归属优先于路径包含" in files["skill"] or "数据归属优先于路径包含" in files["memory"], "数据归属优先于路径包含")
check("CONTEXT_CONTAMINATED" in files["skill"] and "CONTEXT_CONTAMINATED" in files["memory"], "污染停止规则")
check("DELEGATED_MODE" in files["skill"] and "DELEGATED_MODE" in files["dialogue"], "DELEGATED_MODE")

for token in ["TABLE_STAKES", "BEST_PRACTICES", "AVOID_LIST", "USER_DELTA"]:
    check(token in files["research"] and token in files["research_tpl"], f"产品研究: {token}")

check("Write-through" in files["memory"] and "State Sync" in files["memory"], "Write-through + State Sync")
check(all(x in files["task"] for x in ["R-001", "D-001", "H-001"]), "TASK 含 R/D/H ID")
check("至少存在 1 条" in files["profile"] and "跨任务" in files["profile"], "PROFILE 条件创建")
check("连续失败 2 次" in files["delivery"] or "连续 2 次" in files["delivery"], "Two-Failure Rule")
check(all(x in files["delivery"] for x in ["ACTIVE", "SUPERSEDED", "INVALID"]), "Evidence Lifecycle")
check("Cleanup Gate" in files["delivery"], "Cleanup Gate")
check(all(x in files["log"] for x in ["ACTIVE", "SUPERSEDED", "INVALID", "ROOT_CAUSE_CHECK"]), "LOG 支持证据生命周期与根因检查")

# V0.2 benchmark-hardening additions learned from mature agent/skill projects.
for token in ["PROJECT_ID", "TASK_ID", "RUN_ID"]:
    check(token in files["memory"] and token in files["task"], f"稳定状态身份: {token}")

for token in ["USER_SCOPE", "PROJECT_SCOPE", "TASK_SCOPE", "RUN_SCOPE"]:
    check(token in files["memory"], f"状态作用域分层: {token}")

check("SCOPE_ENFORCEMENT" in files["memory"] and "HARD" in files["memory"] and "SOFT" in files["memory"] and "SCOPE_ENFORCEMENT" in files["task"], "Hard/Soft Scope 区分")
check("STATE_OWNER" in files["memory"] and "STATE_OWNER" in files["task"], "Current Truth 单一写入所有者")
check("多个" in files["memory"] and "TASK_ID" in files["memory"] and ("停止" in files["memory"] or "拒绝" in files["memory"]), "多任务歧义 fail-closed")
check("不回退" in files["memory"] or "不得回退" in files["memory"] or "不能回退" in files["memory"], "显式 Task 绑定失败不回退到兄弟任务")
check("当前状态" in files["memory"] and ("重写" in files["memory"] or "综合" in files["memory"]) and "LOG" in files["memory"], "Current Truth 综合当前状态，历史留 LOG")

for token in ["EVIDENCE_AGAINST", "PROBLEM_STATEMENT", "GOALS", "NON_GOALS"]:
    check(token in files["research"] and token in files["research_tpl"], f"研究反证/问题定义: {token}")
check("confidence" in files["research_tpl"].lower() and ("cited" in files["research_tpl"].lower() or "assumption" in files["research_tpl"].lower()), "研究证据置信度 + cited/assumption")
check("不可信数据" in files["research"] and "指令" in files["research"], "外部/导入资料按不可信数据处理")
check(("2–3" in files["research"] or "2-3" in files["research"]) and "写" in files["research"], "研究小批次 Writeback Gate")
check("REFERENCE_EXAMPLES" in files["research_tpl"], "产品/视觉任务可选参考样例")

# Eval harness: paired baseline/skill prompts and repeatable metadata live in repo.
evals_path = ROOT / "evals" / "evals.json"
check(evals_path.exists(), "标准化 evals/evals.json 存在")
if evals_path.exists():
    try:
        data = json.loads(evals_path.read_text(encoding="utf-8"))
        evals = data.get("evals", [])
        check(len(evals) >= 4, f"至少 4 个行为 eval（实际 {len(evals)}）")
        check(all("prompt" in e and "expected_output" in e for e in evals), "每个 eval 含 prompt + expected_output")
    except Exception as e:
        check(False, f"evals.json 可解析: {e}")

for ok, msg in results:
    print(("PASS  " if ok else "FAIL  ") + msg)
failed = sum(not ok for ok, _ in results)
print(f"总计: {len(results)} 项, 通过 {len(results)-failed}, 失败 {failed}")
if failed:
    sys.exit(1)
print("结果: PASS（仅行为契约静态检查）")
