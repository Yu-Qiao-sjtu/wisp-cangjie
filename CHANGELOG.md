# Changelog

## 1.3.0 — 2026-10-07

- **编排纪律 v1**：借鉴 Paper2Agent 编排工程的构建期轻规则，落地四个协作约定：
  - **阶段屏障** — 02 / 03 / 06 / 07 各阶段文档新增"阶段完成条件"清单，上一阶段未满足不得进入下一阶段，禁止边测边交付；
  - **独占所有权（并行纪律）** — 阶段 1 每个 extractor 独占自己的候选文件，跨文件共享内容由单一合并方串行合并并登记归属；
  - **独立验证机械核对** — 新增 `run_ref` 机制（分配 → 产出首行回显 → PIPELINE_STATE 参与者登记 → 盲测与蒸馏交集核对 → 落盘 `test-results.md` "独立性登记"）；
  - **轻量状态契约** — 新增 `references/templates/PIPELINE_STATE.md.template`（阶段进度 / 参与者登记 / 独立性登记 / 关键哈希 / 重试回炉），SKILL.md 与阶段 5 交接处引用。
- `TOOL_VERSION` 升至 `wisp-cangjie v1.3.0`。

## 1.2.0 — 2026-10-07

- **论文成为一等源类型（论文模式 v2.3）**：新增 `references/methodology/08-paper-mode.md` 差异层 SOP — 阶段 0 论文结构理解（IMRaD 骨架 + 可复现资源清单）、阶段 1 的 5+1 提取器、阶段 4 断言分级与复现/泛化双极查询、阶段 5 学术引用规范替代脱敏。书籍模式（书/视频/播客/课程等长内容）默认流程不变。
- 新增论文模式第 6 提取器 `references/extractors/reproducibility-extractor.md`（实验条件/参数/协议/资源锚点/复现障碍）。
- Capability Bundle 新增可选字段 `book.source_type`（book / long-content / paper）；能力卡新增可选 `verifiability` 分级（reproducible / checkable / subjective）——均为可选，旧 Bundle 向后兼容。
- 阶段 4 压力测试增强：捷径检测清单（输入真被使用 / 产物隔离 / 硬编码检测 / 边界判停）、断言强度按 verifiability 分级、回炉预算 2 轮（超限降级 router/参考并记录，不带病发布）。
- `repair` 流加入修复预算（同一 failure case 最多 6 次尝试，超限 fail-closed 写入 `unresolved.md` 请用户裁决）与尝试历史分目录留痕（`attempt-<N>/`）。
- `update` 流按 content_hash 复用未变更块的既有审查决策（不重跑阶段 1/1.5/1.6），只有新增/修改块进入增量提取。
- 阶段 5 交付前合规复核分模式（书籍=脱敏清单 / 论文=学术引用规范）；安装冒烟改为从安装位置本身执行，冒烟 prompt 与结果进收尾汇报。
- 内嵌能力卡资源链接统一为包根相对，消除 broken-ref 硬门误拦。
- `compile` 产物输出顶层 `tags`（合法性校验 + schema 声明），恢复宿主 search 标签通道。
- 支持生成 `wisp:` frontmatter 元数据，编译期受控词表硬校验。
- 补充面向宿主检索的 description / tags 写法（TUTORIAL + 交付 SOP）。
- `TOOL_VERSION` 升至 `wisp-cangjie v1.2.0`。

## 1.1.0 — 2026-09-15

- 附带生态技能 `skills/research-roadmap/`：论文／报告／基金技术路线图绘制（SVG + PNG，按需可编辑 PPT / draw.io）。布线硬规则由随附 `skills/research-roadmap/scripts/check_graph.py` 强制（多段路由斜向段＝ERROR、短间距拐弯＝WARN）。
- 新增 `docs/technical-roadmap-experience.zh-CN.md`：一次真实基金技术路线图交付的完整返工教训与固化规则对照。
- research-roadmap 增补模型能力要求：验收门**必须有视觉能力模型**（如 GPT-5.6-sol／High，以能力为准不绑定型号）；纯文本模型只能交付标注"未完成视觉验收"的 SVG。
- 新增 `skills/research-roadmap/references/style-defaults.md` 集中默认模板规格（SVG 配色字号、PPT 双字体 10 号／A4 页面／无阴影等），用户模板按提取协议覆盖，未覆盖项回退默认值。

## 1.0.0 — 2026-09-15

- 首个公开版本。
- RIA-TV++ 六阶段蒸馏流水线：整书理解 → 并行提取 → 三重验证 → 晋级门 → 能力卡 → 压力测试，编译交付 single / pack 两种产物。
- `scripts/distill.py` 确定性 CLI：`doctor` / `compile` / `replan-output` / `update` / `repair` / `rollback` / `eval`，带 staging 校验、发布哈希登记、原子发布与快照回滚。
- wisp house 布局（`SKILL.md` + `references/` + `scripts/` + `assets/`），通过 wisp-science store 包检查（`inspect_repository`）。
- 自带回归评测工具（触发评测 / 输出评测）与 JSON Schema 契约（`assets/schemas/`）。
