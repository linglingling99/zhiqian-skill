# TASK —— Current Truth

> 当前任务唯一有效来源。聊天里的新状态必须写回本文件后，才进入下一关键动作；历史过程留在 LOG，不把 TASK 变成聊天流水账。

## Identity

- PROJECT_ID：
- TASK_ID：
- RUN_ID：
- STATE_OWNER：
- SCOPE_ENFORCEMENT：`HARD / SOFT`

## 目标

- Goal：
- 给谁用 / 解决什么：

## Scope & Data Ownership

- WORK_ROOT：
- ALLOWED_READ_ROOTS：
- ALLOWED_WRITE_ROOTS：
- EXPLICIT_EXCEPTIONS：
- CONTEXT_CONTAMINATED：FALSE

> 默认不读取父目录、兄弟任务、其他项目、共享 memory 或未明确归属的数据。`SOFT` 只代表指令边界，不代表宿主真正隔离。

## 当前范围

- 包含：
- 不包含 / 延后：

## Requirements

| ID | 内容 | 类型（要求/偏好） | 状态 | 来源 |
|----|------|-------------------|------|------|
| R-001 | | | 待确认/已确认 | |

## Decisions

| ID | 决定 | 理由 | 来源/证据 | 替代了谁 | 状态 |
|----|------|------|-----------|----------|------|
| D-001 | | | | | ACTIVE |

## Assumptions

| ID | 假设 | 为什么重要 | 最小验证 | 状态 |
|----|------|------------|----------|------|
| H-001 | | | | OPEN/VERIFIED/REJECTED |

## Research-linked Decisions

| 决定 ID | RESEARCH 依据 | 对方案的影响 |
|---------|---------------|--------------|
| | | |

## 执行准备

| 项 | 当前状态 | 缺口 / 下一动作 |
|----|----------|-----------------|
| Model | | |
| Skill | | |
| Tool | | |
| Connector / MCP | | |
| Open Source | | |
| Data | | |
| Permission | | |

## 验收标准

- [ ] 

## Current Stage / Next Step

- 当前阶段：
- 下一步（单一动作）：
- 最后同步时间：

## CHANGE_IMPACT_GATE（重大变更时填写）

- CHANGE_SET_ID：
- 旧状态：
- 新状态：
- 变更来源 / 原因：
- 影响文件：
  - [ ] TASK Current Truth
  - [ ] RESEARCH 当前影响结论（如有）
  - [ ] ACTIVE outputs / 产品规格
  - [ ] Handoff / 开发交接资料
  - [ ] 验收 / 测试说明
- `STALE_TERM_SCAN`：`NOT_RUN / PASS / FAIL`
- 发现的旧语义：
- 未解决 `UPDATE_REQUIRED`：`0`

> 平台、用户群体、登录/权限、数据模式、核心范围或交付格式改变时，完成本 Gate 后才能继续关键执行。

## SCHEMA_GATE

- [ ] Identity / Scope 字段完整
- [ ] 当前 R/D/H 与真实状态一致
- [ ] 重大变更已做 CHANGE_IMPACT_GATE
- [ ] Current Truth 不混用已失效要求

## 变更记录

| 日期 | R/D/H/范围变更 | 原因 |
|------|----------------|------|
| | | |
