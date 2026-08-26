# Quantifying the strength of published Austro-Tai lexical evidence

**Working title (Diachronica-oriented)**  
*How surprising are Austro-Tai lookalikes? Meaning-blind permutation tests of Smith’s (2025) reconstructions and of dual-attested Lexibank form inventories*

**Subtitle option**  
*Filtering weakly attested reconstructions, and a reconstruction-free Lexibank set-versus-set check*

**Target journal:** *Diachronica* (John Benjamins)  
**Preprint:** arXiv `cs.CL` + LingBuzz (same PDF)

**Status:** Section drafts include Study 1 (Smith) + Study 2 (Lexibank/Blust attested). Empirical numbers frozen Aug 2026.

**Draft prose:**
[`INTRODUCTION.md`](INTRODUCTION.md) · [`LITERATURE.md`](LITERATURE.md) · [`DATA.md`](DATA.md) · [`METHODS.md`](METHODS.md) · [`RESULTS.md`](RESULTS.md) · [`DISCUSSION.md`](DISCUSSION.md) · [`APPENDIX.md`](APPENDIX.md) · [`REFERENCES.md`](REFERENCES.md)

**Assembled preprint:** [`MANUSCRIPT.md`](MANUSCRIPT.md) · Chinese: [`MANUSCRIPT_zh.md`](MANUSCRIPT_zh.md) → [`preprint.pdf`](preprint.pdf) / [`preprint_zh.pdf`](preprint_zh.pdf) (rebuild: `./build_preprint.sh`, `./build_preprint_zh.sh`). Figures: [`figures/null_histogram.png`](figures/null_histogram.png) (Study 1), [`figures/null_histogram_study2.png`](figures/null_histogram_study2.png) (Study 2).


---

## Frozen empirical snapshot (for Results)

### Study 1 — Smith (2025) reconstructions

| Quantity | Value |
|----------|------:|
| Smith gloss-aligned PAN–PKD pairs | 120 |
| Coverage gaps | 13 |
| Unjustified PKDs (`attestation_score` = 1) | 14 |
| Unjustified PANs (`attestation_score` = 1) | 27 |
| **Tier A pairs** | **79** |
| Observed hits (a generosity score of 4 or higher) | **27** (34.2%) |
| Null mean hits (N = 100) | **5.68** (range 1–12) |
| One-sided p | **0.0099** |

### Study 2 — Lexibank dual-attested ∩ Blust-210

| Quantity | Value |
|----------|------:|
| Dual-attested concepts (≥15 TK & AN) | 373 |
| After Blust-210 Concepticon filter | **194** |
| Observed hits @≥4 / ≥3 / ≥2 | **11 / 17 / 121** |
| Null mean @≥4 / ≥3 / ≥2 (N = 30) | **2.23 / 5.73 / 91.7** |
| Null max @≥4 / ≥3 / ≥2 | 6 / 15 / 103 |
| One-sided p @≥2, ≥3, ≥4 | **0.032** (1/31; no null ≥ observed) |

---

## Abstract (draft)

The Austro-Tai hypothesis posits a genetic link between Austronesian and Kra-Dai (Tai-Kadai). Published lexical comparisons are hard to quantify: lists may mix robust etymologies with weakly justified or lookalike-friendly reconstructions, and similarity judgments inflate when meanings are known. I report two meaning-blind permutation screens in which an LLM (`gpt-4.1`, via API) scores segmental form similarity without seeing meanings. **Study 1** audits Alexander D. Smith’s (2025) gloss-aligned Proto-Austronesian (PAN) and Proto-Kra-Dai (PKD) reconstructions: after Lexibank (List et al. 2022) attestation filters, 27 of 79 **Tier A** pairs—those with adequate Lexibank coverage and attestation scores of at least 2 for both PAN and PKD—meet a generous hit threshold (generosity score of 4 or higher) against a null mean of 5.7 (100 permutations; one-sided *p* ≈ 0.01). **Study 2** is designed to be more robust to reconstruction cherry-picking. It compares phylogenetically sampled modern Lexibank form groups for the same Concepticon meaning—restricted to dual-attested concepts on the Blust/ABVD basic-vocabulary list (194 concepts; Greenhill, Blust & Gray 2008)—and shuffles Austronesian form groups across Tai-Kadai slots. Hits at a generosity score of 4 or higher / 3 or higher / 2 or higher are 11 / 17 / 121 against null means of about 2.2 / 5.7 / 91.7 (30 permutations; *p* ≈ 0.032 at each of those thresholds). Convergence across a reconstruction audit and a reconstruction-free Lexibank screen supports excess form resemblance under these controls—not genetic proof, which requires systematic sound correspondences. I situate the results in the Austro-Tai literature (Benedict; Ostapirat; Sagart) and discuss limits of LLM-based screening.

**Keywords:** Austro-Tai; Kra-Dai; Austronesian; lexical comparison; chance resemblance; permutation test; Lexibank; large language models; Blust basic vocabulary

---

## Section outline

### 1. Introduction

- Problem: macro-comparison and the difficulty of assessing **how much** published lookalike evidence exceeds chance.
- Two confounders: (i) **semantic priming** in cognate judgments; (ii) **reconstruction quality / cherry-picking** among weakly attested proto-forms.
- Claim of this paper: quantify the strength of evidence in a **fixed, published** Austro-Tai package under explicit controls—not propose a new cognate set.
- Preview of design: Lexibank attestation filters → meaning-blind form screen → permutation null.
- Roadmap.

### 2. Background: Austro-Tai and the assessment of lexical evidence

#### 2.1 Literature map (survey bullets to expand)

- **Early proposal:** Benedict (1942, 1975)—Austro-Tai as a deep relationship grounded largely in lexical lookalikes; influence and controversy.
- **Modern KD–AN comparative work:** Ostapirat (2005, 2013)—argument from basic vocabulary and **regular phonological correspondences**; sister-family construal.
- **Alternative architecture:** Sagart (2004, 2005, 2019)—Kra-Dai in an Austronesian (or AN-related) phylogenetic frame; numerals and higher phylogeny; tonogenesis models linking KD tones to AN codas (cf. Liao & Gehrmann 2025 in *Diachronica*).
- **Contact and areal alternatives:** Chinese loans into Kra-Dai; mainland SEA contact; why lookalikes need not equal genealogy.
- **Competing macros (brief contrast only):** Sino-Austronesian / Austric, etc.—enough to show Austro-Tai is one among contested higher groupings.
- **Methodological literature on chance resemblance:** Ringe and related critiques of multilateral comparison; warnings about semantic latitude; need for **null models** when evaluating published lists.
- **Gap:** few studies apply an explicit **permutation / chance baseline** to an *entire published Austro-Tai alignment set* after filtering reconstructions that daughters do not support.

#### 2.2 Justification for using Smith (2025)

*Stub paragraph (to polish in draft):*

> I take as my object of evaluation Alexander D. Smith’s (2025) *Austro-Tai comparative dataset (Reconstructions)* (Zenodo), rather than compiling a new etymological list. Three properties motivate that choice. First, the spreadsheet provides **gloss-aligned** Proto-Austronesian and Proto-Kra-Dai reconstructions in a single package explicitly aimed at Austro-Tai comparison, which makes a slot-wise permutation test well-defined: PKD forms can be held fixed while PAN forms are shuffled across meanings. Second, the release is **open, versioned, and preliminary** by the author’s own framing; it is therefore an apt target for an external audit of “what has been presented,” including checks on whether proposed proto-forms are recoverable from modern Lexibank daughters. Third, anchoring the study in an independent published dataset reduces **researcher degrees of freedom** in selecting which comparisons count as evidence. My question is not whether every Smith reconstruction is correct, but how much residual PAN–PKD form similarity remains—and how surprising it is—after weakly supported reconstructions are set aside.

Additional points to weave in:
- Smith columns for branch attestation (PT/PH/PK/…) as a second, author-internal signal of breadth.
- Disclaimer culture: preliminary reconstructions invite exactly this kind of stress test.
- I do **not** treat Smith as consensus Proto-Kra-Dai or as replacing Ostapirat/Sagart; I treat it as a **contemporary evidence package**.

### 3. Data

- Smith v1.1: ~120 gloss-aligned pairs after parsing constraints (both PAN and PKD present).
- Lexibank 2 (`lexibank-analysed` v2.2): Concepticon-linked forms.
- Explicit Smith gloss → Lexibank concept map (no fuzzy matching).
- Tai-Kadai: all attested forms per concept for PKD validation.
- Austronesian: ~978 Lexibank languages; **stratified sample** (~80 forms) with floors (Formosan / Western MP / SHWNG / Oceanic) via Glottolog-derived clades.

### 4. Methods

#### 4.1 Reconstruction attestation (Layer 1)
- LLM scores PKD vs TK daughters (`attestation_score` 1–5).
- LLM scores PAN vs stratified AN sample (`attestation_score` 1–5).
- Coverage gaps: &lt; 3 TK or &lt; 3 AN languages (or unmapped concept) → excluded from Tier A.
- Score = 1 → “unjustified” reconstruction: reported, **excluded from Tier A**.

#### 4.2 Meaning-blind form similarity (Layer 2)
- Prompt: compare shapes only; no gloss; opaque comparison IDs.
- Generosity 1–5; hit threshold ≥ 4 (state robustness intent for ≥ 3 in discussion/appendix).
- Cache keyed by (PKD, PAN) so observed and null share the same scoring function.

#### 4.3 Permutation null
- Shuffle PAN among Tier A PKD slots; one-sided *p* = (*k*+1)/(*N*+1), *N* = 100.
- Interpretation: tests excess **form resemblance** in the published pairing, not genetic relatedness.

#### 4.4 What I are not doing
- No claim of regular sound correspondences.
- No Bayesian phylogeny / dating.
- LLM is a reproducible screen, not a substitute for the comparative method.

### 5. Results

- Flowchart / table: 120 → gaps / unjustified PKD / unjustified PAN → **79 Tier A**.
- Observed **27/79** hits vs null mean **5.68** (max 12); *p* ≈ **0.01**.
- Optional figure: histogram of null hit counts with observed marked.
- Brief qualitative appendix pointers: high-scoring hits; examples of score-1 PKD/PAN.
- Sensitivity: how many hits would need to be discarded before *p* &gt; 0.05 (under fixed null).

### 6. Discussion

- Result as **quantified strength of evidence** for this package under stated controls.
- Relation to Ostapirat/Sagart: compatible with “there is non-chance lexical signal to explain,” agnostic on sister vs AN-internal.
- Limits: model choice (`gpt-4.1` via API), prompt generosity, Lexibank coverage bias, AN sampling scheme, Smith’s preliminary character.
- Why meaning-blindness matters; residual risk that models “know” famous etymologies (acknowledge; permutation still binds form-pair scores).
- Future: larger *N*; human expert re-rating of Tier A hits; correspondence-constrained scoring.

### 7. Conclusion

- Published Smith alignments, after reconstruction filters, show PAN–PKD form similarity far above a shuffled null.
- This strengthens the case that the **lexical evidence as packaged** is not a pure artifact of meaning-matched browsing—while leaving genetic proof to classical comparative work.

### Appendix (planned)

- A. Prompt texts (attestation + meaning-blind judge).  
- B. Clade sampling algorithm and floors.  
- C. Full Tier A hit table.  
- D. Unjustified PKD/PAN lists.  
- E. Software/data availability (github.com/jeremycollinsmpi/austro-tai-llm-test, Zenodo Smith, Lexibank).

---

## Suggested figures and tables

1. **Figure 1.** Exclusion flowchart (120 → Tier A 79).  
2. **Figure 2.** Null histogram of hit counts; vertical line at observed 27.  
3. **Table 1.** Literature positions on Austro-Tai (Benedict / Ostapirat / Sagart)—compact.  
4. **Table 2.** Attestation score distributions (PKD, PAN).  
5. **Table 3.** Top observed hits (gloss, PAN, PKD, generosity, attestation scores).

---

## Drafting order (recommended)

1. ~~Methods §4 + Results §5~~ (done).  
2. ~~Data §3 + Smith justification (§2.2)~~ (done).  
3. ~~Literature survey §2.1~~ (done).  
4. ~~Introduction + Discussion~~ (done).  
5. ~~Appendix + preprint PDF~~ (done: `APPENDIX.md`, `preprint.pdf` via `./build_preprint.sh`). Study 2 Lexibank/Blust write-up in `MANUSCRIPT.md`; Chinese translation `MANUSCRIPT_zh.md`. Next: polish Ostapirat 2013 citation; author metadata; arXiv `cs.CL` + LingBuzz upload; *Diachronica* submit.

---

## Open choices (minor; do not block drafting)

- Exact title wording (question vs declarative).  
- Whether robustness for a generosity score of 3 or higher goes in main text or appendix.  
- How much Sagart “AN-internal KD” detail vs Ostapirat “sisters” in the survey (recommend balanced, ~1–1.5 pages each strand).
