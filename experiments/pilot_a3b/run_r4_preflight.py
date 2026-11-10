"""Execute the current R4 pre-flight using metadata only.

No Test payload loader is accepted or called. Outcome-dependent fields remain
unevaluated before the formal run, so an unapproved pre-run state returns HOLD.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from pathlib import Path

from formal_preflight import run_formal_preflight, write_preflight_report
from formal_runner import _code_sha256
from formal_scenario_generator import build_candidate_manifest

HERE = Path(__file__).parent
REPO_ROOT = HERE.parent.parent
DEFAULT_PREREGISTRATION = REPO_ROOT / "64_A3B_PREREGISTRATION_CANDIDATE_R4.md"


def run_current_preflight(
    outdir,
    *,
    git_head=None,
    ci_conclusion,
    tests_passed,
    approvals=None,
    preregistration_path=DEFAULT_PREREGISTRATION,
    code_paths=None,
    ledger_path=None,
):
    """Build and execute a fail-closed pre-flight without reading Test payload."""
    manifest, audit = build_candidate_manifest()
    preregistration = Path(preregistration_path)
    preregistration_exists = preregistration.is_file()
    preregistration_sha = (
        hashlib.sha256(preregistration.read_bytes()).hexdigest()
        if preregistration_exists else "0" * 64
    )
    approvals = dict(approvals or {})
    hashes = dict(manifest["hashes"])
    primary_ids = manifest["power_design_candidate"]["primary_analysis_composition_ids"]
    summary = manifest["splits"]["test_locked"]["summary"]
    analysis_schema_valid = all((HERE / name).is_file() for name in (
        "formal_analysis.py", "formal_runner.py", "power_hierarchical.py",
        "split_access.py", "formal_preflight.py",
    ))
    ledger_state = "CONSUMED" if ledger_path and Path(ledger_path).exists() else "UNUSED"
    context = {
        "r4_preregistration_sha256": preregistration_sha,
        "implementation_sha256": _code_sha256(code_paths),
        "git_head": git_head or subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=str(REPO_ROOT), text=True
        ).strip(),
        "independent_review_status": approvals.get("independent_review_status", "PENDING"),
        "advisor_mde_status": approvals.get("advisor_mde_status", "PENDING"),
        "user_approved": approvals.get("user_approved", False),
        "ci_conclusion": ci_conclusion,
        "tests_passed": bool(tests_passed),
        "manifest_hashes": hashes,
        "split_overlap_count": 0 if audit["catalog_audit"]["ok"] else 1,
        "train_runner_split": "train",
        "validation_use": "selection_only",
        "test_payload_exposed": False,
        "test_payload_disclosed": False,
        "test_family_count": summary["n_families"],
        "test_scenario_count": summary["n_scenarios"],
        "expected_roster_valid": bool(
            manifest["gate"]["passed"] and len(primary_ids) == len(set(primary_ids)) == 5
        ),
        "paired_rows_valid": False,
        "duplicate_count": None,
        "labelled_null_count": None,
        "metadata_mismatch_count": None,
        "n_observed_families": 0,
        "family_composition_counts": {},
        "family_loss": [],
        "technical_missing_runs": 0,
        "design_deviation": True,
        "analysis_schema_valid": analysis_schema_valid,
        "budget_within_cap": True,
        "seed_recorded": True,
        "stopping_rule_frozen": True,
        "test_access_log_count": 0,
        "one_time_ledger_state": ledger_state,
    }
    result = run_formal_preflight(context)
    if not preregistration_exists:
        result["blocking_reasons"].append("R4 preregistration file is missing")
        result["status"] = "HOLD"
    result["execution_context"] = {
        "scope": "metadata-only pre-run gate",
        "outcome_ledger_state": "NOT_RUN",
        "manifest_gate": "PASS" if manifest["gate"]["passed"] else "FAIL",
        "test_summary": summary,
        "primary_composition_ids": primary_ids,
        "approval_record": {
            "independent_review_status": context["independent_review_status"],
            "advisor_mde_status": context["advisor_mde_status"],
            "user_approved": context["user_approved"],
        },
    }
    json_path, markdown_path = Path(outdir) / "preflight.json", Path(outdir) / "preflight.md"
    write_preflight_report(result, json_path, markdown_path)
    return result, json_path, markdown_path


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--outdir", required=True)
    parser.add_argument("--ci-conclusion", required=True)
    parser.add_argument("--tests-passed", action="store_true")
    parser.add_argument("--git-head", default=None)
    parser.add_argument("--approvals", default=None, help="JSON file with approval metadata only")
    args = parser.parse_args()
    approvals = None
    if args.approvals:
        approvals = json.loads(Path(args.approvals).read_text(encoding="utf-8"))
    result, json_path, markdown_path = run_current_preflight(
        args.outdir,
        git_head=args.git_head,
        ci_conclusion=args.ci_conclusion,
        tests_passed=args.tests_passed,
        approvals=approvals,
    )
    print("R4 pre-flight:", result["status"])
    for reason in result["blocking_reasons"]:
        print("-", reason)
    print("wrote", json_path, markdown_path)


if __name__ == "__main__":
    main()
