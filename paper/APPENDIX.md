# Appendix

Companion files in the software release: `output/judgments_observed.csv`, `data/unjustified_pairs.tsv`, `data/unjustified_pan_pairs.tsv`, `output/permutation_results.json`, `output/lexibank_attestation_audit.csv`.

## Appendix A. Prompt texts

### A.1 Meaning-blind form similarity (prompt version `v2`)

**System prompt** (`src/judge.py`):

```
You are a comparative linguist scoring how similar proposed proto-language **forms** look, for exploratory Austro-Tai research.

Rules:
- Compare **phonetic and segmental shape only**. Do NOT use, infer, or mention meaning, semantics, glosses, or cognate labels.
- Each item gives a Proto-Kra-Dai (PKD) form and a candidate Proto-Austronesian (PAN) form. Score how similar the PAN form would be to the PKD form **if** it were the Austronesian reconstruction paired with that PKD slot, without knowing what concept either form represents.
- Do NOT require established regular sound correspondences; be generous on shape but not absurd.
- Ignore tone marks/superscripts when comparing shapes, but mention them if relevant.
- If the PAN side lists multiple alternate reconstructions, treat any plausible segmental match as supporting a higher score.

Return ONLY valid JSON (no markdown fences) as an array of objects with keys:
- comparison_id (string; echo the id from the input)
- generosity (integer 1-5; 5 = very similar shapes under a generous comparison)
- plausible_sound_correspondences (string; brief note or "none noted")
- reasoning (string; 1-3 sentences; do not refer to meaning)
```

**User prompt pattern:**

```
For each item, score how similar the proto-Austronesian form would be to the proto-Kra-Dai form if it were the Austronesian reconstruction for the same slot. Compare shapes only; do not use meaning.

+ JSON array of objects with keys: comparison_id, proto_austronesian, proto_kra_dai, proto_tai_branch (opaque batch index as comparison_id; no gloss).
```

### A.2 PKD attestation vs Lexibank Tai-Kadai (prompt version `v2`)

**System prompt** (`src/reconstruction_validate.py`):

```
You are a comparative linguist assessing how well a proposed Proto-Kra-Dai (PKD) reconstruction is supported by attested modern Tai-Kadai word forms from Lexibank.

Rules:
- Compare the PKD form to attested daughter-language forms for the same meaning.
- Ignore tone marks/superscripts when comparing shapes, but mention them if relevant.
- Reward systematic reflexes across multiple languages; penalize if attested forms cluster around a different shape.
- Do NOT require perfect regular sound correspondences, but note major mismatches.
- If branch-level proto-Tai (PT) is given and contradicts most attested forms, lower the score.

Return ONLY valid JSON (no markdown fences) as an array of objects with keys:
- pair_id (string)
- attestation_score (integer 1-5; 5 = strongly supported across attested forms)
- supporting_reflexes (string; brief note on languages/forms that fit)
- problematic_reflexes (string; forms that do not fit, or "none noted")
- reasoning (string; 2-4 sentences)
```

**User prompt pattern:**

```
Score how well each PKD reconstruction is supported by the attested Tai-Kadai forms listed.

+ JSON array with pair_id, gloss, proto_kra_dai, proto_tai_branch, lexibank_concept, n_attested_languages_in_lexibank, attested_forms.
```

### A.3 PAN attestation vs stratified Austronesian sample (prompt version `v1`)

**System prompt** (`src/pan_validate.py`):

```
You are a comparative linguist assessing how well a proposed Proto-Austronesian (PAN) reconstruction is supported by attested modern Austronesian word forms sampled from Lexibank.

Rules:
- Compare the PAN form to attested daughter-language forms for the same meaning.
- The sample is phylogenetically stratified (Formosan, Western Malayo-Polynesian, SHWNG, Oceanic, etc.). Weight evidence across clades; do not let Oceanic alone decide the score.
- Prefer support that includes Formosan and/or widespread Western MP reflexes for a high score.
- Ignore tone marks/superscripts when comparing shapes, but mention them if relevant.
- Reward systematic reflexes across multiple clades; penalize if attested forms cluster around a different shape.
- Do NOT require perfect regular sound correspondences, but note major mismatches.
- If alternate PAN reconstructions are listed, treat any well-supported alternate as supporting a higher score.

Return ONLY valid JSON (no markdown fences) as an array of objects with keys:
- pair_id (string)
- attestation_score (integer 1-5; 5 = strongly supported across sampled clades)
- supporting_reflexes (string; brief note on languages/forms/clades that fit)
- problematic_reflexes (string; forms that do not fit, or "none noted")
- reasoning (string; 2-4 sentences)
```

**User prompt pattern:**

```
Score how well each PAN reconstruction is supported by the sampled Austronesian forms listed.
Each attested form includes its coarse phylogenetic clade.

+ JSON array with pair_id, gloss, proto_austronesian, lexibank_concept_id, counts, attested_forms[{language,clade,form}].
```

## Appendix B. Austronesian clade sampling

Language → clade map: `data/lexibank/austronesian_language_clades.csv` (coarse labels derived from Glottolog under Austronesian `aust1307`).

Sampling algorithm (`src/an_sampling.sample_austronesian_forms`):

1. Deduplicate to at most one form per language.
2. Satisfy per-clade floors when possible: Formosan **12**, Western Malayo-Polynesian **20**, SHWNG **8**, Oceanic **20**.
3. Fill remaining slots up to target **80** by round-robin across clades with leftover forms.
4. Use fixed seed `AN_SAMPLE_SEED = 1` for reproducibility.

## Appendix C. Tier A hits (a generosity score of 4 or higher)

Observed hits: **27** / 79 Tier A pairs (18 with generosity 5; 9 with generosity 4). Null (*N* = 100): mean 5.68, range 1–12; one-sided *p* = 0.0099.

| Gloss | PAN | PKD | Gen. | PKD att. | PAN att. |
|-------|-----|-----|-----:|---------:|---------:|
| 1sg | *aku | *aku | 5 | 4 | 5 |
| 2sg | *-Su; *-mu (plural) | *-məː | 5 | 2 | 4 |
| afraid; fear | *talaw | *C-laːw | 5 | 4 | 4 |
| dark; black | *-dəm | *(C̥V/m)-dam | 5 | 4 | 4 |
| die | *(m/p-)aCay | *p-ataːy | 5 | 4 | 5 |
| drop; fall | *-tuq | *tok | 5 | 5 | 2 |
| eat | *ka(ʔ)ən | *(i-)kan | 5 | 4 | 5 |
| fart | *qətut | *k[a/ə]tu2t | 5 | 3 | 2 |
| five | *lima | *ɭVmaː | 5 | 3 | 5 |
| hold; grab | *-[g/k]əm | *N-kamᴬ | 5 | 5 | 3 |
| moon | *bulaN | *buɭaːl | 5 | 2 | 5 |
| nine | *siwa | (*s(i)waː) | 5 | 2 | 5 |
| six | *(x)ənəm | *xən[a/ə]m | 5 | 5 | 5 |
| this | *-ni | *niː | 5 | 5 | 5 |
| tongue2 | *Səma | *Səmaːᴬ | 5 | 4 | 2 |
| tooth | *[l/n/ŋ]ipan | *(l)ipan | 5 | 3 | 4 |
| vomit | *utaq | *utaːk | 5 | 2 | 4 |
| water | *daNum | *danam | 5 | 5 | 5 |
| bird; chicken | *maNuk | *malok | 4 | 4 | 5 |
| deep | *daləm | *C-alək | 4 | 5 | 2 |
| excrement | *Caqi; (PMP *taqay) | *CV-q[i/aːj] | 4 | 2 | 3 |
| fire | *Sapuy | *apuy | 4 | 2 | 5 |
| head | *quluh | *kuɭuː | 4 | 2 | 5 |
| louse | *kuCu | *C-uʈuː | 4 | 2 | 5 |
| shoulder | *qabaRa | *CV-baː | 4 | 5 | 5 |
| sky | *Rabun | *C-bu1n | 4 | 4 | 2 |
| wash | *basəq | *C-sak | 4 | 5 | 4 |

## Appendix D. Unjustified reconstructions (attestation_score = 1)

### D.1 Unjustified PKDs (*n* = 14)

| Gloss | PAN | PKD |
|-------|-----|-----|
| buy/sell | *saliw | *aɭiːw |
| leech | *matək/*məCaq | (*tak) |
| nest | *Rubu | *aruːk |
| otter | *Sanaq | *anaːk |
| pick up; lift; take | *saput; *piliq | *kep |
| plant | *mula | *muɭaː |
| sharp | *tazəm | *C.cəmᴬ |
| shrimp | *qudaŋ; *kabus | *(q)udaːŋ |
| sick | *sakit | *keːt |
| skinny | *Niwaŋ | *CV-roːm |
| stomach | *biCuka; *tiaN | *amok |
| tie; bundle | *Sikət; *baluN; *bəjbəj | *CV-ruːk |
| to taste | *taɲam | *ɟim |
| turtle | *qaCipa (soft-shell) | *C̥-(i)paːᴬ |

### D.2 Unjustified PANs (*n* = 27)

| Gloss | PAN | PKD |
|-------|-----|-----|
| ant | *alujah; *aNay | *Vmu2c |
| bathe | *diRus | *aːp |
| bear | *Cumay | *Cumaj |
| boat | *luja | *C̬udaː |
| borrow | *Səzam | *Səzəːm |
| centipede | *qalu-Sipan | *CV-rip |
| child1 | *aNak | *aləːk |
| dream | *S[ə/i]pi | *CV([+H])pan |
| fish poison | *tuba | *C̥V[+H]baː |
| forget | *alim | *CV-ləːm |
| hook | *kawit; *kabit | *C-bet |
| hot; warm | *lasuq | *C-uluːl |
| hungry | (PMP *lapaR) | *C-iaːk |
| knife | *RabiS; *tadaw | *miːt |
| leg | *paqa | *paqaː |
| nest | *Rubu | *aruːk |
| plant | *mula | *muɭaː |
| rattan | *quay | *(q)uaːy |
| raw; (a)live | *qudip | *(q)udip |
| shadow | *qaNiŋu; *liŋaw | *aŋ[u/aːw] |
| sick | *sakit | *keːt |
| skinny | *Niwaŋ | *CV-roːm |
| sour | *qa(R)səm | *qas[a/ə]m |
| star | *qajaw | *adaːw |
| taro | *biRaq | *biRaːk |
| to taste | *taɲam | *ɟim |
| turtle | *qaCipa (soft-shell) | *C̥-(i)paːᴬ |

## Appendix E. Data and software availability

- **Smith (2025) reconstructions:** Zenodo DOI [10.5281/zenodo.15597357](https://doi.org/10.5281/zenodo.15597357), release v1.1 (*Austro-Tai comparative dataset (Reconstructions)*).
- **Lexibank 2:** List et al. (2022) and Blum et al. (2025); `lexibank-analysed` v2.2 (Concepticon-linked forms; Tai-Kadai and Austronesian subsets as described in §3–4).
- **Blust / ABVD concept list:** Concepticon contribution Blust-2008-210 (Greenhill, Blust & Gray 2008).
- **Analysis code and frozen outputs:** [https://github.com/jeremycollinsmpi/austro-tai-llm-test](https://github.com/jeremycollinsmpi/austro-tai-llm-test) (Study 1: parse → attest / validate-pan → judge → permute → report; Study 2: attested-core → attested-judge → attested-permute; post hoc `sinitic-screen`; algorithmic sanity `algo-study1` / `algo-study2`). Model: `gpt-4.1` via project NLP chat endpoint. Reported LLM tables are reproducible from the released judgment caches and frozen summaries (`output/permutation_results.json`; `output/attested_permutation_results_blust194_n30.json` and `output/attested_judgments_null_blust194_n30.csv`; `output/sinitic_screen_hits.csv`). Algorithmic SCA/NED results: `output/algo_permutation_study1.json`, `output/algo_permutation_study2_blust194.json`, and their length-stratified counterparts `output/algo_permutation_study1_length.json`, `output/algo_permutation_study2_blust194_length.json` (produced with `--length-controlled`; per-slot distances in the matching `algo_judgments_*.csv`), plus the band-sensitivity runs `*_length_coarse.json` and `*_length_quartile.json` (`--band-scheme coarse|quartile`). Semantic-category exclusion reruns (§4.9): `output/category_exclusion_rerun.json` (all LLM and algorithmic variants; regenerate with `scripts/category_exclusion_rerun.py`, which makes no API calls) and `output/algo_permutation_study*_excl_{core,wide}.json`; exclusion sets are defined in `src/categories.py`. Live re-queries against a changed or discontinued `gpt-4.1` endpoint are not guaranteed to match LLM caches bit-for-bit; algorithmic scores are deterministic given LingPy and the frozen inputs.

## Appendix F. Study 2 hits (Blust dual-attested Lexibank)

Observed on **194** concepts; null *N* = 30; one-sided *p* = 1/31 ≈ 0.032 at a generosity score of 2 or higher, 3 or higher, and 4 or higher.

**Generosity score of 4 or higher (*n* = 11):** eye; nose; eat; water; bite; shoulder; mother; this; we; blow (of wind); be dead or die.

**Generosity score of 3 (*n* = 6; total at 3 or higher = 17):** fire; I; wing; ten; dust; lightning.

Full scores and model notes: `output/attested_judgments_observed_blust194.csv`.

## Appendix G. Sinitic loan plausibility screen

Post hoc exploratory meaning-aware screen (§4.7) on observed hits with a generosity score of 4 or higher (*n* = 38). Score 1–5 = how plausible a **Chinese loan into Tai-Kadai and/or Austronesian** is as an explanation of the shared resemblance. This is not a classical etymology; full reasons: `output/sinitic_screen_hits.csv`.

**Summary.** Counts at scores 1–5: **21 / 14 / 2 / 1 / 0** (mean ≈ 1.55). Only three items scored 3 or higher: Study 1 *eat* (3); Study 2 *we* (3); Study 2 *be dead or die* (4).

| Study | Gloss / concept | Hit score | Chinese-loan plausibility | Suggested direction |
|------:|-----------------|----------:|--------------------------:|---------------------|
| 1 | 1sg | 5 | 1 | not applicable |
| 1 | 2sg | 5 | 1 | not applicable |
| 1 | afraid; fear | 5 | 2 | not applicable |
| 1 | bird; chicken | 4 | 2 | not applicable |
| 1 | dark; black | 5 | 2 | not applicable |
| 1 | deep | 4 | 1 | not applicable |
| 1 | die | 5 | 2 | not applicable |
| 1 | drop; fall | 5 | 2 | not applicable |
| 1 | eat | 5 | 3 | into Kra-Dai |
| 1 | excrement | 4 | 1 | not applicable |
| 1 | fart | 5 | 1 | not applicable |
| 1 | fire | 4 | 2 | not applicable |
| 1 | five | 5 | 1 | not applicable |
| 1 | head | 4 | 1 | not applicable |
| 1 | hold; grab | 5 | 2 | not applicable |
| 1 | louse | 4 | 1 | not applicable |
| 1 | moon | 5 | 1 | not applicable |
| 1 | nine | 5 | 1 | not applicable |
| 1 | shoulder | 4 | 2 | not applicable |
| 1 | six | 5 | 1 | not applicable |
| 1 | sky | 4 | 2 | not applicable |
| 1 | this | 5 | 1 | not applicable |
| 1 | tongue2 | 5 | 1 | not applicable |
| 1 | tooth | 5 | 1 | not applicable |
| 1 | vomit | 5 | 1 | not applicable |
| 1 | wash | 4 | 2 | not applicable |
| 1 | water | 5 | 1 | not applicable |
| 2 | eye | 4 | 1 | not applicable |
| 2 | nose | 4 | 1 | not applicable |
| 2 | eat | 4 | 2 | into Kra-Dai |
| 2 | water | 4 | 1 | not applicable |
| 2 | bite | 4 | 2 | not applicable |
| 2 | shoulder | 4 | 2 | not applicable |
| 2 | mother | 4 | 1 | not applicable |
| 2 | this | 4 | 1 | not applicable |
| 2 | we | 4 | 3 | into Kra-Dai |
| 2 | blow (of wind) | 4 | 2 | not applicable |
| 2 | be dead or die | 4 | 4 | into Kra-Dai |

