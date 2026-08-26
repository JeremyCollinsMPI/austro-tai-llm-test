from __future__ import annotations

import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
OUTPUT_DIR = ROOT / "output"
CACHE_DIR = ROOT / "cache"

SMITH_XLSX = DATA_DIR / "Smith.ATReconstructions.v1.1.xlsx"
ALIGNED_PAIRS_TSV = DATA_DIR / "aligned_pairs.tsv"
LEXIBANK_DIR = DATA_DIR / "lexibank"

DEFAULT_NLP_API_URL = "http://13.229.134.226:5000/chat"
DEFAULT_MODEL = os.environ.get("NLP_MODEL", "gpt-4.1")
DEFAULT_MAX_COMPLETION_TOKENS = int(os.environ.get("NLP_MAX_COMPLETION_TOKENS", "8000"))
DEFAULT_BATCH_SIZE = int(os.environ.get("JUDGE_BATCH_SIZE", "15"))
DEFAULT_PERMUTATIONS = int(os.environ.get("N_PERMUTATIONS", "1000"))
GENEROSITY_THRESHOLD = int(os.environ.get("GENEROSITY_THRESHOLD", "4"))

LEXIBANK_VERSION = "v2.2"
LEXIBANK_BASE_URL = f"https://raw.githubusercontent.com/lexibank/lexibank-analysed/{LEXIBANK_VERSION}/cldf"
LEXIBANK_FILES = ("concepts.csv", "languages.csv", "forms.csv.zip")
LEXIBANK_ATTESTATION_CACHE = LEXIBANK_DIR / "tai_kadai_attestation.json"
LEXIBANK_AN_ATTESTATION_CACHE = LEXIBANK_DIR / "austronesian_attestation.json"
ELIGIBLE_PAIRS_TSV = DATA_DIR / "eligible_pairs.tsv"

BRANCH_COLUMNS = ("pt", "ph", "pob", "pk", "pks", "lak")
MIN_BRANCH_ATTESTATION = 2
MIN_LEXIBANK_TAI_KADAI_ATTESTATION = 3
MIN_LEXIBANK_AUSTRONESIAN_ATTESTATION = 3
# Primary Austro-Tai permutation (Tier A) requires PKD/PAN attestation_score >= this.
MIN_ATTESTATION_SCORE_FOR_PERMUTATION = 2
# None = send every Tai-Kadai Lexibank form for the concept (no sample cap).
MAX_LEXIBANK_FORMS_PER_CONCEPT: int | None = None
LEXIBANK_AUDIT_SAMPLE_FORMS = 5

# Austronesian PAN validation: stratified sample (not all 978 languages).
AN_SAMPLE_TARGET = 80
AN_CLADE_FLOORS = {
    "formosan": 12,
    "western_mp": 20,
    "shwng": 8,
    "oceanic": 20,
}
AN_SAMPLE_SEED = 1

UNJUSTIFIED_PAIRS_TSV = DATA_DIR / "unjustified_pairs.tsv"
UNJUSTIFIED_PAN_PAIRS_TSV = DATA_DIR / "unjustified_pan_pairs.tsv"

PROMPT_VERSION = "v2"
RECONSTRUCTION_PROMPT_VERSION = "v2"
PAN_RECONSTRUCTION_PROMPT_VERSION = "v1"
