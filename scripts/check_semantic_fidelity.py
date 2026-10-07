#!/usr/bin/env python
"""check_semantic_fidelity.py — 语义保真机械检查（纯确定性，不调用模型）。

对应方法论 v2.4「语义留痕不变量」的机械部分（issue #15）：

层 A  母本结构（按 assets/schemas/semantic-map.schema.json）
      - schema_version / source_id / mode / nodes 必填；id / type / status / relation /
        task_ids 的模式与枚举；links.to 指向的节点必须存在；
      - 每个节点 source_anchor.location 必填；explicit 节点 quote 必填且 ≤150 字；
      - 每条 claim 关联 ≥1 evidence 节点，或显式标 missing（不虚报零缺口）。
层 B  锚点可回查（--source <源文>）
      - 引文归一化（忽略空白 / 标点 / Markdown 强调标记 / 引号样式）后应能在源文中找到；
      - 拼接引用（多片段用 / 、 ； 或换行分隔）逐段核验，报告“分段命中 n/m 段”。
层 C  候选挂链（--candidates / --verified，v2.4 链位置核查的机械部分）
      - 候选项携带 chain_refs 时，引用必须指向母本已存在的节点（悬空引用记 ERROR）；
      - decision=verified 的候选项必须挂回母本 ≥1 节点（无链记 ERROR，对应“挂不上
        母本逻辑链的候选不得标 verified”）。

用法:
  python scripts/check_semantic_fidelity.py <semantic-map.md> \
      [--source <源文文件>] [--candidates <候选项目录或文件>] [--verified <verified.md>]
退出码: 0 = 无 ERROR；1 = 存在 ERROR；2 = 输入无效。
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

import yaml

ID_RE = re.compile(r"^(c|e|r|a|b)[0-9]{2,}$")
SOURCE_ID_RE = re.compile(r"^src-[a-z0-9-]+$")
TASK_ID_RE = re.compile(r"^task-[0-9]+$")
TYPE_OF_PREFIX = {"c": "claim", "e": "evidence", "r": "reasoning", "a": "assumption", "b": "boundary"}
RELATIONS = {"supports", "derives", "qualifies", "contradicts", "elaborates"}
STATUSES = {"explicit", "inferred", "missing"}
MODES = {"book", "paper"}
QUOTE_MAX = 150  # 字符数；英文 ≤100 词由人工复核

YAML_BLOCK_RE = re.compile(r"```yaml\s*\n(.*?)```", re.S)
SEG_SPLIT_RE = re.compile(r"[/、;；|]|\n|…")
KEY_LINE_RE = re.compile(r"^(\s*(?:- )?[A-Za-z0-9_\u4e00-\u9fff]+):\s+(.*)$")

errors: list[str] = []
warnings: list[str] = []


def repair_yaml_like(block: str) -> str:
    """抢救非严格 YAML：给“值内含冒号”的裸行加引号（历史记录的宽松格式）。"""
    out = []
    for line in block.splitlines():
        m = KEY_LINE_RE.match(line)
        if m and ": " in m.group(2):
            val = m.group(2)
            if (val.startswith('"') and val.endswith('"')) or (val.startswith("'") and val.endswith("'")):
                out.append(line)
                continue
            out.append(line.split(":", 1)[0] + ': "' + val.replace('"', '\\"') + '"')
        else:
            out.append(line)
    return "\n".join(out)


def load_yaml_blocks(text: str) -> list:
    """返回文件中全部 ```yaml 块解析结果的扁平列表（dict 与 list 条目都收）。

    解析失败时按宽容规则抢救（值内含冒号的裸行加引号）并记 WARN——历史记录
    常为非严格 YAML，机械校验不应因此静默跳过；建议未来产物直接使用严格格式。
    """
    out: list = []
    rescued: list[str] = []
    for block in YAML_BLOCK_RE.findall(text):
        try:
            data = yaml.safe_load(block)
        except yaml.YAMLError:
            try:
                data = yaml.safe_load(repair_yaml_like(block))
                rescued.append(block.strip().splitlines()[0][:40] if block.strip() else "?")
            except yaml.YAMLError as err2:
                errors.append(f"[yaml] 块解析失败且抢救无效: {err2}")
                continue
        if isinstance(data, list):
            out.extend(data)
        elif data is not None:
            out.append(data)
    if rescued:
        warnings.append(
            f"[yaml] {len(rescued)} 个块非严格 YAML，已按宽容规则抢救解析"
            f"（建议未来产物用严格格式）; 样例: {rescued[0]}…"
        )
    return out


def normalize(s: str) -> str:
    """归一化：小写化 ASCII、去除空白与全部标点，仅保留字母 / 数字 / 汉字。"""
    return "".join(ch for ch in s.lower() if ch.isalnum())


def check_structure(map_data: dict) -> list[dict]:
    """层 A：母本结构校验。返回节点列表（结构错误也继续，尽量多报问题）。"""
    if map_data.get("schema_version") != 1:
        errors.append("[A] schema_version 缺失或不等于 1")
    sid = map_data.get("source_id")
    if not (isinstance(sid, str) and SOURCE_ID_RE.match(sid)):
        errors.append(f"[A] source_id 缺失或不符合 ^src-[a-z0-9-]+$: {sid!r}")
    if map_data.get("mode") not in MODES:
        errors.append(f"[A] mode 缺失或非 book/paper: {map_data.get('mode')!r}")
    nodes = map_data.get("nodes")
    if not (isinstance(nodes, list) and nodes):
        errors.append("[A] nodes 缺失或为空")
        return []
    ids: set[str] = set()
    for node in nodes:
        if isinstance(node, dict) and isinstance(node.get("id"), str):
            if node["id"] in ids:
                errors.append(f"[A] 节点 id 重复: {node['id']}")
            ids.add(node["id"])
    counts: dict[str, int] = {}
    for node in nodes:
        if not isinstance(node, dict):
            errors.append(f"[A] 节点不是映射: {node!r}")
            continue
        nid = node.get("id", "?")
        ntype = node.get("type")
        counts[ntype if isinstance(ntype, str) else "?"] = counts.get(ntype if isinstance(ntype, str) else "?", 0) + 1
        if not (isinstance(nid, str) and ID_RE.match(nid)):
            errors.append(f"[A] {nid}: id 不符合 ^(c|e|r|a|b)[0-9]{{2,}}$")
        elif ntype in TYPE_OF_PREFIX.values() and TYPE_OF_PREFIX[nid[0]] != ntype:
            warnings.append(f"[A] {nid}: id 前缀（{TYPE_OF_PREFIX[nid[0]]}）与 type（{ntype}）不一致")
        if ntype not in TYPE_OF_PREFIX.values():
            errors.append(f"[A] {nid}: type 非法: {ntype!r}")
        if node.get("status") not in STATUSES:
            errors.append(f"[A] {nid}: status 非法: {node.get('status')!r}")
        statement = node.get("statement")
        if not (isinstance(statement, str) and statement.strip()):
            errors.append(f"[A] {nid}: statement 缺失或为空")
        anchor = node.get("source_anchor")
        if not (isinstance(anchor, dict) and isinstance(anchor.get("location"), str) and anchor["location"].strip()):
            errors.append(f"[A] {nid}: source_anchor.location 缺失（锚点全覆盖要求每节点有出处）")
        quote = anchor.get("quote") if isinstance(anchor, dict) else None
        if node.get("status") == "explicit":
            if not (isinstance(quote, str) and quote.strip()):
                errors.append(f"[A] {nid}: explicit 节点 quote 缺失")
            elif len(quote) > QUOTE_MAX:
                warnings.append(f"[A] {nid}: quote 长度 {len(quote)} > {QUOTE_MAX} 字")
        elif isinstance(quote, str) and len(quote) > QUOTE_MAX:
            warnings.append(f"[A] {nid}: quote 长度 {len(quote)} > {QUOTE_MAX} 字")
        links = node.get("links", [])
        if links is None:
            links = []
        if not isinstance(links, list):
            errors.append(f"[A] {nid}: links 不是列表")
            links = []
        for link in links:
            if not isinstance(link, dict) or not isinstance(link.get("to"), str):
                errors.append(f"[A] {nid}: links 条目缺 to: {link!r}")
                continue
            if not ID_RE.match(link["to"]):
                errors.append(f"[A] {nid}: links.to 不符合节点 id 模式: {link['to']!r}")
            elif link["to"] not in ids:
                errors.append(f"[A] {nid}: links.to 指向不存在的节点: {link['to']}")
            if link.get("relation") not in RELATIONS:
                errors.append(f"[A] {nid}: relation 非法: {link.get('relation')!r}")
        for tid in node.get("task_ids", []) or []:
            if not (isinstance(tid, str) and TASK_ID_RE.match(tid)):
                warnings.append(f"[A] {nid}: task_ids 条目不符合 ^task-[0-9]+$: {tid!r}")
    # claim 支撑检查：每条 claim 关联 ≥1 evidence，或显式标 missing
    ev_ids = {n["id"] for n in nodes if isinstance(n, dict) and isinstance(n.get("id"), str) and n.get("type") == "evidence"}
    for node in nodes:
        if not isinstance(node, dict) or node.get("type") != "claim":
            continue
        if node.get("status") == "missing":
            continue
        tos = [l.get("to") for l in (node.get("links") or []) if isinstance(l, dict)]
        if not any(isinstance(t, str) and t in ev_ids for t in tos):
            errors.append(f"[A] {node.get('id')}: claim 未关联任何 evidence（应显式标 missing 或补证据节点）")
    print(f"[A] 母本结构: {len(nodes)} 节点 (" + " / ".join(f"{k} {v}" for k, v in sorted(counts.items())) + ")")
    return nodes


def check_anchors(nodes: list[dict], source_text: str) -> None:
    """层 B：锚点可回查（引文归一化后回查源文；拼接引用分段核验）。"""
    src_norm = normalize(source_text)
    full_hit = seg_hit = miss = exempt = 0
    for node in nodes:
        anchor = node.get("source_anchor")
        quote = anchor.get("quote") if isinstance(anchor, dict) else None
        nid = node.get("id", "?")
        if node.get("status") == "missing" and not (isinstance(quote, str) and quote.strip()):
            exempt += 1
            continue
        if not (isinstance(quote, str) and quote.strip()):
            miss += 1
            warnings.append(f"[B] {nid}: 无引文，无法回查（非 missing 节点）")
            continue
        if normalize(quote) and normalize(quote) in src_norm:
            full_hit += 1
            continue
        segments = [s for s in SEG_SPLIT_RE.split(quote) if len(normalize(s)) >= 4]
        if len(segments) > 1:
            hit = [s for s in segments if normalize(s) in src_norm]
            if len(hit) == len(segments):
                seg_hit += 1
                continue
            miss += 1
            lost = [s.strip() for s in segments if normalize(s) not in src_norm]
            warnings.append(f"[B] {nid}: 分段命中 {len(hit)}/{len(segments)}，未命中片段: {' | '.join(lost[:3])}")
        else:
            miss += 1
            warnings.append(f"[B] {nid}: 引文未能在源文中回查: {quote[:60]}…")
    total = full_hit + seg_hit + miss
    print(f"[B] 锚点可回查: 整段命中 {full_hit} / 分段命中 {seg_hit} / 未命中 {miss}" + (f" / 豁免 {exempt}（missing 无引文）" if exempt else "") + f"（共 {total} 条应查引文）")


def check_chains(candidates: list[dict], verified: list[dict], node_ids: set[str]) -> None:
    """层 C：候选挂链（带链引用存在性 + verified 必须有链）。"""
    has_chain: dict[str, int] = {}
    dangling = 0
    for cand in candidates:
        cid = cand.get("id")
        refs = cand.get("chain_refs")
        if refs is None:
            if isinstance(cid, str):
                has_chain.setdefault(cid, 0)
            continue
        if not isinstance(refs, list) or not refs:
            warnings.append(f"[C] 候选 {cid}: chain_refs 为空（如为 verified 将违规）")
            if isinstance(cid, str):
                has_chain.setdefault(cid, 0)
            continue
        if isinstance(cid, str):
            has_chain[cid] = len(refs)
        for ref in refs:
            if ref not in node_ids:
                dangling += 1
                errors.append(f"[C] 候选 {cid}: chain_refs 指向不存在的母本节点: {ref!r}")
    with_chain = sum(1 for v in has_chain.values() if v > 0)
    print(f"[C] 候选挂链: {len(candidates)} 个候选项 / {with_chain} 个带链" + (f" / 悬空引用 {dangling}" if dangling else ""))
    if not verified:
        return
    v_total = v_ok = 0
    v_bad: list[str] = []
    for item in verified:
        if not isinstance(item, dict) or item.get("decision") != "verified":
            continue
        v_total += 1
        vid = item.get("id")
        if isinstance(vid, str) and has_chain.get(vid, 0) > 0:
            v_ok += 1
        else:
            v_bad.append(str(vid))
    if v_bad:
        errors.append(
            f"[C] verified 缺链 {len(v_bad)} 项（v2.4 链位置核查：挂不上母本逻辑链的候选不得标 verified，应转 needs_review）: "
            + ", ".join(v_bad)
        )
    print(f"[C] verified 条目: {v_total} 项中 {v_ok} 项已挂链，{len(v_bad)} 项缺链")


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description="语义保真机械检查（issue #15）")
    ap.add_argument("map", help="semantic-map.md 路径")
    ap.add_argument("--source", help="源文文件（启用层 B 锚点可回查）")
    ap.add_argument("--candidates", help="候选项目录或文件（启用层 C 挂链检查）")
    ap.add_argument("--verified", help="verified.md（检查 decision=verified 条目是否挂链）")
    args = ap.parse_args(argv[1:])

    map_path = Path(args.map)
    if not map_path.is_file():
        print(f"[input] 文件不存在: {map_path}")
        return 2
    blocks = load_yaml_blocks(map_path.read_text(encoding="utf-8"))
    map_data = next((b for b in blocks if isinstance(b, dict) and "nodes" in b), None)
    if map_data is None:
        print(f"[input] 未在 {map_path} 中找到含 nodes 的内嵌 YAML 块")
        return 2

    print(f"=== 语义保真检查: {map_path} ===")
    nodes = check_structure(map_data)

    if args.source:
        src = Path(args.source)
        if not src.is_file():
            print(f"[input] 源文不存在: {src}")
            return 2
        check_anchors(nodes, src.read_text(encoding="utf-8"))
    else:
        print("[B] 锚点可回查: 跳过（未提供 --source）")

    if args.candidates or args.verified:
        candidates: list[dict] = []
        if args.candidates:
            cand_path = Path(args.candidates)
            files = sorted(cand_path.rglob("*.md")) if cand_path.is_dir() else [cand_path]
            for f in files:
                candidates.extend(b for b in load_yaml_blocks(f.read_text(encoding="utf-8")) if isinstance(b, dict))
        verified: list[dict] = []
        if args.verified:
            vf = Path(args.verified)
            if not vf.is_file():
                print(f"[input] verified 文件不存在: {vf}")
                return 2
            verified = [b for b in load_yaml_blocks(vf.read_text(encoding="utf-8")) if isinstance(b, dict)]
        node_ids = {n["id"] for n in nodes if isinstance(n, dict) and isinstance(n.get("id"), str)}
        check_chains(candidates, verified, node_ids)
    else:
        print("[C] 候选挂链: 跳过（未提供 --candidates / --verified）")

    print()
    for w in warnings:
        print(f"WARN  {w}")
    for e in errors:
        print(f"ERROR {e}")
    print(f"\n结果: {len(errors)} errors, {len(warnings)} warnings")
    return 1 if errors else 0


if __name__ == "__main__":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
    raise SystemExit(main(sys.argv))
