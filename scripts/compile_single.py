#!/usr/bin/env python
"""compile_single.py — 从 Capability Bundle 确定性编译 single 入口（v0.2，Bundle 原生）。

输入是唯一编译事实源 Capability Bundle：

    <bundle-dir>/                    # 通常是 books/<slug>/.distill/capabilities/
    ├── verified.yaml                # capability-bundle.schema.json
    ├── destinations.json            # 去向映射
    ├── cards/<slug>.md              # RIA 能力卡（R/I/A1/A2/E/B，正文逐字保留）
    └── book/{overview.md,glossary.md}

输出（--variant single）：1 个发现入口 + 全部能力卡 + overview/glossary/cheatsheet/索引。
--variant router 生成 compact pack 的来源路由入口视图（晋级能力在路由表标注改由独立 Skill 处理）。

本脚本纯确定性、不调用模型。主入口 description、核心原则、意图路由全部来自 Bundle，脚本不猜测。

用法: python scripts/compile_single.py --bundle <dir> --out <dir> [--variant single|router]
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from distill_common import TOOL_VERSION, load_yaml  # noqa: E402

MD_LINK_RE = re.compile(r"\[([^\]]+)\]\(([^)#\s]+?)(?:#[^)\s]*)?\)")


def sanitize_links(text: str, available: set[str]) -> str:
    """把指向未随产物分发文件的相对链接降级为纯文本，避免死链。"""

    def repl(m: re.Match) -> str:
        target = m.group(2)
        if target.startswith(("http://", "https://", "mailto:", "/")):
            return m.group(0)
        return m.group(0) if target.lstrip("./") in available else m.group(1)

    return MD_LINK_RE.sub(repl, text)


def active_capabilities(bundle: dict) -> list[dict]:
    return [c for c in bundle["capabilities"] if c.get("status", "active") == "active"]


def promoted_capabilities(bundle: dict) -> list[dict]:
    return [c for c in active_capabilities(bundle) if c.get("promotion", {}).get("destination") == "promoted"]


def capability_resources(bundle_dir: Path, cap: dict) -> dict[str, str]:
    """只打包显式声明的 UTF-8 资源，不跟随符号链接、不执行脚本。"""
    resources = cap.get("resources", [])
    if not isinstance(resources, list) or any(not isinstance(p, str) for p in resources):
        raise ValueError("resources 必须是相对文件路径列表")
    if len(set(resources)) != len(resources):
        raise ValueError("resources 不能重复声明同一路径")
    files = {}
    for rel in resources:
        # 采用可移植的受限路径，既防越界，也使生成的 Markdown 链接无歧义。
        if not re.fullmatch(r"resources/(?:[A-Za-z0-9_-]+/)*[A-Za-z0-9_-]+(?:\.[A-Za-z0-9_-]+)*", rel):
            raise ValueError(f"无效资源路径（必须在 resources/ 下）: {rel!r}")
        path = bundle_dir / rel
        cur = bundle_dir
        for part in Path(rel).parts:
            cur = cur / part
            if cur.is_symlink():
                raise ValueError(f"资源不能是符号链接: {rel}")
        if not path.resolve().is_relative_to(bundle_dir.resolve()) or not path.is_file():
            raise ValueError(f"资源不存在、不是文件或越界: {rel}")
        try:
            content = path.read_bytes().decode("utf-8")
        except UnicodeDecodeError as exc:
            raise ValueError(f"当前只支持 UTF-8 文本资源: {rel}") from exc
        if "\x00" in content:
            raise ValueError(f"不支持二进制资源: {rel}")
        files[rel] = content
    return files


def resource_links(cap: dict, prefix: str = "") -> str:
    if not cap.get("resources"):
        return ""
    lines = ["", "## 配套资源", "", "路径相对于本文件；脚本需先检查运行条件，不因附带而自动执行。", ""]
    lines.extend(f"- [{rel}]({prefix}{rel})" for rel in cap["resources"])
    return "\n".join(lines) + "\n"


def router_table(caps: list[dict], variant: str) -> str:
    rows = ["| 用户意图 | 先读 | 补读/备注 |", "|---|---|---|"]
    for cap in caps:
        intents = "；".join(cap["intents"])
        card = f"references/capabilities/{cap['slug']}.md"
        extra = "、".join(f"references/capabilities/{s}.md" for s in cap.get("also_read", [])) or "—"
        if variant == "router" and cap.get("promotion", {}).get("destination") == "promoted":
            extra = f"已晋级为独立 Skill `{cap['slug']}`（已安装时优先直接使用；本卡仅作原文与背景补充）"
        rows.append(f"| {intents} | {card} | {extra} |")
    return "\n".join(rows)


def build_entry_md(bundle: dict, variant: str) -> str:
    entry = bundle["entry"] if variant == "single" else bundle["router_entry"]
    caps = active_capabilities(bundle)
    book = bundle["book"]
    entrypoint_count = 1 if variant == "single" else 1 + len(promoted_capabilities(bundle))
    fm_lines = [
        "---",
        f"name: {entry['name']}",
        "description: |",
        *[f"  {line}" for line in entry["description"].strip().splitlines()],
        "metadata:",
        f"  distill.generated-by: {TOOL_VERSION}",
        f"  distill.variant: {variant}",
        f"  distill.bundle-id: {bundle['bundle_id']}",
        f"  distill.capability-count: {len(caps)}",
        f"  distill.entrypoint-count: {entrypoint_count}",
        "---",
        "",
    ]
    e = bundle["entry"]
    principles = "\n".join(f"{i}. {p}" for i, p in enumerate(e["core_principles"], 1))
    out_of_scope = "\n".join(f"- {x}" for x in e["out_of_scope"])
    stops = "\n".join(f"- {x}" for x in e["stop_conditions"])
    prereq = e.get("prerequisites") or []
    prereq_block = ""
    if prereq:
        items = "\n".join(f"{i}. {p}" for i, p in enumerate(prereq, 1))
        confirm_lines = "\n".join(f"  {i}. {p} → 已具备 / 缺失？" for i, p in enumerate(prereq, 1))
        pointer = "\n各输入的具体获取方法（数据库导出步骤、无订阅替代方案、本地语料模式）见 `references/input-guide.md`。\n" if e.get("input_guide") else "\n"
        prereq_block = f"""
## 运行前置条件（必须由用户完成/提供的部分）

{items}
{pointer}
**开始前必做（强制）**：激活本技能后、执行任何分析之前，必须先向用户出示下方「输入确认卡」并等待答复；用户确认可用材料与输入路线（A：数据库导出 / B：替代数据库 / C：本地语料并声明覆盖限制）之前，不得开始工作，也不得默认替用户选择路线。

> 📋 输入确认卡（原样出示给用户）
> 请逐条确认以下输入的状态，并选择输入路线：
{confirm_lines}
> 输入路线：A（Scopus 导出）｜ B（替代数据库，见 input-guide）｜ C（本地语料，将声明覆盖限制）
> （路线 A/B 的操作步骤见 `references/input-guide.md`）

以上环节 AI 无法代劳或需要用户材料时，**先向用户说明并等待提供，不要跳过或臆造数据**；用户选择路线 C 时，所有"未见报道/空白"类结论必须显式限定在语料范围内。

"""

    body = f"""# {book['title']} — {'全书能力入口' if variant == 'single' else '来源路由入口（compact pack）'}

## 触发与不触发

**适用**：与本书能力域相关的咨询与任务（见下方路由表的意图列）。
**不适用**：
{out_of_scope}
{prereq_block}
## 核心原则（常驻速览，概览类问题读到这里即可回答）

{principles}

## 能力路由（先读本表，按意图加载 1 张能力卡）

{router_table(caps, variant)}

**非能力类查询**：
- 书名/作者/章节/整书概览 → references/overview.md
- 术语解释 → references/glossary.md
- 决策规则速查（不需要原文依据时） → references/cheatsheet.md
- 完整意图与关键词索引（本表未覆盖的意图先查这里） → references/capability-index.md

## 加载规则

- 每次任务先读本文件，再按路由表加载 **1** 张能力卡；任务明确跨域时最多加载 2 张。
- 概览/书名类问题不加载能力卡，用「核心原则」与 overview.md 回答。
- 路由表与 capability-index.md 都无法命中的意图，明确告知超出本书范围，不要硬套。

## 边界与判停

{stops}
"""
    return "\n".join(fm_lines) + body


def build_index_md(caps: list[dict]) -> str:
    rows = ["# 能力索引（完整版）", "", "| capability_id | 标题 | 重要度 | 意图 | 关键词 | 能力卡 |", "|---|---|---|---|---|---|"]
    for c in caps:
        rows.append(
            f"| {c['capability_id']} | {c['title']} | {c['importance']} | {'；'.join(c['intents'])} | "
            f"{'、'.join(c['keywords'])} | capabilities/{c['slug']}.md |"
        )
    return "\n".join(rows) + "\n"


def build_cheatsheet_md(caps: list[dict], book: dict) -> str:
    rows = [f"# 决策规则速查 — {book['title']}", "", "| 能力 | 一句话规则 |", "|---|---|"]
    for c in caps:
        rows.append(f"| {c['title']} | {c['one_liner']} |")
    rows.append("")
    rows.append("> 速查只给结论；需要原文依据、案例或反例时读对应能力卡。")
    return "\n".join(rows) + "\n"


def build_tree(bundle_dir: Path, variant: str) -> dict[str, str]:
    """返回 {相对路径: 内容}。纯函数，供 compile_pack.py 与 distill.py 复用。"""
    bundle = load_yaml(bundle_dir / "verified.yaml")
    caps = active_capabilities(bundle)

    files: dict[str, str] = {}
    files["SKILL.md"] = build_entry_md(bundle, variant)
    for cap in caps:
        files.update(capability_resources(bundle_dir, cap))
        files[f"references/capabilities/{cap['slug']}.md"] = (
            (bundle_dir / cap["card"]).read_text(encoding="utf-8") + resource_links(cap, "../../"))
    files["references/capability-index.md"] = build_index_md(caps)
    files["references/cheatsheet.md"] = build_cheatsheet_md(caps, bundle["book"])
    guide = (bundle.get("entry") or {}).get("input_guide")
    if guide:
        files["references/input-guide.md"] = guide.strip() + "\n"

    available = {p.removeprefix("references/") for p in files if p.startswith("references/")}
    for name in ("overview.md", "glossary.md"):
        src = bundle_dir / "book" / name
        if src.exists():
            files[f"references/{name}"] = sanitize_links(src.read_text(encoding="utf-8"), available)
    return files


def write_tree(files: dict[str, str], out: Path) -> None:
    for rel, content in files.items():
        p = out / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_bytes(content.encode("utf-8"))


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--bundle", required=True, help="Capability Bundle 目录（含 verified.yaml）")
    ap.add_argument("--out", required=True)
    ap.add_argument("--variant", choices=["single", "router"], default="single")
    args = ap.parse_args()

    files = build_tree(Path(args.bundle), args.variant)
    write_tree(files, Path(args.out))
    print(f"已生成 {args.variant} 产物: {args.out}（{len(files)} 个文件）")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
