---
name: human-ai-collab
description: Use when a user brings a vague or high-rework-cost real task, a new product/service/workflow, needs cross-session handoff, or explicitly wants the AI to clarify what should be built before acting. Do not use for simple one-off questions, trivial edits, or quick fact checks.
---

# Human AI Collab｜人机协作 Skill

把“用户有一个想法”变成“AI 能稳定执行、结果可验证、资料可交接”的生产协作。目标不是增加流程，而是让普通用户少解释、少返工，同时让关键判断真实落盘。

## 核心循环

1. **Scope Gate**：第一次文件操作前确定 `WORK_ROOT`、`ALLOWED_READ_ROOTS`、`ALLOWED_WRITE_ROOTS`、`EXPLICIT_EXCEPTIONS`。数据归属优先于路径包含；父目录、兄弟任务、共享 memory、其他项目默认不读不写。
2. **Read current truth**：若存在 `INDEX.md` / `TASK.md`，先读当前状态；没有则从真实任务开始，不先做问卷。
3. **Outcome-first clarification**：只问当前会改变方案的 1–2 个结果层问题。用户说“你决定/你看着办/我不懂”时进入 `DELEGATED_MODE`：可逆、低风险、免费且不外发的决定由 AI 自主完成；发布、付费、授权、外发、重要删除等仍需确认。
4. **Research before invention**：新产品、网站、App、小程序、工具、服务或陌生业务，存在成熟同类时，先做同类研究，提炼 `TABLE_STAKES`、`BEST_PRACTICES`、`AVOID_LIST`、`USER_DELTA`；影响方案的研究必须写入 `RESEARCH.md`。能力不足时再单独做 Model / Skill / Tool / Connector / Open Source / Data / Permission 研究。
5. **Write-through state**：`TASK.md` 是 Current Truth。确认后的需求 `R-*`、决定 `D-*`、重要假设 `H-*` 在进入下一关键动作前增量写入；重大变更后先同步再继续。不能说“已记录”但文件没变。
6. **Execute with discipline**：生产资料足够后再执行。相同类型失败连续 2 次，禁止直接第 3 次撞墙，先做根因检查并换策略。
7. **Evidence before claims**：验证证据只有 `ACTIVE / SUPERSEDED / INVALID`。只有 ACTIVE 证据能支持最终验收；后台进程、临时目录、旧证据和测试数据未清理前，不声称完成。
8. **Handoff**：完成前让 `INDEX.md + TASK.md + LOG.md + RESEARCH.md（如有）` 能在不依赖原聊天的情况下解释目标、状态、决定、风险、证据和下一步。

## 信息分层

| 类型 | 处理 |
|---|---|
| 用户偏好 | 尊重，不做真假判断 |
| 用户要求 | 写入需求 |
| 用户自述事实 | 高风险/有争议时核查 |
| 已核对事实 | 作为依据 |
| AI 推断 | 明确标记，不冒充事实 |
| 待验证假设 | 记录最小验证办法 |
| 已确认决策 | 记 `D-*`，变更留痕 |

**User confirmation ≠ factual verification。AI disagreement ≠ user wrong。**

## 三个硬门

### 1. Scope / contamination

任何读写前先判断“是否属于当前任务”，不能因为文件位于允许父目录就读取。若误读其他项目、其他实验组或未授权用户数据：

`CONTEXT_CONTAMINATED = TRUE`

立即停止需要独立性的分析/审计，记录事故；不能用“我保证不用”继续。需要独立结论时，换干净会话并只提供合法 workspace。

### 2. State Sync

复杂任务至少在三处核对：
- 执行前：聊天当前状态 == TASK Current Truth。
- 重大变更后：先更新 Current Truth。
- 完成前：R/D/H、研究结论、验收状态与实际产物一致。

`PROFILE.md` 不是必建文件：只有至少 1 条“用户已确认 + 跨任务仍有价值”的协作信息时才创建。

### 3. Completion

没有新鲜证据，不说“完成/通过/已保存/已清理”。没有文件写权限就输出可保存内容；没有网络就标记外部核验未完成；没有安装/授权能力就只推荐，不冒充执行。

## 按需读取的参考

- `references/dialogue.md`：小白友好澄清、授权模式、确认边界。
- `references/research.md`：产品/领域研究 + 能力研究双路径。
- `references/memory.md`：Scope、Write-through、状态同步与接续。
- `references/delivery.md`：失败处理、证据生命周期、清理与验收。

模板：`assets/templates/index.md`、`profile.md`、`task.md`、`research.md`、`log.md`。
