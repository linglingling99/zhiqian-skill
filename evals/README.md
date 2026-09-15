# human-ai-collab Evaluation Protocol

本目录用于真实行为测试，不把静态字符串检查当成 Skill 有效性证明。

## 配对原则

每个 eval 同时跑两种配置：

- `baseline`：不加载 human-ai-collab；
- `with_skill`：加载当前待测版本。

改善既有 Skill 时，可额外加入 `old_skill`（旧版本快照）作为第三组。

同一 eval 尽量保持：模型、思考强度、工具、权限、初始文件、用户响应策略一致。两边执行者不知道评分规则、另一组输出或组别目的。

## 重复与方差

一次运行只算案例，不算稳定结论。正式复测优先每个核心 eval 至少重复 3 次；记录每次结果，再比较均值、离散程度和失败模式。若资源有限，先跑 1 次发现致命缺陷，再决定是否扩大样本。

## 必留数据

平台真实提供时记录：

- total_tokens / credits；
- duration_ms / wall-clock time；
- user turns / AI questions；
- tool calls / failures / rework；
- files and reusable assets；
- scope incidents；
- product output；
- handoff result。

平台拿不到的字段必须为 `NOT_AVAILABLE` / `null`，不估算。

## 评估分层

1. **客观断言**：Scope 越界、R/D/H 同步、证据状态、文件存在、是否重复提问等，优先脚本/可复核证据。
2. **产品盲评**：隐藏 baseline / skill 身份，只看最终产品质量。
3. **成本分析**：时间、token/credits、工具调用、返工、用户负担。
4. **真实 Handoff**：新 AI 只拿 workspace，不给原聊天和 evaluation，恢复上下文并完成一个小变更。

## 防止无区分度测试

若某个断言 baseline 和 with_skill 几乎总能同时通过，它不能证明 Skill 有增量价值；保留作底线检查，但不要当核心胜负指标。

若结果波动大，报告方差/失败分布，不用单次最好结果代表版本能力。
