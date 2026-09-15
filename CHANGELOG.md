# Changelog

## 1.0.0 — 2026-09-15

- 首个公开版本。
- RIA-TV++ 六阶段蒸馏流水线：整书理解 → 并行提取 → 三重验证 → 晋级门 → 能力卡 → 压力测试，编译交付 single / pack 两种产物。
- `scripts/distill.py` 确定性 CLI：`doctor` / `compile` / `replan-output` / `update` / `repair` / `rollback` / `eval`，带 staging 校验、发布哈希登记、原子发布与快照回滚。
- wisp house 布局（`SKILL.md` + `references/` + `scripts/` + `assets/`），通过 wisp-science store 包检查（`inspect_repository`）。
- 自带回归评测工具（触发评测 / 输出评测）与 JSON Schema 契约（`assets/schemas/`）。
