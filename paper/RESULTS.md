# 5. Results

## 5.1 From Smith’s sheet to Tier A

Starting from **120** gloss-aligned PAN–PKD pairs, Layer 1 exclusions left **79** Tier A pairs for the permutation test (Table 1).

**Table 1.** Sample construction (raw flag counts, then a disjoint exclusion path).

| Stage | *n* |
|-------|----:|
| Smith pairs with both PAN and PKD | 120 |
| Coverage gaps (unmapped concept, or &lt; 3 Lexibank Tai-Kadai or Austronesian languages) | 13 |
| Unjustified PKDs (`attestation_score` = 1; flag may co-occur with gaps) | 14 |
| Unjustified PANs (`attestation_score` = 1; flag may co-occur with gaps) | 27 |
| **Tier A** (no coverage gap; PKD and PAN scores of at least 2) | **79** |

The raw unjustified counts overlap with coverage gaps and with each other, so they do not sum to 120 − 79. A **disjoint** accounting of the **41** excluded pairs is: coverage gap (**13**); no gap but PAN score 1 only (**19**); no gap but PKD score 1 only (**5**); no gap but score 1 on both sides (**4**). Tier A retains only slots where both reconstructions clear a minimal attestation bar against modern Lexibank evidence.

Among pairs that received attestation scores, PKD scores were distributed as 14 / 31 / 11 / 27 / 34 for scores 1 through 5 respectively (*n* = 117 scored). PAN scores on the stratified Austronesian sample were 27 / 27 / 12 / 14 / 31 (*n* = 111 scored). Thus a non-trivial fraction of the published package, especially on the Austronesian side under my sampling scheme, was judged poorly supported by daughters and was withheld from the chance test of form pairing.

Within Tier A, PKD attestation scores were predominantly 2–5 (25, 9, 22, and 23 pairs at scores 2–5), and PAN scores were likewise 2–5 (24, 11, 13, and 31). Tier A is therefore not restricted to only the most secure reconstructions; it excludes the weakest Layer 1 cases while still including many middling scores.

## 5.2 Observed meaning-blind hits

On the **79** Tier A pairs, the meaning-blind judge assigned a generosity score of 4 or higher to **27** pairs (**34.2%**). Of these hits, **18** scored 5 and **9** scored 4.

Hit rates by Layer 1 attestation band are uneven mainly on the PAN side. Grouping Tier A by PAN attestation score, hits (generosity ≥ 4) are **5/24** (21%) at score 2, **2/11** (18%) at 3, **6/13** (46%) at 4, and **14/31** (45%) at 5. By PKD attestation score the rates are flatter (**8/25**, **3/9**, **8/22**, **8/23** at scores 2–5; about 32–36%). Using the minimum of the two scores, mid-strength slots (min = 2 or 3) hit at about **25–30%**, while min = 4 or 5 hits at about **44–50%**. The signal is therefore not confined to the most secure Layer 1 pairs, but it is stronger where PAN attestation is higher. That gradient has two natural readings: better-supported PAN reconstructions may carry more genuine comparative signal, or they may disproportionately be the famous, phonotactically regular etyma that are easiest for both humans and models to match. Under the SCA ≤ 0.40 diagnostic (§5.7), the PAN-band pattern is weaker and less monotonic (**6/24**, **3/11**, **3/13**, **13/31** at scores 2–5; about 23–27% except 42% at score 5), which argues against treating the LLM gradient as pure Layer 1 circularity while still leaving room for a “canonical etyma” contribution at the top of the attestation scale.

Illustrative high-scoring form pairs (generosity 5) include near-identity or near-identity modulo length/diacritics such as 1sg PAN \**aku* ~ PKD \**aku*; ‘die’ \**(m/p-)aCay* ~ \**p-ataːy*; ‘eat’ \**ka(ʔ)ən* ~ \**(i-)kan*; ‘moon’ \**bulaN* ~ \**buɭaːl*; and ‘nine’ \**siwa* ~ \**(s(i)waː)*. These examples are listed for transparency; the statistical claim below concerns the **aggregate** hit count, not any single etymology.

## 5.3 Permutation null

Across **100** random reassignments of Tier A PAN forms to Tier A PKD slots, the number of hits (pairs with a generosity score of 4 or higher) had mean **5.68**, median **6**, and range **1–12** (first–third quartiles approximately 4–7). The observed count of **27** lies far above every null draw: no permutation produced 27 or more hits. The one-sided *p*-value is therefore

$$
p = \frac{0 + 1}{100 + 1} \approx 0.0099.
$$

Under this screen, the published pairing yields roughly **four to five times** as many high form-similarity scores as the average null world (27 vs 5.7), and about **twice** as many as the most extreme null world in the sample (27 vs 12).

## 5.4 Sensitivity

Holding the empirical null distribution fixed, I asked how far the observed hit count would have to fall before *p* exceeded 0.05. With this null, an observed count of **10** still yields *p* ≈ 0.030, whereas **9** yields *p* ≈ 0.069. Relative to the actual **27** hits, that corresponds to discarding at least **18** of the 27 hits (two-thirds of them) before the result would cease to be significant at the 5% level under this null sample. This is a sensitivity calculation, not a new experiment: if entire slots were removed from Tier A, the null would also change. It does indicate, however, that the gap between observed and null is not a fragile one-hit margin.

## 5.5 Interim summary (Study 1)

After excluding coverage gaps and reconstructions scored as unsupported by Lexibank daughters, Smith’s (2025) remaining PAN–PKD alignments show meaning-blind form similarity well above a shuffled baseline (*p* ≈ 0.01, *N* = 100).

## 5.6 Study 2: Lexibank dual-attested concepts (Blust filter)

### Concept set

Intersecting Lexibank concepts with at least 15 Tai-Kadai and at least 15 Austronesian languages (**373**) with the Blust/ABVD 210 Concepticon list (Greenhill, Blust & Gray 2008) yielded **194** analysis concepts. Coverage is high for core vocabulary (many concepts have 60+ Tai-Kadai and 500+ Austronesian languages before sampling).

### Observed set-versus-set scores

On the **194** concepts, generosity scores were dominated by 1–2 (73 and 104 concepts respectively), with **6** scoring 3 and **11** scoring 4 (none scoring 5). Primary hits (a generosity score of 4 or higher) are: *eye*, *nose*, *eat*, *water*, *bite*, *shoulder*, *mother*, *this*, *we*, *blow (of wind)*, and *be dead or die*. Adding a generosity score of 3 brings in *fire*, *I*, *wing*, *ten*, *dust*, and *lightning* (**17** total at a score of 3 or higher). At the liberal cutoff of a score of 2 or higher, **121** concepts qualify, useful for sensitivity, but too inclusive for a primary claim.

Judge notes for hits with a score of 4 or higher typically cite recurring skeletons familiar from classical comparisons (e.g. *mata*-like clusters for ‘eye’; *nam* / *danum*-like shapes for ‘water’; *kVn* for ‘eat’; *kat*-like shapes for ‘bite’). I treat these as transparency, not as etymological endorsements.

### Permutation null

Across **30** random reassignments of Austronesian form groups to Tai-Kadai slots, hit counts were as follows (each row is a cutoff on the 1–5 generosity score):

| Generosity cutoff | Observed | Null mean | Null range | One-sided *p* |
|----------:|---------:|----------:|------------|-------------:|
| 2 or higher | 121 | 91.7 | 80–103 | 0.032 |
| 3 or higher | 17 | 5.7 | 1–15 | 0.032 |
| 4 or higher | 11 | 2.2 | 0–6 | 0.032 |
| 5 | 0 | 0.2 | 0–1 | 1.0 |

No null world reached the observed count at a score of 2 or higher, 3 or higher, or 4 or higher, so each of those *p*-values equals the add-one floor **1/31 ≈ 0.032** (an upper bound on the one-sided *p* given *N* = 30, not a finely estimated tail probability). The gap at a score of 4 or higher is especially clear: observed **11** versus null mean **2.2** (max **6**). At a score of 2 or higher the absolute null is high (~92), as expected for a liberal threshold, but the observed count still sits above every null draw.

### Relation to Study 1

Study 2’s hit rate at a score of 4 or higher (**11/194 ≈ 5.7%**) is lower than Study 1’s Tier A hit rate (**27/79 ≈ 34%**), which is expected: comparing diverse modern form groups is a harder screen than comparing two curated proto-strings. The important parallel is directional and statistical: in both designs, same-slot / same-meaning pairings exceed a form-preserving shuffle. Study 2 does so **without** relying on Smith’s choice of reconstructions.

## 5.7 Algorithmic sanity check (SCA / NED)

Under the same Tier A slots and PAN-shuffle null as Study 1, but with LingPy SCA and NED distances instead of the LLM (§4.8; *N* = 1000), mean distances are substantially lower (more similar) in the published pairing than in the null. To show effect size as well as significance, I report *z* = (observed mean − null mean) / null SD (negative *z* means more similar than chance):

| Metric | Observed mean | Null mean (range) | *z* | One-sided *p* |
|--------|-------------:|------------------:|----:|-------------:|
| SCA | 0.574 | 0.768 (0.712–0.814) | −13.4 | 0.001 |
| NED | 0.730 | 0.906 (0.865–0.938) | −15.0 | 0.001 |

Secondary hits at distance ≤ 0.40: SCA **25** vs null mean **2.2** (max 10); NED **13** vs null mean **0.3** (max 3); both *p* = 0.001 (add-one floor 1/1001). No null world matched the observed mean or hit count on either metric.

For Study 2’s Blust form groups (same mean-of-best aggregation and group-shuffle null; *N* = 1000), mean distances are again lower than the null, but the absolute gaps are modest (about 0.016 on each metric). No null draw reached the observed SCA mean (null minimum 0.383 vs observed 0.381), so *p* = 0.001 is legitimate; standardized effects are real but much smaller than in Study 1:

| Metric | Observed mean | Null mean (range) | *z* | One-sided *p* |
|--------|-------------:|------------------:|----:|-------------:|
| SCA | 0.381 | 0.398 (0.383–0.410) | ≈ −3.9 | 0.001 |
| NED | 0.620 | 0.636 (0.628–0.645) | ≈ −6.2 | 0.001 |

Study 2 *z* values use null SDs estimated from the empirical null range and calibrated to Study 1’s exact/range ratio; Study 1 *z* uses the exact null SD. Secondary SCA hits at distance ≤ 0.40 are **120** vs null mean **96.4** (max 117; *p* = 0.001). The same NED ≤ 0.40 cutoff yields **0** observed set-level hits (null mean ≈ 0.1), so that particular threshold is too strict for Study 2’s aggregated modern forms; the primary claim for Study 2’s algorithmic screen is the mean-distance test, which both SCA and NED pass.

Across both studies, then, excess same-slot / same-meaning resemblance is not unique to the LLM judge: Study 1’s algorithmic gaps are large in *z* terms, while Study 2’s are significant but modest.

## 5.8 Summary of findings

Study 1 finds that Smith’s remaining PAN–PKD alignments, after Lexibank attestation filters, show meaning-blind form similarity far above a shuffled baseline (*p* ≈ 0.01). Study 2 finds that dual-attested Lexibank form inventories on a Blust concept filter likewise exceed a group-shuffle null at a generosity score of 2 or higher, 3 or higher, and 4 or higher (*p* ≈ 0.032, *N* = 30). Algorithmic SCA/NED screens under the same null designs also beat chance on mean distance (*p* = 0.001, *N* = 1000; §5.7), a parallel check that does not rely on LLM prior knowledge. The next section discusses what this does and does not imply for the Austro-Tai hypothesis.
