from __future__ import annotations

import csv
import io
import json
import zipfile
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path

import pandas as pd
import requests

from .config import (
    ELIGIBLE_PAIRS_TSV,
    LEXIBANK_AN_ATTESTATION_CACHE,
    LEXIBANK_ATTESTATION_CACHE,
    LEXIBANK_AUDIT_SAMPLE_FORMS,
    LEXIBANK_BASE_URL,
    LEXIBANK_DIR,
    LEXIBANK_FILES,
    MAX_LEXIBANK_FORMS_PER_CONCEPT,
    MIN_ATTESTATION_SCORE_FOR_PERMUTATION,
    MIN_BRANCH_ATTESTATION,
    MIN_LEXIBANK_AUSTRONESIAN_ATTESTATION,
    MIN_LEXIBANK_TAI_KADAI_ATTESTATION,
    OUTPUT_DIR,
    UNJUSTIFIED_PAIRS_TSV,
    UNJUSTIFIED_PAN_PAIRS_TSV,
)
from .gloss_concepts import GLOSS_TO_LEXIBANK_CONCEPT
from .parse_smith import AlignedPair, read_aligned_pairs


@dataclass
class AttestationAudit:
    pair_id: str
    gloss: str
    pkd: str
    branch_attestation_count: int
    attested_branches: str
    lexibank_concept_id: str
    lexibank_concept_name: str
    lexibank_concepticon_gloss: str
    lexibank_tai_kadai_language_count: int
    lexibank_austronesian_language_count: int
    lexibank_sample_forms: str
    low_branch_attestation: bool
    low_lexibank_attestation: bool
    coverage_gap: bool
    unjustified_pkd: bool
    unjustified_pan: bool
    included_in_permutation_test: bool
    attestation_score: str
    attestation_score_reasoning: str
    pan_attestation_score: str
    pan_attestation_score_reasoning: str
    cherry_pick_risk: bool

    def to_row(self) -> dict[str, object]:
        return {
            "pair_id": self.pair_id,
            "gloss": self.gloss,
            "pkd": self.pkd,
            "branch_attestation_count": self.branch_attestation_count,
            "attested_branches": self.attested_branches,
            "lexibank_concept_id": self.lexibank_concept_id,
            "lexibank_concept_name": self.lexibank_concept_name,
            "lexibank_concepticon_gloss": self.lexibank_concepticon_gloss,
            "lexibank_tai_kadai_language_count": self.lexibank_tai_kadai_language_count,
            "lexibank_austronesian_language_count": self.lexibank_austronesian_language_count,
            "lexibank_sample_forms": self.lexibank_sample_forms,
            "low_branch_attestation": int(self.low_branch_attestation),
            "low_lexibank_attestation": int(self.low_lexibank_attestation),
            "coverage_gap": int(self.coverage_gap),
            "unjustified_pkd": int(self.unjustified_pkd),
            "unjustified_pan": int(self.unjustified_pan),
            "included_in_permutation_test": int(self.included_in_permutation_test),
            "attestation_score": self.attestation_score,
            "attestation_score_reasoning": self.attestation_score_reasoning,
            "pan_attestation_score": self.pan_attestation_score,
            "pan_attestation_score_reasoning": self.pan_attestation_score_reasoning,
            "cherry_pick_risk": int(self.cherry_pick_risk),
        }


def download_lexibank(force: bool = False) -> Path:
    LEXIBANK_DIR.mkdir(parents=True, exist_ok=True)
    for filename in LEXIBANK_FILES:
        target = LEXIBANK_DIR / filename
        if target.exists() and not force:
            continue
        url = f"{LEXIBANK_BASE_URL}/{filename}"
        print(f"Downloading {url} ...")
        response = requests.get(url, timeout=600)
        response.raise_for_status()
        target.write_bytes(response.content)
    return LEXIBANK_DIR


@dataclass(frozen=True)
class ConceptRecord:
    concept_id: str
    name: str
    concepticon_gloss: str


def _load_concept_records() -> dict[str, ConceptRecord]:
    download_lexibank()
    concepts = pd.read_csv(LEXIBANK_DIR / "concepts.csv")
    records: dict[str, ConceptRecord] = {}
    for _, row in concepts.iterrows():
        concept_id = str(row["ID"])
        records[concept_id] = ConceptRecord(
            concept_id=concept_id,
            name=str(row["Name"]),
            concepticon_gloss=str(row.get("Concepticon_Gloss") or ""),
        )
    return records


def match_concept(gloss: str, concept_records: dict[str, ConceptRecord]) -> ConceptRecord | None:
    if gloss not in GLOSS_TO_LEXIBANK_CONCEPT:
        return None
    concept_id = GLOSS_TO_LEXIBANK_CONCEPT[gloss]
    if concept_id is None:
        return None
    return concept_records.get(concept_id)


def _build_attestation_cache(force: bool = False) -> dict[str, dict[str, object]]:
    download_lexibank(force=force)
    forms_zip = LEXIBANK_DIR / "forms.csv.zip"
    if (
        LEXIBANK_ATTESTATION_CACHE.exists()
        and not force
        and LEXIBANK_ATTESTATION_CACHE.stat().st_mtime >= forms_zip.stat().st_mtime
    ):
        return json.loads(LEXIBANK_ATTESTATION_CACHE.read_text(encoding="utf-8"))

    languages = pd.read_csv(LEXIBANK_DIR / "languages.csv")
    tai_kadai_ids = set(languages.loc[languages["Family"] == "Tai-Kadai", "ID"].astype(str))
    language_names = dict(zip(languages["ID"].astype(str), languages["Name"].astype(str)))

    attestation_counts: dict[str, set[str]] = defaultdict(set)
    sample_forms: dict[str, list[str]] = defaultdict(list)
    forms_by_concept: dict[str, list[dict[str, str]]] = defaultdict(list)

    print("Scanning Lexibank forms for Tai-Kadai attestation ...")
    with zipfile.ZipFile(forms_zip) as archive:
        with archive.open("forms.csv") as raw:
            reader = csv.DictReader(io.TextIOWrapper(raw, encoding="utf-8"))
            for row in reader:
                language_id = str(row["Language_ID"])
                if language_id not in tai_kadai_ids:
                    continue
                concept_id = str(row["Parameter_ID"])
                form = str(row.get("Form") or row.get("Value") or "").strip()
                if not form:
                    continue
                attestation_counts[concept_id].add(language_id)
                language_name = language_names.get(language_id, language_id)
                if len(sample_forms[concept_id]) < LEXIBANK_AUDIT_SAMPLE_FORMS:
                    sample_forms[concept_id].append(f"{language_name}:{form}")
                if (
                    MAX_LEXIBANK_FORMS_PER_CONCEPT is None
                    or len(forms_by_concept[concept_id]) < MAX_LEXIBANK_FORMS_PER_CONCEPT
                ):
                    forms_by_concept[concept_id].append({"language": language_name, "form": form})

    cache = {
        concept_id: {
            "count": len(language_ids),
            "samples": sample_forms.get(concept_id, []),
            "forms": forms_by_concept.get(concept_id, []),
        }
        for concept_id, language_ids in attestation_counts.items()
    }
    LEXIBANK_ATTESTATION_CACHE.write_text(json.dumps(cache, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Cached Tai-Kadai attestation for {len(cache)} Lexibank concepts")
    return cache


def _build_austronesian_attestation_cache(force: bool = False) -> dict[str, dict[str, object]]:
    from .an_sampling import load_language_clades

    download_lexibank(force=force)
    forms_zip = LEXIBANK_DIR / "forms.csv.zip"
    if (
        LEXIBANK_AN_ATTESTATION_CACHE.exists()
        and not force
        and LEXIBANK_AN_ATTESTATION_CACHE.stat().st_mtime >= forms_zip.stat().st_mtime
    ):
        return json.loads(LEXIBANK_AN_ATTESTATION_CACHE.read_text(encoding="utf-8"))

    languages = pd.read_csv(LEXIBANK_DIR / "languages.csv")
    an_ids = set(languages.loc[languages["Family"] == "Austronesian", "ID"].astype(str))
    language_names = dict(zip(languages["ID"].astype(str), languages["Name"].astype(str)))
    clades = load_language_clades()

    attestation_counts: dict[str, set[str]] = defaultdict(set)
    forms_by_concept: dict[str, list[dict[str, str]]] = defaultdict(list)

    print("Scanning Lexibank forms for Austronesian attestation ...")
    with zipfile.ZipFile(forms_zip) as archive:
        with archive.open("forms.csv") as raw:
            reader = csv.DictReader(io.TextIOWrapper(raw, encoding="utf-8"))
            for row in reader:
                language_id = str(row["Language_ID"])
                if language_id not in an_ids:
                    continue
                concept_id = str(row["Parameter_ID"])
                form = str(row.get("Form") or row.get("Value") or "").strip()
                if not form:
                    continue
                attestation_counts[concept_id].add(language_id)
                forms_by_concept[concept_id].append(
                    {
                        "language_id": language_id,
                        "language": language_names.get(language_id, language_id),
                        "form": form,
                        "clade": clades.get(language_id, "other_austronesian"),
                    }
                )

    cache = {
        concept_id: {
            "count": len(language_ids),
            "forms": forms_by_concept.get(concept_id, []),
        }
        for concept_id, language_ids in attestation_counts.items()
    }
    LEXIBANK_AN_ATTESTATION_CACHE.write_text(json.dumps(cache, ensure_ascii=False), encoding="utf-8")
    print(f"Cached Austronesian attestation for {len(cache)} Lexibank concepts")
    return cache


def _load_lexibank_attestation(
    force: bool = False,
) -> tuple[dict[str, dict[str, object]], dict[str, ConceptRecord]]:
    concept_records = _load_concept_records()
    attestation = _build_attestation_cache(force=force)
    return attestation, concept_records


def _load_austronesian_attestation(force: bool = False) -> dict[str, dict[str, object]]:
    return _build_austronesian_attestation_cache(force=force)


def has_coverage_gap(concept: ConceptRecord | None, language_count: int) -> bool:
    return concept is None or language_count < MIN_LEXIBANK_TAI_KADAI_ATTESTATION


def is_unjustified_score(attestation_score: str) -> bool:
    return attestation_score.isdigit() and int(attestation_score) < MIN_ATTESTATION_SCORE_FOR_PERMUTATION


def is_unjustified_pkd(attestation_score: str) -> bool:
    """True when Lexibank validation scored the PKD reconstruction at 1 (not supported)."""
    return is_unjustified_score(attestation_score)


def is_unjustified_pan(attestation_score: str) -> bool:
    """True when Lexibank validation scored the PAN reconstruction at 1 (not supported)."""
    return is_unjustified_score(attestation_score)


def load_validation_scores(path: Path | None = None) -> dict[str, dict[str, str]]:
    path = path or (OUTPUT_DIR / "reconstruction_validation.csv")
    if not path.exists():
        return {}
    with path.open(newline="", encoding="utf-8") as handle:
        return {
            row["pair_id"]: {
                "attestation_score": str(row.get("attestation_score") or ""),
                "reasoning": row.get("reasoning") or "",
            }
            for row in csv.DictReader(handle)
            if row.get("pair_id")
        }


def load_pan_validation_scores(path: Path | None = None) -> dict[str, dict[str, str]]:
    path = path or (OUTPUT_DIR / "pan_reconstruction_validation.csv")
    if not path.exists():
        return {}
    with path.open(newline="", encoding="utf-8") as handle:
        return {
            row["pair_id"]: {
                "attestation_score": str(row.get("attestation_score") or ""),
                "reasoning": row.get("reasoning") or "",
            }
            for row in csv.DictReader(handle)
            if row.get("pair_id")
        }


def audit_attestation(
    pairs: list[AlignedPair] | None = None,
    *,
    force: bool = False,
    validation_scores: dict[str, dict[str, str]] | None = None,
    pan_validation_scores: dict[str, dict[str, str]] | None = None,
) -> list[AttestationAudit]:
    pairs = pairs or read_aligned_pairs()
    attestation, concept_records = _load_lexibank_attestation(force=force)
    an_attestation = _load_austronesian_attestation(force=force)
    validation_scores = validation_scores or {}
    pan_validation_scores = pan_validation_scores or {}

    audits: list[AttestationAudit] = []
    for pair in pairs:
        concept = match_concept(pair.gloss, concept_records)
        concept_id = concept.concept_id if concept else ""
        att = attestation.get(concept_id, {"count": 0, "samples": [], "forms": []})
        an_att = an_attestation.get(concept_id, {"count": 0, "forms": []})
        language_count = int(att.get("count") or 0)
        an_language_count = int(an_att.get("count") or 0)
        low_branch = pair.branch_attestation_count < MIN_BRANCH_ATTESTATION
        low_lexibank = language_count < MIN_LEXIBANK_TAI_KADAI_ATTESTATION
        gap = has_coverage_gap(concept, language_count)
        # Also treat sparse AN coverage as a coverage gap for Tier A.
        if an_language_count < MIN_LEXIBANK_AUSTRONESIAN_ATTESTATION:
            gap = True
        score_row = validation_scores.get(pair.pair_id, {})
        score = score_row.get("attestation_score", "")
        score_reason = score_row.get("reasoning", "")
        pan_row = pan_validation_scores.get(pair.pair_id, {})
        pan_score = pan_row.get("attestation_score", "")
        pan_reason = pan_row.get("reasoning", "")
        unjustified = is_unjustified_pkd(score)
        unjustified_pan_flag = is_unjustified_pan(pan_score)
        included = (not gap) and (not unjustified) and (not unjustified_pan_flag)
        cherry = (
            low_branch
            or low_lexibank
            or (score.isdigit() and int(score) <= 2)
            or (pan_score.isdigit() and int(pan_score) <= 2)
        )
        audits.append(
            AttestationAudit(
                pair_id=pair.pair_id,
                gloss=pair.gloss,
                pkd=pair.pkd,
                branch_attestation_count=pair.branch_attestation_count,
                attested_branches=pair.attested_branches,
                lexibank_concept_id=concept_id,
                lexibank_concept_name=concept.name if concept else "",
                lexibank_concepticon_gloss=concept.concepticon_gloss if concept else "",
                lexibank_tai_kadai_language_count=language_count,
                lexibank_austronesian_language_count=an_language_count,
                lexibank_sample_forms=" | ".join(att.get("samples") or []),
                low_branch_attestation=low_branch,
                low_lexibank_attestation=low_lexibank,
                coverage_gap=gap,
                unjustified_pkd=unjustified,
                unjustified_pan=unjustified_pan_flag,
                included_in_permutation_test=included,
                attestation_score=score,
                attestation_score_reasoning=score_reason,
                pan_attestation_score=pan_score,
                pan_attestation_score_reasoning=pan_reason,
                cherry_pick_risk=cherry,
            )
        )
    return audits


def write_attestation_audit(audits: list[AttestationAudit], path: Path | None = None) -> Path:
    path = path or (OUTPUT_DIR / "lexibank_attestation_audit.csv")
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = list(AttestationAudit.__dataclass_fields__)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for audit in audits:
            writer.writerow(audit.to_row())
    return path


def write_eligible_pairs(pairs: list[AlignedPair], audits: list[AttestationAudit], path: Path | None = None) -> Path:
    path = path or ELIGIBLE_PAIRS_TSV
    included_ids = {audit.pair_id for audit in audits if audit.included_in_permutation_test}
    eligible = [pair for pair in pairs if pair.pair_id in included_ids]
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = list(AlignedPair.__dataclass_fields__)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, delimiter="\t")
        writer.writeheader()
        for pair in eligible:
            writer.writerow(pair.to_row())
    return path


def write_unjustified_pairs(pairs: list[AlignedPair], audits: list[AttestationAudit], path: Path | None = None) -> Path:
    """PKDs scored attestation_score=1 — kept for reporting, excluded from Tier A permutation."""
    path = path or UNJUSTIFIED_PAIRS_TSV
    unjustified_ids = {audit.pair_id for audit in audits if audit.unjustified_pkd}
    selected = [pair for pair in pairs if pair.pair_id in unjustified_ids]
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = list(AlignedPair.__dataclass_fields__)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, delimiter="\t")
        writer.writeheader()
        for pair in selected:
            writer.writerow(pair.to_row())
    return path


def write_unjustified_pan_pairs(
    pairs: list[AlignedPair], audits: list[AttestationAudit], path: Path | None = None
) -> Path:
    path = path or UNJUSTIFIED_PAN_PAIRS_TSV
    unjustified_ids = {audit.pair_id for audit in audits if audit.unjustified_pan}
    selected = [pair for pair in pairs if pair.pair_id in unjustified_ids]
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = list(AlignedPair.__dataclass_fields__)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, delimiter="\t")
        writer.writeheader()
        for pair in selected:
            writer.writerow(pair.to_row())
    return path


def read_eligible_pairs(path: Path | None = None) -> list[AlignedPair]:
    path = path or ELIGIBLE_PAIRS_TSV
    if not path.exists():
        raise FileNotFoundError(
            f"Eligible pairs file not found: {path}. Run `./run.sh attest` first."
        )
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


def run_attestation_audit(*, force: bool = False, skip_validation: bool = False) -> Path:
    pairs = read_aligned_pairs()
    attestation, concept_records = _load_lexibank_attestation(force=force)
    an_attestation = _load_austronesian_attestation(force=force)

    validation_scores: dict[str, dict[str, str]] = {}
    pan_validation_scores: dict[str, dict[str, str]] = {}
    if not skip_validation:
        from .pan_validate import validate_pan_batch
        from .reconstruction_validate import validate_batch

        audit_draft = audit_attestation(pairs, force=force, validation_scores={}, pan_validation_scores={})
        audit_by_id = {audit.pair_id: audit for audit in audit_draft}
        eligible_for_pkd = [
            pair
            for pair in pairs
            if audit_by_id[pair.pair_id].lexibank_concept_id
            and audit_by_id[pair.pair_id].lexibank_tai_kadai_language_count > 0
        ]
        if eligible_for_pkd:
            scores = validate_batch(eligible_for_pkd, audit_by_id, attestation, batch_size=2)
            validation_scores = {
                score.pair_id: {
                    "attestation_score": str(score.attestation_score),
                    "reasoning": score.reasoning,
                }
                for score in scores
            }
            validation_path = OUTPUT_DIR / "reconstruction_validation.csv"
            fieldnames = [
                "pair_id",
                "gloss",
                "pkd",
                "pt",
                "attestation_score",
                "supporting_reflexes",
                "problematic_reflexes",
                "reasoning",
                "n_attested_forms_sent",
            ]
            with validation_path.open("w", newline="", encoding="utf-8") as handle:
                writer = csv.DictWriter(handle, fieldnames=fieldnames)
                writer.writeheader()
                for score in scores:
                    writer.writerow(score.to_row())

        concept_by_pair = {
            audit.pair_id: audit.lexibank_concept_id
            for audit in audit_draft
            if audit.lexibank_concept_id and audit.lexibank_austronesian_language_count > 0
        }
        eligible_for_pan = [pair for pair in pairs if pair.pair_id in concept_by_pair]
        if eligible_for_pan:
            pan_scores = validate_pan_batch(eligible_for_pan, an_attestation, concept_by_pair, batch_size=2)
            pan_validation_scores = {
                score.pair_id: {
                    "attestation_score": str(score.attestation_score),
                    "reasoning": score.reasoning,
                }
                for score in pan_scores
            }
            pan_path = OUTPUT_DIR / "pan_reconstruction_validation.csv"
            fieldnames = list(pan_scores[0].to_row().keys()) if pan_scores else []
            with pan_path.open("w", newline="", encoding="utf-8") as handle:
                writer = csv.DictWriter(handle, fieldnames=fieldnames)
                writer.writeheader()
                for score in pan_scores:
                    writer.writerow(score.to_row())
    else:
        validation_scores = load_validation_scores()
        pan_validation_scores = load_pan_validation_scores()

    audits = audit_attestation(
        pairs,
        force=force,
        validation_scores=validation_scores,
        pan_validation_scores=pan_validation_scores,
    )
    audit_path = write_attestation_audit(audits)
    eligible_path = write_eligible_pairs(pairs, audits)
    unjustified_path = write_unjustified_pairs(pairs, audits)
    unjustified_pan_path = write_unjustified_pan_pairs(pairs, audits)
    flagged = sum(1 for audit in audits if audit.cherry_pick_risk)
    excluded_gap = sum(1 for audit in audits if audit.coverage_gap)
    unjustified = sum(1 for audit in audits if audit.unjustified_pkd)
    unjustified_pan = sum(1 for audit in audits if audit.unjustified_pan)
    included = sum(1 for audit in audits if audit.included_in_permutation_test)
    print(
        f"Wrote attestation audit to {audit_path} "
        f"({flagged}/{len(audits)} cherry-pick flags; {excluded_gap} coverage gaps; "
        f"{unjustified} unjustified PKDs; {unjustified_pan} unjustified PANs; "
        f"{included} Tier A eligible for permutation)"
    )
    print(f"Wrote eligible pairs to {eligible_path}")
    print(f"Wrote unjustified PKD pairs to {unjustified_path}")
    print(f"Wrote unjustified PAN pairs to {unjustified_pan_path}")
    return audit_path
