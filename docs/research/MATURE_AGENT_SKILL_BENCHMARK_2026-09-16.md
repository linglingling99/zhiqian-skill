# Mature Agent / Skill Benchmark｜2026-09-16

> 目的：在第二轮 WorkBuddy A/B 前，用成熟、高使用量/高星项目校对 human-ai-collab 的运行结构。Stars 只是成熟度信号，不是质量或安全证明；数字为本次调研快照，会随时间变化。
>
> 本轮新增项目只做**概念/架构参考**，没有复制其源码；原有第三方取材仍按 `provenance/` 记录。

## 对照项目

| 项目 | 调研时约 Stars | 重点看什么 | 对 human-ai-collab 的启发 |
|---|---:|---|---|
| obra/superpowers | 287k | Skill 调度、Skill TDD、progressive disclosure | Skill 修改也要 RED→GREEN；description 主要负责触发；主入口保持短，细节下沉 references |
| anthropics/skills / skill-creator | 176k | Skill 创建、A/B、benchmark | with-skill 与 baseline 成对运行；改旧 Skill 时旧版也可作 baseline；记录时间/token；多轮看均值、方差、delta |
| github/spec-kit | 137k | Spec-driven / idea assessment | intake→research→define→shape→decide 的分工；Research 同时寻找支持和反证；问题、目标、非目标、成功指标先于方案 |
| mem0ai/mem0 | 65k | 长期记忆与 scope | user / agent / app / run 需要显式 scope；启发 USER/PROJECT/TASK/RUN 四层状态，不允许自动混合 |
| vercel-labs/skills | 31k | Skill discovery | 先理解能力缺口，再搜索；搜索/推荐/安装分开；来源、成熟度、适配和权限都要检查 |
| langchain-ai/deepagents | 29k | agent harness、filesystem、memory、安全 | 模型自律不是安全边界；真正隔离要由 tool/sandbox enforce，Skill 必须区分 HARD / SOFT Scope |
| OthmanAdi/planning-with-files | 27k | 文件化计划、恢复、并发任务隔离 | PLAN/TASK identity pin；多个任务时 fail-closed；显式绑定失败不 fallback；一个 owner 写共享 Current Truth |
| coleam00/context-engineering-intro | 13k | Context Engineering / PRP | 除规则和文档外，高质量 examples 也是生产上下文；产品/视觉任务可选收集少量 reference examples |
| basicmachines-co/basic-memory | 4k | local-first Markdown、capture/continue | 当前状态应被综合重写，不是无限 append；稳定 thread/run key；恢复时先重建 current state 再继续 |

## 我们已有优势

与这些项目相比，human-ai-collab 的定位不同：它不是 coding harness、memory database 或大型 SDD 流程，而是面向普通用户的**轻量人机生产协作层**。

当前值得保留的差异：

1. **Outcome-first + DELEGATED_MODE**：让不懂专业术语的人只回答结果问题；低风险可逆决定由 AI 接手。
2. **事实/偏好/假设/决定分层**：用户确认不等于事实核验，AI 不同意也不等于用户错。
3. **产品调研 + 能力调研分开**：先知道“应该做什么”，再知道“靠什么做”。
4. **单一安装、模块化 references**：避免把用户变成多个 Skill 的调度员。
5. **本地 Markdown 可迁移**：不绑定某个特定 memory 服务或知识库软件。

## 这轮对照发现的结构缺口

### 1. 状态身份不够明确

V0.2 只有路径 Scope，不够。加入：

- `PROJECT_ID`
- `TASK_ID`
- `RUN_ID`
- `STATE_OWNER`

借鉴 Mem0 的 entity scope 与 planning-with-files 的 plan binding：状态必须知道“属于谁/哪个项目/哪个任务/哪一次运行”。

### 2. Scope 必须区分 HARD / SOFT

Deep Agents 明确强调边界应该在 tool/sandbox 层 enforce，而不是期待 LLM 自律。

加入：

`SCOPE_ENFORCEMENT: HARD | SOFT`

- HARD = 宿主真实限制路径/权限；
- SOFT = 只有 Skill 规则。

SOFT 不能宣传成真正数据隔离。

### 3. 多任务选择必须 fail-closed

借鉴 planning-with-files 的新版本：

- 显式 TASK_ID 不存在 → stop；
- 多个候选任务、没有唯一 current task → stop；
- 不按 mtime / 最近文件 / 相似名字 fallback 到另一个任务。

### 4. Current Truth 要综合，不要无限 append

借鉴 Basic Memory capture：

- TASK 保持“现在是什么”；
- LOG 保留“过去发生了什么”；
- 被替代的决定在当前正文中退出，只保留替代关系/历史证据。

### 5. Research 需要反证和证据质量

借鉴 Spec Kit assess：

新增：

- `PROBLEM_STATEMENT`
- `GOALS`
- `NON_GOALS`
- `SUCCESS_SIGNAL`
- `EVIDENCE_AGAINST`
- `CITED / ASSUMPTION`
- `confidence: HIGH / MEDIUM / LOW`

目标是避免“竞品都这么做，所以我们也做”这种伪研究。

### 6. Research 必须有 writeback cadence

借鉴 planning-with-files 的“看几次就落盘”原则，但不照搬平台 Hook：

> 连续读取约 2–3 个有意义来源，或即将离开 research phase 前，把影响判断的结论写入 RESEARCH。

解决 V0.1 最大问题之一：嘴上说记录，实际文件没同步。

### 7. Product context 可选带 examples

借鉴 Context Engineering：产品/视觉任务可保存少量 `REFERENCE_EXAMPLES`，逐个写“借什么 / 不借什么”。

不是所有任务都搜截图，也不为了参考而复制产品。

### 8. Eval 不能只跑一次

借鉴 Anthropic skill-creator + Superpowers Skill TDD：

- baseline / with-skill 同批运行；
- 改进版可加入 old-skill 组；
- token/credits/time 有真实数据才记录；
- objective assertions + 产品盲评；
- 正式结论尽量重复 ≥3 次，看 mean / variance / delta；
- baseline 同样能通过的断言属于“底线”，不是 Skill 增量证明。

仓库新增 `evals/evals.json` 与 `evals/README.md`。

## 明确不融入的部分

为了保持沙龙版轻量，本轮不引入：

- planning-with-files 的宿主专用 Hooks / session scanning / 自动注入机制；
- Basic Memory 完整 MCP / knowledge graph / cloud sync；
- Deep Agents 的完整 harness / subagent runtime；
- Spec Kit 的五阶段独立命令与整套 SDD 目录；
- Superpowers“每个任务都必须重流程”的硬门；
- 默认全局、免确认安装第三方 Skill。

这些能力有价值，但会改变 human-ai-collab 的产品定位和跨宿主可移植性。

## 第二轮 WorkBuddy 前的验收

进入真人 A/B 前至少满足：

- GitHub CI 全绿；
- `PROJECT_ID / TASK_ID / RUN_ID / STATE_OWNER` 存在；
- HARD/SOFT scope 可见；
- 多任务歧义 fail-closed；
- Product Research 有反证和置信度；
- Write-through 有小批次落盘门；
- `evals/evals.json` 可复用；
- README 明确 V0.2 仍是 RC，不宣称胜过 Baseline。
