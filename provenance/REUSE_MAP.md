# REUSE_MAP —— 取材去向与改动

本文件记录：每个来源仓库、commit、原文件、所取范围、原文件 SHA-256、新文件、复制/改写/仅借鉴、删了什么、为什么删、验证方法。

## 读取的真实文件与 SHA-256

| 来源 | 文件 | SHA-256 |
|------|------|---------|
| U1 superpowers | `skills/brainstorming/SKILL.md` | `74edf03ea6d24ef53db48677b93558d14a979bdf052ca3f57ecdca0c66791608` |
| U1 superpowers | `skills/verification-before-completion/SKILL.md` | `2befe7fc55bcadaa3d97dd9e8efeb633d2561c0ebe74c5a8b17c4d9e7e4520b3` |
| U2 planning-with-files | `skills/planning-with-files/SKILL.md` | `04d1390b030ae4c7c8f4f7affe498617a25cd10f4e90ff9b2ac6cceff3a1b48a` |
| U2 planning-with-files | `skills/planning-with-files/templates/task_plan.md` | `3c4b61444270f689c3dab81b7113467fb87e9705175aea9c3a3b970bd4e777a3` |
| U2 planning-with-files | `skills/planning-with-files/templates/findings.md` | `bb9237ccbf08148d7f7f23ad58fbc9bd7c879c6d0cbca1d533b5b5f21c26c529` |
| U2 planning-with-files | `skills/planning-with-files/templates/progress.md` | `28fc357000ed2b18910c4e436f0f2e02f4abf0acd29cce370a2670640974f31c` |
| U3 vercel-skills | `skills/find-skills/SKILL.md` | `c00eeea0e13e74fe4a9d84ba0a8542205a1b736d65f13134fe1a6647eb14976f` |
| U4 anthropic-skills | `skills/skill-creator/SKILL.md` | `dcd4803e61e913e6fc27294184cd3a71f09f5e924ff20c8a9a20173e7b3c2bcf` |
| U4 anthropic-skills | `skills/skill-creator/agents/grader.md` | `57134da0c1a4eea33fbd74a1c9c44aa814f07d6bc64de303edb586f941e5d21a` |
| U4 anthropic-skills | `skills/skill-creator/agents/comparator.md` | `fe1fc9787c495d864c5d6eada47396478572325fde1b33a96d78bf4b849b7a3e` |
| U4 anthropic-skills | `skills/skill-creator/agents/analyzer.md` | `bf68f4cac5a56c673a928c2e6d619586c5b93ea364026ab37547772cb45a663a` |

## 逐项取材

### E01：dialogue.md ← brainstorming

- 来源：U1 `skills/brainstorming/SKILL.md`
- 所取范围：三路径（spike/bounded/architectural）分级思路、"一次只问一个关键问题""提出 2–3 备选带推荐""获批再动手""简单不等于免审"、Red Flags 反模式表、方案自检四步。
- 新文件：`references/dialogue.md`
- 处理方式：**改写**（去代码特化，泛化到通用任务）
- 删掉：固定开发术语（writing-plans / frontend-design / mcp-builder 等上游路由）、"每个任务都要完整规划"、`docs/superpowers/specs/` 路径、Visual Companion 浏览器伴侣机制。
- 为什么删：上游是面向特定 Agent 产品链的；本 Skill 不做开发术语绑定，也不强制浏览器伴侣。
- 验证方法：对照原文逐段核对，确认没有遗留上游路由名或强制完整规划措辞。

### E02：delivery.md ← verification-before-completion

- 来源：U1 `skills/verification-before-completion/SKILL.md`
- 所取范围：证据先于声称的"门（gate）"五步、常见声称与所需证据表、危险信号、红-绿回归、需求逐条对照。
- 新文件：`references/delivery.md`
- 处理方式：**改写**
- 删掉：只适用于某具体仓库的测试命令、没有环境也强行跑命令。
- 为什么删：本 Skill 需跨平台、不绑定具体仓库。
- 验证方法：确认新文件不包含任何具体测试命令；保留"没有环境就交付执行资料"的降级路径。

### E03：memory.md ← planning-with-files 主 SKILL.md

- 来源：U2 `skills/planning-with-files/SKILL.md`
- 所取范围：Restore Project State、Where Files Go、File Purposes、Read Before Decide、重要发现/错误落盘、方法与用户数据分离、五问重启。
- 新文件：`references/memory.md`
- 处理方式：**改写**
- 删掉：整个 YAML hooks（UserPromptSubmit/PreToolUse/PostToolUse/Stop/PreCompact）、`CLAUDE_*` 路径、session-catchup 会话存储扫描、强制 2-action 计数、自动停止钩子、gated/autonomous 模式、attestation 机制、parallel-plan 脚本。
- 为什么删：这些是宿主绑定的自动化机制，本 Skill 首版明确不做自动恢复；靠显式文件读取+增量写入。
- 验证方法：新文件无 `hook`、`CLAUDE`、`session-catchup`、`attest`、`.planning` 等字样。

### E04：task.md ← task_plan.md

- 来源：U2 `templates/task_plan.md`
- 所取范围：目标、阶段、决定、下一步、错误记录的结构。
- 新文件：`assets/templates/task.md`
- 处理方式：**改写**（字段改为：目标/范围/需求/决定/待验证/缺口/验收/下一步/变更）
- 删掉：固定的 Phase 1–5 阶段、`pending/in_progress/complete` 强制状态枚举、与日志重复的当前决定。
- 为什么删：不要求所有任务固定相同阶段数；决定只放一处（TASK），日志只作证据。
- 验证方法：模板字段与本说明第 5 节一致；不含强制阶段枚举。

### E05：research.md ← findings.md

- 来源：U2 `templates/findings.md`
- 所取范围：来源/证据/结论/限制/核验日期的结构化记录。
- 新文件：`assets/templates/research.md`
- 处理方式：**改写**
- 删掉："Visual/Browser Findings" 强制小节、把作者推广数字当证据。
- 为什么删：不做无条件浏览器采集；不虚构发现。
- 验证方法：模板只含来源、证据、结论、限制、核验日期字段。

### E06：log.md ← progress.md

- 来源：U2 `templates/progress.md`
- 所取范围：实际动作、产物、检查、错误、恢复点的时序记录。
- 新文件：`assets/templates/log.md`
- 处理方式：**改写**
- 删掉："Test Results" 强制的测试表格式、"5-Question Reboot" 内嵌表（移到 memory.md 作为接续方法）、固定 Session/Phase 结构。
- 为什么删：不强制每项任务都产测试表；恢复检查归口到 memory。
- 验证方法：模板字段聚焦动作/产物/检查/错误/恢复点。

### E07：research.md（行为规则）← find-skills

- 来源：U3 `skills/find-skills/SKILL.md`
- 所取范围：按任务缺口搜索、核对来源与适配性、列出最少候选、搜索/推荐/安装分阶段。
- 新文件：`references/research.md`
- 处理方式：**改写**
- 删掉：无条件搜索、`npx skills add <owner/repo@skill> -g -y` 全局免确认安装、以 leaderboard 安装量/Star 当安全许可、运行期自动更新全部技能、skills.sh 专属 CLI。
- 为什么删：首版默认限定项目范围、需用户批准后安装；热度≠安全。
- 验证方法：新文件无 `-g -y`、无 `npx skills` 全局安装命令、明确"搜索/推荐/安装三阶段"。

### E08：skill-creator → 仅来源记录（完整副本已从分发仓库移除）

- 来源：U4 `skills/skill-creator/`
- 所取范围：作为开发/评估方法的来源记录；借鉴其"逐项评分（grader）""盲测比较（comparator）""归因分析（analyzer）"作为后续独立测试的方法参考。
- 处理方式：**仅来源记录**。原完整副本已确认 `tests/` 与运行 Skill 均不依赖后，从分发仓库移除。
- 删掉：未进入运行入口；后续评估须允许平局/负收益/证据不足，不强迫分胜负。
- 为什么：skill-creator 是制作/测试工具，不是参与者日常使用的一层；分发仓库不携带其完整副本以减少体积。
- 记录保留：commit、文件 SHA-256、许可全文仍保留于 `sources.lock.json`、本文件与 `licenses/skill-creator-Apache-2.0.txt`。

## 许可复核说明

- U1/U2/U3 为 MIT，U4 skill-creator 为 Apache-2.0。许可全文分别保留于 `provenance/licenses/` 与 `skills/human-ai-collab/licenses/`。
- 新 Skill 自身内容为改写重组，非原样复制；第三方版权声明见 `THIRD_PARTY_NOTICES.md`。
- 新项目自身许可采用 MIT，Copyright (c) 2026 Heyi（`LICENSE`）；不把第三方代码标成"独立原创"。
