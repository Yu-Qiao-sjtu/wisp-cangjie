# Changelog

## 1.1.0 — 2026-09-15

- 附带生态技能 `skills/research-roadmap/`：论文／报告／基金技术路线图绘制（SVG + PNG，按需可编辑 PPT / draw.io）。布线硬规则由随附 `scripts/check_graph.py` 强制（多段路由斜向段＝ERROR、短间距拐弯＝WARN）。
- 新增 `docs/technical-roadmap-experience.zh-CN.md`：一次真实基金技术路线图交付的完整返工教训与固化规则对照。
- research-roadmap 增补模型能力要求：验收门**必须有视觉能力模型**（如 GPT-5.6-sol／High，以能力为准不绑定型号）；纯文本模型只能交付标注"未完成视觉验收"的 SVG。
- 新增 `references/style-defaults.md` 集中默认模板规格（SVG 配色字号、PPT 双字体 10 号／A4 页面／无阴影等），用户模板按提取协议覆盖，未覆盖项回退默认值。

## 1.0.0 — 2026-09-15

- 首个公开版本。
- RIA-TV++ 六阶段蒸馏流水线：整书理解 → 并行提取 → 三重验证 → 晋级门 → 能力卡 → 压力测试，编译交付 single / pack 两种产物。
- `scripts/distill.py` 确定性 CLI：`doctor` / `compile` / `replan-output` / `update` / `repair` / `rollback` / `eval`，带 staging 校验、发布哈希登记、原子发布与快照回滚。
- wisp house 布局（`SKILL.md` + `references/` + `scripts/` + `assets/`），通过 wisp-science store 包检查（`inspect_repository`）。
- 自带回归评测工具（触发评测 / 输出评测）与 JSON Schema 契约（`assets/schemas/`）。
