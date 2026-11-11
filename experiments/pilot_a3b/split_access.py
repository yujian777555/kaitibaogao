"""R4 split-access controls and atomic one-time final-evaluation gate.

Development/optimization APIs can consume Train only. Ordinary evaluation
APIs may consume Train or Validation, never Test/Battery/unknown splits.
Test payload access is reserved for a separately approved one-time wrapper.
All tests in this module use synthetic sentinels only.
"""
from __future__ import annotations

import hashlib
import json
import os
from copy import deepcopy
from pathlib import Path


DEVELOPMENT_SPLITS = frozenset(("train", "validation"))


def _canonical_sha256(value):
    payload = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _validate_preflight_binding(preflight_result, approval_record):
    """Bind execution to the exact approved pre-run artifact, not a caller flag."""
    preflight_result = preflight_result or approval_record.get("preflight_artifact")
    if not isinstance(preflight_result, dict):
        raise PermissionError("final evaluation requires the actual pre-run result")
    if (preflight_result.get("phase") != "PRE_RUN_AUTHORIZATION"
            or preflight_result.get("status") != "GO"):
        raise PermissionError("final evaluation requires PRE_RUN_AUTHORIZATION GO")
    provenance = preflight_result.get("provenance", {})
    if provenance.get("git_head") != approval_record.get("git_head"):
        raise PermissionError("pre-flight git HEAD does not match the approval record")
    if provenance.get("implementation_sha256") != approval_record.get("code_sha256"):
        raise PermissionError("pre-flight code hash does not match the approval record")
    test_lock = preflight_result.get("test_lock", {})
    if (test_lock.get("access_log_count") != 0
            or test_lock.get("one_time_ledger_state") != "UNUSED"):
        raise PermissionError("pre-flight Test lock is not unused")
    if approval_record.get("preflight_sha256") != _canonical_sha256(preflight_result):
        raise PermissionError("approval record is not bound to the exact pre-flight artifact")


def public_manifest_view(manifest):
    """Return a safe manifest view with no Test scenario/family payload."""
    splits = manifest.get("splits")
    if not isinstance(splits, dict):
        raise ValueError("manifest splits must be an object")
    if "train" not in splits or "validation" not in splits or "test_locked" not in splits:
        raise ValueError("manifest must contain train, validation, and test_locked")

    locked = splits["test_locked"]
    safe_test = {
        "summary": deepcopy(locked.get("summary")),
        "family_sha256": locked.get("family_sha256"),
        "scenario_sha256": locked.get("scenario_sha256"),
        "payload_disclosed": False,
    }
    return {
        "schema_version": manifest.get("schema_version"),
        "generator_version": manifest.get("generator_version"),
        "status": manifest.get("status"),
        "semantic_contract_version": manifest.get("semantic_contract_version"),
        "seed_base": manifest.get("seed_base"),
        "hashes": deepcopy(manifest.get("hashes", {})),
        "splits": {
            "train": deepcopy(splits["train"]),
            "validation": deepcopy(splits["validation"]),
            "test_locked": safe_test,
        },
    }


def scenarios_for_split(manifest, split):
    """Return a copied Train/Validation scenario list; Test is never returned."""
    if split not in DEVELOPMENT_SPLITS:
        raise PermissionError("Test split is restricted to the final-evaluation gate")
    try:
        scenarios = manifest["splits"][split]["scenarios"]
    except (KeyError, TypeError) as exc:
        raise ValueError(f"manifest lacks {split} scenarios") from exc
    copied = deepcopy(scenarios)
    if not isinstance(copied, list) or not copied:
        raise ValueError(f"{split} scenarios must be a non-empty list")
    for scenario in copied:
        if not isinstance(scenario, dict) or scenario.get("split") != split:
            raise ValueError(f"scenario split metadata mismatch for {split}")
    return copied


def validate_evolution_scenarios(scenarios):
    """Fail before fitness evaluation unless every scenario is explicitly Train."""
    if not scenarios:
        raise ValueError("evolution requires a non-empty Train scenario set")
    for scenario in scenarios:
        if not isinstance(scenario, dict) or scenario.get("split") != "train":
            raise ValueError("run_evolution accepts train split only")


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


def validate_evaluation_scenarios(scenarios):
    """Ordinary evaluator accepts Train/Validation, but never Test or Battery."""
    if not scenarios:
        raise ValueError("evaluation requires a non-empty Train/Validation scenario set")
    for scenario in scenarios:
        if not isinstance(scenario, dict) or scenario.get("split") not in DEVELOPMENT_SPLITS:
            raise ValueError("test split is restricted to the final-evaluation gate")


def consume_final_evaluation_once(
    ledger_path,
    approval_record,
    expected_manifest_sha256,
    actual_manifest_sha256,
    expected_code_sha256,
    actual_code_sha256,
    payload_loader,
    evaluator,
    *,
    preflight_result=None,
):
    """Consume an atomic one-time ledger before invoking the Test payload loader.

    The ledger remains consumed if payload loading or evaluation fails. This is
    deliberate fail-closed behavior: a failed final attempt cannot be retried
    by silently opening Test a second time.
    """
    _validate_preflight_binding(preflight_result, approval_record)
    required = (
        approval_record.get("status") == "APPROVED"
        and approval_record.get("preflight_status") == "GO"
        and approval_record.get("ci_conclusion") == "success"
        and approval_record.get("tests_passed") is True
        and approval_record.get("independent_review_status") == "ACCEPTED"
        and approval_record.get("advisor_mde_approved") is True
        and approval_record.get("user_approved") is True
    )
    if not required:
        raise PermissionError("final evaluation requires pre-flight GO, successful CI/tests, independent, advisor, and user approval")
    if (approval_record.get("manifest_sha256") != expected_manifest_sha256
            or approval_record.get("code_sha256") != expected_code_sha256):
        raise ValueError("approval record hash mismatch")
    if actual_manifest_sha256 != expected_manifest_sha256:
        raise ValueError("manifest hash mismatch")
    if actual_code_sha256 != expected_code_sha256:
        raise ValueError("code hash mismatch")

    path = Path(ledger_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    record = {
        "state": "CONSUMED",
        "manifest_sha256": expected_manifest_sha256,
        "code_sha256": expected_code_sha256,
    }
    flags = os.O_CREAT | os.O_EXCL | os.O_WRONLY
    try:
        fd = os.open(str(path), flags, 0o600)
    except FileExistsError as exc:
        raise RuntimeError("final-evaluation one-time ledger already consumed") from exc
    try:
        payload = json.dumps(record, sort_keys=True).encode("utf-8")
        os.write(fd, payload)
        os.fsync(fd)
    finally:
        os.close(fd)

    test_payload = payload_loader()
    return evaluator(test_payload)


def validate_execution_receipt(receipt, manifest_sha256, code_sha256, outcome_ledger):
    """Verify receipt, consumed ledger, outcome hash, and one-time access log."""
    if not isinstance(receipt, dict) or receipt.get("status") != "COMPLETED":
        raise PermissionError("final evaluation requires a completed receipt")
    if (receipt.get("manifest_sha256") != manifest_sha256
            or receipt.get("code_sha256") != code_sha256):
        raise PermissionError("final-evaluation receipt hash mismatch")
    ledger_path = Path(receipt.get("ledger_path", ""))
    if not ledger_path.is_file():
        raise PermissionError("one-time final-evaluation ledger is missing")
    consumed = json.loads(ledger_path.read_text(encoding="utf-8"))
    if (consumed.get("state") != "CONSUMED"
            or consumed.get("manifest_sha256") != manifest_sha256
            or consumed.get("code_sha256") != code_sha256):
        raise PermissionError("one-time ledger does not match the receipt")
    if not isinstance(outcome_ledger, dict):
        raise PermissionError("final evaluator did not return a run-ledger object")
    if receipt.get("outcome_ledger_sha256") != _canonical_sha256(outcome_ledger):
        raise PermissionError("outcome ledger does not match the receipt")
    access_log_path = Path(receipt.get("access_log_path", ""))
    if not access_log_path.is_file():
        raise PermissionError("one-time Test access log is missing")
    access_record = json.loads(access_log_path.read_text(encoding="utf-8"))
    if (access_record.get("event") != "TEST_PAYLOAD_LOAD_ATTEMPT"
            or access_record.get("state") != "RECORDED"
            or access_record.get("manifest_sha256") != manifest_sha256
            or access_record.get("code_sha256") != code_sha256
            or receipt.get("test_access_log_count") != 1):
        raise PermissionError("one-time Test access log does not match the receipt")
    return True


def execute_final_evaluation_once(
    ledger_path,
    approval_record,
    preflight_result,
    expected_manifest_sha256,
    actual_manifest_sha256,
    expected_code_sha256,
    actual_code_sha256,
    payload_loader,
    evaluator,
):
    """Production wrapper: require pre-run GO, consume once, then issue a bound receipt."""
    if not isinstance(preflight_result, dict) or preflight_result.get("phase") != "PRE_RUN_AUTHORIZATION" or preflight_result.get("status") != "GO":
        raise PermissionError("final evaluation requires a successful PRE_RUN_AUTHORIZATION GO")
    approved = dict(approval_record)
    approved["preflight_status"] = preflight_result["status"]
    approved["preflight_artifact"] = preflight_result
    access_log_path = Path(str(ledger_path) + ".access.json")

    def logged_payload_loader():
        access_record = {
            "event": "TEST_PAYLOAD_LOAD_ATTEMPT",
            "state": "RECORDED",
            "manifest_sha256": actual_manifest_sha256,
            "code_sha256": actual_code_sha256,
        }
        flags = os.O_CREAT | os.O_EXCL | os.O_WRONLY
        try:
            fd = os.open(str(access_log_path), flags, 0o600)
        except FileExistsError as exc:
            raise RuntimeError("Test access log already exists; refusing another load") from exc
        try:
            os.write(fd, json.dumps(access_record, sort_keys=True).encode("utf-8"))
            os.fsync(fd)
        finally:
            os.close(fd)
        return payload_loader()

    outcome_ledger = consume_final_evaluation_once(
        ledger_path, approved,
        expected_manifest_sha256, actual_manifest_sha256,
        expected_code_sha256, actual_code_sha256,
        logged_payload_loader, evaluator,
        preflight_result=preflight_result,
    )
    if not isinstance(outcome_ledger, dict):
        raise ValueError("final evaluator must return a run-ledger object")
    canonical = json.dumps(outcome_ledger, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    receipt = {
        "status": "COMPLETED",
        "manifest_sha256": actual_manifest_sha256,
        "code_sha256": actual_code_sha256,
        "ledger_path": str(ledger_path),
        "access_log_path": str(access_log_path),
        "test_access_log_count": 1,
        "outcome_ledger_sha256": __import__("hashlib").sha256(canonical).hexdigest(),
    }
    return outcome_ledger, receipt
