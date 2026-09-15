#!/usr/bin/env python3
"""human-ai-collab 静态校验脚本（候选版）。

检查范围：
1. SKILL.md 存在且 frontmatter 含 name/description，name 与目录名一致。
2. SKILL.md 引用的 references/ 与 assets/templates/ 文件均存在。
3. THIRD_PARTY_NOTICES.md 与 licenses/ 许可文件齐全。
4. 无宿主绑定残留（hooks / CLAUDE 路径 / 会话扫描 / 自动全局安装等）。
5. 运行包内不含用户资料或测试答案文件。
6. 相对路径一致、无硬编码绝对路径。

本脚本只做静态检查，不代表 Skill 行为有效。行为有效性由独立 A/B 测试判断。
"""
import json
import os
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent  # repo/
SKILL = ROOT / "skills" / "human-ai-collab"

FORBIDDEN = [
    "CLAUDE_PLUGIN_ROOT",
    "CLAUDE_SKILL_DIR",
    "session-catchup",
    "UserPromptSubmit",
    "PreToolUse",
    "PostToolUse",
    "hooks:",
    "-g -y",
    "npx skills add",
    "attest-plan",
    "writing-plans",
    "frontend-design",
    "mcp-builder",
]

# 通用绝对路径模式（用于检测混入的本机路径，不暴露任何具体开发者路径）
ABSOLUTE_PATH_PATTERN = re.compile(
    r"/(Users|home|root|tmp)/[^\s`\"'<>|]*|"
    r"[A-Za-z]:\\[^\s`\"'<>|]*"
)

# 敏感内容模式（密钥 / Token / 密码 / 私钥）
SENSITIVE_PATTERN = re.compile(
    r"(?i)(api[_-]?key\s*[:=]|secret\s*[:=]|password\s*[:=]|passwd\s*[:=]|"
    r"bearer\s+[A-Za-z0-9._-]{20,}|-----BEGIN (RSA|OPENSSH|EC|DSA) PRIVATE KEY-----)"
)

# 缓存 / 临时文件特征
CACHE_MARKERS = (".DS_Store", "__pycache__", ".pyc", ".pytest_cache")

REQUIRED_REFERENCES = [
    "references/dialogue.md",
    "references/memory.md",
    "references/research.md",
    "references/delivery.md",
]

REQUIRED_TEMPLATES = [
    "assets/templates/index.md",
    "assets/templates/profile.md",
    "assets/templates/task.md",
    "assets/templates/research.md",
    "assets/templates/log.md",
]

REQUIRED_LICENSES = [
    "licenses/superpowers-MIT.txt",
    "licenses/planning-with-files-MIT.txt",
    "licenses/vercel-skills-MIT.txt",
    "licenses/skill-creator-Apache-2.0.txt",
]

results = []


def check(ok, msg):
    results.append((ok, msg))


# 1. 目录与 SKILL.md
if not SKILL.is_dir():
    check(False, f"Skill 目录不存在: {SKILL}")
    print("FAIL: 无法继续")
    sys.exit(1)

skill_md = SKILL / "SKILL.md"
if not skill_md.exists():
    check(False, "SKILL.md 不存在")
else:
    check(True, "SKILL.md 存在")
    text = skill_md.read_text(encoding="utf-8")
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        check(False, "SKILL.md 缺少 frontmatter 起始 ---")
    else:
        check(True, "frontmatter 起始符存在")
        # 提取 frontmatter
        end = None
        for i in range(1, len(lines)):
            if lines[i].strip() == "---":
                end = i
                break
        if end is None:
            check(False, "frontmatter 未闭合")
            fm = ""
        else:
            fm = "\n".join(lines[1:end])
            check(True, "frontmatter 闭合")
        has_name = "name:" in fm
        has_desc = "description:" in fm
        check(has_name, "frontmatter 含 name")
        check(has_desc, "frontmatter 含 description")
        name_val = ""
        for l in fm.splitlines():
            if l.startswith("name:"):
                name_val = l.split(":", 1)[1].strip()
        check(name_val == "human-ai-collab",
              f"name 与目录一致 (name={name_val!r}, dir=human-ai-collab)")

# 2. 引用文件存在
for ref in REQUIRED_REFERENCES:
    p = SKILL / ref
    check(p.exists(), f"引用文件存在: {ref}")

for tpl in REQUIRED_TEMPLATES:
    p = SKILL / tpl
    check(p.exists(), f"模板文件存在: {tpl}")


def exact_exists(rel_path):
    """精确存在性检查（逐级区分大小写，避免 macOS 大小写不敏感 FS 掩盖断链）。"""
    cur = SKILL
    for part in rel_path.split("/"):
        if part not in os.listdir(cur):
            return False
        cur = cur / part
    return cur.is_file()


# 2b. 动态解析 SKILL.md 与 references 中的相对 .md 引用，验证逐一存在且大小写精确
md_sources = [skill_md] + [p for p in (SKILL / "references").glob("*.md")]
ref_set = set()
for p in md_sources:
    content = p.read_text(encoding="utf-8", errors="replace")
    for m in re.findall(r"`((?:references|assets/templates)/[A-Za-z0-9_-]+\.md)`", content):
        ref_set.add(m)
broken = [r for r in sorted(ref_set) if not exact_exists(r)]
if broken:
    check(False, "断链或大小写不一致的引用: " + "; ".join(broken))
else:
    check(True, f"SKILL.md/references 引用的 .md 路径均存在且大小写精确（{len(ref_set)} 条）")

# 3. THIRD_PARTY_NOTICES 与许可
check((SKILL / "THIRD_PARTY_NOTICES.md").exists(), "THIRD_PARTY_NOTICES.md 存在")
for lic in REQUIRED_LICENSES:
    p = SKILL / lic
    check(p.exists(), f"许可文件存在: {lic}")

# 4. 禁用内容扫描（仅 .md）
all_md = [p for p in SKILL.rglob("*.md")]
forbidden_hits = []
for p in all_md:
    content = p.read_text(encoding="utf-8", errors="replace")
    for w in FORBIDDEN:
        if w in content:
            forbidden_hits.append(f"{p.relative_to(SKILL)}: {w}")
if forbidden_hits:
    check(False, "发现宿主绑定/上游残留: " + "; ".join(forbidden_hits))
else:
    check(True, "无宿主绑定或上游路由残留")

# 5. 运行包不含用户资料/测试答案（检查是否有 02/03 文件或超大个人档案混入）
suspicious = []
for p in SKILL.rglob("*"):
    if p.is_file():
        name = p.name.lower()
        if "profile" in name and "templates" not in str(p.relative_to(SKILL)):
            suspicious.append(str(p.relative_to(SKILL)))
if suspicious:
    check(False, "疑似用户资料混入: " + "; ".join(suspicious))
else:
    check(True, "运行包内无用户真实资料文件")

# 5b. 全仓库清洁度：绝对路径 / 敏感内容 / 缓存文件 / 02-03 测试文件
TEXT_SUFFIXES = (".md", ".json", ".py", ".txt")
abs_hits, sen_hits, cache_hits, test_hits = [], [], [], []
for p in sorted(ROOT.rglob("*")):
    if not p.is_file():
        continue
    rel = str(p.relative_to(ROOT))
    # 缓存 / 临时文件
    if any(m in rel for m in CACHE_MARKERS):
        cache_hits.append(rel)
        continue
    # 02 / 03 测试文件特征（按文件名或内容关键词）
    if re.search(r"02_|03_|独立双会话测试|双会话共同任务|测试与审计", rel):
        test_hits.append(rel)
        continue
    if p.suffix in TEXT_SUFFIXES:
        content = p.read_text(encoding="utf-8", errors="replace")
        if ABSOLUTE_PATH_PATTERN.search(content):
            abs_hits.append(rel)
        if SENSITIVE_PATTERN.search(content):
            sen_hits.append(rel)

check(not abs_hits, "全仓库无本机绝对路径" if not abs_hits else "发现本机绝对路径: " + "; ".join(abs_hits))
check(not sen_hits, "全仓库无密钥/Token/密码" if not sen_hits else "发现敏感内容: " + "; ".join(sen_hits))
check(not cache_hits, "全仓库无缓存/临时文件" if not cache_hits else "发现缓存/临时文件: " + "; ".join(cache_hits))
check(not test_hits, "全仓库无 02/03 测试文件" if not test_hits else "发现测试文件: " + "; ".join(test_hits))

# 6. provenance 存在
for pr in ["provenance/REUSE_MAP.md", "provenance/sources.lock.json"]:
    check((ROOT / pr).exists(), f"provenance 存在: {pr}")

# 7. sources.lock.json 可解析
lock_path = ROOT / "provenance" / "sources.lock.json"
if lock_path.exists():
    try:
        data = json.loads(lock_path.read_text(encoding="utf-8"))
        n = len(data.get("sources", []))
        check(n == 4, f"sources.lock.json 含 4 个来源 (实际 {n})")
    except Exception as e:  # noqa: BLE001
        check(False, f"sources.lock.json 解析失败: {e}")

# 汇总
print("=" * 60)
passed = sum(1 for ok, _ in results if ok)
failed = sum(1 for ok, _ in results if not ok)
for ok, msg in results:
    print(("PASS  " if ok else "FAIL  ") + msg)
print("=" * 60)
print(f"总计: {len(results)} 项, 通过 {passed}, 失败 {failed}")
if failed:
    print("结果: FAIL")
    sys.exit(1)
print("结果: PASS（仅静态检查，不代表行为有效）")
