from __future__ import annotations

import csv
import re
from dataclasses import asdict, dataclass
from pathlib import Path

import openpyxl

from .config import ALIGNED_PAIRS_TSV, BRANCH_COLUMNS, SMITH_XLSX

MISSING_MARKERS = {"", "-", "\xa0-", "None", None}
HEADER_ROW_INDEX = 1
DATA_START_INDEX = 3


@dataclass
class AlignedPair:
    pair_id: str
    gloss: str
    pan: str
    pkd: str
    pt: str
    pat: str
    chinese_flag: str
    notes: str
    branch_attestation_count: int
    attested_branches: str

    def to_row(self) -> dict[str, str | int]:
        return asdict(self)


def _clean(value: object) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    if text in MISSING_MARKERS:
        return None
    return text


def _count_branch_attestation(row: dict[str, str | None]) -> tuple[int, list[str]]:
    attested: list[str] = []
    for col in BRANCH_COLUMNS:
        if _clean(row.get(col)):
            attested.append(col.upper())
    return len(attested), attested


def _slug(gloss: str, index: int) -> str:
    slug = re.sub(r"[^a-z0-9]+", "_", gloss.lower()).strip("_")
    slug = slug[:40] or "item"
    return f"{index:03d}_{slug}"


def load_smith_rows(xlsx_path: Path = SMITH_XLSX) -> list[dict[str, str | None]]:
    workbook = openpyxl.load_workbook(xlsx_path, read_only=True, data_only=True)
    worksheet = workbook["Reconstructions"]
    rows = list(worksheet.iter_rows(values_only=True))
    field_names = [
        "_",
        "chinese",
        "pat",
        "pan",
        "pkd",
        "pt",
        "ph",
        "pob",
        "pk",
        "pks",
        "lak",
        "gloss",
        "middle_chinese",
        "notes",
    ]
    parsed: list[dict[str, str | None]] = []
    for row in rows[DATA_START_INDEX:]:
        if not row or not any(row):
            continue
        values = list(row[: len(field_names)]) + [None] * max(0, len(field_names) - len(row))
        record = {name: _clean(values[i]) for i, name in enumerate(field_names)}
        gloss = record.get("gloss")
        if not gloss or gloss.startswith("="):
            continue
        parsed.append(record)
    return parsed


def build_aligned_pairs(rows: list[dict[str, str | None]] | None = None) -> list[AlignedPair]:
    if rows is None:
        rows = load_smith_rows()
    pairs: list[AlignedPair] = []
    index = 1
    for row in rows:
        pan = row.get("pan")
        pkd = row.get("pkd")
        gloss = row.get("gloss")
        if not pan or not pkd or not gloss:
            continue
        branch_count, branches = _count_branch_attestation(row)
        pairs.append(
            AlignedPair(
                pair_id=_slug(gloss, index),
                gloss=gloss,
                pan=pan,
                pkd=pkd,
                pt=row.get("pt") or "",
                pat=row.get("pat") or "",
                chinese_flag=row.get("chinese") or "",
                notes=row.get("notes") or "",
                branch_attestation_count=branch_count,
                attested_branches=",".join(branches),
            )
        )
        index += 1
    return pairs


def write_aligned_pairs(pairs: list[AlignedPair], path: Path = ALIGNED_PAIRS_TSV) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = list(AlignedPair.__dataclass_fields__)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, delimiter="\t")
        writer.writeheader()
        for pair in pairs:
            writer.writerow(pair.to_row())
    return path


def read_aligned_pairs(path: Path = ALIGNED_PAIRS_TSV) -> list[AlignedPair]:
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle, delimiter="\t")
        pairs: list[AlignedPair] = []
        for row in reader:
            pairs.append(
                AlignedPair(
                    pair_id=row["pair_id"],
                    gloss=row["gloss"],
                    pan=row["pan"],
                    pkd=row["pkd"],
                    pt=row.get("pt") or "",
                    pat=row.get("pat") or "",
                    chinese_flag=row.get("chinese_flag") or "",
                    notes=row.get("notes") or "",
                    branch_attestation_count=int(row.get("branch_attestation_count") or 0),
                    attested_branches=row.get("attested_branches") or "",
                )
            )
        return pairs


def main() -> None:
    pairs = build_aligned_pairs()
    out = write_aligned_pairs(pairs)
    print(f"Wrote {len(pairs)} gloss-aligned PAN/PKD pairs to {out}")


if __name__ == "__main__":
    main()
