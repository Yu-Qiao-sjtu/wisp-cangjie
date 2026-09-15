<div align="center">
  <img src="assets/logo.svg" width="168" alt="Wisp Cangjie logo">

# Wisp Cangjie

**把书、长视频、播客蒸馏成可调用的 Wisp Skill · The skill factory of the Wisp Science ecosystem**

`RIA-TV++ 蒸馏流水线` · `确定性编译 CLI` · `wisp house 格式`
</div>

## 这是什么

仓颉造字,把经验固化成可传承的符号;Wisp Cangjie 把长内容里的方法论蒸馏成 agent 可调用的 skill。

给它一本书、一份长视频转写、一期播客或一门课程,它会走完一条六阶段流水线
(整书理解 → 并行提取 → 三重验证 → 晋级门 → 能力卡 → 压力测试),
把其中的方法论拆成原子化能力,再由确定性编译器打包成 **1 个 single 入口**
或 **1 个来源路由入口 + 少量晋级 skill**。产物格式与
[wisp-science](https://github.com/xuzhougeng/wisp-science) 的 bundled skill 完全一致,
复制进 `~/.wisp/skills/` 即可被发现和调用。

不做书摘、读后感和作者人设角色扮演 — 只做能在真实场景被 agent 调用的方法论。

## 快速上手

对装好本 skill 的 wisp agent 说:

```text
帮我把《穷查理宝典》蒸馏成 skill
把这个播客的文字稿蒸馏成 skill: <path>
拆书: <book.txt>,做成 wisp skill
```

流水线自带断点续跑(`PIPELINE_STATE.md`)、三处用户确认门(骨架 / 入选名单 / 输出模式)
与 8 条质量红线。产物附带回归评测用例(`test-prompts.json` / `output_cases`),
后续修订 skill 时重跑评测,防止触发与输出质量回退。

## 安装

方式一 — 克隆后复制到 wisp 用户级技能目录(所有项目可用):

```bash
git clone https://github.com/Yu-Qiao-sjtu/wisp-cangjie.git
cp -r wisp-cangjie ~/.wisp/skills/
```

方式二 — 从 wisp store 安装:选择本仓库根目录的 `wisp-cangjie` 包。

依赖:`python` + `pyyaml`(必需);`tiktoken`、`jsonschema`(可选,缺失时自动降级)。
环境自检:`python scripts/distill.py doctor`。

## 使用手册

手册分三层,按需往下查:

| 层 | 文件 | 给谁看 | 内容 |
| --- | --- | --- | --- |
| ① 项目手册 | `README.md`(本文件) | 使用者 | 这是什么、怎么装、怎么触发、生态定位 |
| ② 技能入口 | `SKILL.md` | wisp agent | 何时用、输入要求、六阶段工作流、8 条质量红线、行为边界。**wisp 加载技能时读的就是它** |
| ③ 阶段细则 | `references/methodology/`(9 篇 SOP) | wisp agent | 每个阶段的具体执行方法:Adler 整书理解、5 提取器并行、三重验证、晋级门、RIA++ 能力卡、压力测试、编译交付 |

配套参考:

- `references/extractors/` — 5 个提取器 prompt(框架 / 原则 / 案例 / 反例 / 术语);
- `references/templates/` — 各阶段产出模板;
- `scripts/distill.py` — 确定性 CLI(`doctor` / `compile` / `replan-output` / `update` / `repair` / `rollback` / `eval`),用法 `python scripts/distill.py --help`;
- `validation/README.md` — 如何用 wisp-science 的测试套件校验本包。

## 这是 Skill,不是 Agent

**Wisp Cangjie 是一个 Skill(技能包),不是 Agent。** 它是"教 wisp agent 学会拆书蒸馏的一套流程知识 + 确定性工具箱":

- **Skill 本体**(`SKILL.md` + `references/`)是教科书和 SOP,自己不会动;
- **`scripts/`** 是被动的确定性工具:编译、评测、原子发布、回滚 — 只做编排和校验,**不自己跑模型**;
- 真正干活的是 **wisp 这个 Agent**:它加载本技能后按 SOP 执行 — 读文本、调模型蒸馏、在阶段确认点询问用户;并行提取用的是宿主自身的 sub-agent 能力(不支持时自动串行降级)。

类比:wisp 是厨师(Agent),Wisp Cangjie 是一本带量勺和计时器的菜谱(Skill)。这也是为什么它装在 `~/.wisp/skills/` 下、能通过 wisp store 校验 — 它是生态中的一个技能包,只是这个技能的用途是**生产更多技能**。

## 产出结构

```text
books/<slug>/
├── PIPELINE_STATE.md          # 断点续跑状态
├── BOOK_OVERVIEW.md           # 整书理解(骨架/术语/批判)
├── verified.md                # 通过三重验证的单元
├── coverage-audit.md          # 关键任务覆盖审计
├── GLOSSARY.md / DIGEST.md    # 术语词典 / 面向读者的精华长文
├── candidates/  rejected/     # 审计轨迹
└── .distill/capabilities/     # Capability Bundle(唯一编译事实源)
    ├── verified.yaml          # 能力元数据(assets/schemas/capability-bundle.schema.json)
    ├── cards/<slug>.md        # RIA++ 能力卡(R/I/A1/A2/E/B)
    └── destinations.json      # promoted / router 去向映射
```

## Wisp Skill 生态

Wisp Cangjie 是 wisp skill 生态的"技能工厂" — 输入长内容,输出符合 house 格式的新技能:

| 角色 | 项目 | 说明 |
| --- | --- | --- |
| 运行时 | [wisp-science](https://github.com/xuzhougeng/wisp-science) | 科研 agent 运行时、skill 商店与打包规范 |
| 技能工厂 | **wisp-cangjie**(本仓库) | 把书 / 视频 / 播客蒸馏成可安装的 wisp skill |
| 生态技能示例 | research-roadmap、manuscript-polish、nsfc-grant-writing、signaling-pathway-atlas | 同一 house 格式,已安装在本地技能目录 |

蒸馏出的每个 skill 都自带 `SKILL.md` + `references/` + `scripts/`,
放进 `~/.wisp/skills/` 即进入生态 — 蒸馏越多,生态越繁茂。

## 包结构

```text
wisp-cangjie/
├── SKILL.md                   # 技能入口(When to use / Inputs / Workflow / Boundaries)
├── references/
│   ├── methodology/           # 六阶段 SOP(00-overview + 01~07)
│   ├── extractors/            # 5 个并行提取器 prompt
│   └── templates/             # 产出模板
├── scripts/                   # distill.py 编译/评测/更新/修复/回滚 CLI + 15 个确定性脚本
└── assets/
    ├── logo.svg
    └── schemas/               # Capability Bundle / 评测 / 契约 JSON Schema
```

## License

Apache-2.0
