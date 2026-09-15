# CHANGELOG

> 有效性与兼容性结论只按真实证据记录，不把候选规则写成“已经有效”。

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
