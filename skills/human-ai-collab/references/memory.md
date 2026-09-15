# Scope、Write-through 与本地接续（memory）

文件系统是可迁移状态，不是形式化文档仓库。核心要求：**合法读取、实时同步、单一真源、可接手。**

## 1. Scope Firewall

复杂任务第一次文件操作前，在 `TASK.md` 记录：

```text
WORK_ROOT
ALLOWED_READ_ROOTS
ALLOWED_WRITE_ROOTS
EXPLICIT_EXCEPTIONS
```

默认禁止：父目录、兄弟任务、其他项目、其他实验组、共享 memory、未明确归属的用户资料。

**数据归属优先于路径包含。** 即使一个文件物理上位于允许父目录，只要不属于当前任务，也不能读取。

安装 Skill、上传发布等需要越出工作根时，只给具体目标的一次性最小例外，不能顺势扩大到整个用户目录。

### Context contamination stop

误读非本任务上下文时：
1. 标记 `CONTEXT_CONTAMINATED = TRUE`；
2. 记录读到了什么路径/类型；
3. 停止需要独立性的分析、评分、审计；
4. 不允许说“我保证不用所以不影响”；
5. 需要独立结论时，换干净会话，只输入合法 workspace，并重做受污染阶段。

## 2. 目录结构

```text
资料主目录/
├── INDEX.md
├── PROFILE.md          # 仅在满足创建门槛时存在
└── tasks/<task-id>/
    ├── TASK.md         # Current Truth
    ├── LOG.md
    ├── RESEARCH.md     # 有影响方案的真实研究才建
    ├── materials/
    ├── outputs/
    └── versions/       # 重大里程碑按需
```

公共 Skill 只放方法/模板；用户数据不得写回 Skill 仓库。

## 3. Write-through State

`TASK.md` 是唯一 Current Truth。重要状态变化不能只留在聊天里。

- 新确认需求 → 写 `R-*`；
- 新决定/替代旧决定 → 写 `D-*`；
- 影响方案的重要假设 → 写 `H-*`；
- 状态/范围/验收改变 → 同步对应小节。

**先写状态，再进入下一关键动作。** 写前先读当前版本，避免覆盖并发变化。

### State Sync Gate

- **执行前**：聊天当前状态 == TASK Current Truth。
- **重大变更后**：先同步再继续。
- **完成前**：R/D/H、研究结论、产物、验收状态一致。

任何一处不一致，不能声称“已记录/已完成”。

## 4. 文件创建门槛

- `PROFILE.md`：只有至少 1 条“用户已确认 + 跨任务仍有价值”的协作信息才创建。只有待确认观察时不建。
- `RESEARCH.md`：只有真实外部/宿主事实影响方案时创建。
- `versions/`：只在重大执行前、破坏性变更前、重要交付前按需快照，不机械复制。

## 5. Handoff

换会话/换 AI 后：
1. 读 `INDEX.md`；
2. 读当前 `TASK.md`；
3. 读最近 `LOG.md`；
4. 有 `RESEARCH.md` 再读；
5. 回答：目标、阶段、已确认需求、关键决定/理由、未验证假设、下一步。

读取后才宣称接续。本地文件可携带，不等于宿主有自动记忆。
