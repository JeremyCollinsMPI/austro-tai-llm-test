# Austro-Tai LLM cognate screen

Repository: [github.com/jeremycollinsmpi/austro-tai-llm-test](https://github.com/jeremycollinsmpi/austro-tai-llm-test) — companion code, data tables, and frozen outputs for the working preprint in `paper/`.

Exploratory statistical test of the **Austro-Tai hypothesis** using gloss-aligned proto-forms from Alexander D. Smith's reconstruction spreadsheet ([Zenodo 10.5281/zenodo.15597357](https://zenodo.org/records/15597357)).

For each eligible meaning in Smith's data, we hold a **Proto-Kra-Dai (PKD)** form fixed and compare it to a **Proto-Austronesian (PAN)** form. The LLM (via `http://13.229.134.226:5000/chat`) returns a **generosity score (1–5)** for **shape similarity only** — gloss/meaning is **not** sent to the API and must not influence the score. The question is: *if this PAN form were the Austronesian reconstruction for the same slot as this PKD form, how similar do the shapes look?* A **permutation test** shuffles PAN forms among slots to estimate how often high scores occur by chance.

**Lexibank attestation** (Tai-Kadai wordlists from Lexibank 2) serves two roles:

1. **Coverage filter** — pairs with unmapped glosses or fewer than 3 attested Tai-Kadai languages for the mapped Concepticon concept are **excluded** from the permutation test.
2. **PKD validation** — an LLM scores how well each PKD reconstruction fits **all** attested Tai-Kadai daughter forms for that concept in Lexibank (**attestation_score 1–5**, not yes/no).
3. **PAN validation** — same idea for Proto-Austronesian, using a **phylogenetically stratified** Lexibank Austronesian sample (~80 forms; Formosan / Western MP / SHWNG / Oceanic floors), not all ~978 AN languages.
4. **Tier A vs unjustified reconstructions** — PKD or PAN `attestation_score = 1` are kept in the report but excluded from the permutation. Tier A = coverage OK (TK and AN) and both scores ≥ 2 when available (`data/eligible_pairs.tsv`).

Smith gloss → Lexibank concept IDs are **explicit** in `src/gloss_concepts.py` (no fuzzy matching).

## Quick start

```bash
chmod +x run.sh
./run.sh parse          # Smith xlsx -> data/aligned_pairs.tsv
./run.sh attest         # Lexibank audit + PKD/PAN validation API + eligible_pairs.tsv
./run.sh validate-pan   # PAN validation only (stratified AN sample)
./run.sh judge          # observed LLM judgments on eligible pairs (batched, cached)
./run.sh matrix         # optional: precompute PKD x PAN scores (~14k API batches; run once)
./run.sh permute        # permutation null (uses pair cache; fast after matrix)
./run.sh report         # output/report.md

# or end-to-end (without full matrix warm-up)
./run.sh all --permutations 100
```

Skip the validation API during attest (Lexibank counts only):

```bash
./run.sh attest --skip-validation
./run.sh validate       # run PKD vs attested-forms scoring later
```

**Permutation cost:** Each unmatched `(gloss, PKD, PAN)` tuple triggers an API call. After `./run.sh judge`, observed pairs are cached. For many permutations, run `./run.sh matrix` once overnight so null draws become cache lookups.

Local venv (without Docker):

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
export NLP_API_URL=http://13.229.134.226:5000/chat
python -m src.main parse
python -m pytest -q
```

## Configuration

See `.env.example`. Important variables:

| Variable | Default | Purpose |
|----------|---------|---------|
| `NLP_API_URL` | `http://13.229.134.226:5000/chat` | Chat API endpoint |
| `NLP_MODEL` | `gpt-4.1` | Model passed in request body |
| `GENEROSITY_THRESHOLD` | `4` | Cognate generosity ≥ this counts as a hit |
| `JUDGE_BATCH_SIZE` | `15` | Pairs per cognate-judge LLM call |
| `N_PERMUTATIONS` | `1000` | Null permutations |

Judgments are cached in `cache/judgments.sqlite3` keyed by prompt + pair batch. PKD validation scores are cached in `cache/reconstruction_scores.sqlite3`.

## Outputs

| File | Description |
|------|-------------|
| `data/aligned_pairs.tsv` | Gloss-aligned PAN/PKD pairs (~120) |
| `data/eligible_pairs.tsv` | Tier A subset for judge/permute (coverage OK + PKD/PAN score ≥ 2) |
| `data/unjustified_pairs.tsv` | PKDs with attestation_score = 1 (report only; not in permutation) |
| `data/unjustified_pan_pairs.tsv` | PANs with pan_attestation_score = 1 (report only) |
| `data/lexibank/austronesian_language_clades.csv` | Lexibank AN language → coarse Glottolog clade |
| `output/judgments_observed.csv` | Per-pair generosity, reasoning, sound-correspondence notes |
| `output/judgments_perm_XXXX.csv` | Null-world judgments |
| `output/permutation_results.json` | Observed hits vs null distribution, p-value |
| `output/lexibank_attestation_audit.csv` | Branch + Lexibank counts, coverage gaps, attestation scores |
| `output/reconstruction_validation.csv` | PKD vs attested-forms LLM scores (from `attest` or `validate`) |
| `output/report.md` | Human-readable summary |

## Method notes

Three separate LLM/deterministic checks:

| Check | Method | Score |
|-------|--------|-------|
| PAN↔PKD shape similarity (Austro-Tai test) | LLM in `judge.py` — **meaning-blind** | **generosity** 1–5 |
| Meaning attestation in wordlists | Lexibank form counting | language count |
| PKD vs daughter forms | LLM in `reconstruction_validate.py` | **attestation_score** 1–5 |

- **Not a proof of genetic relationship.** Sound correspondences are not enforced; the LLM scores segmental shape only (no meaning in the cognate prompt).
- **Null model:** shuffle PAN forms among Tier A PKD slots while keeping PKD fixed; one-sided p = P(null hits ≥ observed hits). Score-1 PKDs/PANs (and their paired forms) are omitted from this shuffle.
- **Coverage gaps:** unmapped concept, `< 3` Tai-Kadai languages, or `< 3` Austronesian languages in Lexibank → omitted before permutation test.
- **Unjustified PKDs/PANs:** `attestation_score = 1` → listed in the report; not counted as Austro-Tai evidence in the p-value.
- **PAN sampling:** ~80 languages max, with floors Formosan 12 / Western MP 20 / SHWNG 8 / Oceanic 20 (one form per language).
- **Cherry-pick flag:** weak Smith branch attestation, sparse Lexibank coverage, or (when validation has run) attestation_score ≤ 2.
- Smith's spreadsheet disclaimer applies: preliminary reconstructions, likely errors.

## Data sources

- Smith, Alexander D. (2025). *Austro-Tai comparative dataset (Reconstructions)*. Zenodo — spreadsheet shipped under `data/Smith.ATReconstructions.v1.1.xlsx`.
- Lexibank 2 (`lexibank/lexibank-analysed` v2.2): language/concept tables and clade maps are under `data/lexibank/`; bulk `forms.csv.zip` and attestation JSON caches are **not** committed (run `./run.sh attest` to download/rebuild).
- Blust / ABVD Concepticon list: `data/attested_pilot/Blust-2008-210.tsv`.
- Frozen paper results: `output/permutation_results.json` (Study 1); `output/attested_permutation_results_blust194_n30.json` and related CSVs (Study 2). Manuscript: `paper/MANUSCRIPT.md`.

Judgments use an OpenAI-compatible chat endpoint (`NLP_API_URL`, default in `.env.example`).

## Tests

```bash
./run.sh test
```
