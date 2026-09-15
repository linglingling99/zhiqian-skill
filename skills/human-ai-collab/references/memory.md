# Scope、状态身份、Write-through 与本地接续（memory）

文件系统是可迁移状态，不是形式化文档仓库。核心要求：**身份明确、合法读取、实时同步、单一真源、可接手。**

## 1. 先绑定状态身份

复杂任务第一次读取/写入前，确定并写入稳定标识：

```text
PROJECT_ID
TASK_ID
RUN_ID
STATE_OWNER
```

- `PROJECT_ID`：项目稳定标识；同一项目跨会话不随意变化。
- `TASK_ID`：当前任务稳定标识；只指向一个 `tasks/<task-id>/`。
- `RUN_ID`：一次会话/一次执行尝试的标识；重跑、污染恢复或独立接手使用新 RUN_ID。
- `STATE_OWNER`：当前唯一允许改写 `INDEX.md` / `TASK.md` Current Truth 的协调者。并行 worker 只写自己的运行记录/产物或返回发现，不并发改写共享 Current Truth。

### Fail-closed 任务选择

- 显式 `TASK_ID` 必须解析到 `WORK_ROOT` 内对应任务；解析失败就**停止**，不得回退到最近修改的任务、兄弟目录或猜测另一个任务。
- 当存在多个可选任务而 `INDEX.md` 没有唯一当前任务、用户也没指定 `TASK_ID` 时，停止并要求明确任务；不能按 mtime、目录名相似度或“看起来像”自动选。
- 新 AI 接手时先核对 `PROJECT_ID + TASK_ID`，再读取 Current Truth。

## 2. 四层状态作用域

不同寿命的信息不能混在同一层：

| Scope | 放什么 | 默认位置 | 升级条件 |
|---|---|---|---|
| `USER_SCOPE` | 用户已确认、跨任务稳定的背景/偏好/授权习惯 | `PROFILE.md` | 必须用户确认且跨任务仍有价值 |
| `PROJECT_SCOPE` | 项目级入口、任务列表、长期项目约束 | `INDEX.md` | 对多个任务持续有效 |
| `TASK_SCOPE` | 当前任务目标、R/D/H、研究、验收、产物 | `TASK.md` / `RESEARCH.md` | 与当前任务直接相关且已确认/有证据 |
| `RUN_SCOPE` | 本次会话动作、临时发现、错误、验证证据 | `LOG.md` / 当前 run 证据 | 经过核验后才可提升到 TASK_SCOPE |

**Promotion Rule**：`RUN_SCOPE → TASK_SCOPE` 需要相关且经过确认/验证；`TASK_SCOPE → USER_SCOPE` 必须用户确认并明确具有跨任务价值。一次表现、一次推断、一次临时决定不能自动升级成用户长期画像。

## 3. Scope Firewall：区分硬边界与软边界

复杂任务第一次文件操作前，在 `TASK.md` 记录：

```text
WORK_ROOT
ALLOWED_READ_ROOTS
ALLOWED_WRITE_ROOTS
EXPLICIT_EXCEPTIONS
SCOPE_ENFORCEMENT: HARD | SOFT
```

- `HARD`：宿主/沙箱/权限系统真实限制了 AI 只能访问指定根目录。
- `SOFT`：只有 Skill 指令要求 AI 自律，宿主实际上仍能访问更多路径。

**SOFT 不是安全隔离。** 如果宿主不能提供硬路径限制，必须明确说明；多项目、多用户、A/B 实验或敏感资料场景应优先配置 `HARD` 宿主边界，而不是相信模型永不越界。

默认禁止：父目录、兄弟任务、其他项目、其他实验组、共享 memory、未明确归属的用户资料。

**数据归属优先于路径包含。** 即使一个文件物理上位于允许父目录，只要不属于当前 `PROJECT_ID / TASK_ID`，也不能读取。

安装 Skill、上传发布等需要越出工作根时，只给具体目标的一次性最小 `EXPLICIT_EXCEPTIONS`，不能顺势扩大到整个用户目录。

### Context contamination stop

误读非本任务上下文时：
1. 标记 `CONTEXT_CONTAMINATED = TRUE`；
2. 记录所属 `RUN_ID`、读到的路径/类型；
3. 停止需要独立性的分析、评分、审计；
4. 不允许说“我保证不用所以不影响”；
5. 需要独立结论时，新建干净 `RUN_ID` / 干净会话，只输入合法 workspace，并重做受污染阶段。

## 4. 目录结构

```text
资料主目录/
├── INDEX.md
├── PROFILE.md          # 仅在满足创建门槛时存在
└── tasks/<task-id>/
    ├── TASK.md         # Current Truth
    ├── LOG.md          # RUN_SCOPE 历史与证据
    ├── RESEARCH.md     # 有影响方案的真实研究才建
    ├── materials/
    ├── outputs/
    └── versions/       # 重大里程碑按需
```

公共 Skill 只放方法/模板；用户数据不得写回 Skill 仓库。

## 5. SCHEMA_GATE：核心文件从对应模板起步

第一次创建 `INDEX.md / TASK.md / RESEARCH.md / LOG.md / PROFILE.md` 时，必须从 `assets/templates/` 的**对应模板**起步，而不是临场发明一个缩水版结构。

- 模板字段暂时不适用时写 `NOT_APPLICABLE`；无法获得时写 `NOT_AVAILABLE`。
- 不允许因为“我知道大概意思”就静默删掉 Identity、Scope、来源/核验日期、Evidence Ledger、变更记录等关键字段。
- `PROFILE.md` 仍受创建门槛约束：没有稳定且用户已确认的跨任务信息，就**不创建**，而不是创建空壳。
- 交接前执行 `SCHEMA_GATE`：现有核心文件必须至少保留模板中的关键身份、Current Truth、证据和恢复字段。

## 6. Write-through State

`TASK.md` 是当前任务唯一 Current Truth。重要状态变化不能只留在聊天里。

- 新确认需求 → 写 `R-*`；
- 新决定/替代旧决定 → 写 `D-*`；
- 影响方案的重要假设 → 写 `H-*`；
- 状态/范围/验收改变 → 同步对应小节。

**先写状态，再进入下一关键动作。** 写前先读当前版本并确认 `STATE_OWNER`，避免并发覆盖。

### Current Truth 是“当前状态”，不是历史堆积

`TASK.md` 应持续**综合/重写当前状态**：已经被替代的方案不得继续作为当前要求混在正文中。替代关系保留在 D-*、变更记录和 `LOG.md`，必要时再进 `versions/`。这样新 AI 从头读到尾看到的是“现在到底是什么”，而不是整段聊天历史的复制。

### CHANGE_IMPACT_GATE：核心变更必须做依赖一致性复核

用户改变以下任一核心维度时，不允许只新增一条 D-* 就继续：

- 产品/交付平台（例如小程序 → Web）；
- 用户群体或核心场景；
- 注册/登录/权限策略；
- 数据保存与同步方式；
- 核心范围、关键功能或验收标准；
- 对外发布/交付格式。

先生成一个 `CHANGE_SET_ID`，然后：

1. 写清**旧状态 → 新状态**以及改变原因；
2. 列出**影响文件**：`TASK.md`、`RESEARCH.md` 中当前结论、ACTIVE outputs、handoff/开发资料、验收与测试说明；
3. 更新 Current Truth 和所有仍标 ACTIVE 的相关产物；历史记录留在 LOG / superseded decision，不把旧状态继续留在当前正文；
4. 做 `STALE_TERM_SCAN`：主动搜索被替代平台名、旧权限/数据模式、旧范围关键词和与之绑定的派生表述；
5. 对每个残留判断：`HISTORICAL_OK / UPDATE_REQUIRED / INVALID`；
6. 只要仍有 `UPDATE_REQUIRED`，不得进入下一关键执行或声称 State Sync 完成。

`RESEARCH.md` 可以保留当时研究对象的历史名称，但如果其“对当前方案的影响”仍是 ACTIVE，就必须同步到当前平台/范围，不得让新 AI 误以为旧方案仍有效。

### State Sync Gate

- **执行前**：聊天当前状态 == TASK Current Truth。
- **重大变更后**：完成 `CHANGE_IMPACT_GATE + STALE_TERM_SCAN` 后再继续。
- **完成前**：R/D/H、研究结论、ACTIVE 产物、验收状态一致。

任何一处不一致，不能声称“已记录/已完成”。

## 7. 文件创建门槛

- `PROFILE.md`：只有至少 1 条“用户已确认 + 跨任务仍有价值”的协作信息才创建。只有待确认观察时不建。
- `RESEARCH.md`：只有真实外部/宿主事实影响方案时创建。
- `versions/`：只在重大执行前、破坏性变更前、重要交付前按需快照，不机械复制。

## 8. Handoff

换会话/换 AI 后：
1. 读 `INDEX.md`，确认 `PROJECT_ID` 与唯一 `TASK_ID`；
2. 读当前 `TASK.md`；
3. 读最近 `LOG.md` / 当前有效 RUN；
4. 有 `RESEARCH.md` 再读；
5. 重建：目标、阶段、已确认需求、关键决定/理由、未验证假设、有效证据、下一步；
6. 在动手前用一句话确认自己接手的是哪个项目/任务，避免错接兄弟任务。

读取后才宣称接续。本地文件可携带，不等于宿主有自动记忆。
