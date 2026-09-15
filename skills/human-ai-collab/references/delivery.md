# 执行、失败处理与证据验收（delivery）

## 1. Evidence before claims

没有本次新鲜证据，不声称完成、正确、通过、已保存或已清理。

每个重要声称都走：识别证据 → 执行检查 → 读取输出/退出码 → 对照需求 → 再陈述。

## 2. Two-Failure Rule

同一类型工具/命令连续失败 2 次：

**禁止直接第 3 次重试。**

先做 `ROOT_CAUSE_CHECK`：
- 实际错误是什么；
- 哪个假设可能错；
- 环境/权限/路径/参数有什么差异；
- 下一次为什么换策略。

修的是根因，不是继续碰运气。

## 3. Evidence Lifecycle

正式证据只有：
- `ACTIVE`：当前仍支持结论；
- `SUPERSEDED`：曾有效但被新版本替代；
- `INVALID`：验证方法/环境/输入有问题，不得支持最终结论。

最终验收只引用 `ACTIVE`。错误截图、旧结果不能和最终证据混在一起。

## 4. Cleanup Gate

完成前检查：
- 后台进程/服务已退出；
- 临时目录和测试数据按约定清理；
- 最终证据指向当前产物；
- 打包时检查源目录与解压后目录一致；
- 未清理项明确列出，不冒充完成。

“执行过 rm/kill”不是“已清理”；必须重新检查目标状态。

## 5. Requirement reconciliation

重读 `TASK.md`：
- 每个已确认 R-* 是否满足/明确延期；
- 每个关键 H-* 是否已验证或仍标未知；
- 研究驱动的 D-* 是否与实现一致；
- 当前产物路径真实存在。

### Major-change reconciliation

如果本 RUN 出现过平台、登录/权限、数据模式、用户群体、核心范围或交付格式变化：

1. 确认 `CHANGE_IMPACT_GATE` 已记录；
2. 对 Current Truth、ACTIVE 产品规格、Handoff/开发资料和验收说明运行 `STALE_TERM_SCAN`；
3. 被替代语义只能处于：
   - `HISTORICAL_OK`：明确历史上下文；
   - `INVALID`：旧证据/旧产物，不再支持当前结论；
   - 若仍是 `UPDATE_REQUIRED`，则 State Sync 未完成；
4. 不允许出现“D-* 已改成 Web，但 Goal/交接仍写小程序”这类部分同步。

漂亮文档不是交付，真实产物也不能替代状态同步。

## 6. SCHEMA_GATE

交付前检查核心文件是否仍符合对应模板的必要结构：

- `TASK.md`：Identity / Scope / R-D-H / Current Stage / 变更影响；
- `RESEARCH.md`（如有）：问题定义、证据类型、置信度、Sources、来源/核验日期、Decision Impact；
- `LOG.md`：Identity、变更同步、错误、Evidence Ledger、恢复点；
- `INDEX.md`：当前 PROJECT_ID / TASK_ID 与入口一致。

字段不适用写 `NOT_APPLICABLE`，不可获得写 `NOT_AVAILABLE`，不要静默删掉整个字段/章节后仍声称文件完整。

## 7. Handoff readiness

交付前，假设新 AI 只能看 workspace：它应能知道目标、状态、决定理由、风险、证据与下一步。不能靠原聊天补关键背景。

没有执行环境时，交付“怎么执行/怎么验证/什么算成功”的资料，并明确 NOT VERIFIED。
