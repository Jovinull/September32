"""``s32`` — the project's command line.

One entry point for everything a contributor needs to do, so that the README can
say ``s32 doctor`` instead of describing eleven scripts.

``argparse`` from the standard library, not Typer or Click. The CLI is a dozen
subcommands with simple arguments; a dependency would buy tab completion and
colour, and cost a package that everyone who touches the project has to install.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import TYPE_CHECKING

from s32tools import paths

if TYPE_CHECKING:
    from s32_engine.types import ContentLibrary
    from s32tools.renpy_sdk import SdkInfo

    SubParsers = argparse._SubParsersAction[argparse.ArgumentParser]


def main(argv: list[str] | None = None) -> int:
    """Parse arguments and dispatch. Returns the process exit code."""
    parser = _build_parser()
    args = parser.parse_args(argv)

    if not hasattr(args, "handler"):
        parser.print_help()
        return 2
    handler = args.handler
    return int(handler(args))


def _build_parser() -> argparse.ArgumentParser:
    """Build the full parser tree."""
    parser = argparse.ArgumentParser(
        prog="s32",
        description="September 32 development tooling.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Common flows:\n"
            "  s32 doctor                    is this checkout workable?\n"
            "  s32 validate                  is the authored content sound?\n"
            "  s32 simulate --runs 2000      what can a player actually reach?\n"
            "  s32 assets fetch && s32 assets install\n"
        ),
    )
    sub = parser.add_subparsers(dest="command")

    doctor = sub.add_parser("doctor", help="report on the state of this checkout")
    doctor.set_defaults(handler=_cmd_doctor)

    validate = sub.add_parser("validate", help="validate authored content")
    validate.add_argument("--strict", action="store_true", help="treat warnings as failures")
    validate.add_argument("--no-static", action="store_true", help="skip reachability analysis")
    validate.set_defaults(handler=_cmd_validate)

    schemas = sub.add_parser("schemas", help="regenerate JSON Schemas from the engine's enums")
    schemas.add_argument("--check", action="store_true", help="fail if they are out of date")
    schemas.set_defaults(handler=_cmd_schemas)

    simulate = sub.add_parser("simulate", help="run headless playthroughs")
    simulate.add_argument("--runs", type=int, default=500, help="number of playthroughs")
    simulate.add_argument("--seed", type=int, default=0, help="base seed (runs use seed+i)")
    simulate.add_argument("--profile", action="append", help="restrict to a profile; repeatable")
    simulate.add_argument("--out", type=Path, help="report directory")
    simulate.add_argument(
        "--quiet", action="store_true", help="write reports, print only a summary"
    )
    simulate.set_defaults(handler=_cmd_simulate)

    coverage = sub.add_parser("coverage", help="report storylet coverage")
    coverage.add_argument("--runs", type=int, default=300, help="simulation runs to fold in")
    coverage.add_argument("--out", type=Path, help="report directory")
    coverage.set_defaults(handler=_cmd_coverage)

    graph = sub.add_parser("graph", help="export the narrative graph")
    graph.add_argument("--format", choices=("mermaid", "dot", "markdown"), default="markdown")
    graph.add_argument("--out", type=Path, help="output file")
    graph.set_defaults(handler=_cmd_graph)

    explain = sub.add_parser("explain", help="show one storylet's requirements and effects")
    explain.add_argument("storylet")
    explain.set_defaults(handler=_cmd_explain)

    compare = sub.add_parser("compare", help="compare two simulation reports")
    compare.add_argument("before", type=Path, help="baseline simulation.json")
    compare.add_argument("after", type=Path, help="current simulation.json")
    compare.add_argument("--label-before", default="before")
    compare.add_argument("--label-after", default="after")
    compare.add_argument("--out", type=Path, help="write the comparison here")
    compare.set_defaults(handler=_cmd_compare)

    report_cmd = sub.add_parser("report", help="regenerate every report at once")
    report_cmd.add_argument("--runs", type=int, default=500)
    report_cmd.set_defaults(handler=_cmd_report)

    _add_assets(sub)
    _add_renpy(sub)
    return parser


def _add_assets(sub: SubParsers) -> None:
    """Add the ``s32 assets ...`` subtree."""
    assets = sub.add_parser("assets", help="fetch, verify, install and credit third-party assets")
    asub = assets.add_subparsers(dest="assets_command")

    fetch = asub.add_parser("fetch", help="download from official sources")
    fetch.add_argument("--group", default="all", help="characters|backgrounds|cc0|audio|fonts|all")
    fetch.add_argument("--asset", action="append", help="fetch one source by id; repeatable")
    fetch.add_argument("--force", action="store_true", help="re-download even if cached")
    fetch.set_defaults(handler=_cmd_assets_fetch)

    install = asub.add_parser("install", help="extract, process and copy into the game")
    install.add_argument("--no-game", action="store_true", help="stop after assets/processed")
    install.set_defaults(handler=_cmd_assets_install)

    verify = asub.add_parser("verify", help="check hashes, evidence and licence hygiene")
    verify.set_defaults(handler=_cmd_assets_verify)

    credits_cmd = asub.add_parser("credits", help="regenerate all credit surfaces")
    credits_cmd.add_argument("--check", action="store_true", help="fail if they are out of date")
    credits_cmd.set_defaults(handler=_cmd_assets_credits)

    evidence = asub.add_parser("evidence", help="regenerate per-asset licence evidence")
    evidence.set_defaults(handler=_cmd_assets_evidence)

    images = asub.add_parser("images", help="regenerate Ren'Py image definitions")
    images.set_defaults(handler=_cmd_assets_images)

    audit = asub.add_parser("audit", help="measure character-art consistency")
    audit.add_argument("--out", type=Path, help="output file")
    audit.set_defaults(handler=_cmd_assets_audit)

    paper = asub.add_parser("paper", help="regenerate the deterministic document textures")
    paper.set_defaults(handler=_cmd_assets_paper)

    sheets = asub.add_parser("sheets", help="build contact sheets")
    sheets.add_argument("--out", type=Path, help="output directory")
    sheets.set_defaults(handler=_cmd_assets_sheets)


def _add_renpy(sub: SubParsers) -> None:
    """Add the ``s32 renpy ...`` subtree."""
    renpy_cmd = sub.add_parser("renpy", help="drive the pinned Ren'Py SDK")
    rsub = renpy_cmd.add_subparsers(dest="renpy_command")

    install = rsub.add_parser("install", help="download and unpack the pinned SDK")
    install.add_argument("--force", action="store_true")
    install.set_defaults(handler=_cmd_renpy_install)

    lint = rsub.add_parser("lint", help="run Ren'Py's own lint")
    lint.set_defaults(handler=_cmd_renpy_lint)

    test = rsub.add_parser("test", help="run Ren'Py testcases")
    test.add_argument("case", nargs="*", help="testcase names; default is all smoke tests")
    test.add_argument("--seed", type=int, default=4211, help="pins S32_SEED for determinism")
    test.set_defaults(handler=_cmd_renpy_test)

    run = rsub.add_parser("run", help="launch the game")
    run.set_defaults(handler=_cmd_renpy_run)


# ---------------------------------------------------------------------------
# Handlers
# ---------------------------------------------------------------------------


def _library() -> ContentLibrary:
    """Load the content library, reporting a content error cleanly."""
    from s32_engine.definitions import load_library

    return load_library(paths.data_dir())


def _cmd_doctor(_args: argparse.Namespace) -> int:
    from s32tools import doctor

    checks = doctor.run_checks()
    print(doctor.report(checks))
    return doctor.exit_code(checks)


def _cmd_validate(args: argparse.Namespace) -> int:
    from s32_engine.errors import ContentError
    from s32tools.validation import static_analysis
    from s32tools.validation.content import Report, schema_validate, validate_library

    try:
        library = _library()
    except ContentError as exc:
        print(f"FAILED to load content: {exc}")
        return 1

    combined = Report()
    combined.findings.extend(schema_validate(paths.data_dir(), paths.schemas_dir()).findings)
    combined.findings.extend(validate_library(library, rpy_root=paths.game_dir()).findings)
    if not args.no_static:
        combined.findings.extend(static_analysis.analyse(library).findings)

    print(combined.format())
    return 0 if combined.ok(strict=args.strict) else 1


def _cmd_schemas(args: argparse.Namespace) -> int:
    from s32tools.validation import schemas

    target = paths.schemas_dir()
    if args.check:
        stale = schemas.check_all(target)
        if stale:
            print("JSON Schemas are out of date:")
            for item in stale:
                print(f"  {item}")
            print("\nRun: s32 schemas")
            return 1
        print("JSON Schemas are up to date.")
        return 0

    written = schemas.write_all(target)
    for path in written:
        print(f"wrote {path.relative_to(paths.repo_root())}")
    return 0


def _cmd_simulate(args: argparse.Namespace) -> int:
    from s32tools.simulation import report as sim_report
    from s32tools.simulation.profiles import DEFAULT_PROFILES, get
    from s32tools.simulation.simulator import Simulator

    library = _library()
    names = args.profile or list(DEFAULT_PROFILES)
    profiles = [get(name) for name in names]

    simulator = Simulator(library)
    result = simulator.run_many(args.runs, profiles, seed=args.seed)

    out = args.out or (paths.reports_dir() / "simulation")
    out.mkdir(parents=True, exist_ok=True)
    (out / "simulation.json").write_text(sim_report.to_json(result, library), encoding="utf-8")
    markdown = sim_report.to_markdown(result, library)
    (out / "simulation.md").write_text(markdown, encoding="utf-8")

    if args.quiet:
        print(
            f"{args.runs} runs, seed {args.seed}: "
            f"{len(result.reachable)}/{result.library_size} storylets reached, "
            f"{result.dead_ends} dead end(s)"
        )
    else:
        print(markdown)
    print(f"\nreports: {out}")
    return 1 if (result.unreachable or result.dead_ends) else 0


def _cmd_coverage(args: argparse.Namespace) -> int:
    from s32tools.coverage import storylet_coverage
    from s32tools.simulation.profiles import DEFAULT_PROFILES, get
    from s32tools.simulation.simulator import Simulator

    library = _library()
    simulator = Simulator(library)
    simulation = simulator.run_many(args.runs, [get(n) for n in DEFAULT_PROFILES], seed=0)
    coverage = storylet_coverage.analyse(library, simulation)

    out = args.out or (paths.reports_dir() / "coverage")
    out.mkdir(parents=True, exist_ok=True)
    (out / "coverage.json").write_text(
        storylet_coverage.to_json(coverage, library), encoding="utf-8"
    )
    markdown = storylet_coverage.to_markdown(coverage, library)
    (out / "coverage.md").write_text(markdown, encoding="utf-8")
    print(markdown)
    print(f"\nreports: {out}")
    return 0


def _cmd_graph(args: argparse.Namespace) -> int:
    from s32tools.narrative import graph

    library = _library()
    renderer = {"mermaid": graph.to_mermaid, "dot": graph.to_dot, "markdown": graph.to_markdown}[
        args.format
    ]
    text = renderer(library)

    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(text, encoding="utf-8")
        print(f"wrote {args.out}")
    else:
        default = paths.reports_dir() / "graph"
        default.mkdir(parents=True, exist_ok=True)
        suffix = {"mermaid": ".mmd", "dot": ".dot", "markdown": ".md"}[args.format]
        path = default / f"narrative_graph{suffix}"
        path.write_text(text, encoding="utf-8")
        print(f"wrote {path}")
    return 0


def _cmd_explain(args: argparse.Namespace) -> int:
    library = _library()
    storylet = library.storylets.get(args.storylet)
    if storylet is None:
        print(f"no such storylet: {args.storylet}")
        print("\nAvailable:")
        for sid in library.storylet_ids():
            print(f"  {sid}")
        return 1

    print(f"{storylet.id}  —  {storylet.title}")
    print(f"  label       {storylet.label}")
    print(f"  category    {storylet.category}   status {storylet.status}")
    print(f"  priority    {storylet.priority}   weight {storylet.weight}")
    print(f"  repeat      {storylet.repeat_policy}   cooldown {storylet.cooldown}d")
    print(f"  location    {storylet.location or 'anywhere'}")
    print(f"  time slots  {', '.join(storylet.time_slots) or 'any'}")
    print(f"  phases      {', '.join(storylet.phases) or 'any'}")
    print(f"  characters  {', '.join(storylet.characters) or 'none'}")
    print(f"  tags        {', '.join(storylet.tags) or 'none'}")
    print("  requires:")
    for req in storylet.requirements or ("(none)",):
        print(f"      {req}")
    if storylet.blockers:
        print("  blocked by:")
        for blocker in storylet.blockers:
            print(f"      {blocker}")
    print("  effects:")
    for effect in storylet.effects or ("(none)",):
        print(f"      {effect}")
    if storylet.grants:
        print(f"  grants:     {', '.join(storylet.grants)}")
    if storylet.summary:
        print(f"\n  {storylet.summary}")
    return 0


def _cmd_compare(args: argparse.Namespace) -> int:
    from s32tools.simulation.compare import load, to_markdown

    text = to_markdown(
        load(args.before),
        load(args.after),
        label_before=args.label_before,
        label_after=args.label_after,
    )
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(text, encoding="utf-8")
        print(f"wrote {args.out}")
    else:
        print(text)
    return 0


def _cmd_report(args: argparse.Namespace) -> int:
    """Regenerate every report. Used by CI and before a review."""
    failures = 0
    for handler, namespace in (
        (_cmd_validate, argparse.Namespace(strict=False, no_static=False)),
        (
            _cmd_simulate,
            argparse.Namespace(runs=args.runs, seed=0, profile=None, out=None, quiet=True),
        ),
        (_cmd_coverage, argparse.Namespace(runs=max(100, args.runs // 2), out=None)),
        (_cmd_graph, argparse.Namespace(format="markdown", out=None)),
    ):
        print(f"\n=== {handler.__name__.removeprefix('_cmd_')} ===")
        failures += 1 if handler(namespace) else 0
    return 0 if failures == 0 else 1


# -- assets -----------------------------------------------------------------


def _cmd_assets_fetch(args: argparse.Namespace) -> int:
    from s32tools.assets import sources
    from s32tools.assets.fetch import fetch_source
    from s32tools.assets.verify import record_download

    selected = (
        [sources.get(a) for a in args.asset] if args.asset else list(sources.GROUPS[args.group])
    )
    blocked = 0
    for source in selected:
        result = fetch_source(source, paths.downloads_dir(), force=args.force)
        print(f"{source.id:<26} {result.status:<11} {result.message}")
        if result.ok and result.path is not None:
            record = record_download(paths.catalog_path().parent, source.id, result.path)
            print(f"{'':<26} sha256 {record.original_sha256}  {record.size_bytes / 1e6:.1f} MB")
        elif result.manual_instructions:
            blocked += 1
            print()
            print(result.manual_instructions)
            print()
    if blocked:
        print(f"\n{blocked} source(s) need manual download. Everything else is ready.")
    return 0


def _record_new_downloads() -> list[str]:
    """Hash any archive not yet in the acquisition log, and report on it.

    An archive that is already recorded and still matches is left alone. One
    that no longer matches is reported loudly rather than quietly re-recorded:
    a changed hash means the file on disk is not the one that was reviewed, and
    silently updating the record would erase the only evidence of that.
    """
    from s32tools.assets.fetch import sha256_of
    from s32tools.assets.manifest import load
    from s32tools.assets.verify import record_download

    downloads = paths.downloads_dir()
    if not downloads.is_dir():
        return []

    manifest = load(paths.catalog_path())
    messages: list[str] = []

    for pack_dir in sorted(p for p in downloads.iterdir() if p.is_dir()):
        if pack_dir.name.startswith("_"):
            continue
        archives = sorted(p for p in pack_dir.iterdir() if p.suffix.lower() == ".zip")
        if not archives:
            continue

        entry = manifest.entries.get(pack_dir.name)
        archive = archives[0]

        if entry is None:
            messages.append(
                f"{pack_dir.name:<26} on disk but not in assets.toml — add an entry with its "
                "licence before using it"
            )
            continue

        if not entry.original_sha256:
            record = record_download(paths.catalog_path().parent, pack_dir.name, archive)
            messages.append(f"{pack_dir.name:<26} recorded sha256 {record.original_sha256[:16]}")
        elif sha256_of(archive) != entry.original_sha256:
            messages.append(
                f"{pack_dir.name:<26} SHA-256 MISMATCH — {archive.name} is not the file the "
                "manifest records. Do not use it; re-fetch or investigate."
            )
    return messages


def _cmd_assets_install(args: argparse.Namespace) -> int:
    from s32tools.assets.import_pack import extract_downloads
    from s32tools.assets.install import counts_by_kind, install_all, write_log

    # Record any archive that is on disk but not yet in the acquisition log.
    # This is what makes a manual download a first-class citizen: however the
    # file arrived, its hash ends up recorded the same way.
    for line in _record_new_downloads():
        print(line)

    # Extract next. `fetch` deliberately only downloads, so that re-running the
    # pipeline after a naming change does not re-download 90 MB — which means
    # this is the step that turns archives into a vendor tree.
    extracted = extract_downloads(paths.downloads_dir(), paths.vendor_dir())
    for asset_id, extraction in sorted(extracted.items()):
        print(f"{asset_id:<26} extracted {extraction.count} file(s)")
    if extracted:
        print()

    asset_ids = (
        sorted(p.name for p in paths.vendor_dir().iterdir() if p.is_dir())
        if paths.vendor_dir().is_dir()
        else []
    )
    if not asset_ids:
        print("nothing to install.")
        print("  assets/.downloads/ is empty — run `s32 assets fetch` first,")
        print("  or follow the MANUAL DOWNLOAD REQUIRED instructions it printed.")
        return 1

    report = install_all(
        asset_ids,
        paths.vendor_dir(),
        paths.processed_dir(),
        paths.game_dir(),
        to_game=not args.no_game,
    )
    for asset_id, result in report.processed.items():
        print(f"{asset_id:<26} {len(result.written):>4} written, {len(result.skipped):>4} skipped")
        if result.unmapped:
            print(f"{'':<26} unmapped: {', '.join(result.unmapped[:5])}")
    write_log(report, paths.catalog_path().parent / "import_log.json")
    print(f"\nprocessed: {counts_by_kind(paths.processed_dir())}")
    if not args.no_game:
        print(f"copied into game/: {report.copied_to_game} files")
    return 0


def _cmd_assets_verify(_args: argparse.Namespace) -> int:
    from s32tools.assets.verify import verify_all

    manifest, problems = verify_all(
        paths.catalog_path(), paths.evidence_dir(), paths.downloads_dir()
    )
    print(f"{len(manifest.entries)} manifest entries")
    for asset_id, entry in sorted(manifest.entries.items()):
        redistributable = "repo-safe" if entry.redistributable_in_repo else "LOCAL ONLY"
        print(f"  {asset_id:<26} {entry.license_name[:44]:<46} {redistributable}")
    if problems:
        print(f"\n{len(problems)} problem(s):")
        for problem in problems:
            print(f"  - {problem}")
        return 1
    print("\nAll entries have evidence, terms and matching hashes.")
    return 0


def _cmd_assets_credits(args: argparse.Namespace) -> int:
    from s32tools.assets.generate_credits import check_all, write_all
    from s32tools.assets.manifest import load

    manifest = load(paths.catalog_path())
    if args.check:
        stale = check_all(paths.repo_root(), manifest)
        if stale:
            print("Credit files are out of date:")
            for item in stale:
                print(f"  {item}")
            print("\nRun: s32 assets credits")
            return 1
        print("Credit files are up to date.")
        return 0

    for path in write_all(paths.repo_root(), manifest):
        print(f"wrote {path.relative_to(paths.repo_root())}")
    return 0


def _cmd_assets_evidence(_args: argparse.Namespace) -> int:
    from s32tools.assets.evidence import write_all
    from s32tools.assets.manifest import load

    manifest = load(paths.catalog_path())
    written = write_all(manifest, paths.evidence_dir())
    for path in written:
        print(f"wrote {path.relative_to(paths.repo_root())}")
    print()
    print(f"{len(written)} evidence file(s). Review them: a generated record is")
    print("only evidence once a human has confirmed it matches the page.")
    return 0


def _cmd_assets_images(_args: argparse.Namespace) -> int:
    from s32tools.assets.generate_renpy_images import generate

    result = generate(_library(), paths.processed_dir(), paths.game_dir())
    target = paths.game_dir() / "engine" / "01_s32_images.rpy"
    target.write_text(result.text, encoding="utf-8")

    print(f"wrote {target.relative_to(paths.repo_root())}")
    print(f"  characters with art: {', '.join(result.characters_defined) or 'none'}")
    if result.characters_without_art:
        print(f"  ART GAP: {', '.join(result.characters_without_art)}")
    print(f"  background definitions: {result.backgrounds_defined}")
    for char_id, wanted in result.missing_expressions.items():
        print(f"  {char_id}: substituted {len(wanted)} expression(s): {', '.join(wanted[:6])}")
    return 0


def _cmd_assets_audit(args: argparse.Namespace) -> int:
    from s32tools.assets.audit_report import run, to_markdown

    metrics = run(paths.vendor_dir())
    if not metrics:
        print("no character packs in assets/vendor — run `s32 assets fetch --group characters`")
        return 1

    text = to_markdown(metrics)
    target = args.out or (paths.reports_dir() / "character_asset_audit.md")
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(text, encoding="utf-8")
    print(text)
    print(f"\nwrote {target}")
    return 0


def _cmd_assets_paper(_args: argparse.Namespace) -> int:
    from s32tools.assets.paper import build, digest

    target = paths.game_dir() / "images" / "documents"
    for path in build(target):
        print(f"wrote {path.relative_to(paths.repo_root())}")
    print()
    print("sha256:")
    for name, value in digest(target).items():
        print(f"  {name:16} {value}")
    print()
    print("First-party and deterministic, so these ARE committed.")
    return 0


def _cmd_assets_sheets(args: argparse.Namespace) -> int:
    from s32tools.assets.contact_sheet import build_all

    out = args.out or (paths.reports_dir() / "contact-sheets")
    written = build_all(paths.processed_dir(), out)
    if not written:
        print("nothing to sheet — run `s32 assets install` first")
        return 1
    for path in written:
        print(f"wrote {path}")
    return 0


# -- ren'py -----------------------------------------------------------------


def _cmd_renpy_install(args: argparse.Namespace) -> int:
    from s32tools.renpy_sdk import install

    info, message = install(paths.renpy_sdk_dir(), force=args.force)
    print(message)
    return 0 if info else 1


def _sdk_or_fail() -> SdkInfo | None:
    """Return the SDK, or print how to get one and return ``None``."""
    from s32tools.renpy_sdk import ENV_VAR, RENPY_VERSION, locate

    info = locate()
    if info is None:
        print(
            f"Ren'Py {RENPY_VERSION} is not installed.\n"
            f"  s32 renpy install\n"
            f"  ...or set {ENV_VAR} to an existing SDK."
        )
    return info


def _cmd_renpy_lint(_args: argparse.Namespace) -> int:
    from s32tools.renpy_sdk import headless_env, run

    info = _sdk_or_fail()
    if info is None:
        return 1

    result = run(info, paths.repo_root(), "lint", extra_env=headless_env())
    print(result.stdout)
    if result.stderr.strip():
        print(result.stderr, file=sys.stderr)

    # Ren'Py's lint exits 0 even when it reports problems, so the report text is
    # what decides. Anything that is not the statistics block is a finding.
    findings = [
        line
        for line in result.stdout.splitlines()
        if line.strip() and (".rpy:" in line or line.startswith(("Error", "Warning")))
    ]
    if findings:
        print(f"\n{len(findings)} lint finding(s).")
        return 1
    return result.returncode


def _cmd_renpy_test(args: argparse.Namespace) -> int:
    from s32tools.renpy_sdk import headless_env, run

    info = _sdk_or_fail()
    if info is None:
        return 1

    cases = args.case or [
        "smoke_main_menu",
        "smoke_start_and_choose",
        "smoke_director_runs",
        "smoke_rollback",
        "smoke_debug_screens",
        "smoke_journal",
        "archive_opens_and_closes",
        "archive_pages_with_the_keyboard",
        "archive_effects_apply_once",
        "archive_index_hides_locked_documents",
        "archive_survives_rollback",
    ]
    env = {**headless_env(), "S32_SEED": str(args.seed)}

    failures = 0
    for case in cases:
        result = run(info, paths.repo_root(), "test", case, extra_env=env)
        passed = "Status: PASSED" in result.stdout
        print(f"{'PASS' if passed else 'FAIL'}  {case}")
        if not passed:
            failures += 1
            print(result.stdout[-3000:])
    print(f"\n{len(cases) - failures}/{len(cases)} testcases passed.")
    return 1 if failures else 0


def _cmd_renpy_run(_args: argparse.Namespace) -> int:
    from s32tools.renpy_sdk import run

    info = _sdk_or_fail()
    if info is None:
        return 1
    result = run(info, paths.repo_root(), timeout=86400)
    print(result.stdout)
    return result.returncode


if __name__ == "__main__":
    raise SystemExit(main())
