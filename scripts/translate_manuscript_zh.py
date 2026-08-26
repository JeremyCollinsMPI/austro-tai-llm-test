#!/usr/bin/env python3
"""Translate paper/MANUSCRIPT.md to Chinese via the project NLP API (gpt-4.1)."""
from __future__ import annotations

import json
import re
import time
from pathlib import Path

from src.nlp_client import chat

ROOT = Path(__file__).resolve().parents[1]
PAPER = ROOT / "paper"
SRC = PAPER / "MANUSCRIPT.md"
OUT = PAPER / "MANUSCRIPT_zh.md"
CACHE = PAPER / "translation_cache_zh.json"
PROGRESS = PAPER / "translation_progress_zh.md"

SYSTEM = """你是一位专业的学术翻译，专长历史语言学与计算语言学。
请将用户提供的英文 Markdown 学术论文片段译为规范、流畅的简体中文。

硬性要求：
1. 只输出译文 Markdown，不要前言、后记或解释。
2. 保留全部 Markdown 结构：标题层级、表格、列表、链接、图片路径、LaTeX/数学、代码块原样。
3. 专名处理：Austro-Tai→澳台假说；Austronesian→南岛语；Kra-Dai/Tai-Kadai→侗台语（壮侗/台-卡岱）；PAN→原始南岛语（PAN）；PKD→原始侗台语（PKD）；Lexibank、Blust、ABVD、Concepticon、Zenodo、Diachronica、人名与 DOI 保持原文。
4. meaning-blind→意义盲（不呈现词义）；permutation→置换检验；generosity→宽裕度；hit→命中；Tier A→A 级；Study 1/2→研究1/研究2。
5. 参考文献条目（作者、年份、题名、期刊）保持拉丁文原样，仅可翻译小节标题。
6. 代码、文件路径、命令、JSON/CSV 文件名不要翻译。
7. 文风：正式学术中文，避免生硬直译与西式长句堆砌；数字与统计符号保持原样。
"""


def split_chunks(text: str, soft_limit: int = 4200) -> list[tuple[str, str]]:
    """Split markdown into chunks on # / ## headings, respecting size."""
    lines = text.splitlines(keepends=True)
    blocks: list[str] = []
    cur: list[str] = []

    def flush() -> None:
        nonlocal cur
        if cur:
            blocks.append("".join(cur))
            cur = []

    for line in lines:
        if re.match(r"^#{1,2} ", line) and cur and sum(len(x) for x in cur) > 200:
            flush()
        cur.append(line)
        if sum(len(x) for x in cur) >= soft_limit and re.match(r"^#{2,3} ", line):
            # start of a subsection that already overflowed: keep going until next heading flush
            pass
    flush()

    # Re-split any block that is still huge on ### or blank lines
    refined: list[str] = []
    for block in blocks:
        if len(block) <= soft_limit * 1.5:
            refined.append(block)
            continue
        parts = re.split(r"(?m)^(#{2,3} .+)$", block)
        acc = parts[0]
        i = 1
        while i < len(parts):
            piece = parts[i] + (parts[i + 1] if i + 1 < len(parts) else "")
            if len(acc) + len(piece) <= soft_limit:
                acc += piece
            else:
                if acc.strip():
                    refined.append(acc)
                acc = piece
            i += 2
        if acc.strip():
            refined.append(acc)

    out: list[tuple[str, str]] = []
    for idx, ch in enumerate(refined, start=1):
        title = ""
        m = re.search(r"(?m)^#{1,3} (.+)$", ch)
        if m:
            title = m.group(1).strip()[:60]
        slug = re.sub(r"[^a-zA-Z0-9]+", "_", title)[:40].strip("_") or "chunk"
        out.append((f"{idx:02d}_{slug}", ch))
    return out


def load_cache() -> dict[str, str]:
    if CACHE.exists():
        return json.loads(CACHE.read_text(encoding="utf-8"))
    return {}


def save_cache(cache: dict[str, str]) -> None:
    CACHE.write_text(json.dumps(cache, ensure_ascii=False, indent=2), encoding="utf-8")


def translate_chunk(english: str, *, max_tokens: int = 12000) -> str:
    user = (
        "请翻译以下 Markdown 片段为简体中文（只输出译文）：\n\n"
        + english
    )
    return chat(
        user,
        system_content=SYSTEM,
        max_completion_tokens=max_tokens,
    )


def main() -> None:
    english = SRC.read_text(encoding="utf-8")
    chunks = split_chunks(english)
    print(f"Split into {len(chunks)} chunks from {SRC}")
    cache = load_cache()
    translated: list[str] = []

    for i, (cid, text) in enumerate(chunks, start=1):
        key = cid + "::" + str(hash(text))
        # also try stable key by cid+len
        stable = f"{cid}::{len(text)}::{text[:80]}"
        if stable in cache:
            zh = cache[stable]
            print(f"[{i}/{len(chunks)}] cache hit {cid} ({len(text)} chars)")
        else:
            print(f"[{i}/{len(chunks)}] translating {cid} ({len(text)} chars) ...")
            zh = translate_chunk(text)
            # strip accidental fences
            zh = zh.strip()
            if zh.startswith("```"):
                zh = re.sub(r"^```(?:markdown|md)?\n", "", zh)
                zh = re.sub(r"\n```$", "", zh)
            cache[stable] = zh
            save_cache(cache)
            time.sleep(0.4)
        translated.append(zh)
        PROGRESS.write_text(
            "\n\n".join(translated) + "\n",
            encoding="utf-8",
        )

    note = (
        "> 本文为英文工作预印本的中文译本（经项目 NLP API / `gpt-4.1` 翻译并整理）；"
        "实证数字与 `MANUSCRIPT.md` 冻结快照一致（2026年8月）。\n\n"
    )
    body = "\n\n".join(translated).strip() + "\n"
    if not body.lstrip().startswith(">"):
        body = note + body
    OUT.write_text(body, encoding="utf-8")
    print(f"Wrote {OUT} ({len(body)} chars)")


if __name__ == "__main__":
    main()
