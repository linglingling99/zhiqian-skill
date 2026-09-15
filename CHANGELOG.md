# CHANGELOG

本项目遵循：新增 / 删除 / 未触及 三栏记录；有效性与兼容性结论以实测为准，不写"任意 AI 通用"。

## [0.1.0] 候选版本 —— 2026-09-15

### 发布前收口（2026-09-15）

- README 升级为中文项目首页：增加流程图、对比说明、生产资料结构、安装与状态矩阵。
- 能力缺口从 Skill/Tool 扩展为 Model / Skill / Tool / Connector / 数据 / 权限的统一检查。
- `TASK.md` 增加轻量“执行准备”和“复盘与认知更新”，用于生产资料就绪和反馈沉淀。
- `PROFILE.md` 增加可纠正的 AI 观察区，明确待确认观察不能升级为永久标签。
- 任务分级允许在新证据表明任务变简单时说明理由后降档，避免流程过重。

### 新增

- `skills/human-ai-collab/SKILL.md`：唯一运行入口（触发/不触发、六原则、信息分层、轻量流程、边界）。
- `references/dialogue.md`：需求澄清与方案确认（取材改写自 Superpowers brainstorming）。
- `references/memory.md`：本地资料落盘与接续（取材改写自 planning-with-files）。
- `references/research.md`：能力缺口与来源核查（取材改写自 Vercel find-skills）。
- `references/delivery.md`：执行与证据验收（取材改写自 Superpowers verification-before-completion）。
- `assets/templates/`：index / profile / task / research / log 五份建档模板。
- `provenance/REUSE_MAP.md` 与 `provenance/sources.lock.json`：取材来源与去向。
- `THIRD_PARTY_NOTICES.md` 与 `licenses/`：第三方来源声明与许可全文。
- `tests/validate_skill.py`：静态校验脚本。
- README：新增「安装前自检」「安装成功后如何判断」章节。
- LICENSE 版权主体确定为 `Copyright (c) 2026 Heyi`；维护者署名「合一 / Heyi」。

### 删除（相对上游机制，主动不继承）

- planning-with-files 的 YAML hooks、CLAUDE 路径、会话存储扫描、强制 2-action 计数、自动停止钩子。
- find-skills 的无条件搜索、全局 `-g -y` 安装、以热度当安全许可、运行期自动更新全部技能。
- brainstorming 的"每个任务都要求完整规划"、固定开发术语、上游技能路由。
- skill-creator 的"自动开子会话""强迫分胜负""把生成后总结当原始对话""未验证工具接口"。
- `dev-tools/skill-creator/` 完整副本：确认 `tests/` 与运行 Skill 均不依赖后，从分发仓库移除；来源、commit、许可记录保留于 `provenance/` 与 `licenses/`。

### 未触及

- 未做任何真实 A/B 测试。
- 未在真实宿主环境验证加载/触发/跨会话接续。
- 未发布 GitHub；未上传任何用户资料。

### 已知限制

- 尚未经过独立测试；有效性待定。
- 未实现自动恢复钩子，跨会话接续依赖用户显式提交本地入口文件。
