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
from split_access import public_manifest_view

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
    config_path=None,
    access_log_path=None,
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
    config_file = Path(config_path) if config_path is not None else HERE / "r4_execution_config.json"
    execution_config = (
        json.loads(config_file.read_text(encoding="utf-8")) if config_file.is_file() else {}
    )
    public_view = public_manifest_view(manifest)
    public_test = public_view["splits"]["test_locked"]
    test_payload_exposed = any(key in public_test for key in ("scenarios", "families", "clusters"))
    access_count = 0
    if access_log_path is not None and Path(access_log_path).is_file():
        access_count = sum(
            bool(line.strip()) for line in Path(access_log_path).read_text(encoding="utf-8").splitlines()
        )
    expected_budget = "48*(60+1)*216 real simulator episodes plus explicitly counted safety-battery episodes; cached genomes are not new unique evaluations"
    budget_within_cap = bool(
        execution_config.get("population") == 48
        and execution_config.get("generations") == 60
        and execution_config.get("train_scenarios") == audit["split_summaries"]["train"]["n_scenarios"]
        and execution_config.get("budget_rule") == expected_budget
    )
    seed_recorded = bool(
        execution_config.get("optimizer_seeds") == [411, 522, 633]
        and execution_config.get("power_base_seed") == 20261114
        and execution_config.get("signflip_base_seed") == 20261112
        and execution_config.get("signflip_mc_seed") == 20261113
    )
    stopping_rule_frozen = execution_config.get("stopping_rule") == "budget_exhaustion_no_early_significance_stop"
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
        "train_runner_split": execution_config.get("train_runner_split"),
        "validation_use": execution_config.get("validation_use"),
        "test_payload_exposed": test_payload_exposed,
        "test_payload_disclosed": manifest["splits"]["test_locked"].get("payload_disclosed") is not False,
        "test_family_count": summary["n_families"],
        "test_scenario_count": summary["n_scenarios"],
        "expected_roster_valid": bool(
            manifest["gate"]["passed"] and len(primary_ids) == len(set(primary_ids)) == 5
        ),
        "analysis_schema_valid": analysis_schema_valid,
        "budget_within_cap": budget_within_cap,
        "seed_recorded": seed_recorded,
        "stopping_rule_frozen": stopping_rule_frozen,
        "test_access_log_count": access_count,
        "one_time_ledger_state": ledger_state,
    }
    result = run_formal_preflight(context)
    if not preregistration_exists:
        result["blocking_reasons"].append("R4 preregistration file is missing")
        result["status"] = "HOLD"
    result["execution_context"] = {
        "phase": "PRE_RUN_AUTHORIZATION",
        "scope": "metadata-only pre-run authorization gate; no outcome rows are expected here",
        "outcome_ledger_state": "NOT_RUN",
        "execution_config_sha256": hashlib.sha256(config_file.read_bytes()).hexdigest() if config_file.is_file() else None,
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
    parser.add_argument("--config-path", default=None)
    parser.add_argument("--ledger-path", default=None)
    parser.add_argument("--access-log-path", default=None)
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
        config_path=args.config_path,
        ledger_path=args.ledger_path,
        access_log_path=args.access_log_path,
    )
    print("R4 pre-flight:", result["status"])
    for reason in result["blocking_reasons"]:
        print("-", reason)
    print("wrote", json_path, markdown_path)


if __name__ == "__main__":
    main()
