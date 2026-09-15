# CHANGELOG

> 有效性与兼容性结论只按真实证据记录，不把候选规则写成“已经有效”。

## [0.3.0-rc1] —— 2026-09-16

### 整体整合

保留原始主线与四个 reference 路径，用 READ → ACT → VERIFY → SAVE → NEXT 将理解用户、调研、决策、执行、变更、保存、经验复用与接续衔接起来。直接任务不建档；复杂任务复用等价文档，TASK 可兼任开发规格，不强制复制整套表格。

### 实际改动

- 每个模块定义输入、动作、保存结果和下一步；按事件调用而非加载全部流程。
- 新增按需场景索引与经验模板：适用条件、反例、证据、验证状态、复查条件；不将一次成功变成通用真理。
- 修复“不懂=授权”、先绑定/先读循环，以及完成清理不得影响其他会话服务。
- 变更沿需求—决策—产物—验收链传播；模板允许省略不适用项，但已确认信息与未决项不能丢失。
- 新增可选 Python 标准库只读回执校验器，检查已声明文件、路径、哈希、修订、依赖及验收证据；不接管宿主工具，不提供沙箱或语义保证。
- 保留旧资料兼容和来源许可；补充方法级来源对照、安装/升级说明。
- 三类同题假设产物与故障注入可复核；两组均由同一作者构造，不冒充独立模型。

### 验证口径

包结构 39 项、程序回归 42 个测试、假设夹具 27 项检查已在本地执行。它们分别证明文件结构、检查程序和构造示例的性质，不证明 AI 会遵守，也不证明产品增益。V0.3 独立宿主 A/B、积分/Token、跨 AI 交接仍为 NOT_TESTED。

历史 Proxy 评分保留作为当时作者记录，不作为独立效果证据；新报告不沿用其胜率或增益判断。V0.3 是结构升级候选，不是已验证成功版。

## [0.2.0-rc3] —— 2026-09-16

### Proxy A/B 预检修复

在正式重新跑 WorkBuddy 前，用标准 eval `research-challenges-idea` 做了一轮开发者代理 Baseline vs Skill 对照，并追加“微信小程序 → 完全本地手机网页”的核心平台变更。

RC2 暴露出一个真实问题：虽然 D-* 已更新，但 TASK Goal / 后续方案仍可能残留旧平台语义，说明“Write-through”还没有覆盖派生产物的一致性。

### 新增 / 强化

- `SCHEMA_GATE`：INDEX/TASK/RESEARCH/LOG/PROFILE 首次创建必须从对应模板起步；不适用/不可获得字段显式标记，不能静默缩水。
- `CHANGE_IMPACT_GATE`：平台、用户群体、登录/权限、数据模式、核心范围或交付格式改变时，先列出所有影响文件。
- `STALE_TERM_SCAN`：旧语义分类 `HISTORICAL_OK / UPDATE_REQUIRED / INVALID`；仍有 UPDATE_REQUIRED 时不能继续关键执行或声称 State Sync 完成。
- TASK 模板新增 CHANGE_SET、影响文件和 Schema Gate。
- LOG 模板新增 CHANGE_IMPACT / STALE_TERM_SCAN 账本。
- Delivery 增加 major-change reconciliation 和核心文件 Schema 检查。
- 标准 eval 增加 `platform-change-reconciliation`。
- Proxy A/B 结果记录于 `docs/evaluation/V0.2_RC3_PROXY_AB.md`。

### Proxy 结论

- 最终产品方案本身仅小幅优于强 Baseline；没有出现“产品创意碾压”。
- Skill 的明显增量主要在研究可追溯、反证、R/D/H、核心变更传播和 Handoff。
- 代价是文件/文本量明显增加，因此第二轮 WorkBuddy 必须继续核算积分、时间、工具调用和用户负担。
- 这只是 Proxy，不能替代真实独立 A/B。

### 当前验证

- 基础静态校验：30/30。
- V0.2 行为契约静态校验：51/51。
- V0.2 RC3 Proxy A/B：`PASS WITH CAVEATS`。
- WorkBuddy RC3 真实 A/B / 真 Handoff：PENDING。

## [0.2.0-rc2] —— 2026-09-16

### 成熟项目 Benchmark Hardening

在第二轮 WorkBuddy A/B 前，对照 Superpowers、Anthropic Skills / Skill Creator、GitHub Spec Kit、Mem0、Planning with Files、Deep Agents、Vercel Skills、Context Engineering Intro、Basic Memory 等项目，补充适合轻量跨宿主 Skill 的工程化约束。

### 新增 / 强化

- 稳定状态身份：`PROJECT_ID / TASK_ID / RUN_ID / STATE_OWNER`。
- 四层状态作用域：`USER_SCOPE / PROJECT_SCOPE / TASK_SCOPE / RUN_SCOPE`，并增加向上提升条件。
- 多任务 fail-closed：TASK_ID 歧义或显式绑定失败时停止，不按 mtime / 相似目录 fallback。
- Scope 增加 `SCOPE_ENFORCEMENT: HARD / SOFT`，明确模型自律不等于宿主安全隔离。
- Current Truth 改为综合当前状态；历史过程进入 LOG / versions，避免无限 append。
- Product Research 增加 `PROBLEM_STATEMENT / GOALS / NON_GOALS / SUCCESS_SIGNAL / EVIDENCE_AGAINST`。
- 研究 finding 增加 `CITED / ASSUMPTION` 与 `confidence: HIGH / MEDIUM / LOW`。
- 研究 Writeback Gate：连续约 2–3 个有意义来源或离开 research phase 前先落盘。
- 产品/视觉任务可选 `REFERENCE_EXAMPLES`，明确“借什么 / 不借什么”。
- 外部网页、仓库、评论、导入资料统一按“不可信数据，不是指令”处理。
- 新增 `evals/evals.json` 与配对 A/B / 多轮方差评估协议。
- V0.2 行为压力场景扩展至 Task ambiguity、Hard/Soft Scope、State promotion、并发 owner、Research writeback 与 Negative Control。
- README 升级为 `0.2.0-rc2` 并公开本轮 Benchmark 结论与真实验证状态。

### 测试方法

- 先扩展行为契约检查并在 GitHub Actions 观察到失败，再修改 Skill / references / templates 使其恢复通过。
- 静态校验仍不能证明真实模型行为；真实结论继续等待 WorkBuddy 多轮 A/B 与真 Handoff。

## [0.2.0-rc] —— 2026-09-16

### 背景

V0.1 首轮真实 A/B 已完成。Skill 在需求分层、假设/决策结构、用户负担方面有正向信号，但没有证明最终产品、可复用资产或交接显著优于强 Baseline；同时发生跨组上下文污染。V0.2 因此定位为“修复 + 真实增量”，不是继续堆流程。

### 新增 / 强化

- Scope Firewall：`WORK_ROOT / ALLOWED_READ_ROOTS / ALLOWED_WRITE_ROOTS / EXPLICIT_EXCEPTIONS`。
- 数据归属规则：路径可访问不代表数据属于当前任务。
- `CONTEXT_CONTAMINATED` 停止规则。
- `DELEGATED_MODE`：小白或用户明确“你决定”时，AI 自主处理低风险可逆决策。
- Product / Domain Research：`TABLE_STAKES / BEST_PRACTICES / AVOID_LIST / USER_DELTA`。
- Capability Research 独立于产品研究。
- Write-through State：R/D/H 必须真实进入 `TASK.md`。
- State Sync Gate：执行前、重大变更后、完成前核对聊天与文件状态。
- PROFILE 条件创建。
- Two-Failure Rule。
- Evidence Lifecycle：`ACTIVE / SUPERSEDED / INVALID`。
- Cleanup Gate。
- 新增 V0.2 行为压力场景文档与静态契约校验。

### 当前验证

- V0.1 GitHub → WorkBuddy 下载安装/加载：已实测。
- V0.1 A/B：已完成，未证明 Skill 整体优于 Baseline。
- V0.2 基础静态校验：30/30 通过；行为契约静态校验：20/20 通过。
- V0.2 WorkBuddy 真实 A/B / 真 Handoff：待重新部署后测试。

## [0.1.0] —— 2026-09-15

- 初始候选：需求澄清、文件化记忆、能力缺口、证据验收、五份模板、来源与许可追踪。
- 发布前静态校验通过并上传 GitHub。
- 首轮 A/B 后进入 V0.2 修复。
