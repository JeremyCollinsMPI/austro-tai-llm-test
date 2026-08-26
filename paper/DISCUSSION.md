# 6. Discussion

## 6.1 What the results do and do not show

After Lexibank-facing filters, Smith’s (2025) remaining PAN–PKD alignments show meaning-blind form similarity far above a shuffled baseline (*p* ≈ 0.01 under *N* = 100 permutations). Independently, dual-attested Lexibank form groups on a Blust/ABVD concept filter also exceed a group-shuffle null at the primary generosity cutoffs (a score of 4 or higher, and also 3 or higher and 2 or higher; *p* ≈ 0.032 under *N* = 30). The natural reading is that **excess form resemblance under these screens is not an artifact of a single reconstruction spreadsheet**: Study 2 never sees Smith’s proto-forms, yet still finds same-meaning form groups more similar than cross-meaning form groups.

That is a claim about **strength of evidence under stated controls**, not a demonstration of genetic relatedness. Classical arguments for Austro-Tai (especially Ostapirat 2005, 2013) turn on **regular phonological correspondences** and reconstructibility. The scoring model may note plausible segment matches in free text, but it does not enforce a correspondence system, reconstruct intermediate stages, or distinguish inheritance from old loans that have been internalized in daughter vocabularies. Contact with Sinitic and mainland Southeast Asian languages remains a live alternative for some lookalikes in principle. I therefore investigated whether the observed hits themselves look like a **Chinese loan** pathway into Tai-Kadai and/or Austronesian (§4.7; Appendix G): across **38** hits (Study 1 and Study 2 combined), Chinese-loan plausibility scores were overwhelmingly low (21 scored 1, 14 scored 2; mean ≈ 1.55), with only **three** items at 3 or higher and a single score of 4 (*be dead or die* in Study 2). That pattern makes a story in which **Sinitic is the common donor** for the hit set look unattractive under this screen, it does not rule out non-Sinitic contact, older areal diffusion, or item-specific loans outside the hit list. Excess aggregate hits therefore still motivate further comparative work, including correspondence inventories over Study 2’s hit concepts, they do not finish it.

Relative to the two main modern phylogenetic frames, Ostapirat’s (2005, 2013) sister-family construal and Sagart’s (2004, 2005, 2019) Austronesian-linked architecture, the results are **compatible with “there is non-chance lexical signal to explain”** and **agnostic** on tree geometry.

## 6.2 Why Study 2 is the more robust check

Study 1 answers: given Smith’s published alignments, and after removing reconstructions Lexibank daughters do not support, is the residual pairing surprising? That is the right question for auditing a **fixed evidence package**, and anchoring in Smith reduces researcher freedom in picking etymologies (§2.2). It does not fully answer a different worry: that the package itself may preferentially include lookalike-friendly reconstructions.

Study 2 addresses that worry by construction. Concepts are selected by Lexibank coverage and a pre-existing Austronesian basic-vocabulary list (Blust/ABVD), not by an Austro-Tai author’s alignments. Forms are modern Lexibank attestations under phylogenetic sampling, not proto-strings chosen for comparison. The null asks whether **same-Concepticon** inventories look more alike than shuffled inventories. Convergence between Study 1 and Study 2 therefore strengthens the claim that the signal is not merely an artifact of reconstructing toward resemblance.

The two studies are not interchangeable. Study 1 speaks directly to a published Austro-Tai spreadsheet; Study 2 speaks to modern lexical inventories and is closer to a “no reconstructions” stress test. Hit rates are lower in Study 2, as expected when comparing heterogeneous daughter samples rather than two curated proto-forms.

## 6.3 Why meaning-blindness and filters matter

If meanings are visible, both humans and models can reward “good etymologies” they already associate with famous comparisons, or stretch similarity when the gloss invites a match. Withholding glosses forces the score to be a function of the strings (or form groups) and the model’s prior over orthographic/phonological resemblance. Caching binds observed and null worlds to the same scoring function.

In Study 1, Layer 1 addresses unsupported reconstructions. In Study 2, coverage floors, Blust filtering, onomatopoeia/dedupe heuristics, and phylogenetic sampling play the analogous role of limiting opportunistic form choice, while still leaving room for within-family diversity and contact-induced lookalikes.

## 6.4 Limits

Several limits bound interpretation.

**Model and prompt.** All scores use `gpt-4.1` via a fixed chat API and fixed prompts. Other models or stricter prompts would change absolute hit rates; the permutation comparison is meaningful only relative to the same scoring function. Threshold choice matters especially in Study 2: a cutoff of 2 or higher yields many hits and a high null baseline; a cutoff of 4 or higher is sparse but cleanly separated from the null.

**Prior knowledge of etymologies.** Large language models may have seen published Austro-Tai comparisons in training data. Meaning-blindness reduces semantic priming but does not erase memorized form pairs (e.g. famous *mata* / *nam* clusters). The permutation null still constrains the argument: memorization would have to favor **matched** pairings over shuffled ones. Residual risk remains and should be checked with expert human re-rating of hits.

**Lexibank and sampling.** Coverage is uneven across concepts and subgroups. Stratified samples avoid Oceanic overweighting but can miss reflexes. Study 2’s onomatopoeia heuristics are imperfect. Blust intersection by Concepticon ID misses some near-matches where Lexibank splits Blust glosses.

**Smith’s preliminary character (Study 1).** The Zenodo package is preliminary and versioned. Future releases may revise reconstructions; my frozen counts apply to v1.1 as parsed.

**Null design and *N*.** Study 1 uses *N* = 100; Study 2 uses *N* = 30 (costly set-versus-set calls). Study 2’s *p* ≈ 0.032 is therefore the add-one floor: no null reached observed, but a finer tail would need larger *N*. Neither null models phonetic natural classes, semantic fields, or borrowing pathways.

**Nursery forms and deixis.** Some Study 2 hits (*mother*, *this*, pronouns) are categories where chance or nursery resemblance is a known risk; primary interpretation should weight body-part and verb hits more heavily pending correspondence work.

## 6.5 Future work

Useful extensions include larger *N* for Study 2’s null tail; human expert re-rating of hits; exploratory **regular correspondence** inventories over Study 2 hit concepts (at a generosity score of 4 or higher, 3 or higher, and 2 or higher); correspondence-constrained scoring (encoding Ostapirat-style systems as hard filters); and parallel audits of other published Austro-Tai lists under Study 1’s two-layer design.

---

# 7. Conclusion

I reported two meaning-blind permutation screens of Austro-Tai lexical resemblance. **Study 1** audited Alexander D. Smith’s (2025) gloss-aligned PAN–PKD reconstructions with Lexibank attestation filters: on 79 Tier A pairs, 27 high form-similarity hits stand against a null mean of about 5.7 (*p* ≈ 0.01, *N* = 100). **Study 2** compared dual-attested Lexibank Tai-Kadai and Austronesian form groups on 194 Blust/ABVD concepts, without reconstructions: hits at a generosity score of 4 or higher / 3 or higher / 2 or higher were 11 / 17 / 121 against null means of about 2.2 / 5.7 / 91.7 (*p* ≈ 0.032, *N* = 30). Study 2 is the more robust check against cherry-picked reconstructions because concept and form selection do not inherit an author’s comparative spreadsheet. Together, the studies strengthen the case that excess form resemblance under these screens is not merely an artifact of meaning-matched browsing, while leaving genetic proof to systematic sound correspondences and classical reconstruction.
