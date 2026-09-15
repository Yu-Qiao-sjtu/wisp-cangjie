# Tutorial — Your first distillation

> This tutorial is for first-time users of Wisp Cangjie and walks you through one
> complete distillation from scratch. Expect 30–60 minutes, most of it waiting for
> the agent to run the pipeline.
> Languages: [简体中文](TUTORIAL.zh-CN.md) · [English](TUTORIAL.en.md)

## Before you start

1. **A Wisp environment** whose agent can see this skill (see the README "Installation" section).
2. **A text transcript of long-form content**: a book as TXT/EPUB/PDF, video subtitles (srt/ass), a podcast transcript, course notes, or a long article. Wisp Cangjie only consumes text — get a transcript first with a downloader/transcription tool; never let the agent distill from memory.
3. **Self-check** (optional but recommended):

```bash
python ~/.wisp/skills/wisp-cangjie/scripts/distill.py doctor
```

`doctor: PASS` means you are ready (missing `tiktoken`/`jsonschema` only affects optional features).

## Step 1 — Trigger the distillation

Say something natural to the Wisp agent, for example:

```text
Distill this book into skills: D:\books\demo-book.txt
```

Three things help: the **text path**, the **title/author** (or video title/creator), and your **purpose** (personal study vs. wiring into a daily workflow).

## Step 2 — Follow the pipeline (what you do)

Six stages run; you only weigh in at three confirmation gates:

| Stage | What happens | What you do |
| --- | --- | --- |
| 0 Overview | The agent reads the full text and produces skeleton/terms/critique (BOOK_OVERVIEW.md) | **Gate ①**: Is the skeleton right? Anything to emphasize? |
| 1 Parallel extraction | 5 extractors sweep the text and pool candidate methodologies | Wait |
| 1.5 Triple verification | Each candidate must pass: source sufficiency / executability / task value | **Gate ②**: Review the shortlist; object if needed |
| 1.6 Promotion gate | Decide which capabilities deserve standalone skills; the rest stay as cards | Wait |
| 2–3 Cards + linking | Each passing capability becomes an R/I/A1/A2/E/B card, cross-linked | Wait |
| 4 Pressure test | Blind trigger tests (including "should NOT trigger" decoys) + real task execution | Wait; failures are automatically reworked |
| 5 Compile & deliver | Compile to single or pack, generate the DIGEST.md long-form summary | **Gate ③**: accept the recommended output mode or switch; choose install location |

Two tips: **pilot first** — run one small item end-to-end before batching; **resume is safe** — if interrupted, just say "continue the distillation"; progress lives in `books/<slug>/PIPELINE_STATE.md`.

## Step 3 — Know the outputs

After the run, the working directory contains:

```text
books/<slug>/
├── DIGEST.md            ← read this first: the human-facing digest
├── GLOSSARY.md          ← glossary of the whole work
├── coverage-audit.md    ← which tasks are covered, which are not (honestly logged)
└── dist/<...>/          ← the compiled skill package (this is what you install)
```

The compiled artifact is a standard skill package: entry `SKILL.md` (triggers + routing table) + `references/capabilities/` (capability cards) + `references/overview.md|glossary.md|cheatsheet.md`. For daily use the entry SKILL.md is enough; to go deeper, follow the routing table to the relevant capability card.

Note: **deliverables are sanitized** — the source document's title, author, chapter titles, and verbatim quotes never appear in the installed skill; full provenance stays in the local `books/<slug>/` audit trail.

## Step 4 — Install

Copy the compiled package into the user-level Wisp skill directory:

```bash
cp -r books/<slug>/dist/<entry-name> ~/.wisp/skills/
```

Restart/refresh the Wisp runtime, then try one "should trigger" question to confirm it fires. Never install **both** the single and pack variants of the same content — pick one.

## Maintenance

- **Prevent regression after edits**: the compiled package's `test-prompts.json` is a regression suite. After editing, re-run `python scripts/distill.py eval trigger ...` (trigger evals) or `eval output ...` (output evals).
- **Content updated**: feed new material via `python scripts/distill.py update --pack <dir> --add <file>`; it diffs and generates pending tasks without silently changing artifacts.
- **Something broke**: `python scripts/distill.py rollback --pack <dir> --list` shows snapshots to roll back to.
- **You hand-edited an artifact**: the compiler refuses to silently overwrite local edits — choose one: `--force-overwrite` (discard edits) / backfill edits into the Bundle and recompile / abort.

## FAQ

- **No subtitles for my video?** Get a transcript with a downloader/transcription tool first; the agent will stop and ask for text rather than distill from memory.
- **What content suits distillation?** Anything with extractable methodology: methodology books, tutorials, interviews, experience-sharing talks. Pure narrative/entertainment gets filtered out by triple verification.
- **Will the output reveal my source?** No — deliverables are sanitized (see above); full provenance stays in your local audit trail.
- **How many at once?** No hard limit, but pilot one item and check quality before batching.
- **Compile says "local modifications detected"?** See the three-way choice at the end of "Maintenance".

## Next steps

- Why the pipeline is designed this way → `references/methodology/00-overview.md`
- To improve this skill → read the hard gates in `SKILL.md`, then run the store validation in `validation/`
