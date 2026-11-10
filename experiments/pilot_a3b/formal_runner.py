"""R4 formal runner: frozen manifest + run ledger -> family-level analysis.

The runner accepts caller-supplied synthetic fixtures during development. Real
locked Test data may only be supplied after the separately approved one-time
final-evaluation gate; this module itself never loads a Test payload.
"""
from __future__ import annotations

import hashlib
import json
import subprocess
from collections import defaultdict
from pathlib import Path

from formal_analysis import analyze_primary_endpoint, analyze_secondary_endpoints

RUNNER_VERSION = "d064-r4-formal-runner-v1"
HERE = Path(__file__).parent
DEFAULT_CODE_FILES = (
    "formal_analysis.py",
    "power_hierarchical.py",
    "formal_runner.py",
    "split_access.py",
    "formal_preflight.py",
    "formal_scenario_generator.py",
)


def _canonical_sha256(value):
    payload = json.dumps(
        value, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def _manifest_sha256(manifest):
    if not isinstance(manifest, dict):
        raise ValueError("frozen manifest must be an object")
    value = {key: item for key, item in manifest.items() if key != "manifest_sha256"}
    return _canonical_sha256(value)


def _code_sha256(code_paths=None):
    paths = [Path(path) for path in (code_paths or [HERE / name for name in DEFAULT_CODE_FILES])]
    if not paths:
        raise ValueError("at least one implementation file is required")
    entries = {}
    for path in paths:
        if not path.is_file():
            raise ValueError(f"implementation file is missing: {path}")
        entries[path.name] = hashlib.sha256(path.read_bytes()).hexdigest()
    return _canonical_sha256(entries)


def _git_head():
    return subprocess.check_output(
        ["git", "rev-parse", "HEAD"], cwd=str(HERE), text=True
    ).strip()


def flatten_run_ledger(ledger):
    """Flatten method/seed runs while preserving and checking row metadata."""
    if not isinstance(ledger, dict) or not isinstance(ledger.get("runs"), list):
        raise ValueError("run ledger must contain a runs list")
    rows_out = []
    for run in ledger["runs"]:
        if not isinstance(run, dict) or not isinstance(run.get("rows"), list):
            raise ValueError("each run must contain a rows list")
        method = run.get("method")
        seed = run.get("seed")
        if not isinstance(method, str) or not method or seed is None:
            raise ValueError("each run requires method and seed")
        for original in run["rows"]:
            if not isinstance(original, dict):
                raise ValueError("ledger rows must be objects")
            row = dict(original)
            if "method" in row and row["method"] != method:
                raise ValueError("row/run method mismatch")
            if "seed" in row and row["seed"] != seed:
                raise ValueError("row/run optimizer seed mismatch")
            row["method"] = method
            row["seed"] = seed
            rows_out.append(row)
    return rows_out


def _family_rosters(expected_roster, primary_result):
    grouped = defaultdict(list)
    for item in expected_roster:
        grouped[item["family_id"]].append(item)
    loss_reasons = primary_result["family_loss_reasons"]
    output = {}
    for family, items in sorted(grouped.items()):
        normalized = [
            {
                "scenario_id": item["scenario_id"],
                "composition_id": item["composition_id"],
                "label": item["label"],
                "split": item["split"],
            }
            for item in sorted(items, key=lambda value: value["scenario_id"])
        ]
        entry = {
            "composition_ids": sorted({item["composition_id"] for item in normalized}),
            "scenario_count": len(normalized),
            "roster_sha256": _canonical_sha256(normalized),
        }
        if family in loss_reasons:
            entry["missing_pattern"] = loss_reasons[family]
        else:
            entry["missing_pattern"] = {
                "valid_compositions": len(entry["composition_ids"]),
                "required_compositions": len(entry["composition_ids"]),
                "incomplete_compositions": [],
            }
        output[family] = entry
    return output


def run_formal_analysis(
    manifest,
    ledger,
    expected_roster,
    expected_optimizer_seeds,
    technical_missing=None,
    *,
    analysis_split="test",
    git_head=None,
    code_paths=None,
):
    """Execute the formal primary and secondary analyses on one locked input."""
    actual_manifest_sha = _manifest_sha256(manifest)
    if manifest.get("manifest_sha256") != actual_manifest_sha:
        raise ValueError("manifest hash mismatch")

    try:
        composition_ids = manifest["power_design_candidate"]["primary_analysis_composition_ids"]
    except (KeyError, TypeError) as exc:
        raise ValueError("manifest lacks the frozen primary composition roster") from exc
    if (not isinstance(composition_ids, list) or len(composition_ids) != 5
            or len(set(composition_ids)) != 5):
        raise ValueError("formal runner requires exactly five unique primary compositions")

    provenance = {
        "manifest_sha256": actual_manifest_sha,
        "code_sha256": _code_sha256(code_paths),
        "git_head": git_head or _git_head(),
        "primary_composition_ids": list(composition_ids),
    }
    run_rows = flatten_run_ledger(ledger)
    technical = list(ledger.get("technical_missing", []))
    if technical_missing is not None:
        technical.extend(technical_missing)
    # Per-run technical records are part of the ledger schema.
    technical.extend(
        record for run in ledger["runs"] for record in run.get("technical_missing", [])
    )

    primary = analyze_primary_endpoint(
        run_rows,
        expected_roster,
        expected_optimizer_seeds,
        technical_missing=technical,
        analysis_split=analysis_split,
        provenance=provenance,
        primary_composition_ids=composition_ids,
    )
    secondary = analyze_secondary_endpoints(
        run_rows,
        expected_roster,
        expected_optimizer_seeds,
        technical_missing=technical,
        analysis_split=analysis_split,
        provenance=provenance,
        primary_composition_ids=composition_ids,
    )
    return {
        "kind": "D064_R4_FORMAL_ANALYSIS_RUN",
        "runner_version": RUNNER_VERSION,
        "status": primary["confirmatory_status"],
        "analysis_split": analysis_split,
        "data_access": "caller_supplied_synthetic_or_unlocked_ledger",
        "provenance": {
            **provenance,
            "primary_composition_roster_sha256": _canonical_sha256(sorted(composition_ids)),
        },
        "input_sha256": primary["input_sha256"],
        "n_ledger_rows": len(run_rows),
        "family_rosters": _family_rosters(expected_roster, primary),
        "primary": primary,
        "secondary": secondary,
    }


def write_formal_analysis_outputs(result, outdir):
    """Write machine-readable results and a compact human report."""
    outdir = Path(outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    json_path = outdir / "formal_analysis.json"
    markdown_path = outdir / "formal_analysis_report.md"
    json_path.write_text(
        json.dumps(result, indent=2, ensure_ascii=False, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    primary = result["primary"]
    student = primary.get("student_t")
    lines = [
        "# D-064-R4 formal family-level analysis",
        "",
        f"- Runner: {result['runner_version']}",
        f"- Input SHA-256: {result['input_sha256']}",
        f"- Manifest SHA-256: {result['provenance']['manifest_sha256']}",
        f"- Code SHA-256: {result['provenance']['code_sha256']}",
        f"- Git HEAD: {result['provenance']['git_head']}",
        f"- Status: {primary['confirmatory_status']}",
        f"- Complete families: {primary['n_families']}",
        f"- Family-equal effect: {primary['family_equal_weight_effect']}",
        f"- Family loss: {primary['family_loss']}",
        f"- Technical missing runs: {primary['technical_missing_runs']}",
        f"- Behavioural failures retained as zero: {primary['behavioural_failure_count']}",
    ]
    if student:
        lines.extend([
            f"- Student-t: t={student['t']}, df={student['df']}, p={student['p_two_sided']}",
            f"- Student-t status: {student['status']}",
            f"- 95% CI: {student['ci95']}",
        ])
    else:
        lines.append("- Student-t: withheld (not confirmatory-eligible)")
    lines.extend([
        f"- H2-H5 secondary status: {result['secondary']['status']}",
        "- H2-H5 classification: exploratory",
        "",
        "This report does not authorize formal A-3b or prove algorithmic improvement.",
    ])
    markdown_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return json_path, markdown_path
