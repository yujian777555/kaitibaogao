"""R4 machine-readable, fail-closed formal pre-flight.

This module accepts metadata and gate results only. It must never load, inspect,
or serialize Test scenario labels or episode outcomes. The only Test fields
permitted here are counts, hashes, split summaries, access-log counts, and the
one-time ledger state.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
GIT_SHA_RE = re.compile(r"^[0-9a-f]{40}$")
REQUIRED_MANIFEST_HASHES = (
    "train_family_sha256",
    "train_scenario_sha256",
    "validation_family_sha256",
    "validation_scenario_sha256",
    "test_family_sha256",
    "test_scenario_sha256",
)
REQUIRED_FIELDS = (
    "r4_preregistration_sha256",
    "implementation_sha256",
    "git_head",
    "independent_review_status",
    "advisor_mde_status",
    "user_approved",
    "ci_conclusion",
    "tests_passed",
    "manifest_hashes",
    "split_overlap_count",
    "train_runner_split",
    "validation_use",
    "test_payload_exposed",
    "test_payload_disclosed",
    "test_family_count",
    "test_scenario_count",
    "expected_roster_valid",
    "paired_rows_valid",
    "duplicate_count",
    "labelled_null_count",
    "metadata_mismatch_count",
    "n_observed_families",
    "family_composition_counts",
    "family_loss",
    "technical_missing_runs",
    "design_deviation",
    "analysis_schema_valid",
    "budget_within_cap",
    "seed_recorded",
    "stopping_rule_frozen",
    "test_access_log_count",
    "one_time_ledger_state",
)


def run_formal_preflight(context):
    """Return GO only when every approval, integrity, split, and design gate passes."""
    reasons = []
    if not isinstance(context, dict):
        return {
            "status": "HOLD",
            "blocking_reasons": ["pre-flight context must be an object"],
            "checked_fields": [],
        }

    missing = [field for field in REQUIRED_FIELDS if field not in context]
    if missing:
        reasons.append("missing required pre-flight fields: " + ", ".join(missing))

    for field in ("r4_preregistration_sha256", "implementation_sha256"):
        value = context.get(field)
        if not isinstance(value, str) or not SHA256_RE.fullmatch(value):
            reasons.append(f"{field} must be a 64-character lowercase SHA-256")
    if not isinstance(context.get("git_head"), str) or not GIT_SHA_RE.fullmatch(context.get("git_head", "")):
        reasons.append("git_head must be a 40-character lowercase commit SHA")

    hashes = context.get("manifest_hashes")
    if not isinstance(hashes, dict):
        reasons.append("manifest_hashes must be an object")
    else:
        for field in REQUIRED_MANIFEST_HASHES:
            value = hashes.get(field)
            if not isinstance(value, str) or not SHA256_RE.fullmatch(value):
                reasons.append(f"invalid or missing manifest hash: {field}")

    if context.get("independent_review_status") != "ACCEPTED":
        reasons.append("independent review is not ACCEPTED")
    if context.get("advisor_mde_status") != "APPROVED":
        reasons.append("advisor MDE approval is not APPROVED")
    if context.get("user_approved") is not True:
        reasons.append("explicit user approval is absent")
    if context.get("ci_conclusion") != "success" or context.get("tests_passed") is not True:
        reasons.append("required tests/CI are not successful")

    if context.get("split_overlap_count") != 0:
        reasons.append("Train/Validation/Test split overlap is nonzero")
    if context.get("train_runner_split") != "train":
        reasons.append("evolution runner is not restricted to Train")
    if context.get("validation_use") != "selection_only":
        reasons.append("Validation is not restricted to selection/stop rules")
    if context.get("test_payload_exposed") is not False:
        reasons.append("Test payload is exposed to a development caller")
    if context.get("test_payload_disclosed") is not False:
        reasons.append("Test payload disclosure flag is not false")
    if context.get("test_family_count") != 40:
        reasons.append("frozen Test family count must be 40")
    if context.get("test_scenario_count") != 1080:
        reasons.append("frozen Test scenario count must be 1080")

    if context.get("expected_roster_valid") is not True:
        reasons.append("frozen expected roster validation failed")
    if context.get("paired_rows_valid") is not True:
        reasons.append("paired AB/NSGA-II rows are incomplete")
    for field in ("duplicate_count", "labelled_null_count", "metadata_mismatch_count"):
        if context.get(field) != 0:
            reasons.append(f"{field} must be zero")

    n_families = context.get("n_observed_families")
    if not isinstance(n_families, int) or isinstance(n_families, bool) or n_families < 34:
        reasons.append("at least 34 complete families are required")
    composition_counts = context.get("family_composition_counts")
    if not isinstance(composition_counts, dict) or not composition_counts:
        reasons.append("family_composition_counts must be a non-empty object")
    elif any(value != 5 for value in composition_counts.values()):
        reasons.append("every retained family must have exactly five primary compositions")
    elif n_families != len(composition_counts):
        reasons.append("observed family count does not match composition-count roster")

    family_loss = context.get("family_loss")
    if not isinstance(family_loss, list):
        reasons.append("family_loss must be an explicit list")
    if context.get("design_deviation") is not False:
        reasons.append("design_deviation is active")
    missing_runs = context.get("technical_missing_runs")
    if not isinstance(missing_runs, int) or isinstance(missing_runs, bool) or missing_runs < 0:
        reasons.append("technical_missing_runs must be a non-negative integer")

    for field in ("analysis_schema_valid", "budget_within_cap", "seed_recorded", "stopping_rule_frozen"):
        if context.get(field) is not True:
            reasons.append(f"{field} gate is not satisfied")

    if context.get("test_access_log_count") != 0:
        reasons.append("Test access log is non-empty")
    if context.get("one_time_ledger_state") != "UNUSED":
        reasons.append("one-time final-evaluation ledger is not UNUSED")

    return {
        "status": "GO" if not reasons else "HOLD",
        "blocking_reasons": reasons,
        "checked_fields": list(REQUIRED_FIELDS),
        "provenance": {
            "r4_preregistration_sha256": context.get("r4_preregistration_sha256"),
            "implementation_sha256": context.get("implementation_sha256"),
            "git_head": context.get("git_head"),
            "manifest_hashes": hashes if isinstance(hashes, dict) else {},
        },
        "design": {
            "n_observed_families": n_families,
            "family_loss": family_loss,
            "technical_missing_runs": missing_runs,
            "family_composition_counts": composition_counts if isinstance(composition_counts, dict) else {},
        },
        "test_lock": {
            "payload_exposed": context.get("test_payload_exposed"),
            "payload_disclosed": context.get("test_payload_disclosed"),
            "access_log_count": context.get("test_access_log_count"),
            "one_time_ledger_state": context.get("one_time_ledger_state"),
        },
    }


def write_preflight_report(result, json_path, markdown_path):
    """Write JSON and Markdown gate outputs; no Test payload is accepted."""
    json_path = Path(json_path)
    markdown_path = Path(markdown_path)
    json_path.parent.mkdir(parents=True, exist_ok=True)
    markdown_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(
        json.dumps(result, indent=2, ensure_ascii=False, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    lines = [
        "# R4 Formal Pre-flight",
        "",
        f"Status: **{result.get('status', 'HOLD')}**",
        "",
        "## Blocking reasons",
        "",
    ]
    reasons = result.get("blocking_reasons", [])
    lines.extend([f"- {reason}" for reason in reasons] if reasons else ["- None"])
    lines.extend([
        "",
        "## Test lock",
        "",
        f"- Payload exposed: {result.get('test_lock', {}).get('payload_exposed')}",
        f"- Payload disclosed: {result.get('test_lock', {}).get('payload_disclosed')}",
        f"- Access log count: {result.get('test_lock', {}).get('access_log_count')}",
        f"- One-time ledger: {result.get('test_lock', {}).get('one_time_ledger_state')}",
        "",
    ])
    markdown_path.write_text("\n".join(lines), encoding="utf-8")
