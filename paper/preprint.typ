= How surprising are Austro-Tai lookalikes? Meaning-blind permutation tests of Smith's (2025) reconstructions and of dual-attested Lexibank form inventories
<how-surprising-are-austro-tai-lookalikes-meaning-blind-permutation-tests-of-smiths-2025-reconstructions-and-of-dual-attested-lexibank-form-inventories>
Jeremy Collins

Companion code and data:
#link("https://github.com/jeremycollinsmpi/austro-tai-llm-test")[github.com/jeremycollinsmpi/austro-tai-llm-test].

== Abstract
<abstract>
The Austro-Tai hypothesis posits a genetic link between Austronesian and
Kra-Dai (Tai-Kadai). Published lexical comparisons are hard to quantify:
lists may mix robust etymologies with weakly justified or
lookalike-friendly reconstructions, and similarity judgments inflate
when meanings are known. I report two meaning-blind permutation screens
in which an LLM (`gpt-4.1`, via API) scores segmental form similarity
without seeing meanings. #strong[Study 1] audits Alexander D. Smith's
(2025) gloss-aligned Proto-Austronesian (PAN) and Proto-Kra-Dai (PKD)
reconstructions: after Lexibank (List et al.~2022) attestation filters,
27 of 79 #strong[Tier A] pairs---those with adequate Lexibank coverage
and attestation scores of at least 2 for both PAN and PKD---meet a
generous hit threshold (generosity score of 4 or higher) against a null
mean of 5.7 (100 permutations; one-sided #emph[p] ≈ 0.01). #strong[Study
2] is designed to be more robust to reconstruction cherry-picking. It
compares phylogenetically sampled modern Lexibank form groups for the
same Concepticon meaning---restricted to dual-attested concepts on the
Blust/ABVD basic-vocabulary list (194 concepts; Greenhill, Blust & Gray
2008)---and shuffles Austronesian form groups across Tai-Kadai slots.
Hits at a generosity score of 4 or higher / 3 or higher / 2 or higher
are 11 / 17 / 121 against null means of about 2.2 / 5.7 / 91.7 (30
permutations; #emph[p] ≈ 0.032 at each of those thresholds). Convergence
across a reconstruction audit and a reconstruction-free Lexibank screen
supports excess form resemblance under these controls---not genetic
proof, which requires systematic sound correspondences. I situate the
results in the Austro-Tai literature (Benedict; Ostapirat; Sagart) and
discuss limits of LLM-based screening.

#strong[Keywords:] Austro-Tai; Kra-Dai; Austronesian; lexical
comparison; chance resemblance; permutation test; Lexibank; large
language models; Blust basic vocabulary

= 1. Introduction
<introduction>
Macro-comparative hypotheses live or die on lexical and phonological
evidence, yet it remains surprisingly hard to say #strong[how strong] a
published lookalike package is. Impressive lists can mix secure
etymologies with weakly justified reconstructions; judgments of
“similarity” inflate when meanings are visible; and without an explicit
chance baseline, it is unclear whether the published pairing of forms
across two proto-languages exceeds what generous form matching would
produce under random reassignment.

The #strong[Austro-Tai] hypothesis---positing a genetic link between
Austronesian and Kra-Dai (Tai-Kadai)---is a long-standing case in point.
From Benedict's early lexical proposals through Ostapirat's
correspondence-based arguments and Sagart's phylogenetic alternatives,
debate has turned on whether shared vocabulary reflects inheritance,
contact, or chance (see §2). What has been rarer is a statistical audit
under controls that address two confounders at once: (i)
#strong[semantic priming] in cognate-style judgments, and (ii)
#strong[selection of favorable forms], whether as weakly attested
reconstructions or as cherry-picked lookalikes among modern languages.

This paper does not assemble a new cognate list, propose regular sound
correspondences, or adjudicate sister-family vs Austronesian-internal
geometries for Kra-Dai. It asks two related questions. #strong[Study 1]
takes Alexander D. Smith's (2025) open Zenodo package of gloss-aligned
Proto-Austronesian (PAN) and Proto-Kra-Dai (PKD) reconstructions as the
object of evaluation: how much form resemblance remains---and how
surprising is it---after weakly attested reconstructions are set aside?
#strong[Study 2] asks a stricter follow-up that does not depend on any
reconstruction package: among well-attested Lexibank concepts (List et
al.~2022), do #strong[groups of modern Tai-Kadai and Austronesian forms]
for the #emph[same] meaning show more shape resemblance than form groups
for #emph[mismatched] meanings under a meaning-blind screen?

Study 1 has two layers. #strong[Layer 1] scores each reconstruction
against modern Lexibank forms (all Tai-Kadai daughters for PKD; a
phylogenetically stratified Austronesian sample for PAN) and excludes
coverage gaps and attestation score 1 from the analysis set (Tier A).
#strong[Layer 2] compares PAN and PKD #strong[forms only] (meanings
withheld) with a fixed LLM screen and tests whether high similarity
scores exceed a null in which PAN shapes are randomly reassigned across
PKD slots. On #strong[79] Tier A pairs I observe #strong[27] hits
(generosity score of 4 or higher) against a null mean of #strong[5.7]
(100 permutations; one-sided #emph[p] ≈ 0.01).

Study 2 is designed to be more robust to reconstruction cherry-picking.
Concept selection follows Lexibank coverage and the Austronesian Basic
Vocabulary (Blust/ABVD) Concepticon list (Greenhill, Blust & Gray 2008)
rather than an author's comparative spreadsheet; within each concept I
draw phylogenetically stratified modern samples (with onomatopoeia and
near-duplicate filters) and score #strong[set-versus-set] shape
resemblance without showing the gloss. The null shuffles Austronesian
form groups across Tai-Kadai slots. On #strong[194] dual-attested Blust
concepts, I find #strong[11] hits at a generosity score of 4 or higher
against a null mean of #strong[2.2] (30 permutations; one-sided #emph[p]
≈ 0.032); the same floor #emph[p] holds at a score of 3 or higher (17 vs
5.7) and even at the liberal cutoff of 2 or higher (121 vs 91.7).

I interpret both results as quantified evidence of #strong[excess form
resemblance under stated controls]---not as proof of genetic
relationship, which would require systematic sound correspondences.
Study 2's convergence with Study 1 is especially informative because it
does not inherit Smith's choice of which proto-forms to align.

Section 2 surveys the Austro-Tai literature and justifies using Smith
(2025) for Study 1. Section 3 describes the data. Section 4 details
methods for both studies. Section 5 reports results. Section 6 discusses
interpretation and limits; Section 7 concludes.

= 2. Background: Austro-Tai and the assessment of lexical evidence
<background-austro-tai-and-the-assessment-of-lexical-evidence>
== 2.1 Literature map
<literature-map>
=== Early proposal and controversy
<early-proposal-and-controversy>
Paul K. Benedict (1942, 1975) advanced #strong[Austro-Tai] as a deep
genetic relationship linking Austronesian with what is now usually
called Kra-Dai (Tai-Kadai), drawing heavily on lexical lookalikes across
basic and cultural vocabulary. The proposal was influential in framing a
research program, and equally influential as a cautionary example in
methodological debates: multilateral comparison without tightly
controlled sound correspondences invites chance resemblance, semantic
stretch, and post hoc selection of favorable pairs. Whatever one's view
of Benedict's specific etymologies, the enduring problem he raises for
later work is how to tell #strong[how much] of a published lookalike
package exceeds what chance and liberal similarity judgments would
produce.

=== Regular correspondences and a sister-family construal
<regular-correspondences-and-a-sister-family-construal>
A major modern strand argues that Kra-Dai and Austronesian are related
as #strong[sister families] (or close relatives) on the strength of
basic vocabulary #strong[and] systematic phonological correspondences.
Ostapirat (2005, 2013) is central here: the claim is not merely that
many forms look alike when meanings are matched, but that segmental (and
related) correspondences can be stated with comparative-method
discipline. On this view, Austro-Tai is a classical genetic hypothesis
to be won or lost on regularity and reconstructibility, not on raw list
length. My study does #strong[not] re-implement Ostapirat's
correspondence system; I return to it in the Discussion as the standard
against which “non-chance form resemblance under a generous screen”
remains a weaker, preliminary kind of evidence.

=== Alternative phylogenetic architecture
<alternative-phylogenetic-architecture>
A second modern strand, associated especially with Sagart (2004, 2005,
2019), places Kra-Dai in a more #strong[Austronesian-internal] (or
AN-adjacent) phylogenetic frame---linking numerals, subgrouping
arguments, and models of how Kra-Dai tone systems might relate to
Austronesian coda history (see also recent tonogenesis discussion such
as Liao & Gehrmann 2025 in #emph[Diachronica]). The empirical overlap
with Ostapirat's comparisons can be substantial even when the
#strong[tree geometry] differs: both traditions posit more than
accidental lexical connection between the families, but they disagree on
where Kra-Dai sits relative to Formosan and Malayo-Polynesian
diversification. My permutation result is intentionally
#strong[agnostic] on sister-family vs AN-internal architecture; excess
form similarity in a published alignment set is compatible with either
genealogy once chance browsing is set aside.

=== Contact, loans, and areal lookalikes
<contact-loans-and-areal-lookalikes>
Kra-Dai languages have long histories of contact with Sinitic and with
mainland Southeast Asian neighbors. Chinese loans, calques, and areal
diffusion can produce meaning-matched form similarities that are not
inheritance from a shared Austro-Tai parent. Published reconstruction
packages may flag some Chinese comparisons (Smith's sheet includes
Chinese-related columns and notes); my Layer 2 judge never sees those
flags or the glosses, but Layer 1 attestation against Lexibank daughters
does not by itself separate inheritance from old loans that have become
family-internal. Contact therefore remains a live alternative
explanation for residual lookalikes and a limit on interpreting
aggregate hit counts as phylogenetic proof.

=== Competing higher groupings (brief)
<competing-higher-groupings-brief>
Austro-Tai is one among several contested higher-order proposals
involving Austronesian (e.g.~strands of Austric or Sino-Austronesian
argumentation). I mention them only to locate Austro-Tai in a crowded
macro-comparative landscape: the present paper audits #strong[one] open
Austro-Tai package under explicit statistical controls, not the relative
merits of every macro-family hypothesis.

=== Chance resemblance and the need for null models
<chance-resemblance-and-the-need-for-null-models>
Methodological critiques of multilateral comparison (notably Ringe and
related work) stress that large vocabularies, phonetic latitude, and
semantic flexibility make impressive-looking lists easy to assemble.
When the object of evaluation is itself a #strong[published list], the
natural statistical question is comparative: relative to a well-defined
null, how often would equally “generous” form matches arise if
proto-shapes were randomly re-paired across meanings? Explicit
permutation or chance baselines remain uncommon for entire Austro-Tai
alignment sets---especially after first removing reconstructions that
modern daughters do not support. That is the gap this paper addresses.

#strong[Table 1 (schematic).] Positions in the Austro-Tai debate
(compact).

#figure(
  align(center)[#table(
    columns: (13.33%, 18.33%, 41.67%, 26.67%),
    align: (auto,auto,auto,auto,),
    table.header([Strand], [Exemplars], [Core claim
      (simplified)], [Relevance here],),
    table.hline(),
    [Early lexical macro-comparison], [Benedict (1942, 1975)], [Deep
    AN--KD link via lookalikes], [Motivates quantifying list strength],
    [Sisters + correspondences], [Ostapirat (2005, 2013)], [Relatedness
    via regular sound change], [Stronger standard than my screen],
    [AN-linked phylogeny / tonogenesis], [Sagart (2004--2019); cf.~Liao
    & Gehrmann (2025)], [KD placed in/near AN
    diversification], [Compatible with non-chance lexical signal;
    different tree],
    [Contact / loans], [Sinitic and mainland SEA contact
    traditions], [Lookalikes need not be genetic], [Limits causal
    interpretation of hits],
    [Chance / method critique], [Ringe and related], [Need nulls and
    tight controls], [Motivates permutation design],
  )]
  , kind: table
  )

== 2.2 Justification for using Smith (2025)
<justification-for-using-smith-2025>
I take as my object of evaluation Alexander D. Smith's (2025)
#emph[Austro-Tai comparative dataset (Reconstructions)] (Zenodo), rather
than compiling a new etymological list. Three properties motivate that
choice.

First, the spreadsheet provides #strong[gloss-aligned]
Proto-Austronesian and Proto-Kra-Dai reconstructions in a single package
explicitly aimed at Austro-Tai comparison. That structure makes a
slot-wise permutation test well-defined: PKD forms (and meaning slots)
can be held fixed while PAN forms are shuffled across slots, so that the
null world preserves the same inventory of shapes and asks only whether
the #strong[published pairing] is special.

Second, the release is #strong[open, versioned, and preliminary] by the
author's own framing. Preliminary reconstruction packages invite exactly
the stress test I perform: external checks on whether proposed
proto-forms are recoverable from modern Lexibank daughters, and a
quantified assessment of residual form similarity after weak
reconstructions are set aside. Branch-level Kra-Dai columns in the sheet
(Proto-Tai, Proto-Hlai, etc.) supply an author-internal signal of
comparative breadth; I report them descriptively but do not use them as
my primary eligibility filter, so that Tier A is defined by
Lexibank-facing criteria rather than by reifying Smith's branch coding.

Third, anchoring the study in an independent published dataset reduces
#strong[researcher degrees of freedom] in selecting which comparisons
count as evidence. Had I assembled my own cognate list, critics could
fairly ask whether the list was tuned to survive the permutation test.
By freezing Smith's alignments as the object of audit, the researcher's
main choices become the attestation rules, the meaning-blind prompt, and
the hit threshold---choices I state explicitly and can vary in
robustness checks---rather than which etymologies enter the denominator.

I do #strong[not] treat Smith (2025) as consensus Proto-Kra-Dai, as a
definitive PAN lexicon, or as superseding Ostapirat or Sagart. I treat
it as a #strong[contemporary evidence package]: a transparent inventory
of what has been presented for Austro-Tai comparison in an openly
citable form. My question is not whether every Smith reconstruction is
correct, but how much residual PAN--PKD form similarity remains---and
how surprising that residual is under a meaning-blind null---after
reconstructions unsupported by Lexibank daughters are removed.

= 3. Data
<data>
== 3.1 Smith's (2025) Austro-Tai reconstruction package
<smiths-2025-austro-tai-reconstruction-package>
My comparative object is Alexander D. Smith's openly released
#emph[Austro-Tai comparative dataset (Reconstructions)] on Zenodo (DOI
#link("https://doi.org/10.5281/zenodo.15597357")[10.5281/zenodo.15597357]\;
I use release #strong[v1.1]). The spreadsheet lists gloss-aligned
reconstructions aimed at Austro-Tai comparison. I retain a row when both
a Proto-Austronesian (PAN) string and a Proto-Kra-Dai (PKD) string are
present, yielding #strong[120] pairs after parsing.

Besides the two proto-forms, the sheet records branch-level Kra-Dai
material (e.g.~Proto-Tai, Proto-Hlai, Proto-Kam-Sui, and related
columns), optional Chinese-loan flags, and free-text notes. I compute a
simple #strong[branch attestation count] (how many Kra-Dai branch
columns are non-empty) as descriptive metadata. That count is
#strong[not] used as the primary gate for Tier A membership: Layer 1
filters (Lexibank coverage and attestation scores) are defined
independently of Smith's branch columns, so that my exclusions do not
merely rediscover the author's own internal breadth coding.

I treat the package as a #strong[published evidence inventory], not as a
consensus reconstruction of Proto-Kra-Dai or as a replacement for
Ostapirat's or Sagart's comparative proposals. Justification for
anchoring the study in this release appears in §2.2.

== 3.2 Lexibank modern forms
<lexibank-modern-forms>
Modern forms used to audit reconstructions come from Lexibank 2 (List et
al.~2022), specifically the `lexibank-analysed` release #strong[v2.2].
Forms are Concepticon-linked. I map each Smith gloss to a Lexibank
concept ID with an #strong[explicit] dictionary (no fuzzy string
matching), to avoid systematic mis-links (e.g.~#emph[blow] → BLOW (OF
WIND) rather than LOW). Unmapped glosses are coverage gaps.

- #strong[Tai-Kadai side.] For PKD attestation I use #strong[all]
  Lexibank forms whose language is classified as Tai-Kadai for the
  mapped concept.
- #strong[Austronesian side.] Lexibank includes on the order of
  #strong[978] Austronesian languages. Using every form for every
  concept would be costly and would overweight Oceanic. I therefore
  assign each Lexibank Austronesian language a coarse Glottolog-derived
  clade (Formosan; Western Malayo-Polynesian; South Halmahera--West New
  Guinea; Oceanic) and draw a #strong[phylogenetically stratified]
  sample of up to #strong[80] languages per concept (floors 12 / 20 / 8
  \/ 20 across those clades where available; at most one form per
  language; remainder filled by round-robin). Details of sampling and
  attestation prompts are in §4.

== 3.3 Analysis inventories
<analysis-inventories>
From the 120 Smith pairs I derive:

#figure(
  align(center)[#table(
    columns: (64.71%, 35.29%),
    align: (auto,auto,),
    table.header([Inventory], [Role],),
    table.hline(),
    [Coverage-gap pairs], [Unmapped concept, or \< 3 Lexibank Tai-Kadai
    or \< 3 Austronesian languages for the concept],
    [Unjustified PKDs], [PKD `attestation_score` = 1 vs Lexibank
    Tai-Kadai forms],
    [Unjustified PANs], [PAN `attestation_score` = 1 vs the stratified
    Austronesian sample],
    [#strong[Tier A]], [No coverage gap; PKD and PAN scores of at least
    2 --- input to meaning-blind judging and permutation],
  )]
  , kind: table
  )

Counts and the path from 120 pairs to #strong[79] Tier A pairs are
reported in §5. Software, caches, and machine-readable tables
accompanying this paper reproduce these inventories from the same
inputs.

== 3.4 Study 2: Dual-attested Lexibank concepts (no reconstructions)
<study-2-dual-attested-lexibank-concepts-no-reconstructions>
Study 2 uses Lexibank forms directly. I retain Concepticon concepts with
at least #strong[15] Tai-Kadai and #strong[15] Austronesian languages in
Lexibank (#strong[373] concepts), then intersect with the Blust / ABVD
210-item Concepticon list (Greenhill, Blust & Gray 2008; #strong[194]
concepts). Within each concept I draw stratified Tai-Kadai and
Austronesian samples (§4.6). Machine-readable inventories:
`data/attested_pilot/core_concepts_blust.tsv`,
`data/attested_pilot/Blust-2008-210.tsv`.

= 4. Methods
<methods>
My analysis has two studies that share a meaning-blind LLM screen and a
permutation null, but differ in what is being paired.

#strong[Study 1] (Smith reconstructions) has two layers. #strong[Layer
1] asks whether each published proto-form is supported by modern
Lexibank daughters for the same Concepticon meaning. #strong[Layer 2]
asks whether, among reconstructions that pass Layer 1, the published
PAN--PKD pairings show more #strong[segmental form similarity] than
expected if PAN shapes were randomly reassigned across PKD slots.

#strong[Study 2] (Lexibank attested forms) drops reconstructions. For
dual-attested Concepticon concepts on a Blust/ABVD basic-vocabulary
filter, it compares #strong[groups of modern Tai-Kadai and Austronesian
forms] for the same meaning against a null that shuffles Austronesian
form groups across Tai-Kadai slots. The motivation is robustness: Study
2 cannot inherit cherry-picking of lookalike-friendly proto-forms from a
reconstruction spreadsheet.

Both studies withhold meanings from the similarity judge. All LLM calls
used the chat endpoint configured for this project with model `gpt-4.1`.
Prompts and scoring rules are fixed in the accompanying software
release; responses were parsed as JSON, with light sanitization and up
to three retries on malformed output. Scores were cached so that
identical inputs were never re-queried inconsistently between observed
and null analyses.

== 4.1 Data: Smith alignments and Lexibank
<data-smith-alignments-and-lexibank>
I parsed Alexander D. Smith's (2025) Austro-Tai reconstruction
spreadsheet (Zenodo release v1.1) into gloss-aligned pairs in which both
a Proto-Austronesian (PAN) and a Proto-Kra-Dai (PKD) reconstruction are
present. After excluding rows without both sides, #strong[120] pairs
remained. Smith's sheet also records branch-level Kra-Dai reflexes
(e.g.~Proto-Tai, Proto-Hlai, Proto-Kam-Sui); I retain branch attestation
counts as descriptive metadata but do not use them as the primary filter
for Tier A membership.

Modern forms come from Lexibank 2 (`lexibank-analysed` v2.2; List et
al.~2022). Each Smith gloss was mapped to a Lexibank concept ID by an
#strong[explicit] dictionary (no fuzzy string matching), to avoid errors
such as mapping #emph[blow] to LOW rather than BLOW (OF WIND). For
Proto-Kra-Dai validation I used all Lexibank forms whose language is
classified as Tai-Kadai. For Proto-Austronesian validation, Lexibank
contains on the order of #strong[978] Austronesian languages; sending
every form is impractical and would overweight Oceanic. I therefore
built a Glottolog-derived coarse clade label for each Lexibank
Austronesian language (Formosan; Western Malayo-Polynesian; South
Halmahera--West New Guinea; Oceanic) and drew a #strong[phylogenetically
stratified sample] of up to #strong[80] languages per concept, with
floors of 12 Formosan, 20 Western MP, 8 SHWNG, and 20 Oceanic where
available (at most one form per language), filling any remainder by
round-robin across clades.

== 4.2 Layer 1: Reconstruction attestation
<layer-1-reconstruction-attestation>
For each aligned pair with at least one Lexibank daughter form on the
relevant side, I asked the LLM to score how well the proposed proto-form
is supported by the attested modern forms for that meaning
(`attestation_score` on a 1--5 scale), returning brief notes on
supporting and problematic reflexes.

- #strong[PKD attestation] used the full Tai-Kadai form list for the
  mapped concept (uncapped in this release; typically well under 100
  forms).
- #strong[PAN attestation] used the stratified Austronesian sample
  described above.

I defined a #strong[coverage gap] when the gloss could not be mapped to
a Lexibank concept, or when fewer than #strong[three] Tai-Kadai
languages or fewer than #strong[three] Austronesian languages attested
the concept in Lexibank. Coverage-gap pairs were excluded from the
permutation test (Tier A) because the reconstruction cannot be checked
against a minimally diverse modern sample.

Separately, I labeled a reconstruction #strong[unjustified] when its
attestation score equaled #strong[1] (daughters cluster on shapes
incompatible with the proposed proto-form under the model's assessment).
Unjustified PKDs and unjustified PANs remain in the descriptive
inventory of Smith's package but are excluded from Tier A: a
meaning-blind “hit” against an unsupported reconstruction would not
constitute evidence that the #emph[published comparative package] is
well founded.

#strong[Tier A]---the analysis set for Layer 2---therefore requires: no
coverage gap, PKD `attestation_score` of at least #strong[2], and PAN
`attestation_score` of at least #strong[2] (when a score is available).

== 4.3 Layer 2: Meaning-blind form similarity
<layer-2-meaning-blind-form-similarity>
For each Tier A pair I submitted the PKD form and the PAN form to the
LLM #strong[without] the gloss, without Smith's notes or loanword flags,
and without opaque IDs that embed the meaning (batch indices such as
`001`, `002` were used instead). The system prompt instructed the model
to score segmental shape similarity only---as if the PAN string were a
candidate Austronesian reconstruction for the same slot as the PKD
string---and not to infer or mention meaning. The model returned a
#strong[generosity] score from 1 to 5 together with optional notes on
plausible segmental correspondences. A score of 5 means the shapes look
very similar under a generous reading; a score of 1 means little
resemblance. I count a #strong[hit] when the generosity score is
#strong[4 or 5] (written below as a generosity score of 4 or higher).
Scores of 3 are treated as non-hits in the primary analysis; lower
cutoffs (3 or higher; 2 or higher) can be examined as robustness checks.

Judgments were cached by the pair `(PKD, PAN)` under a fixed prompt
version. Consequently, the same form combination receives the same score
in the observed alignment and in every permutation that recreates it.

== 4.4 Permutation null
<permutation-null>
The permutation test asks a simple question: #strong[if the published
PAN--PKD pairings were just one of many ways to match the same set of
forms, how often would a random matching look as good as Smith's?]

Concretely: I keep every Tier A PKD form in its meaning slot, then
#strong[shuffle the Tier A PAN forms] among those slots (like
reshuffling cards into fixed positions). I do this #strong[100] times
(fixed random seed). For each shuffled world I count how many pairs
would still be “hits” under the same rule (generosity score of 4 or
higher), reusing the cache whenever a `(PKD, PAN)` combination had
already been scored. The real Smith pairing is then compared with that
distribution of chance hit counts.

The one-sided #emph[p]-value is

\[ p = , \]

where #emph[k] is the number of shuffles whose hit count is at least as
large as the observed hit count, and #emph[N] = 100 (add-one smoothing).
In plain terms: #emph[p] is roughly the share of random reshuffles that
do as well as or better than the published pairing. This null does
#strong[not] test genetic relatedness, regularity of sound change, or
the correctness of every reconstruction---only whether the published
matching produces unusually many high form-similarity scores relative to
random rematching of the same forms.

== 4.5 Scope and non-claims (Study 1)
<scope-and-non-claims-study-1>
I do not propose new etymologies, estimate divergence dates, or claim
that high generosity scores equal demonstrated cognacy in the
comparative-method sense. The LLM is used as a #strong[reproducible
generous screen] for segmental resemblance. Systematic sound
correspondences---central to classical arguments for Austro-Tai
(e.g.~Ostapirat 2005)---are not enforced here. Study 1's contribution is
a quantified answer to a narrower question: after setting aside
reconstructions that Lexibank daughters do not support, how surprising
is the residual form similarity in Smith's published alignments under a
meaning-blind null?

== 4.6 Study 2: Dual-attested Lexibank set-versus-set screen
<study-2-dual-attested-lexibank-set-versus-set-screen>
Study 1 still begins from a #strong[published reconstruction package].
Even after Layer 1 filters, critics may worry that Smith's spreadsheet
preferentially records lookalike-friendly proto-forms. Study 2 removes
reconstructions from the design entirely.

=== Concept inventory
<concept-inventory>
I considered Lexibank Concepticon concepts attested in at least
#strong[15] Tai-Kadai and #strong[15] Austronesian languages
(#strong[373] concepts). To focus on meanings standardly used in
Austronesian comparative work, I intersected this pool with the
#strong[Blust / ABVD 210]-item Concepticon list (Greenhill, Blust & Gray
2008), yielding #strong[194] dual-attested concepts (exact Concepticon
ID match). Sixteen Blust items fall outside the dual-attested pool of
concepts with at least 15 languages on each side, often because Lexibank
splits broader Blust glosses (e.g.~FOOT OR LEG vs separate FOOT / LEG).

=== Sampling within concepts
<sampling-within-concepts>
For each concept I built phylogenetically stratified form samples:

- #strong[Tai-Kadai.] Glottolog-derived coarse clades (Tai, Kam--Sui,
  Kra, Hlai, Lakkia--Biao, Be, other); floors then round-robin fill
  toward a target of \~40 languages (at most one form per language).
- #strong[Austronesian.] Same clade scheme and floors as Study 1's PAN
  sample (target \~80).

Before sampling I applied light filters: drop likely onomatopoeic /
expressive shapes (very short forms; clear reduplication) and
deduplicate near-identical normalized spellings within clade. Tone
digits and common separators were ignored in normalization.

=== Meaning-blind set scoring
<meaning-blind-set-scoring>
The LLM received two #strong[groups] of forms (clade label + form string
only)---no gloss, no language names beyond clade tags---and scored
hypothetical cognacy from segmental shape alone (generosity 1--5), with
instructions to prefer #emph[widespread] shared skeletons over isolated
lookalikes and to ignore recognized word meanings. Scores were cached by
the group contents under a fixed prompt version. I report how many
concepts reach a generosity score of #strong[2 or higher], #strong[3 or
higher], and #strong[4 or higher]\; the primary interpretive threshold
remains a score of 4 or higher, with 3 or higher as a secondary cut and
2 or higher as a liberal sensitivity check.

=== Permutation null
<permutation-null-1>
The Study 2 null is the same idea as in Study 1, applied to form groups
rather than single proto-strings. I keep each Tai-Kadai form group in
its Concepticon slot, then #strong[randomly reassign Austronesian form
groups] to those slots (#strong[30] shuffles; fixed seed)---so many
trials pair, for example, the Tai-Kadai forms for ‘eye' with
Austronesian forms that originally belonged to some other meaning. For
each shuffle I recount how many slots would still be hits at each
generosity cutoff. Incomplete permutations were resumable from disk;
every null judgment (score, notes, reasoning, and the source concept of
the Austronesian form group) was stored so thresholds can be recomputed
post hoc. The one-sided #emph[p]-value uses the same
(#emph[k]+1)/(#emph[N]+1) estimator as Study 1.

Study 2 therefore tests whether #strong[same-meaning] modern form
inventories look more alike, under a generous meaning-blind screen, than
#strong[cross-meaning] inventories drawn from the same concept
set---without relying on which reconstructions an author chose to
publish.

= 5. Results
<results>
== 5.1 From Smith's sheet to Tier A
<from-smiths-sheet-to-tier-a>
Starting from #strong[120] gloss-aligned PAN--PKD pairs, Layer 1
exclusions left #strong[79] Tier A pairs for the permutation test (Table
1).

#strong[Table 1.] Sample construction.

#figure(
  align(center)[#table(
    columns: (58.33%, 41.67%),
    align: (auto,right,),
    table.header([Stage], [#emph[n]],),
    table.hline(),
    [Smith pairs with both PAN and PKD], [120],
    [Coverage gaps (unmapped concept, or \< 3 Lexibank Tai-Kadai or
    Austronesian languages)], [13],
    [Unjustified PKDs (`attestation_score` = 1)], [14],
    [Unjustified PANs (`attestation_score` = 1)], [27],
    [#strong[Tier A] (no coverage gap; PKD and PAN scores of at least
    2)], [#strong[79]],
  )]
  , kind: table
  )

Categories are not disjoint: some pairs are both coverage-limited and
score-1 on one side, and #strong[6] pairs are unjustified on both the
PKD and PAN sides. The important design point is that Tier A retains
only slots where both reconstructions clear a minimal attestation bar
against modern Lexibank evidence.

Among pairs that received attestation scores, PKD scores were
distributed as 14 / 31 / 11 / 27 / 34 for scores 1 through 5
respectively (#emph[n] = 117 scored). PAN scores on the stratified
Austronesian sample were 27 / 27 / 12 / 14 / 31 (#emph[n] = 111 scored).
Thus a non-trivial fraction of the published package---especially on the
Austronesian side under my sampling scheme---was judged poorly supported
by daughters and was withheld from the chance test of form pairing.

Within Tier A, PKD attestation scores were predominantly 2--5 (25, 9,
22, and 23 pairs at scores 2--5), and PAN scores were likewise 2--5 (24,
11, 13, and 31). Tier A is therefore not restricted to only the most
secure reconstructions; it excludes the weakest Layer 1 cases while
still including many middling scores.

== 5.2 Observed meaning-blind hits
<observed-meaning-blind-hits>
On the #strong[79] Tier A pairs, the meaning-blind judge assigned a
generosity score of 4 or higher to #strong[27] pairs (#strong[34.2%]).
Of these hits, #strong[18] scored 5 and #strong[9] scored 4.

Illustrative high-scoring form pairs (generosity 5) include
near-identity or near-identity modulo length/diacritics such as 1sg PAN
\*#emph[aku] \~ PKD \*#emph[aku]\; ‘die' \*#emph[\(m/p-)aCay] \~
\*#emph[p-ataːy]\; ‘eat' \*#emph[ka(ʔ)ən] \~ \*#emph[\(i-)kan]\; ‘moon'
\*#emph[bulaN] \~ \*#emph[buɭaːl]\; and ‘nine' \*#emph[siwa] \~
\*#emph[\(s(i)waː)]. These examples are listed for transparency; the
statistical claim below concerns the #strong[aggregate] hit count, not
any single etymology.

== 5.3 Permutation null
<permutation-null-2>
Across #strong[100] random reassignments of Tier A PAN forms to Tier A
PKD slots, the number of hits (pairs with a generosity score of 4 or
higher) had mean #strong[5.68], median #strong[6], and range
#strong[1--12] (first--third quartiles approximately 4--7). The observed
count of #strong[27] lies far above every null draw: no permutation
produced 27 or more hits. The one-sided #emph[p]-value is therefore

\[ p = . \]

Under this screen, the published pairing yields roughly #strong[four to
five times] as many high form-similarity scores as the average null
world (27 vs 5.7), and about #strong[twice] as many as the most extreme
null world in the sample (27 vs 12).

== 5.4 Sensitivity
<sensitivity>
Holding the empirical null distribution fixed, I asked how far the
observed hit count would have to fall before #emph[p] exceeded 0.05.
With this null, an observed count of #strong[10] still yields #emph[p] ≈
0.030, whereas #strong[9] yields #emph[p] ≈ 0.069. Relative to the
actual #strong[27] hits, that corresponds to discarding at least
#strong[18] of the 27 hits (two-thirds of them) before the result would
cease to be significant at the 5% level under this null sample. This is
a sensitivity calculation, not a new experiment: if entire slots were
removed from Tier A, the null would also change. It does indicate,
however, that the gap between observed and null is not a fragile one-hit
margin.

== 5.5 Interim summary (Study 1)
<interim-summary-study-1>
After excluding coverage gaps and reconstructions scored as unsupported
by Lexibank daughters, Smith's (2025) remaining PAN--PKD alignments show
meaning-blind form similarity well above a shuffled baseline (#emph[p] ≈
0.01, #emph[N] = 100).

== 5.6 Study 2: Lexibank dual-attested concepts (Blust filter)
<study-2-lexibank-dual-attested-concepts-blust-filter>
=== Concept set
<concept-set>
Intersecting Lexibank concepts with at least 15 Tai-Kadai and at least
15 Austronesian languages (#strong[373]) with the Blust/ABVD 210
Concepticon list (Greenhill, Blust & Gray 2008) yielded #strong[194]
analysis concepts. Coverage is high for core vocabulary (many concepts
have 60+ Tai-Kadai and 500+ Austronesian languages before sampling).

=== Observed set-versus-set scores
<observed-set-versus-set-scores>
On the #strong[194] concepts, generosity scores were dominated by 1--2
(73 and 104 concepts respectively), with #strong[6] scoring 3 and
#strong[11] scoring 4 (none scoring 5). Primary hits (a generosity score
of 4 or higher) are: #emph[eye], #emph[nose], #emph[eat], #emph[water],
#emph[bite], #emph[shoulder], #emph[mother], #emph[this], #emph[we],
#emph[blow (of wind)], and #emph[be dead or die]. Adding a generosity
score of 3 brings in #emph[fire], #emph[I], #emph[wing], #emph[ten],
#emph[dust], and #emph[lightning] (#strong[17] total at a score of 3 or
higher). At the liberal cutoff of a score of 2 or higher, #strong[121]
concepts qualify---useful for sensitivity, but too inclusive for a
primary claim.

Judge notes for hits with a score of 4 or higher typically cite
recurring skeletons familiar from classical comparisons
(e.g.~#emph[mata]-like clusters for ‘eye'; #emph[nam] /
#emph[danum]-like shapes for ‘water'; #emph[kVn] for ‘eat';
#emph[kat]-like shapes for ‘bite'). I treat these as transparency, not
as etymological endorsements.

=== Permutation null
<permutation-null-3>
Across #strong[30] random reassignments of Austronesian form groups to
Tai-Kadai slots, hit counts were as follows (each row is a cutoff on the
1--5 generosity score):

#figure(
  align(center)[#table(
    columns: (18.97%, 17.24%, 18.97%, 20.69%, 24.14%),
    align: (right,right,right,auto,right,),
    table.header([Generosity cutoff], [Observed], [Null mean], [Null
      range], [One-sided #emph[p]],),
    table.hline(),
    [2 or higher], [121], [91.7], [80--103], [0.032],
    [3 or higher], [17], [5.7], [1--15], [0.032],
    [4 or higher], [11], [2.2], [0--6], [0.032],
    [5], [0], [0.2], [0--1], [1.0],
  )]
  , kind: table
  )

No null world reached the observed count at a score of 2 or higher, 3 or
higher, or 4 or higher, so each of those #emph[p]-values equals the
add-one floor #strong[1/31 ≈ 0.032]. The gap at a score of 4 or higher
is especially clear: observed #strong[11] versus null mean #strong[2.2]
(max #strong[6]). At a score of 2 or higher the absolute null is high
(\~92), as expected for a liberal threshold, but the observed count
still sits above every null draw.

=== Relation to Study 1
<relation-to-study-1>
Study 2's hit rate at a score of 4 or higher (#strong[11/194 ≈ 5.7%]) is
lower than Study 1's Tier A hit rate (#strong[27/79 ≈ 34%]), which is
expected: comparing diverse modern form groups is a harder screen than
comparing two curated proto-strings. The important parallel is
directional and statistical: in both designs, same-slot / same-meaning
pairings exceed a form-preserving shuffle. Study 2 does so
#strong[without] relying on Smith's choice of reconstructions.

== 5.7 Summary of findings
<summary-of-findings>
Study 1 finds that Smith's remaining PAN--PKD alignments, after Lexibank
attestation filters, show meaning-blind form similarity far above a
shuffled baseline (#emph[p] ≈ 0.01). Study 2 finds that dual-attested
Lexibank form inventories on a Blust concept filter likewise exceed a
group-shuffle null at a generosity score of 2 or higher, 3 or higher,
and 4 or higher (#emph[p] ≈ 0.032, #emph[N] = 30). The next section
discusses what this does and does not imply for the Austro-Tai
hypothesis.

== Figure: Null distribution
<figure-null-distribution>
#figure(image("figures/null_histogram.png", alt: "Null histogram of hit counts with observed count marked"),
  caption: [
    Null histogram of hit counts with observed count marked
  ]
)

#strong[Figure 2.] Distribution of hit counts (generosity score of 4 or
higher) under 100 random reassignments of Tier A PAN forms to Tier A PKD
slots. Red line: observed hits (27).

= 6. Discussion
<discussion>
== 6.1 What the results do and do not show
<what-the-results-do-and-do-not-show>
After Lexibank-facing filters, Smith's (2025) remaining PAN--PKD
alignments show meaning-blind form similarity far above a shuffled
baseline (#emph[p] ≈ 0.01 under #emph[N] = 100 permutations).
Independently, dual-attested Lexibank form groups on a Blust/ABVD
concept filter also exceed a group-shuffle null at the primary
generosity cutoffs (a score of 4 or higher, and also 3 or higher and 2
or higher; #emph[p] ≈ 0.032 under #emph[N] = 30). The natural reading is
that #strong[excess form resemblance under these screens is not an
artifact of a single reconstruction spreadsheet]: Study 2 never sees
Smith's proto-forms, yet still finds same-meaning form groups more
similar than cross-meaning form groups.

That is a claim about #strong[strength of evidence under stated
controls], not a demonstration of genetic relatedness. Classical
arguments for Austro-Tai (especially Ostapirat 2005, 2013) turn on
#strong[regular phonological correspondences] and reconstructibility.
The scoring model may note plausible segment matches in free text, but
it does not enforce a correspondence system, reconstruct intermediate
stages, or distinguish inheritance from old loans that have been
internalized in daughter vocabularies. Contact with Sinitic and mainland
Southeast Asian languages remains a live alternative for some
lookalikes. Excess aggregate hits therefore motivate further comparative
work---including correspondence inventories over Study 2's hit
concepts---they do not finish it.

Relative to the two main modern phylogenetic frames---Ostapirat's
sister-family construal and Sagart's Austronesian-linked
architecture---the results are #strong[compatible with “there is
non-chance lexical signal to explain”] and #strong[agnostic] on tree
geometry.

== 6.2 Why Study 2 is the more robust check
<why-study-2-is-the-more-robust-check>
Study 1 answers: given Smith's published alignments, and after removing
reconstructions Lexibank daughters do not support, is the residual
pairing surprising? That is the right question for auditing a
#strong[fixed evidence package], and anchoring in Smith reduces
researcher freedom in picking etymologies (§2.2). It does not fully
answer a different worry: that the package itself may preferentially
include lookalike-friendly reconstructions.

Study 2 addresses that worry by construction. Concepts are selected by
Lexibank coverage and a pre-existing Austronesian basic-vocabulary list
(Blust/ABVD), not by an Austro-Tai author's alignments. Forms are modern
Lexibank attestations under phylogenetic sampling, not proto-strings
chosen for comparison. The null asks whether #strong[same-Concepticon]
inventories look more alike than shuffled inventories. Convergence
between Study 1 and Study 2 therefore strengthens the claim that the
signal is not merely an artifact of reconstructing toward resemblance.

The two studies are not interchangeable. Study 1 speaks directly to a
published Austro-Tai spreadsheet; Study 2 speaks to modern lexical
inventories and is closer to a “no reconstructions” stress test. Hit
rates are lower in Study 2, as expected when comparing heterogeneous
daughter samples rather than two curated proto-forms.

== 6.3 Why meaning-blindness and filters matter
<why-meaning-blindness-and-filters-matter>
If meanings are visible, both humans and models can reward “good
etymologies” they already associate with famous comparisons, or stretch
similarity when the gloss invites a match. Withholding glosses forces
the score to be a function of the strings (or form groups) and the
model's prior over orthographic/phonological resemblance. Caching binds
observed and null worlds to the same scoring function.

In Study 1, Layer 1 addresses unsupported reconstructions. In Study 2,
coverage floors, Blust filtering, onomatopoeia/dedupe heuristics, and
phylogenetic sampling play the analogous role of limiting opportunistic
form choice---while still leaving room for within-family diversity and
contact-induced lookalikes.

== 6.4 Limits
<limits>
Several limits bound interpretation.

#strong[Model and prompt.] All scores use `gpt-4.1` via a fixed chat API
and fixed prompts. Other models or stricter prompts would change
absolute hit rates; the permutation comparison is meaningful only
relative to the same scoring function. Threshold choice matters
especially in Study 2: a cutoff of 2 or higher yields many hits and a
high null baseline; a cutoff of 4 or higher is sparse but cleanly
separated from the null.

#strong[Prior knowledge of etymologies.] Large language models may have
seen published Austro-Tai comparisons in training data.
Meaning-blindness reduces semantic priming but does not erase memorized
form pairs (e.g.~famous #emph[mata] / #emph[nam] clusters). The
permutation null still constrains the argument: memorization would have
to favor #strong[matched] pairings over shuffled ones. Residual risk
remains and should be checked with expert human re-rating of hits.

#strong[Lexibank and sampling.] Coverage is uneven across concepts and
subgroups. Stratified samples avoid Oceanic overweighting but can miss
reflexes. Study 2's onomatopoeia heuristics are imperfect. Blust
intersection by Concepticon ID misses some near-matches where Lexibank
splits Blust glosses.

#strong[Smith's preliminary character (Study 1).] The Zenodo package is
preliminary and versioned. Future releases may revise reconstructions;
my frozen counts apply to v1.1 as parsed.

#strong[Null design and #emph[N].] Study 1 uses #emph[N] = 100; Study 2
uses #emph[N] = 30 (costly set-versus-set calls). Study 2's #emph[p] ≈
0.032 is therefore the add-one floor: no null reached observed, but a
finer tail would need larger #emph[N]. Neither null models phonetic
natural classes, semantic fields, or borrowing pathways.

#strong[Nursery forms and deixis.] Some Study 2 hits (#emph[mother],
#emph[this], pronouns) are categories where chance or nursery
resemblance is a known risk; primary interpretation should weight
body-part and verb hits more heavily pending correspondence work.

== 6.5 Future work
<future-work>
Useful extensions include larger #emph[N] for Study 2's null tail; human
expert re-rating of hits; exploratory #strong[regular correspondence]
inventories over Study 2 hit concepts (at a generosity score of 4 or
higher, 3 or higher, and 2 or higher); correspondence-constrained
scoring (encoding Ostapirat-style systems as hard filters); and parallel
audits of other published Austro-Tai lists under Study 1's two-layer
design.

#divider()

= 7. Conclusion
<conclusion>
I reported two meaning-blind permutation screens of Austro-Tai lexical
resemblance. #strong[Study 1] audited Alexander D. Smith's (2025)
gloss-aligned PAN--PKD reconstructions with Lexibank attestation
filters: on 79 Tier A pairs, 27 high form-similarity hits stand against
a null mean of about 5.7 (#emph[p] ≈ 0.01, #emph[N] = 100).
#strong[Study 2] compared dual-attested Lexibank Tai-Kadai and
Austronesian form groups on 194 Blust/ABVD concepts, without
reconstructions: hits at a generosity score of 4 or higher / 3 or higher
\/ 2 or higher were 11 / 17 / 121 against null means of about 2.2 / 5.7
\/ 91.7 (#emph[p] ≈ 0.032, #emph[N] = 30). Study 2 is the more robust
check against cherry-picked reconstructions because concept and form
selection do not inherit an author's comparative spreadsheet. Together,
the studies strengthen the case that excess form resemblance under these
screens is not merely an artifact of meaning-matched browsing---while
leaving genetic proof to systematic sound correspondences and classical
reconstruction.

= Appendix
<appendix>
Companion files in the software release:
`output/judgments_observed.csv`, `data/unjustified_pairs.tsv`,
`data/unjustified_pan_pairs.tsv`, `output/permutation_results.json`,
`output/lexibank_attestation_audit.csv`.

== Appendix A. Prompt texts
<appendix-a.-prompt-texts>
=== A.1 Meaning-blind form similarity (prompt version `v2`)
<a.1-meaning-blind-form-similarity-prompt-version-v2>
#strong[System prompt] (`src/judge.py`):

```
You are a comparative linguist scoring how similar proposed proto-language **forms** look, for exploratory Austro-Tai research.

Rules:
- Compare **phonetic and segmental shape only**. Do NOT use, infer, or mention meaning, semantics, glosses, or cognate labels.
- Each item gives a Proto-Kra-Dai (PKD) form and a candidate Proto-Austronesian (PAN) form. Score how similar the PAN form would be to the PKD form **if** it were the Austronesian reconstruction paired with that PKD slot—without knowing what concept either form represents.
- Do NOT require established regular sound correspondences; be generous on shape but not absurd.
- Ignore tone marks/superscripts when comparing shapes, but mention them if relevant.
- If the PAN side lists multiple alternate reconstructions, treat any plausible segmental match as supporting a higher score.

Return ONLY valid JSON (no markdown fences) as an array of objects with keys:
- comparison_id (string; echo the id from the input)
- generosity (integer 1-5; 5 = very similar shapes under a generous comparison)
- plausible_sound_correspondences (string; brief note or "none noted")
- reasoning (string; 1-3 sentences; do not refer to meaning)
```

#strong[User prompt pattern:]

```
For each item, score how similar the proto-Austronesian form would be to the proto-Kra-Dai form if it were the Austronesian reconstruction for the same slot. Compare shapes only; do not use meaning.

+ JSON array of objects with keys: comparison_id, proto_austronesian, proto_kra_dai, proto_tai_branch (opaque batch index as comparison_id; no gloss).
```

=== A.2 PKD attestation vs Lexibank Tai-Kadai (prompt version `v2`)
<a.2-pkd-attestation-vs-lexibank-tai-kadai-prompt-version-v2>
#strong[System prompt] (`src/reconstruction_validate.py`):

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

#strong[User prompt pattern:]

```
Score how well each PKD reconstruction is supported by the attested Tai-Kadai forms listed.

+ JSON array with pair_id, gloss, proto_kra_dai, proto_tai_branch, lexibank_concept, n_attested_languages_in_lexibank, attested_forms.
```

=== A.3 PAN attestation vs stratified Austronesian sample (prompt version `v1`)
<a.3-pan-attestation-vs-stratified-austronesian-sample-prompt-version-v1>
#strong[System prompt] (`src/pan_validate.py`):

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

#strong[User prompt pattern:]

```
Score how well each PAN reconstruction is supported by the sampled Austronesian forms listed.
Each attested form includes its coarse phylogenetic clade.

+ JSON array with pair_id, gloss, proto_austronesian, lexibank_concept_id, counts, attested_forms[{language,clade,form}].
```

== Appendix B. Austronesian clade sampling
<appendix-b.-austronesian-clade-sampling>
Language → clade map: `data/lexibank/austronesian_language_clades.csv`
(coarse labels derived from Glottolog under Austronesian `aust1307`).

Sampling algorithm (`src/an_sampling.sample_austronesian_forms`):

+ Deduplicate to at most one form per language.
+ Satisfy per-clade floors when possible: Formosan #strong[12], Western
  Malayo-Polynesian #strong[20], SHWNG #strong[8], Oceanic #strong[20].
+ Fill remaining slots up to target #strong[80] by round-robin across
  clades with leftover forms.
+ Use fixed seed `AN_SAMPLE_SEED = 1` for reproducibility.

== Appendix C. Tier A hits (a generosity score of 4 or higher)
<appendix-c.-tier-a-hits-a-generosity-score-of-4-or-higher>
Observed hits: #strong[27] / 79 Tier A pairs (18 with generosity 5; 9
with generosity 4). Null (#emph[N] = 100): mean 5.68, range 1--12;
one-sided #emph[p] = 0.0099.

#figure(
  align(center)[#table(
    columns: 6,
    align: (auto,auto,auto,right,right,right,),
    table.header([Gloss], [PAN], [PKD], [Gen.], [PKD att.], [PAN att.],),
    table.hline(),
    [1sg], [\*aku], [\*aku], [5], [4], [5],
    [2sg], [#emph[\-Su; ]-mu (plural)], [\*-məː], [5], [2], [4],
    [afraid; fear], [\*talaw], [\*C-laːw], [5], [4], [4],
    [dark; black], [\*-dəm], [\*(C̥V/m)-dam], [5], [4], [4],
    [die], [\*(m/p-)aCay], [\*p-ataːy], [5], [4], [5],
    [drop; fall], [\*-tuq], [\*tok], [5], [5], [2],
    [eat], [\*ka(ʔ)ən], [\*(i-)kan], [5], [4], [5],
    [fart], [\*qətut], [\*k\[a/ə\]tu2t], [5], [3], [2],
    [five], [\*lima], [\*ɭVmaː], [5], [3], [5],
    [hold; grab], [\*-\[g/k\]əm], [\*N-kamᴬ], [5], [5], [3],
    [moon], [\*bulaN], [\*buɭaːl], [5], [2], [5],
    [nine], [\*siwa], [\(\*s(i)waː)], [5], [2], [5],
    [six], [\*(x)ənəm], [\*xən\[a/ə\]m], [5], [5], [5],
    [this], [\*-ni], [\*niː], [5], [5], [5],
    [tongue2], [\*Səma], [\*Səmaːᴬ], [5], [4], [2],
    [tooth], [\*\[l/n/ŋ\]ipan], [\*(l)ipan], [5], [3], [4],
    [vomit], [\*utaq], [\*utaːk], [5], [2], [4],
    [water], [\*daNum], [\*danam], [5], [5], [5],
    [bird; chicken], [\*maNuk], [\*malok], [4], [4], [5],
    [deep], [\*daləm], [\*C-alək], [4], [5], [2],
    [excrement], [#emph[Caqi; (PMP
    ]taqay)], [\*CV-q\[i/aːj\]], [4], [2], [3],
    [fire], [\*Sapuy], [\*apuy], [4], [2], [5],
    [head], [\*quluh], [\*kuɭuː], [4], [2], [5],
    [louse], [\*kuCu], [\*C-uʈuː], [4], [2], [5],
    [shoulder], [\*qabaRa], [\*CV-baː], [4], [5], [5],
    [sky], [\*Rabun], [\*C-bu1n], [4], [4], [2],
    [wash], [\*basəq], [\*C-sak], [4], [5], [4],
  )]
  , kind: table
  )

== Appendix D. Unjustified reconstructions (attestation\_score = 1)
<appendix-d.-unjustified-reconstructions-attestation_score-1>
=== D.1 Unjustified PKDs (#emph[n] = 14)
<d.1-unjustified-pkds-n-14>
#figure(
  align(center)[#table(
    columns: 3,
    align: (auto,auto,auto,),
    table.header([Gloss], [PAN], [PKD],),
    table.hline(),
    [buy/sell], [\*saliw], [\*aɭiːw],
    [leech], [#emph[matək/]məCaq], [\(\*tak)],
    [nest], [\*Rubu], [\*aruːk],
    [otter], [\*Sanaq], [\*anaːk],
    [pick up; lift; take], [#emph[saput; ]piliq], [\*kep],
    [plant], [\*mula], [\*muɭaː],
    [sharp], [\*tazəm], [\*C.cəmᴬ],
    [shrimp], [#emph[qudaŋ; ]kabus], [\*(q)udaːŋ],
    [sick], [\*sakit], [\*keːt],
    [skinny], [\*Niwaŋ], [\*CV-roːm],
    [stomach], [#emph[biCuka; ]tiaN], [\*amok],
    [tie; bundle], [#emph[Sikət; ]baluN; \*bəjbəj], [\*CV-ruːk],
    [to taste], [\*taɲam], [\*ɟim],
    [turtle], [\*qaCipa (soft-shell)], [\*C̥-(i)paːᴬ],
  )]
  , kind: table
  )

=== D.2 Unjustified PANs (#emph[n] = 27)
<d.2-unjustified-pans-n-27>
#figure(
  align(center)[#table(
    columns: 3,
    align: (auto,auto,auto,),
    table.header([Gloss], [PAN], [PKD],),
    table.hline(),
    [ant], [#emph[alujah; ]aNay], [\*Vmu2c],
    [bathe], [\*diRus], [\*aːp],
    [bear], [\*Cumay], [\*Cumaj],
    [boat], [\*luja], [\*C̬udaː],
    [borrow], [\*Səzam], [\*Səzəːm],
    [centipede], [\*qalu-Sipan], [\*CV-rip],
    [child1], [\*aNak], [\*aləːk],
    [dream], [\*S\[ə/i\]pi], [\*CV(\[+H\])pan],
    [fish poison], [\*tuba], [\*C̥V\[+H\]baː],
    [forget], [\*alim], [\*CV-ləːm],
    [hook], [#emph[kawit; ]kabit], [\*C-bet],
    [hot; warm], [\*lasuq], [\*C-uluːl],
    [hungry], [\(PMP \*lapaR)], [\*C-iaːk],
    [knife], [#emph[RabiS; ]tadaw], [\*miːt],
    [leg], [\*paqa], [\*paqaː],
    [nest], [\*Rubu], [\*aruːk],
    [plant], [\*mula], [\*muɭaː],
    [rattan], [\*quay], [\*(q)uaːy],
    [raw; (a)live], [\*qudip], [\*(q)udip],
    [shadow], [#emph[qaNiŋu; ]liŋaw], [\*aŋ\[u/aːw\]],
    [sick], [\*sakit], [\*keːt],
    [skinny], [\*Niwaŋ], [\*CV-roːm],
    [sour], [\*qa(R)səm], [\*qas\[a/ə\]m],
    [star], [\*qajaw], [\*adaːw],
    [taro], [\*biRaq], [\*biRaːk],
    [to taste], [\*taɲam], [\*ɟim],
    [turtle], [\*qaCipa (soft-shell)], [\*C̥-(i)paːᴬ],
  )]
  , kind: table
  )

== Appendix E. Data and software availability
<appendix-e.-data-and-software-availability>
- #strong[Smith (2025) reconstructions:] Zenodo DOI
  #link("https://doi.org/10.5281/zenodo.15597357")[10.5281/zenodo.15597357],
  release v1.1 (#emph[Austro-Tai comparative dataset
  (Reconstructions)]).
- #strong[Lexibank 2:] List et al.~(2022); `lexibank-analysed` v2.2
  (Concepticon-linked forms; Tai-Kadai and Austronesian subsets as
  described in §3--4).
- #strong[Blust / ABVD concept list:] Concepticon contribution
  Blust-2008-210 (Greenhill, Blust & Gray 2008).
- #strong[Analysis code and frozen outputs:]
  #link("https://github.com/jeremycollinsmpi/austro-tai-llm-test")
  (Study 1: parse → attest / validate-pan → judge → permute → report;
  Study 2: attested-core → attested-judge → attested-permute). Model:
  `gpt-4.1` via project NLP chat endpoint. Frozen summaries:
  `output/permutation_results.json` (Study 1);
  `output/attested_permutation_results_blust194_n30.json` and
  `output/attested_judgments_null_blust194_n30.csv` (Study 2).

== Appendix F. Study 2 hits (Blust dual-attested Lexibank)
<appendix-f.-study-2-hits-blust-dual-attested-lexibank>
Observed on #strong[194] concepts; null #emph[N] = 30; one-sided
#emph[p] = 1/31 ≈ 0.032 at a generosity score of 2 or higher, 3 or
higher, and 4 or higher.

#strong[Generosity score of 4 or higher (#emph[n] = 11):] eye; nose;
eat; water; bite; shoulder; mother; this; we; blow (of wind); be dead or
die.

#strong[Generosity score of 3 (#emph[n] = 6; total at 3 or higher =
17):] fire; I; wing; ten; dust; lightning.

Full scores and model notes:
`output/attested_judgments_observed_blust194.csv`.

= References
<references>
Benedict, Paul K. 1942. Thai, Kadai, and Indonesian: A new alignment in
southeastern Asia. #emph[American Anthropologist] 44(4). 576--601.

Benedict, Paul K. 1975. #emph[Austro-Thai language and culture, with a
glossary of roots]. New Haven: HRAF Press.

Greenhill, Simon J., Robert Blust & Russell D. Gray. 2008. The
Austronesian Basic Vocabulary Database: From bioinformatics to lexomics.
#emph[Evolutionary Bioinformatics] 4. 271--283. (Concepticon list
Blust-2008-210.)

Liao, Hanbo & Ryan Gehrmann. 2025. Kra-Dai tonogenesis in Austro-Tai
perspective. #emph[Diachronica] 42(3/4). 382--405.
https:/\/doi.org/10.1075/dia.24028.lia

List, Johann-Mattis, Robert Forkel, Simon J. Greenhill, Christoph
Rzymski, Johannes Englisch & Russell D. Gray. 2022. Lexibank, a public
repository of standardized wordlists of about 2000 language varieties.
#emph[Scientific Data] 9. 316. (Lexibank analysed release used here:
v2.2.)

Ostapirat, Weera. 2005. Kra--Dai and Austronesian: Notes on phonological
correspondences and vocabulary distribution. In Laurent Sagart, Roger
Blench & Alicia Sanchez-Mazas (eds.), #emph[The peopling of East Asia],
107--131. London: RoutledgeCurzon.

Ostapirat, Weera. 2013. Austro-Tai revisited. Paper presented at the
23rd Annual Meeting of the Southeast Asian Linguistics Society (SEALS
23), Bangkok. \[Confirm preferred citation for final submission.\]

Ringe, Don. 1992. On calculating the factor of chance in language
comparison. #emph[Transactions of the American Philosophical Society]
82(1). 1--110.

Sagart, Laurent. 2004. The higher phylogeny of Austronesian and the
position of Tai-Kadai. #emph[Oceanic Linguistics] 43(2). 411--444.

Sagart, Laurent. 2005. Sino-Tibetan--Austronesian: An updated and
improved argument. In Laurent Sagart, Roger Blench & Alicia
Sanchez-Mazas (eds.), #emph[The peopling of East Asia], 161--176.
London: RoutledgeCurzon.

Sagart, Laurent. 2019. A model of the origin of Kra-Dai tones.
#emph[Cahiers de linguistique Asie orientale] 48(1). 1--29.
https:/\/doi.org/10.1163/19606028-04801004

Smith, Alexander D. 2025. Austro-Tai comparative dataset
(Reconstructions) (v1.1). Zenodo.
https:/\/doi.org/10.5281/zenodo.15597357
