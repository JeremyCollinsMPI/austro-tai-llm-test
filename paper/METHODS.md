# 4. Methods

My analysis has two studies that share a meaning-blind LLM screen and a permutation null, but differ in what is being paired.

**Study 1** (Smith reconstructions) has two layers. **Layer 1** asks whether each published proto-form is supported by modern Lexibank daughters for the same Concepticon meaning. **Layer 2** asks whether, among reconstructions that pass Layer 1, the published PAN–PKD pairings show more **segmental form similarity** than expected if PAN shapes were randomly reassigned across PKD slots.

**Study 2** (Lexibank attested forms) drops reconstructions. For dual-attested Concepticon concepts on a Blust/ABVD basic-vocabulary filter, it compares **groups of modern Tai-Kadai and Austronesian forms** for the same meaning against a null that shuffles Austronesian form groups across Tai-Kadai slots. The motivation is robustness: Study 2 cannot inherit cherry-picking of lookalike-friendly proto-forms from a reconstruction spreadsheet.

Both studies withhold meanings from the similarity judge. All LLM calls used the chat endpoint configured for this project with model `gpt-4.1`. Prompts and scoring rules are fixed in the accompanying software release; responses were parsed as JSON, with light sanitization and up to three retries on malformed output. Scores were cached so that identical inputs were never re-queried inconsistently between observed and null analyses. Reported tables replay those frozen caches; live re-queries against a different or discontinued model endpoint would not be bit-identical (see Appendix E).

## 4.1 Data: Smith alignments and Lexibank

I parsed Alexander D. Smith’s (2025) Austro-Tai reconstruction spreadsheet (Zenodo release v1.1) into gloss-aligned pairs in which both a Proto-Austronesian (PAN) and a Proto-Kra-Dai (PKD) reconstruction are present. After excluding rows without both sides, **120** pairs remained. Smith’s sheet also records branch-level Kra-Dai reflexes (e.g. Proto-Tai, Proto-Hlai, Proto-Kam-Sui); I retain branch attestation counts as descriptive metadata but do not use them as the primary filter for Tier A membership.

Modern forms come from Lexibank 2 (`lexibank-analysed` v2.2; List et al. 2022). Each Smith gloss was mapped to a Lexibank concept ID by an explicit dictionary (no fuzzy string matching). For Proto-Kra-Dai validation I used all Lexibank forms whose language is classified as Tai-Kadai. For Proto-Austronesian validation, Lexibank contains on the order of **978** Austronesian languages; sending every form is impractical and would overweight Oceanic. I therefore built a Glottolog-derived coarse clade label for each Lexibank Austronesian language (Hammarström et al. 2024; Formosan; Western Malayo-Polynesian; South Halmahera–West New Guinea; Oceanic) and drew a **phylogenetically stratified sample** of up to **80** languages per concept, with floors of 12 Formosan, 20 Western MP, 8 SHWNG, and 20 Oceanic where available (at most one form per language), filling any remainder by round-robin across clades.

## 4.2 Layer 1: Reconstruction attestation

For each aligned pair with at least one Lexibank daughter form on the relevant side, I asked the LLM to score how well the proposed proto-form is supported by the attested modern forms for that meaning (`attestation_score` on a 1–5 scale), returning brief notes on supporting and problematic reflexes.

- **PKD attestation** used the full Tai-Kadai form list for the mapped concept (uncapped in this release; typically well under 100 forms).
- **PAN attestation** used the stratified Austronesian sample described above.

I defined a **coverage gap** when the gloss could not be mapped to a Lexibank concept, or when fewer than **three** Tai-Kadai languages or fewer than **three** Austronesian languages attested the concept in Lexibank. Coverage-gap pairs were excluded from the permutation test (Tier A) because the reconstruction cannot be checked against a minimally diverse modern sample.

Separately, I labeled a reconstruction **unjustified** when its attestation score equaled **1** (daughters cluster on shapes incompatible with the proposed proto-form under the model’s assessment). Unjustified PKDs and unjustified PANs remain in the descriptive inventory of Smith’s package but are excluded from Tier A: a meaning-blind “hit” against an unsupported reconstruction would not constitute evidence that the *published comparative package* is well founded.

**Tier A**, the analysis set for Layer 2, therefore requires: no coverage gap, PKD `attestation_score` of at least **2**, and PAN `attestation_score` of at least **2** (when a score is available).

## 4.3 Layer 2: Meaning-blind form similarity

For each Tier A pair I submitted the PKD form and the PAN form to the LLM **without** the gloss, without Smith’s notes or loanword flags, and without opaque IDs that embed the meaning (batch indices such as `001`, `002` were used instead). The system prompt instructed the model to score segmental shape similarity only, as if the PAN string were a candidate Austronesian reconstruction for the same slot as the PKD string, and not to infer or mention meaning. The model returned a **liberal resemblance score** on a 1–5 scale (called **generosity** in the software and tables: high scores are intentionally lenient about orthographic variation and partial skeleton matches). A score of 5 means the shapes look very similar under that generous reading; a score of 1 means little resemblance. I count a **hit** when the generosity score is **4 or 5** (written below as a generosity score of 4 or higher). Scores of 3 are treated as non-hits in the primary analysis; lower cutoffs (3 or higher; 2 or higher) can be examined as robustness checks.

Judgments were cached by the pair `(PKD, PAN)` under a fixed prompt version. Consequently, the same form combination receives the same score in the observed alignment and in every permutation that recreates it.

## 4.4 Permutation null

The permutation test asks a simple question: **if the published PAN–PKD pairings were just one of many ways to match the same set of forms, how often would a random matching look as good as Smith’s?**

Concretely: I keep every Tier A PKD form in its meaning slot, then **shuffle the Tier A PAN forms** among those slots (like reshuffling cards into fixed positions). I do this **100** times (fixed random seed). For each shuffled world I count how many pairs would still be “hits” under the same rule (generosity score of 4 or higher), reusing the cache whenever a `(PKD, PAN)` combination had already been scored. The real Smith pairing is then compared with that distribution of chance hit counts.

The one-sided *p*-value is

$$
p = \frac{k + 1}{N + 1},
$$

where *k* is the number of shuffles whose hit count is at least as large as the observed hit count, and *N* = 100 (add-one smoothing). In plain terms: *p* is roughly the share of random reshuffles that do as well as or better than the published pairing. This null does **not** test genetic relatedness, regularity of sound change, or the correctness of every reconstruction; it only asks whether the published matching produces unusually many high form-similarity scores relative to random rematching of the same forms.

## 4.5 Scope and non-claims (Study 1)

I do not propose new etymologies, estimate divergence dates, or claim that high generosity scores equal demonstrated cognacy in the comparative-method sense. The LLM is used as a **reproducible generous screen** for segmental resemblance. Systematic sound correspondences, central to classical arguments for Austro-Tai (e.g. Ostapirat 2005), are not enforced here. Study 1’s contribution is a quantified answer to a narrower question: after setting aside reconstructions that Lexibank daughters do not support, how surprising is the residual form similarity in Smith’s published alignments under a meaning-blind null?

## 4.6 Study 2: Dual-attested Lexibank set-versus-set screen

Study 1 still begins from a **published reconstruction package**. Even after Layer 1 filters, critics may worry that Smith’s spreadsheet preferentially records lookalike-friendly proto-forms. Study 2 removes reconstructions from the design entirely.

### Concept inventory

I considered Lexibank Concepticon concepts attested in at least **15** Tai-Kadai and **15** Austronesian languages (**373** concepts). To focus on meanings standardly used in Austronesian comparative work, I intersected this pool with the **Blust / ABVD 210**-item Concepticon list (Greenhill, Blust & Gray 2008), yielding **194** dual-attested concepts (exact Concepticon ID match). Sixteen Blust items fall outside the dual-attested pool of concepts with at least 15 languages on each side, often because Lexibank splits broader Blust glosses (e.g. FOOT OR LEG vs separate FOOT / LEG).

### Sampling within concepts

For each concept I built phylogenetically stratified form samples:

- **Tai-Kadai.** Glottolog-derived coarse clades (Hammarström et al. 2024; Tai, Kam–Sui, Kra, Hlai, Lakkia–Biao, Be, other); floors then round-robin fill toward a target of ~40 languages (at most one form per language).
- **Austronesian.** Same clade scheme and floors as Study 1’s PAN sample (target ~80).

Before sampling I applied light filters: drop likely onomatopoeic / expressive shapes (very short forms; clear reduplication) and deduplicate near-identical normalized spellings within clade. Tone digits and common separators were ignored in normalization.

### Meaning-blind set scoring

The LLM received two **groups** of forms (clade label + form string only; no gloss, no language names beyond clade tags) and scored hypothetical cognacy from segmental shape alone (generosity 1–5), with instructions to prefer *widespread* shared skeletons over isolated lookalikes and to ignore recognized word meanings. Scores were cached by the group contents under a fixed prompt version. I report how many concepts reach a generosity score of **2 or higher**, **3 or higher**, and **4 or higher**; the primary interpretive threshold remains a score of 4 or higher, with 3 or higher as a secondary cut and 2 or higher as a liberal sensitivity check.

### Permutation null

The Study 2 null is the same idea as in Study 1, applied to form groups rather than single proto-strings. I keep each Tai-Kadai form group in its Concepticon slot, then **randomly reassign Austronesian form groups** to those slots (**30** shuffles; fixed seed), so many trials pair, for example, the Tai-Kadai forms for ‘eye’ with Austronesian forms that originally belonged to some other meaning. For each shuffle I recount how many slots would still be hits at each generosity cutoff. Incomplete permutations were resumable from disk; every null judgment (score, notes, reasoning, and the source concept of the Austronesian form group) was stored so thresholds can be recomputed post hoc. The one-sided *p*-value uses the same (*k*+1)/(*N*+1) estimator as Study 1.

Study 2 therefore tests whether **same-meaning** modern form inventories look more alike, under a generous meaning-blind screen, than **cross-meaning** inventories drawn from the same concept set, without relying on which reconstructions an author chose to publish.

## 4.7 Sinitic loan plausibility screen (post hoc)

Contact with Sinitic is one standard alternative to inheritance for some Austronesian–Kra-Dai lookalikes. After the meaning-blind tests, I therefore ran a separate, **meaning-aware** exploratory screen on the observed hits (Study 1 Tier A pairs and Study 2 Blust concepts with a generosity score of 4 or higher). For each hit the same chat model (`gpt-4.1`) was shown the gloss/concept and the forms (Study 1: PAN and PKD strings; Study 2: concept label plus the model’s earlier shared-shape notes) and asked how plausible it is that the shared resemblance reflects a **Chinese loan into Tai-Kadai and/or Austronesian** (1–5 scale, with a short reason). This is **not** a classical etymological demonstration and does not adjudicate non-Sinitic contact; it is only a transparent check on whether a common Sinitic-donor story looks attractive for the items that drive the permutation results. Machine-readable scores: `output/sinitic_screen_hits.csv`.
