# LOG —— RUN_SCOPE 增量记录

> 只记本次执行真实发生的动作、错误、验证与恢复。Current Truth 在 TASK；LOG 保存历史证据，不反过来覆盖当前决定。

## Identity

- PROJECT_ID：
- TASK_ID：
- RUN_ID：
- STATE_OWNER：

## 时间线

| 时间 | 动作 | 产物/目标 | 检查 | 结果 |
|------|------|-----------|------|------|
| | | | | |

## 确认与变更

| 时间 | R/D/H/状态变更 | 是否已同步 TASK |
|------|----------------|-----------------|
| | | YES/NO |

## CHANGE_IMPACT / STALE_TERM_SCAN

| 时间 | CHANGE_SET_ID | 影响文件 | 旧语义/关键词 | 处理状态 | 结果 |
|------|---------------|----------|-------------|----------|------|
| | | | | HISTORICAL_OK / UPDATE_REQUIRED / INVALID | |

> 重大平台/权限/数据模式/范围/交付变更后，必须记录 `STALE_TERM_SCAN`。存在 `UPDATE_REQUIRED` 时不能声称 State Sync 已完成。

## 错误与 ROOT_CAUSE_CHECK

| 时间 | 错误类型 | 第几次同类失败 | 根因假设 / 换策略 | 结果 |
|------|----------|----------------|-----------------|------|
| | | | | |

> 同类失败连续 2 次后，第 3 次动作前必须先记录 `ROOT_CAUSE_CHECK`，不能原样重试。

## Evidence Ledger

| Evidence ID | 路径/检查 | 状态 | 支持什么结论 | 被谁替代/失效原因 |
|-------------|-----------|------|--------------|------------------|
| E-001 | | ACTIVE / SUPERSEDED / INVALID | | |

最终验收只引用 `ACTIVE`。

## SCHEMA_GATE

- [ ] Identity 字段完整
- [ ] CHANGE_IMPACT（如适用）已落盘
- [ ] Evidence Ledger 能解释当前验收证据
- [ ] 恢复点可供新 AI 继续

## 恢复点

- 当前已完成到哪一步：
- 下一步该做什么：
- 关键文件路径：
- CONTEXT_CONTAMINATED：FALSE
