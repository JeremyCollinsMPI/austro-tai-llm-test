"""Austronesian phylogenetic clade labels and Lexibank form sampling."""

from __future__ import annotations

import csv
import random
from collections import defaultdict
from pathlib import Path

from .config import (
    AN_CLADE_FLOORS,
    AN_SAMPLE_TARGET,
    AN_SAMPLE_SEED,
    LEXIBANK_DIR,
)

AN_CLADES_CSV = LEXIBANK_DIR / "austronesian_language_clades.csv"

CLADE_ORDER = ("formosan", "western_mp", "shwng", "oceanic", "eastern_mp_other", "other_austronesian")


def load_language_clades(path: Path | None = None) -> dict[str, str]:
    """Map Lexibank language ID -> coarse Austronesian clade."""
    path = path or AN_CLADES_CSV
    if not path.exists():
        raise FileNotFoundError(
            f"Missing AN clade map {path}. Regenerate from Glottolog or restore from repo."
        )
    with path.open(newline="", encoding="utf-8") as handle:
        return {
            row["language_id"]: row["clade"]
            for row in csv.DictReader(handle)
            if row.get("language_id") and row.get("clade")
        }


def sample_austronesian_forms(
    forms: list[dict[str, str]],
    *,
    target: int = AN_SAMPLE_TARGET,
    floors: dict[str, int] | None = None,
    seed: int = AN_SAMPLE_SEED,
) -> list[dict[str, str]]:
    """Phylogenetically stratified sample of Austronesian forms.

    Strategy:
    1. At most one form per language (first occurrence kept as candidate pool).
    2. Satisfy per-clade floors when possible (Formosan prioritized).
    3. Fill remaining slots by round-robin across clades that still have leftovers.
    """
    floors = dict(floors or AN_CLADE_FLOORS)
    rng = random.Random(seed)

    by_language: dict[str, dict[str, str]] = {}
    for item in forms:
        lang_id = item.get("language_id") or item.get("language") or ""
        if not lang_id or lang_id in by_language:
            continue
        by_language[lang_id] = item

    by_clade: dict[str, list[dict[str, str]]] = defaultdict(list)
    for item in by_language.values():
        clade = item.get("clade") or "other_austronesian"
        by_clade[clade].append(item)

    for clade in by_clade:
        rng.shuffle(by_clade[clade])

    selected: list[dict[str, str]] = []
    selected_ids: set[str] = set()

    def take(clade: str, n: int) -> None:
        pool = by_clade.get(clade) or []
        while n > 0 and pool:
            item = pool.pop()
            lang_id = item.get("language_id") or item.get("language") or ""
            if lang_id in selected_ids:
                continue
            selected.append(item)
            selected_ids.add(lang_id)
            n -= 1

    # Floors first (Formosan first in CLADE_ORDER).
    for clade in CLADE_ORDER:
        floor = floors.get(clade, 0)
        if floor > 0:
            take(clade, floor)

    # Fill remainder round-robin.
    while len(selected) < target:
        progressed = False
        for clade in CLADE_ORDER:
            if len(selected) >= target:
                break
            if by_clade.get(clade):
                before = len(selected)
                take(clade, 1)
                if len(selected) > before:
                    progressed = True
        if not progressed:
            break

    return selected
