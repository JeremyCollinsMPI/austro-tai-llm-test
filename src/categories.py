"""Semantic-category exclusions for robustness reruns.

Pronouns, demonstratives and nursery kinship terms are the categories where
chance resemblance, sound symbolism and nursery-form convergence are known
risks, so a reader is entitled to ask whether the aggregate effect depends on
them. These sets are used to recompute both studies with those slots removed.

Two nested levels are defined:

- ``core``: personal pronouns, demonstratives, and nursery kin (mother/father).
  This is the set the comparative literature discounts on sight.
- ``wide``: ``core`` plus interrogative pro-forms and the remaining kinship
  terms, i.e. a deliberately over-broad cut used as a stress test.
"""

STUDY1_PRONOUN_DEICTIC = {"1sg", "2sg", "this"}
STUDY1_OTHER_KIN = {"younger siblings"}

STUDY2_PRONOUN = {"I", "THOU", "WE", "YOU", "HE OR SHE", "THEY"}
STUDY2_DEICTIC = {"THIS", "THAT"}
STUDY2_NURSERY_KIN = {"MOTHER", "FATHER"}
STUDY2_INTERROGATIVE = {"WHAT", "WHO", "WHERE", "WHEN", "HOW"}
STUDY2_OTHER_KIN = {"CHILD", "HUSBAND", "WIFE"}

EXCLUSION_LEVELS = ("none", "core", "wide")


def study1_excluded(level: str) -> set[str]:
    """Excluded Smith glosses (as spelled in data/eligible_pairs.tsv)."""
    if level == "none":
        return set()
    if level == "core":
        return set(STUDY1_PRONOUN_DEICTIC)
    if level == "wide":
        return STUDY1_PRONOUN_DEICTIC | STUDY1_OTHER_KIN
    raise ValueError(f"unknown exclusion level: {level}")


def study2_excluded(level: str) -> set[str]:
    """Excluded Concepticon glosses (uppercase, as in the core concept TSV)."""
    if level == "none":
        return set()
    core = STUDY2_PRONOUN | STUDY2_DEICTIC | STUDY2_NURSERY_KIN
    if level == "core":
        return core
    if level == "wide":
        return core | STUDY2_INTERROGATIVE | STUDY2_OTHER_KIN
    raise ValueError(f"unknown exclusion level: {level}")
