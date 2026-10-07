<div align="center">
  <img src="assets/logo.svg" width="168" alt="Wisp Cangjie logo">

# Wisp Cangjie

**Distill books, papers, long videos, and podcasts into callable Wisp Skills · The skill factory of the Wisp ecosystem**

`RIA-TV++ distillation pipeline` · `Deterministic compile CLI` · `Wisp house format`

[English](README.md) · [简体中文](README.zh-CN.md)
</div>

## Acknowledgments

- Wisp Cangjie is built for the Wisp ecosystem created by **Dr. Zhougeng Xu** ([xuzhougeng](https://github.com/xuzhougeng), Chinese Academy of Sciences) — [wisp-science](https://github.com/xuzhougeng/wisp-science) and [wispterm](https://github.com/xuzhougeng/wispterm). The format specification, store validation, and runtime host of everything distilled here come from the Wisp ecosystem.
- The distillation methodology in this project (the RIA-TV++ pipeline, the capability-card system, and the deterministic compile toolchain) originates from [kangarooking/cangjie-skill](https://github.com/kangarooking/cangjie-skill). Wisp Cangjie is a deep adaptation of that work for the Wisp Science ecosystem — many thanks to the original author [kangarooking](https://github.com/kangarooking); his WeChat official account is **袋鼠帝AI客栈**.
- **Paper discovery & tracking** (reference ecosystem for Paper Reader and paper mode):
  - [jmiao24/Paper2Agent](https://github.com/jmiao24/Paper2Agent) — the "paper → interactive agent / MCP" paradigm and dual-component idea (Miao et al., Nature 2026); direct reference for Paper Reader's reserved downstream-conversion option;
  - [openags/paper-search-mcp](https://github.com/openags/paper-search-mcp) — MCP wrapper for multi-source search and download (arXiv / PubMed / bioRxiv / Crossref);
  - [blazickjp/arxiv-mcp-server](https://github.com/blazickjp/arxiv-mcp-server) — arXiv search, download, and analysis MCP;
  - [TideDra/zotero-arxiv-daily](https://github.com/TideDra/zotero-arxiv-daily) — interest-driven recommendations and TLDR digests from a personal library;
  - [dw-dengwei/daily-arXiv-ai-enhanced](https://github.com/dw-dengwei/daily-arXiv-ai-enhanced) — zero-ops fetch–summarize–publish pipeline on GitHub Actions;
  - [colorfulandcjy0806/Arxiv-tracker](https://github.com/colorfulandcjy0806/Arxiv-tracker) — cross-day dedup and anti-duplicate delivery patterns;
  - [AutoLLM/ArxivDigest](https://github.com/AutoLLM/ArxivDigest) and [karpathy/arxiv-sanity-lite](https://github.com/karpathy/arxiv-sanity-lite) — classic personalized recommendation and digest systems for arXiv;
  - [DIYgod/RSSHub](https://github.com/DIYgod/RSSHub) — generic RSS generation when a journal site has none;
  - Open scholarly infrastructure: [arXiv](https://arxiv.org), bioRxiv / medRxiv, PubMed / Europe PMC, Crossref, OpenAlex, Unpaywall, Semantic Scholar API, Hugging Face Daily Papers — data sources and subscription channels.
- **Scheduling & push** (studied while shaping Paper Reader): [huginn/huginn](https://github.com/huginn/huginn), [n8n-io/n8n](https://github.com/n8n-io/n8n), [easychen/rsspush](https://github.com/easychen/rsspush) — "monitor → filter → push" and cron engines that informed the "on-demand CLI, no resident scheduler" decision.
- **PDF parsing** (optional paper-mode backends, planned): [pymupdf/PyMuPDF](https://github.com/pymupdf/PyMuPDF), [kermitt2/grobid](https://github.com/kermitt2/grobid), [opendatalab/MinerU](https://github.com/opendatalab/MinerU), [docling-project/docling](https://github.com/docling-project/docling), [VikParuchuri/marker](https://github.com/VikParuchuri/marker), [facebookresearch/nougat](https://github.com/facebookresearch/nougat).

## What is this

Cangjie — the legendary four-eyed scribe — turned experience into inheritable symbols. Wisp Cangjie turns the methodologies inside long-form content into skills an agent can actually call: it breaks them down into **atomic, agent-invocable capabilities**, then compiles them into the right number of house-format skills and installs them into a Wisp skill directory.

Give it a book, a research paper, a video transcript, a podcast episode, or a course, and it walks a six-stage pipeline (overview → parallel extraction → triple verification → promotion gate → capability cards → pressure test), then deterministically compiles the result into **one single entry** or **one router entry plus a few promoted skills**. The output is fully format-compatible with the bundled skills of [Wisp Science](https://github.com/xuzhougeng/wisp-science) — drop it into `~/.wisp/skills/` and it is discoverable.

It does not do book summaries, book reviews, or author-persona role-play — only methodologies that can be invoked by an agent in real situations.

## Quick start

Ask a Wisp agent that has this skill installed:

```text
Distill "Poor Charlie's Almanack" into skills
Distill this podcast transcript into skills: <path>
Turn this book into a wisp skill: <book.txt>
```

The pipeline supports resume-from-checkpoint (`PIPELINE_STATE.md`), three user confirmation gates (book skeleton / shortlist / output mode), and 9 hard quality gates. Deliverables ship with regression eval cases (`test-prompts.json` / `output_cases`) so later revisions can re-run the evals and prevent quality drift.

## Installation

Option 1 — clone and copy into the user-level Wisp skill directory (available to all projects):

```bash
git clone https://github.com/Yu-Qiao-sjtu/wisp-cangjie.git
cp -r wisp-cangjie ~/.wisp/skills/
```

Option 2 — install from the Wisp store: select the `wisp-cangjie` package at this repository's root.

Dependencies: `python` + `pyyaml` (required); `tiktoken` / `jsonschema` (optional, auto-degrade when missing).
Environment self-check: `python scripts/distill.py doctor`.

## User manual

The manual is layered — go deeper only as needed:

| Layer | File | Audience | Content |
| --- | --- | --- | --- |
| ① Project handbook | `README.md` (this file) | Users | What it is, how to install, how to trigger, ecosystem position |
| ② Skill entry | `SKILL.md` | The Wisp agent | When to use, inputs (incl. source-type routing: paper vs. book mode), six-stage workflow, 9 hard gates, boundaries. **This is what the runtime loads** |
| ③ Stage SOPs | `references/methodology/` (10 docs) | The Wisp agent | Per-stage details: Adler overview, parallel extractors (5 book-mode + 1 paper-mode), triple verification, promotion gate, RIA++ capability cards, pressure test, delivery, and the paper-mode overlay (08) |

Also see:

- `docs/TUTORIAL.en.md` — **start here**: a first-distillation walkthrough from zero to installed;
- `docs/paper-reader-design.zh-CN.md` — design draft for Paper Reader, the upstream source-acquisition entry (direction → fetch → distillation, pending review);
- `references/extractors/` — 6 extractor prompts (framework / principle / case / counter-example / glossary + paper-mode reproducibility);
- `references/templates/` — output templates for each stage;
- `scripts/distill.py` — deterministic CLI (`doctor` / `compile` / `replan-output` / `update` / `repair` / `rollback` / `eval`); run `python scripts/distill.py --help`;
- `validation/README.md` — how to validate this package with the Wisp Science test suite.

## A Skill, not an Agent

**Wisp Cangjie is a Skill (a skill package), not an Agent.** It is process knowledge plus a deterministic toolbox that teaches a Wisp agent how to distill content:

- The **skill body** (`SKILL.md` + `references/`) is the textbook and SOP — it does nothing by itself;
- **`scripts/`** are passive deterministic tools: compile, evaluate, atomically publish, roll back — orchestration and checks only, they **never call a model**;
- The **Wisp agent** does the actual work: it loads this skill, follows the SOP, reads the text, distills with its model, and asks the user at confirmation gates. Parallel extraction uses the host's own sub-agent capability (serial fallback when unavailable).

Analogy: Wisp is the chef (Agent); Wisp Cangjie is a recipe book with measuring spoons and a timer (Skill). That is why it lives in `~/.wisp/skills/` and passes the Wisp store inspection — it is a skill package whose purpose is to **produce more skills**.

## Output structure

```text
books/<slug>/
├── PIPELINE_STATE.md          # resume-from-checkpoint state
├── BOOK_OVERVIEW.md           # whole-book understanding (skeleton/terms/critique)
├── verified.md                # units that passed triple verification
├── coverage-audit.md          # key-task coverage audit
├── GLOSSARY.md / DIGEST.md    # glossary / reader-facing digest
├── candidates/  rejected/     # audit trail
└── .distill/capabilities/     # Capability Bundle (single source of truth)
    ├── verified.yaml          # capability metadata (assets/schemas/capability-bundle.schema.json)
    ├── cards/<slug>.md        # RIA++ capability cards (R/I/A1/A2/E/B)
    └── destinations.json      # promoted / router destination map
```

Deliverables are sanitized in book mode: full provenance (book title, author, chapter titles, verbatim quotes) stays only in the local `books/<slug>/` audit trail — installed or published output never reveals the source document's identity. In paper mode, academic citation anchors (title / authors / year / DOI / journal / figure numbers) may ship with the output instead, while the full text, supplementary materials, and figures are never redistributed.

## Wisp Skill ecosystem

Wisp Cangjie is the "skill factory" of the [Wisp](https://github.com/xuzhougeng) ecosystem — long-form content in, house-format skills out. The Wisp ecosystem is developed and maintained by **Dr. Zhougeng Xu**:

| Role | Project | Description |
| --- | --- | --- |
| Research workbench | [wisp-science](https://github.com/xuzhougeng/wisp-science) | Local-first desktop AI research workbench: Python/R, MCP bioinformatics tools, SSH/WSL/GPU runtimes, skill store and packaging spec |
| Terminal workspace | [wispterm](https://github.com/xuzhougeng/wispterm) | Cross-platform terminal workspace (libghostty-vt) for remote development and AI agent workflows |
| Skill factory | **wisp-cangjie** (this repo) | Distills books / papers / videos / podcasts into installable Wisp skills |
| Example skills | **research-roadmap (bundled in this repo, see `skills/`)**, manuscript-polish, nsfc-grant-writing, signaling-pathway-atlas | Same house format, installed locally |

The `skills/` directory ships a field-tested ecosystem skill. Install it by copying:

```bash
cp -r skills/research-roadmap ~/.wisp/skills/
```

- **research-roadmap** — draws academic technical roadmaps for papers, reports, and grant applications (SVG + PNG, editable PPT / draw.io on demand).
  Hard routing rules (direct links for adjacent cards, orthogonal buses, shared main axis) are enforced by the bundled checker `skills/research-roadmap/scripts/check_graph.py`;
  see [`docs/technical-roadmap-experience.zh-CN.md`](docs/technical-roadmap-experience.zh-CN.md) for the methodology and the rework lessons behind it.

Every distilled skill ships with `SKILL.md` + `references/` + `scripts/` — drop it into `~/.wisp/skills/` and it joins the ecosystem. The more you distill, the richer it grows.

## Package layout

```text
wisp-cangjie/
├── SKILL.md                   # skill entry (When to use / Inputs / Workflow / Boundaries)
├── references/
│   ├── methodology/           # six-stage SOPs (00-overview + 01~07 + 08 paper-mode)
│   ├── extractors/            # 5 book-mode (+1 paper-mode) extractor prompts
│   └── templates/             # output templates
├── scripts/                   # distill.py compile/eval/update/repair/rollback CLI + 15 deterministic scripts
└── assets/
    ├── logo.svg / logo.png
    └── schemas/               # Capability Bundle / eval / contract JSON Schemas
```

## License

Apache-2.0
