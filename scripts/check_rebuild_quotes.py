#!/usr/bin/env python
"""check_rebuild_quotes.py — 盲测重建输出的出处机械回查（纯确定性，不调用模型）。

配合阶段 4b 语义保真测试（`references/methodology/06b-stage4-semantic-fidelity.md`）
的「出处硬约束」：重建链每环节标注的材料内出处必须能在材料中逐字回查。

按约定格式提取每行 `出处: "引文"`（可带 `——` 注释后缀），归一化（忽略空白 /
标点 / 引号样式）后回查材料文件。

用法:
  python scripts/check_rebuild_quotes.py <blind-output.md> --material <card.md> [--material <f2> ...]
退出码: 0 = 全部出处可回查；1 = 存在未命中；2 = 输入无效。
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

QUOTE_LINE_RE = re.compile(r"出处[:：]\s*(.+)$")
STRIP_CHARS = " \"'\u201c\u201d\u2018\u2019「」『』 \t"


def normalize(s: str) -> str:
    return "".join(ch for ch in s.lower() if ch.isalnum())


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description="盲测重建输出的出处机械回查（阶段 4b）")
    ap.add_argument("output", help="盲测输出文件（含 `出处: \"…\"` 行）")
    ap.add_argument("--material", action="append", required=True, help="材料文件（卡片 / 编译产物，可多次给出）")
    args = ap.parse_args(argv[1:])

    out_path = Path(args.output)
    mats = [Path(m) for m in args.material]
    for p in [out_path, *mats]:
        if not p.is_file():
            print(f"[input] 文件不存在: {p}")
            return 2
    mat_norm = [normalize(p.read_text(encoding="utf-8")) for p in mats]

    lines = out_path.read_text(encoding="utf-8").splitlines()
    total = miss = 0
    for i, line in enumerate(lines, 1):
        m = QUOTE_LINE_RE.search(line)
        if not m:
            continue
        seg = m.group(1)
        if "——" in seg:
            seg = seg.split("——", 1)[0]
        quote = seg.strip().strip(STRIP_CHARS)
        nq = normalize(quote)
        if not nq:
            continue
        total += 1
        if any(nq in mn for mn in mat_norm):
            continue
        miss += 1
        print(f"MISS  行 {i}: 出处未能回查: {quote[:80]}…")
    print(f"出处回查: {total} 条, 命中 {total - miss}, 未命中 {miss}")
    return 1 if miss else 0


if __name__ == "__main__":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
    raise SystemExit(main(sys.argv))
