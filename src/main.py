#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path

from src.attested_pilot import build_core_concepts, run_attested_permutation, run_observed_attested
from src.correspondences import run_correspondence_analysis
from src.judge import build_judgment_matrix, run_observed_judgment
from src.lexibank_check import run_attestation_audit
from src.parse_smith import build_aligned_pairs, write_aligned_pairs
from src.permute import run_permutation_test
from src.pan_validate import run_pan_reconstruction_validation
from src.reconstruction_validate import run_reconstruction_validation
from src.report import build_report
from src.sinitic_screen import run_sinitic_screen


def cmd_parse(_: argparse.Namespace) -> None:
    pairs = build_aligned_pairs()
    path = write_aligned_pairs(pairs)
    print(f"Parsed {len(pairs)} pairs -> {path}")


def cmd_judge(args: argparse.Namespace) -> None:
    run_observed_judgment(
        pairs_path=Path(args.pairs) if args.pairs else None,
        output_path=Path(args.output) if args.output else None,
        use_eligible=not args.all_pairs,
    )


def cmd_matrix(args: argparse.Namespace) -> None:
    count = build_judgment_matrix(batch_size=args.batch_size)
    print(f"Matrix entries available: {count}")


def cmd_permute(args: argparse.Namespace) -> None:
    run_permutation_test(
        pairs_path=Path(args.pairs) if args.pairs else None,
        n_permutations=args.permutations,
        seed=args.seed,
        observed_judgments_path=Path(args.observed) if args.observed else None,
        write_perm_csv=args.write_perm_csv,
        use_eligible=not args.all_pairs,
    )


def cmd_attest(args: argparse.Namespace) -> None:
    run_attestation_audit(force=args.force, skip_validation=args.skip_validation)


def cmd_validate(_: argparse.Namespace) -> None:
    run_reconstruction_validation()


def cmd_validate_pan(_: argparse.Namespace) -> None:
    run_pan_reconstruction_validation()


def cmd_attested_core(args: argparse.Namespace) -> None:
    build_core_concepts(
        k=args.k,
        min_langs=args.min_langs,
        force=args.force,
        list_filter=args.list,
        output_path=Path(args.output) if args.output else None,
    )


def cmd_attested_judge(args: argparse.Namespace) -> None:
    core_path = Path(args.core) if args.core else None
    output = Path(args.output) if args.output else None
    run_observed_attested(force=args.force, output_path=output, core_path=core_path)


def cmd_attested_permute(args: argparse.Namespace) -> None:
    core_path = Path(args.core) if args.core else None
    observed = Path(args.observed) if args.observed else None
    results = Path(args.results) if args.results else None
    null_judgments = Path(args.null_judgments) if args.null_judgments else None
    run_attested_permutation(
        n_permutations=args.permutations,
        seed=args.seed,
        force=args.force,
        skip_observed=args.skip_observed,
        resume=not args.no_resume,
        core_path=core_path,
        observed_path=observed,
        results_path=results,
        null_judgments_path=null_judgments,
        label=args.label,
    )


def cmd_correspondences(args: argparse.Namespace) -> None:
    run_correspondence_analysis(
        min_generosity=args.min_generosity,
        observed_path=Path(args.observed) if args.observed else None,
        core_path=Path(args.core) if args.core else None,
        include_nonhit_controls=not args.no_controls,
        label=args.label,
    )


def cmd_sinitic_screen(args: argparse.Namespace) -> None:
    run_sinitic_screen(
        min_generosity=args.min_generosity,
        batch_size=args.batch_size,
        study1_path=Path(args.study1) if args.study1 else None,
        study2_path=Path(args.study2) if args.study2 else None,
        output_path=Path(args.output) if args.output else None,
    )


def cmd_report(_: argparse.Namespace) -> None:
    build_report()


def cmd_all(args: argparse.Namespace) -> None:
    cmd_parse(argparse.Namespace())
    run_attestation_audit(skip_validation=args.skip_validation)
    run_observed_judgment()
    if args.permutations > 0:
        run_permutation_test(n_permutations=args.permutations, seed=args.seed)
    build_report()


def main() -> None:
    parser = argparse.ArgumentParser(description="Austro-Tai LLM cognate permutation test")
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("parse", help="Parse Smith xlsx into aligned_pairs.tsv").set_defaults(func=cmd_parse)

    judge = sub.add_parser("judge", help="Run observed LLM cognate judgments on eligible pairs")
    judge.add_argument("--pairs", help="Override pairs TSV (default: data/eligible_pairs.tsv)")
    judge.add_argument("--output")
    judge.add_argument("--all-pairs", action="store_true", help="Use all aligned pairs instead of eligible subset")
    judge.set_defaults(func=cmd_judge)

    perm = sub.add_parser("permute", help="Run permutation test (shuffled PAN) on eligible pairs")
    perm.add_argument("--pairs")
    perm.add_argument("--observed")
    perm.add_argument("--permutations", type=int, default=1000)
    perm.add_argument("--seed", type=int, default=1)
    perm.add_argument("--write-perm-csv", action="store_true")
    perm.add_argument("--all-pairs", action="store_true")
    perm.set_defaults(func=cmd_permute)

    matrix = sub.add_parser("matrix", help="Precompute PKD x PAN judgment matrix (slow, makes permutations fast)")
    matrix.add_argument("--batch-size", type=int, default=15)
    matrix.set_defaults(func=cmd_matrix)

    attest = sub.add_parser("attest", help="Lexibank audit + optional PKD validation API + eligible_pairs.tsv")
    attest.add_argument("--force", action="store_true", help="Re-download Lexibank and rebuild attestation cache")
    attest.add_argument("--skip-validation", action="store_true", help="Skip NLP attestation-score API calls")
    attest.set_defaults(func=cmd_attest)

    sub.add_parser("validate", help="Run PKD vs attested-forms validation API only").set_defaults(func=cmd_validate)
    sub.add_parser(
        "validate-pan", help="Run PAN vs sampled Austronesian forms validation API only"
    ).set_defaults(func=cmd_validate_pan)

    attested_core = sub.add_parser(
        "attested-core", help="Build dual-attested Lexibank core concept list for attested pilot"
    )
    attested_core.add_argument("--k", type=int, default=50, help="Pilot core size")
    attested_core.add_argument("--min-langs", type=int, default=15, help="Min TK and AN languages")
    attested_core.add_argument(
        "--list",
        choices=["blust", "blust210"],
        help="Optional concept list filter (Blust-2008-210 via Concepticon ID)",
    )
    attested_core.add_argument("--force", action="store_true")
    attested_core.add_argument(
        "--output",
        help="Core concepts TSV path (default: data/attested_pilot/core_concepts.tsv or _blust)",
    )
    attested_core.set_defaults(func=cmd_attested_core)

    attested_judge = sub.add_parser(
        "attested-judge", help="Observed set-vs-set judgments on core concepts (meaning-blind)"
    )
    attested_judge.add_argument("--force", action="store_true")
    attested_judge.add_argument("--core", help="Core concepts TSV (default: data/attested_pilot/core_concepts.tsv)")
    attested_judge.add_argument("--output", help="Observed judgments CSV path")
    attested_judge.set_defaults(func=cmd_attested_judge)

    attested_perm = sub.add_parser(
        "attested-permute", help="Permutation null for attested set-vs-set pilot"
    )
    attested_perm.add_argument("--permutations", type=int, default=20)
    attested_perm.add_argument("--seed", type=int, default=1)
    attested_perm.add_argument("--force", action="store_true")
    attested_perm.add_argument(
        "--skip-observed",
        action="store_true",
        help="Reuse observed judgments CSV if present",
    )
    attested_perm.add_argument("--core", help="Core concepts TSV")
    attested_perm.add_argument("--observed", help="Observed judgments CSV path")
    attested_perm.add_argument("--results", help="Permutation results JSON path")
    attested_perm.add_argument(
        "--null-judgments",
        help="CSV for all null judgments (score + reasoning); default beside --results",
    )
    attested_perm.add_argument(
        "--no-resume",
        action="store_true",
        help="Ignore existing null-judgment CSV and start permutations from scratch",
    )
    attested_perm.add_argument("--label", default="", help="Label stored in results JSON")
    attested_perm.set_defaults(func=cmd_attested_permute)

    corr = sub.add_parser(
        "correspondences",
        help="Exploratory TK↔AN correspondence inventory over attested hits",
    )
    corr.add_argument("--min-generosity", type=int, default=2, help="Include concepts with generosity ≥ this")
    corr.add_argument("--observed", help="Observed attested judgments CSV")
    corr.add_argument("--core", help="Core concepts TSV")
    corr.add_argument("--label", default="blust194")
    corr.add_argument("--no-controls", action="store_true", help="Skip non-hit control concepts")
    corr.set_defaults(func=cmd_correspondences)

    sinitic = sub.add_parser(
        "sinitic-screen",
        help="Ask NLP whether observed hits could be Chinese loans into TK and/or AN",
    )
    sinitic.add_argument("--min-generosity", type=int, default=4)
    sinitic.add_argument("--batch-size", type=int, default=8)
    sinitic.add_argument("--study1", help="Study 1 observed judgments CSV")
    sinitic.add_argument("--study2", help="Study 2 observed judgments CSV")
    sinitic.add_argument("--output", help="Output CSV path")
    sinitic.set_defaults(func=cmd_sinitic_screen)

    sub.add_parser("report", help="Build markdown report").set_defaults(func=cmd_report)

    all_cmd = sub.add_parser("all", help="parse -> attest -> judge -> permute -> report")
    all_cmd.add_argument("--permutations", type=int, default=1000)
    all_cmd.add_argument("--seed", type=int, default=1)
    all_cmd.add_argument("--skip-validation", action="store_true")
    all_cmd.set_defaults(func=cmd_all)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
