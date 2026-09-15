---
name: wisp-cangjie
description: Distill a book, long-video transcript, podcast, course, or interview into a coherent set of executable, independently callable skills that install cleanly into a Wisp skill directory — the skill factory of the wisp-science ecosystem. Use when the user asks to 拆书 / 蒸馏一本书 / 把这本书做成 skill / 把这个视频、播客或课程蒸馏成 skill / 蒸馏出适配 wisp science 的 skill / distill this book into skills — i.e. wants the frameworks, principles, and methodologies in long-form content extracted into atomic, reusable skills an agent can invoke in real situations. NOT for simple summarization, book reviews, or author-persona role-play.
license: Apache-2.0
---

# Wisp Cangjie

仓颉造字,把经验固化成可传承的符号;Wisp Cangjie 把长内容里的方法论蒸馏成 agent 可调用的 skill — 拆解成**原子化、可被 agent 在真实场景下调用**的能力,并按使用目的编译成合适数量的、符合 wisp house 格式的 skill,装进 wisp skill 目录,让读者真正用起来。方法论设计说明见 `references/methodology/00-overview.md`。

> **术语约定**: 本 skill 及 `references/` 资源中所有"书",泛指一切被蒸馏的长内容 — 书籍、长视频转写、播客文字稿、课程、访谈、长文、资料集。

## When to use

用户说类似这些时使用:

- "帮我拆《穷查理宝典》" / "把毛选蒸馏成 skill"
- "把这个 B 站视频/播客/课程蒸馏成 skill"
- "distill this book into skills: <path>"
- "我想把这本书的方法论做成可用的 skill"

蒸馏对象: 方法论、决策框架、操作流程、计算规则、排障经验、清单、原则。**不做**: 书摘、读后感、简单摘要、作者人设角色扮演。

## Inputs

开始前**必须**从用户处确认:

1. **内容文本来源**: PDF / EPUB / TXT / 字幕 / 转写稿路径,或可访问的纯文本。**不要**在没有文本的情况下"凭记忆"蒸馏 — 宁可停下来问用户要。
2. **内容元信息**: 书籍是"书名 + 作者 + 出版年"; 视频/播客/课程是"标题 + 作者 + 发布时间"。用于目录命名和审计。非书籍内容把章节字段映射为时间戳/分 P/集数/讲次,保证可追溯。
3. **使用目的** (决定输出模式): 学习/查阅 → 倾向 single; 接入日常工作流、跨内容组合 → 倾向 pack。不确定时按 single-first 先推荐 single。
4. **是否首次试点**: 第一次使用时,先蒸馏 1 份内容验证流程,再批量。

**依赖**: `python` + `pyyaml` (必需); `tiktoken` / `jsonschema` (可选,缺失时跳过 token 统计与 schema 校验)。全程本地运行,无需网络。声明: 需要读取用户提供的大体量文本;宿主支持并行 sub-agent 时阶段 1 可并行,否则按降级方案串行执行,产出格式不变;长文本超上下文时用 `scripts/build_chunks.py` 建块、`scripts/build_index.py` 建检索索引,供检索式提取器取材。

## Workflow

严格按顺序执行。开始前先检查 `books/<slug>/PIPELINE_STATE.md` 是否存在: 存在则读取并从记录的阶段续跑;每完成一个阶段就更新该文件,并向用户汇报进度,不要静默跑完。

```text
阶段 0:   整书理解 (Adler 四步)  → BOOK_OVERVIEW.md
阶段 1:   5 个提取器并行提取     → 候选方法论单元池
阶段 1.5: 三重验证筛选          → 通过的单元 (用户轻确认)
阶段 1.6: 独立 Skill 晋级门     → promoted / router 去向
阶段 2:   RIA++ 构造能力卡      → .distill/capabilities/
阶段 3:   Zettelkasten 链接     → also_read + GLOSSARY
阶段 4:   压力测试              → 评测用例 + 回炉淘汰
阶段 5:   编译与交付            → single/pack 产物 + DIGEST.md + 安装
```

0. **整书理解**: 按 `references/methodology/01-stage0-adler.md` 执行 Adler 四步 (结构/解释/批判/应用),按 `references/templates/BOOK_OVERVIEW.md.template` 写入 `books/<slug>/BOOK_OVERVIEW.md`,把骨架展示给用户确认后再继续。
1. **并行提取**: 按 `references/methodology/02-stage1-parallel-extract.md`,用 5 个提取器 prompt — 框架 `references/extractors/framework-extractor.md`、原则 `references/extractors/principle-extractor.md`、案例 `references/extractors/case-extractor.md`、反例 `references/extractors/counter-example-extractor.md`、术语 `references/extractors/glossary-extractor.md` — 独立提取到 `books/<slug>/candidates/`。对照阶段 0 的原书关键任务清单做覆盖率硬门检查,有未解释遗漏就补读,不虚报零遗漏。
2. **三重验证**: 按 `references/methodology/03-stage1.5-triple-verify.md`,对每个候选做 V1 来源充分性 / V2 可执行性 / V3 任务增益,分流 verified / reference / needs_review / rejected 并记录依据,更新覆盖审计,再请用户轻确认入选名单。
3. **晋级门**: 按 `references/methodology/03b-stage1.6-promotion-gate.md`,对每个通过单元评审五条独立性判据,写入 promoted / router 去向;未晋级单元保留为能力卡,不淘汰。
4. **能力卡**: 按 `references/methodology/04-stage2-ria-plus.md`,构造 R / I / A1 / A2 / E / B 六段能力卡,把元数据登记进 Capability Bundle (`books/<slug>/.distill/capabilities/verified.yaml`)。
5. **链接**: 按 `references/methodology/05-stage3-zettelkasten.md`,建立能力间 also_read 引用与区分,整理 `books/<slug>/GLOSSARY.md`。
6. **压力测试**: 按 `references/methodology/06-stage4-pressure-test.md`,晋级能力测触发精度,路由能力测可达;两类都必须实际完成代表任务并核对输出,不能拿"会调用"替代"做得对"。机械判分可用 `scripts/run_trigger_evals.py` 与 `scripts/run_output_evals.py`。未通过的回炉重做能力卡。
7. **编译交付**: 按 `references/methodology/07-stage5-deliver.md`: 先生成面向读者的 `books/<slug>/DIGEST.md` (模板 `references/templates/DIGEST.md.template`);再运行 `python scripts/distill.py compile --bundle books/<slug>/.distill/capabilities --out dist/<slug> --output auto`,把决策报告交用户轻确认 (按推荐 / 改 single / 改 pack),确认后加 `--yes` 执行;最后问用户安装位置,把产物安装到宿主 skills 目录 (如 `~/.wisp/skills/`)。

**Hard gates** (违反则阻止输出):

1. 每个能力必须通过全部三重验证;原文引用每段 ≤150 字 (英文 ≤100 词)。
2. 每张能力卡必须有完整的 R / I / A1 / A2 / E / B 六段;无原书案例时如实标注,合成演练不冒充书中事实。
3. 每个 active 能力恰好一个去向 (promoted_to 或 served_by);未晋级能力必须可经来源路由入口到达。
4. 晋级 Skill 的 `description` 必须写明触发条件,并与来源路由入口互有近邻负例。
5. 编译产物必须通过 `scripts/validate_skill_pack.py` (编译器已内置为硬门)。
6. 生成目录只读: 检测到本地手改时不得静默覆盖。
7. 关键任务覆盖必须有可追溯去向;存在重要缺口时只能交付明确标注范围的草稿,不能宣称完整通过。
8. **交付脱敏**: 完整溯源信息(来源书名/作者/人物昵称/章节标题原文/逐字长引文/原文出处字段)只允许留在 `books/<slug>/` 内部审计轨迹中;凡离开该目录的产物(安装副本/发布/编译产物)必须替换为改述与泛称(如"某 9 分文章""因果审读章"),使读者无法反推源文档身份。
9. **净版直写**: 脱敏从阶段 2 构造能力卡起即执行 — 卡片 R 段转述、卡内与 Bundle 的 entry/book 字段不出现来源身份与逐字引文,而不是先编成带溯源的产物再事后清洗;`books/<slug>/.distill/capabilities/book/{overview,glossary}.md` 写脱敏版(供编译进交付物),完整版仅存 `books/<slug>/` 根目录。交付前对编译产物 grep 复查来源身份词,零残留才算通过。

## Boundaries

- **不凭记忆拆书** — 没有文本就停下来向用户要。
- **先试点 1 份内容** — 除非用户明确说"批量"。
- **阶段之间主动汇报进度** — 关键节点 (阶段 0 骨架、阶段 1.5 入选名单、阶段 5 输出模式) 必须用户确认。
- **保留审计轨迹** — `candidates/` 和 `rejected/` 都要留在 `books/<slug>/` 下。
- **输出策略持久化** — update / repair 默认沿用原输出模式,不因新增材料静默改变产物形态。
- **只交付通过测试的产物** — 未通过阶段 4 的能力留在构建目录回炉,不安装。
