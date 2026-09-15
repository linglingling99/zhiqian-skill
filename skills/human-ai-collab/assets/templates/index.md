# INDEX —— 可迁移入口

> 保持极简，只负责定位项目、当前任务与接续入口；全部路径使用相对路径。若当前任务不唯一，不要猜。

## Project

- PROJECT_ID：
- 项目标题：

## 当前任务

- TASK_ID：
- 标题：
- 状态：
- Current Truth：`./tasks/<task-id>/TASK.md`
- 最近日志：`./tasks/<task-id>/LOG.md`
- 研究（如有）：`./tasks/<task-id>/RESEARCH.md`

## 任务列表

| TASK_ID | 标题 | 状态 | 入口 |
|---------|------|------|------|
| | | | `./tasks/<task-id>/TASK.md` |

## 接续顺序

新会话 / 新 AI：先确认 PROJECT_ID → 唯一 TASK_ID → TASK → 最近 LOG → RESEARCH（如有）。如果存在多个候选任务且没有唯一当前任务，停止并要求明确，不按最近修改时间猜。未读取前不宣称已经接续。
