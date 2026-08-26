# 3. Data

## 3.1 Smith’s (2025) Austro-Tai reconstruction package

My comparative object is Alexander D. Smith’s openly released *Austro-Tai comparative dataset (Reconstructions)* on Zenodo (DOI [10.5281/zenodo.15597357](https://doi.org/10.5281/zenodo.15597357); I use release **v1.1**). The spreadsheet lists gloss-aligned reconstructions aimed at Austro-Tai comparison. I retain a row when both a Proto-Austronesian (PAN) string and a Proto-Kra-Dai (PKD) string are present, yielding **120** pairs after parsing.

Besides the two proto-forms, the sheet records branch-level Kra-Dai material (e.g. Proto-Tai, Proto-Hlai, Proto-Kam-Sui, and related columns), optional Chinese-loan flags, and free-text notes. I compute a simple **branch attestation count** (how many Kra-Dai branch columns are non-empty) as descriptive metadata. That count is **not** used as the primary gate for Tier A membership: Layer 1 filters (Lexibank coverage and attestation scores) are defined independently of Smith’s branch columns, so that my exclusions do not merely rediscover the author’s own internal breadth coding.

I treat the package as a **published evidence inventory**, not as a consensus reconstruction of Proto-Kra-Dai or as a replacement for Ostapirat’s (2005, 2013) or Sagart’s (2004, 2005, 2019) comparative proposals. Justification for anchoring the study in this release appears in §2.2.

## 3.2 Lexibank modern forms

Modern forms used to audit reconstructions come from Lexibank 2 (List et al. 2022), specifically the `lexibank-analysed` release **v2.2**. Forms are Concepticon-linked. I map each Smith gloss to a Lexibank concept ID with an **explicit** dictionary (no fuzzy string matching), to avoid systematic mis-links (e.g. *blow* → BLOW (OF WIND) rather than LOW). Unmapped glosses are coverage gaps.

- **Tai-Kadai side.** For PKD attestation I use **all** Lexibank forms whose language is classified as Tai-Kadai for the mapped concept.
- **Austronesian side.** Lexibank includes on the order of **978** Austronesian languages. Using every form for every concept would be costly and would overweight Oceanic. I therefore assign each Lexibank Austronesian language a coarse Glottolog-derived clade (Formosan; Western Malayo-Polynesian; South Halmahera–West New Guinea; Oceanic) and draw a **phylogenetically stratified** sample of up to **80** languages per concept (floors 12 / 20 / 8 / 20 across those clades where available; at most one form per language; remainder filled by round-robin). Details of sampling and attestation prompts are in §4.

## 3.3 Analysis inventories

From the 120 Smith pairs I derive:

| Inventory | Role |
|-----------|------|
| Coverage-gap pairs | Unmapped concept, or &lt; 3 Lexibank Tai-Kadai or &lt; 3 Austronesian languages for the concept |
| Unjustified PKDs | PKD `attestation_score` = 1 vs Lexibank Tai-Kadai forms |
| Unjustified PANs | PAN `attestation_score` = 1 vs the stratified Austronesian sample |
| **Tier A** | No coverage gap; PKD and PAN scores of at least 2 — input to meaning-blind judging and permutation |

Counts and the path from 120 pairs to **79** Tier A pairs are reported in §5. Software, caches, and machine-readable tables accompanying this paper reproduce these inventories from the same inputs.

## 3.4 Study 2: Dual-attested Lexibank concepts (no reconstructions)

Study 2 uses Lexibank forms directly. I retain Concepticon concepts with at least **15** Tai-Kadai and **15** Austronesian languages in Lexibank (**373** concepts), then intersect with the Blust / ABVD 210-item Concepticon list (Greenhill, Blust & Gray 2008; **194** concepts). Within each concept I draw stratified Tai-Kadai and Austronesian samples (§4.6). Machine-readable inventories: `data/attested_pilot/core_concepts_blust.tsv`, `data/attested_pilot/Blust-2008-210.tsv`.
