# Paper Reader 设计文档（草案）

> 状态：待评审 · 定位：为 wisp-cangjie 增加"来源获取"上游入口 · 工作名：paper-reader
> 触发词（草案）：抓取文献 / 追踪论文 / 文献调研 / 某方向的最新文章 / fetch papers

## 1. 背景与定位

wisp-cangjie 当前把 PDF / 文本炼化成可调用 skill，但输入依赖用户手动提供：用户拿到"一篇论文"的路径是断的，发现与获取发生在项目之外。

Paper Reader 补上这一段，定位为 **wisp-cangjie 的可选上游入口**：

- 用户提出"抓取某方向的文章" → 触发 Paper Reader → 确定性 fetch → 用户挑选 → 进入既有论文模式炼化；
- 用户已自备 PDF / 资源 → 走老路（直接进入炼化），Paper Reader 提供 `import` 归一化；
- 参考 Paper2Agent 的下游转换能力作为**保留项**，不写死。

三条设计原则（已与用户对齐）：

1. **按需触发，无定时**——不做每日轮询；需要周期性的用户自行挂 cron 调用 CLI。
2. **抓取零 token**——fetch / 去重 / 打分 / 落盘全部是确定性操作；模型只在用户选定文章后进入炼化时才被调用。
3. **用户显式选择**——clone 之后不自动抓取任何源；每次运行由卡片选择源与方向，文章质量把控权在用户。

## 2. 用户旅程

### 入口 A — 方向 → 文章（自动获取）

```text
用户: 基于 wisp-cangjie 抓取"AI 辅助抗体设计"方向的最新文章
agent: 弹出源选择卡 + 参数卡（见 §3）→ 用户勾选
agent: python scripts/reader.py fetch --sources arxiv,biorxiv --since 14d --keywords "..."
       （确定性: 轮询 → 去重 → 打分 → 落 inbox + report.md）
agent: 展示候选清单（标题/来源/得分/摘要）
用户: 挑选 2 篇
agent: python scripts/reader.py export <id> --to books/<slug>/
       → 进入论文模式六阶段 → 编译交付 skill
```

### 入口 B — 自备 PDF / 资源（老路保持）

用户已有 PDF 时无需改变现有流程；新增 `reader.py import --pdf <path> --to books/<slug>/`
仅把手工准备归一化为一条命令，产出与入口 A 完全相同的输入契约。

### 保留项 C — 下游可执行工件转换（Paper2Agent 式）

精选论文炼化后，转换后端可插拔：默认 = wisp-cangjie 的 skill 编译；
保留 = Paper2Agent 式 MCP / 带测试工件生成。通过适配接口预留，不在首版实现。

## 3. 触发与交互设计

### 3.1 触发面

- 独立 `skills/paper-reader/SKILL.md`：带触发词与顶层 tags，适配宿主 search_skills 打分（受控词表取值以 wisp-science 规范为准）；
- wisp-cangjie 主 `SKILL.md` 增加一句路由："用户要求抓取 / 追踪某方向文献时，先使用 paper-reader 获取来源"。

### 3.2 源选择卡（全部源一次列全）

每次 fetch 前展示，用户勾选（默认沿用上次选择）：

```text
请选择要抓取的文献源（可多选，默认上次选择）:
[1] arXiv（预印本: CS / QBio / 物理）        ~50 条/次   无需登录
[2] bioRxiv / medRxiv（生命科学预印本）       ~80 条/次   无需登录
[3] PubMed（生物医学文献）                     ~40 条/次   无需登录
[4] 期刊 RSS（Nature / Cell / Science 等）    按订阅期刊   无需登录
[5] HF Daily Papers（ML 社区热度）             ~30 条/次   无需登录
[6] 本地 PDF / 资源目录（自备）                —           走 import
```

- 卡片一次列全所有源，每个源带**实现状态**（可用 / 实验中 / 未实现），选中未实现源时明确提示，不静默忽略；
- 交互宿主（Claude Code / WorkBody 等）：渲染为原生选择卡片；
- 文本宿主：降级为编号清单，回复编号即可；
- 自动化 / 老手：`--sources arxiv,biorxiv` 显式指定，跳过卡片。

### 3.3 参数卡

方向关键词（自由文本，或从 `query-templates.md` 选模板）、时间窗口（`--since`，默认 14d）、获取深度：

| 深度 | 动作 | 相对成本 |
| --- | --- | --- |
| metadata | 只取标题 / 摘要 / DOI / 版本 | 最低 |
| pdf | 额外下载 OA PDF | 中（磁盘 + 带宽） |
| fulltext | 额外解析为 Markdown | 高（依赖可选解析器） |

一次抓取只确认一次；炼化前的确认交给论文模式既有确认门，不重复问。

## 4. 源目录

| 源 | 订阅方式 | 备注 |
| --- | --- | --- |
| arXiv | 分类 RSS + API 查询式订阅 | 查询模板见 `references/query-templates.md` |
| bioRxiv / medRxiv | 学科 RSS + api.biorxiv.org | 按日期 / DOI 取详情 |
| PubMed | saved search 查询（可转 RSS） | 官方免费 |
| 期刊 RSS | 原生 RSS（Nature 系等多数有）；缺失时经 RSSHub 生成 | 站点清单可配置 |
| HF Daily Papers | JSON API | ML 侧覆盖好 |
| 本地资源 | 文件系统 | import 路径 |

查询式订阅是"识别内容"的第一层（源级过滤）。蛋白设计方向模板示例：
`protein language model`、`antibody / nanobody design`、`de novo binder`、`miniprotein`、
`RFdiffusion`、`ProteinMPNN`、`AlphaFold3`、`enzyme design`、`generative protein design`。
模板与关键词在配置中可改。

## 5. 系统架构与 CLI

```text
wisp-cangjie/skills/paper-reader/
├── SKILL.md                    # 触发面 + 工作流 + 边界（声明只读网络）
├── references/
│   ├── feeds-guide.md          # 各源订阅写法、速率约束、凭据要求
│   └── query-templates.md      # 领域查询模板（含蛋白设计示例）
└── scripts/
    └── reader.py               # 薄 CLI：只做编排与确定性操作，不调用模型
```

CLI 命令面（全部确定性、可审计）：

| 命令 | 作用 |
| --- | --- |
| `sources` | 输出源目录（JSON + 表格），供卡片渲染 |
| `fetch --sources ... --since ...` | 轮询 → 去重 → 打分 → 落盘 inbox + report.md |
| `list [--unread]` | 候选清单（标题 / 来源 / 得分 / 摘要） |
| `show <id>` | 单条详情（DOI、版本号、代码 / 数据资源链接） |
| `export <id> --to books/<slug>/` | 生成论文模式输入契约（§6） |
| `import --pdf <path> --to <dir>` | 自备资源归一化 |
| `mark <id> --status read\|skip\|distilled` | 状态管理（质量把控留痕） |
| `stats` | 状态总览 |

配置与状态（默认全局，跨项目去重；可配到项目内）：

```text
~/.paper-reader/
├── config.yaml                 # 已启用源、关键词、深度、路径
├── state/seen.json             # 去重: doi / arxiv_id+version → status
└── inbox/<date>/report.md      # 每次抓取的可读清单 + items.json
```

依赖策略（与仓颉一致）：stdlib 优先（Atom / RSS / JSON 标准库解析）；PDF 解析
（pymupdf 等）为可选件，缺失时 `export` 自动降级为"摘要 + 元数据"并标注
`fulltext_available: false`，不虚报全文可用。

## 6. 输入契约（与论文模式的接口）

`export` / `import` 统一产出：

```text
books/<slug>/
├── source.md                   # 正文（或摘要 + 元数据，视深度）
└── source-manifest.json        # 对齐 assets/schemas/source-document.schema.json
    doi | arxiv_id + version | title | authors | venue | published_at
    resources[]（code / dataset / tool + license）
    fulltext_available
```

- **版本锚定**：首次发现即锁定版本；后续检测到新版本只标记 update 待办，不自动重炼
  （呼应论文模式的"版本漂移"条款）；
- 全文与图表不随产物分发，只留引用锚点（沿论文模式引用规范）。

## 7. 识别、过滤、去重（全程零模型调用）

- 一层（源级）：查询表达式自带过滤；
- 二层（确定性打分）：关键词加权命中（标题权重高于摘要），输出可解释得分与命中词；
  排序供人决策，**不自动淘汰**，全部候选入 inbox；
- 去重：DOI 优先；arXiv ID + 版本号次之；标题归一化兜底；
- 可审计：抓取日志记录 HTTP 时间、源、条数。

## 8. 边界与红线

1. 只读公开元数据与 OA 内容；不绕过登录墙 / 付费墙；
2. 遵守源站速率约束（礼貌间隔、标识性 User-Agent）；
3. 全文 / 图表不重分发，产物只带引用锚点；
4. 抓取阶段零 LLM 调用，不因抓取产生 token 消耗；
5. 不自动炼化任何文章——炼化必须由用户选择触发。

## 9. 对主仓库的改动清单（实现时执行）

- 新增 `skills/paper-reader/`（本设计的落地物）；
- 主 `SKILL.md`：增加"来源获取"路由句（§3.1）；
- `README.md` / `README.zh-CN.md`：生态技能表登记 paper-reader；
- 本设计文档登记进 docs 索引。

## 10. 保留项与扩展点

- **Paper2Agent 式下游转换**：转换后端可插拔接口（默认 skill 编译；保留 MCP / 工件生成）；
- **新源适配器**：一个源 = 一段 YAML 声明 + 可选解析器函数，便于社区贡献；
- **定时钩子**：非核心功能；文档提供 cron 示例命令供用户自建（如每日 08:00 跑 fetch，
  炼化仍由用户挑选触发）。

## 11. 里程碑与验收

| 里程碑 | 内容 | 验收 |
| --- | --- | --- |
| M1 | 骨架 + arXiv 源 + import + export 契约 | 端到端演算：方向 → 候选 → export → 论文模式入口；抓取审计零 token |
| M2 | bioRxiv + PubMed；打分排序；卡片交互规范落地 | 三源演练；契约通过 schema 校验 |
| M3 | 期刊 RSS + HF Daily Papers；保留项接口 | 全源卡片可选；扩展点文档齐备 |

贯穿验收：wisp-science 宿主 search 命中（触发词演练）；skill 包通过
`scripts/validate_skill_pack.py`；clean-room 复现（另一台机 clone 后按 TUTORIAL 走通 M1）。

## 12. 待决事项（评审时确认）

1. **落位**：方案 A — 内置 `skills/paper-reader/`（推荐，与 research-roadmap 同轨、随仓库分发）；
   方案 B — 独立仓库后同构分发（利于外部贡献源适配，但安装链路变长）；
2. **CLI 命名**：`reader.py`（暂定），可改 `paper_reader.py`；
3. **M1 范围**：抓取深度是否含 `pdf` 档，或先只做 `metadata`（更快闭环）。
