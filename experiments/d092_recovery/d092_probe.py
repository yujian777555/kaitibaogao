"""D-092 R2.3 executable 960-episode Probe with pre-rollout execution lock."""
from __future__ import annotations

import datetime
import hashlib
import json
import os
import platform as platform_module
import subprocess
import time
from pathlib import Path
from typing import Any, Dict, List, Sequence, Tuple

import numpy as np

from d092_evaluator import EXPECTED_MANIFEST_CANONICAL, EXPECTED_MANIFEST_INTERNAL, load_train_manifest
from d092_genome import canonical_json_bytes, genome_sha256, probe_typed_genomes, sha256_hex
from d092_runtime import run_guarded_episode
from d090_policies import D090Policy
from d088_policies import D088RecoveryPolicy
from d089_budget import public_min_harm

ROOT = Path(__file__).resolve().parents[2]
MANIFEST_PATH = ROOT / "experiments" / "d090_recovery" / "results" / "d090_train_manifest.json"
PROTOCOL_PATH = ROOT / "103_D092_TRAIN_ONLY_PREREGISTRATION.md"
PROBE_SEED = 711
EXPECTED_PROTOCOL_RAW = "75f9c72aa7d3a70880f59f7b803ed88e919d47e9c42e7168ba1b7eddbc3e7522"
EXPECTED_PANEL = "cccb84511a84f3bcd1dd7141b83fb278459e0267cf00a332e96f6d7cb6da6934"
ANCHORS = {
    "Q0": "d090r|train|d090_PAIR_RACE|D3_DEPENDENT_ABORT|r0",
    "Q0b": "d090r|train|d090_PAIR_RACE|D4_BLOCKED_COMPENSATION|r0",
    "Q1": "d090r|train|d090_MULTI_ROUTE|D3_DEPENDENT_ABORT|r0",
    "Q2": "d090r|train|d090_FANOUT_DELAY|D3_DEPENDENT_ABORT|r1",
    "Q3": "d090r|train|d090_DEEP_CHAIN|D3_DEPENDENT_ABORT|r1",
    "Q4": "d090r|train|d090_PAIR_RACE|D3_DEPENDENT_ABORT|r1",
}
P07_EXPECTED = [
    (("COMPENSATE", "C", "primary"), "TIMEOUT"),
    (("WAIT",), "WAITED"),
    (("VERIFY", "C"), "PENDING"),
    (("WAIT",), "WAITED"),
    (("WAIT",), "WAITED"),
    (("VERIFY", "C"), "FAILED"),
    (("COMPENSATE", "C", "primary"), "TIMEOUT"),
    (("COMPENSATE", "B", "primary"), "TIMEOUT"),
    (("WAIT",), "WAITED"),
    (("VERIFY", "B"), "PENDING"),
    (("WAIT",), "WAITED"),
    (("WAIT",), "WAITED"),
    (("VERIFY", "B"), "FAILED"),
    (("VERIFY", "C"), "COMPENSATED"),
]
SOURCE_BINDINGS = [
    "experiments/d090_recovery/d090_scenarios.py",
    "experiments/pilot_a3b/dependency_recovery.py",
    "experiments/d090_recovery/d090_experiment.py",
    "experiments/d090_recovery/d090_genome.py",
    "experiments/d090_recovery/d090_policies.py",
    "experiments/d089_recovery/d089_search_experiment.py",
    "experiments/d089_recovery/d089_genome.py",
    "experiments/d089_recovery/d089_policies.py",
    "experiments/d089_recovery/d089_budget.py",
    "experiments/d088_recovery/d088_genome.py",
    "experiments/d088_recovery/d088_policies.py",
    "experiments/pilot_a3b/dependency_genome.py",
    "experiments/pilot_a3b/dependency_policies.py",
]


def probe_panel_sha256() -> str:
    manifest = load_train_manifest(MANIFEST_PATH)
    return sha256_hex(sorted(scenario["scenario_id"] for scenario in manifest["scenarios"]))


def current_runtime() -> Dict[str, str]:
    if os.environ.get("PYTHONHASHSEED") != "0":
        raise RuntimeError("PYTHONHASHSEED=0 is required")
    if platform_module.python_version() != "3.11.9" or np.__version__ != "1.26.4":
        raise RuntimeError("Probe requires CPython 3.11.9 and NumPy 1.26.4")
    if platform_module.system() != "Linux" or platform_module.machine() != "x86_64":
        raise RuntimeError("Probe requires Linux x86_64")
    release = Path("/etc/os-release").read_text(encoding="utf-8")
    if "ID=ubuntu" not in release or "VERSION_ID=\"22.04\"" not in release:
        raise RuntimeError("Probe requires Ubuntu 22.04")
    return {
        "python_version": platform_module.python_version(),
        "numpy_version": np.__version__,
        "platform": "Ubuntu 22.04 LTS x86_64",
        "pythonhashseed": "0",
    }


def build_execution_lock_payload(runtime: Dict[str, str]) -> Dict[str, Any]:
    manifest = load_train_manifest(MANIFEST_PATH)
    protocol_raw = hashlib.sha256(PROTOCOL_PATH.read_bytes()).hexdigest()
    if protocol_raw != EXPECTED_PROTOCOL_RAW:
        raise RuntimeError("R2.3 protocol hash mismatch")
    panel = probe_panel_sha256()
    if panel != EXPECTED_PANEL:
        raise RuntimeError("Probe panel hash mismatch")
    files = SOURCE_BINDINGS + [str(path.relative_to(ROOT)) for path in sorted((ROOT / "experiments" / "d092_recovery").glob("*.py"))]
    source_files = {}
    for relative in files:
        raw = (ROOT / relative).read_bytes()
        source_files[relative] = {
            "raw_sha256": hashlib.sha256(raw).hexdigest(),
            "canonical_sha256": hashlib.sha256(b"\n".join(raw.splitlines())).hexdigest(),
            "git_blob": subprocess.check_output(["git", "hash-object", relative], cwd=ROOT, text=True).strip(),
        }
    probes = probe_typed_genomes()
    return {
        "protocol": "D092-R2.3",
        "protocol_raw_sha256": protocol_raw,
        "manifest_canonical_sha256": EXPECTED_MANIFEST_CANONICAL,
        "manifest_internal_sha256": EXPECTED_MANIFEST_INTERNAL,
        "probe_panel_sha256": panel,
        "scenario_count": 96,
        "planned_episodes": 960,
        "no_cache": True,
        "seed": PROBE_SEED,
        "seed_basis": "evaluate_train_genome existing documented default seed=711",
        "runtime": runtime,
        "source_head": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
        "source_files": source_files,
        "probe_genomes": {name: {"typed": genome.to_dict(), "genome_sha256": genome_sha256(genome)} for name, genome in probes.items()},
        "status": "LOCKED_BEFORE_ROLLOUT",
    }


def write_execution_lock(outdir: Path) -> Path:
    outdir.mkdir(parents=True, exist_ok=True)
    payload = build_execution_lock_payload(current_runtime())
    payload["created_utc"] = datetime.datetime.now(datetime.timezone.utc).isoformat()
    path = outdir / "execution_lock.json"
    path.write_text(json.dumps(payload, ensure_ascii=False, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    return path


def verify_execution_lock(outdir: Path) -> Tuple[Dict[str, Any], str]:
    path = outdir / "execution_lock.json"
    if not path.exists():
        raise RuntimeError("execution lock must exist before the first rollout")
    lock = json.loads(path.read_text(encoding="utf-8"))
    expected = build_execution_lock_payload(current_runtime())
    for key, value in expected.items():
        if key != "source_head" and lock.get(key) != value:
            raise RuntimeError("execution lock mismatch: " + key)
    if not lock.get("created_utc"):
        raise RuntimeError("execution lock timestamp missing")
    return lock, hashlib.sha256(path.read_bytes()).hexdigest()


def _events(report: Dict[str, Any]) -> List[Tuple[Tuple[str, ...], str]]:
    return [(tuple(event["action"]), event["observation"]) for event in report["trace"]]


def _first_difference(first: Dict[str, Any], second: Dict[str, Any]) -> int | None:
    left, right = _events(first), _events(second)
    for index, (a, b) in enumerate(zip(left, right)):
        if a != b:
            return index
    return None if len(left) == len(right) else min(len(left), len(right))


def _before(report: Dict[str, Any], index: int) -> Dict[str, Any]:
    return report["transition_records"][index]["before"]


def _same_before(first: Dict[str, Any], second: Dict[str, Any], index: int) -> bool:
    return _before(first, index) == _before(second, index)


def _action(report: Dict[str, Any], index: int) -> Tuple[str, ...]:
    return tuple(report["trace"][index]["action"])


def _available(genome, view: Dict[str, Any], fallback: bool = False):
    policy = D090Policy(genome)
    return policy._available_or_fallback(view) if fallback else policy._available(view)


def _ordinary_choice(genome, view: Dict[str, Any], available) -> Tuple[str, str]:
    return D088RecoveryPolicy(genome)._priority(view, available)[1:]


def _tight_choice(genome, view: Dict[str, Any], available) -> Tuple[str, str]:
    return D090Policy(genome)._priority(view, available)[1:]


def p07_trace_prefix_valid(report: Dict[str, Any]) -> bool:
    if len(report["trace"]) < 14 or len(report["transition_records"]) < 14:
        return False
    if _events(report)[:14] != P07_EXPECTED:
        return False
    after7 = report["transition_records"][6]["after"]
    after14 = report["transition_records"][13]["after"]
    return (
        after7["tools"]["C"]["state"] == "COMPENSATED"
        and report["transition_records"][6]["observation"] == "TIMEOUT"
        and after14["decision_count"] == 14
        and after14["budget_remaining"] == 10
        and after14["tools"]["C"]["state"] == "COMPENSATED"
        and not any(route["pending"] for route in after14["tools"]["C"]["routes"])
        and after14["tools"]["B"]["routes"][0]["last_receipt"] == "FAILED"
    )


def _complete_probe(rows: Sequence[Dict[str, Any]]) -> bool:
    return len(rows) == 96 and all(row["report"]["illegal_state_transition_count"] == 0 for row in rows)


def evaluate_probe_criteria(reports: Dict[str, List[Dict[str, Any]]]) -> Dict[str, Dict[str, Any]]:
    required = {f"P{i:02d}" for i in range(10)}
    if set(reports) != required:
        raise ValueError("Probe requires exactly P00-P09")
    result = {}

    def row(probe: str, anchor: str) -> Dict[str, Any]:
        matches = [item for item in reports[probe] if item["report"]["scenario_id"] == ANCHORS[anchor]]
        if len(matches) != 1:
            raise ValueError("missing probe anchor: " + probe + "/" + anchor)
        return matches[0]["report"]

    def finish(probe: str, checks: Dict[str, bool], details: Dict[str, Any]) -> None:
        complete = _complete_probe(reports[probe])
        checks = {"complete_96_and_legal_monitor": complete, **checks}
        result[probe] = {
            "episode_count": len(reports[probe]),
            "checks": checks,
            "details": details,
            "status": "PASS" if all(checks.values()) else "HOLD",
        }

    for probe in ("P00", "P01", "P02", "P03", "P04", "P05", "P06", "P07", "P08", "P09"):
        if probe == "P00":
            finish(probe, {}, {"baseline": "complete 96 rows; no performance gate"})
            continue
        if probe in ("P01", "P02"):
            p00, p01, p02 = row("P00", "Q0"), row("P01", "Q0"), row("P02", "Q0")
            first = next(event for event in p00["trace"] if event["action"][0] == "COMPENSATE")
            other = p01 if probe == "P01" else p02
            first_other = next(event for event in other["trace"] if event["action"][0] == "COMPENSATE")
            q0_ok = (
                first["action"][0] == "COMPENSATE" and first["action"][1] in ("A", "B") and first["action"][2] == "alternate"
                and first_other["action"] == ["COMPENSATE", "C", "primary"]
                and _first_difference(p00, other) is not None
            )
            b1, b2 = row("P01", "Q0b"), row("P02", "Q0b")
            index = _first_difference(b1, b2)
            q0b_ok = False
            if index is not None:
                before = _before(b1, index)
                q0b_ok = (
                    _same_before(b1, b2, index)
                    and _action(b1, index) == ("COMPENSATE", "C", "primary")
                    and _action(b2, index) == ("WAIT",)
                    and any(route["pending"] for tool in ("A", "B") for route in before["tools"][tool]["routes"])
                    and _first_difference(b1, b2) is not None
                )
            finish(probe, {"q0_alternate_vs_primary": q0_ok, "q0b_off_vs_filter": q0b_ok}, {"q0b_first_difference": index})
            continue
        if probe == "P03":
            enabled, disabled = row("P01", "Q1"), row("P03", "Q1")
            before = enabled["transition_records"][0]["before"]
            normal = _available(probe_typed_genomes()["P01"].to_d090(), before)
            fallback = D090Policy(probe_typed_genomes()["P01"].to_d090())._fallback_available(before)
            fallback_set = {(tool, route["name"]) for tool, route in fallback}
            ok = (
                not normal
                and fallback_set == {("A", "alternate"), ("B", "alternate"), ("C", "alternate")}
                and _action(enabled, 0)[0] == "COMPENSATE" and _action(enabled, 0)[2] == "alternate"
                and _action(disabled, 0) == ("ESCALATE",)
                and _first_difference(enabled, disabled) == 0
            )
            finish(probe, {"q1_initial_fallback": ok}, {"fallback_candidates": sorted(fallback_set)})
            continue
        if probe == "P04":
            base, disabled = row("P00", "Q2"), row("P04", "Q2")
            index = _first_difference(base, disabled)
            ok = False
            if index is not None:
                before = _before(base, index)
                available = _available(probe_typed_genomes()["P00"].to_d090(), before, fallback=True)
                can_dispatch = D090Policy(probe_typed_genomes()["P00"].to_d090())._can_dispatch_more(before)
                active = sum(tool["state"] in ("COMMITTED", "PARTIAL") for tool in before["tools"].values())
                ok = (
                    _same_before(base, disabled, index)
                    and active > public_min_harm(before)
                    and bool(available) and can_dispatch
                    and _action(base, index)[0] not in ("ESCALATE", "STOP_SAFE")
                    and _action(disabled, index) in (("ESCALATE",), ("STOP_SAFE",))
                )
            finish(probe, {"q2_completion_override": ok}, {"first_difference": index})
            continue
        if probe in ("P05", "P06"):
            other_probe = probe
            base, other = row("P00", "Q3"), row(other_probe, "Q3")
            index = _first_difference(base, other)
            ok = False
            if index is not None:
                before = _before(base, index)
                available = _available(probe_typed_genomes()["P00"].to_d090(), before)
                if len(available) >= 2:
                    ordinary = _ordinary_choice(probe_typed_genomes()["P00"].to_d090(), before, available)
                    tight = _tight_choice(probe_typed_genomes()["P00"].to_d090(), before, available)
                    budget = before["budget_remaining"]
                    window = budget <= 8 if probe == "P05" else 4 < budget <= 8
                    ok = (
                        _same_before(base, other, index)
                        and window and ordinary != tight
                        and _action(base, index)[1:] == tight
                        and _action(other, index)[1:] == ordinary
                    )
            finish(probe, {"q3_harm_priority_window": ok}, {"first_difference": index})
            continue
        if probe == "P07":
            p06, p07 = row("P06", "Q3"), row("P07", "Q3")
            prefix_ok = p07_trace_prefix_valid(p06) and p07_trace_prefix_valid(p07)
            before = p06["transition_records"][13]["after"] if len(p06["transition_records"]) >= 14 else None
            branch_ok = False
            if before is not None:
                available = _available(probe_typed_genomes()["P06"].to_d090(), before)
                if available:
                    ordinary = _ordinary_choice(probe_typed_genomes()["P06"].to_d090(), before, available)
                    tight = _tight_choice(probe_typed_genomes()["P07"].to_d090(), before, available)
                    index = 14
                    branch_ok = (
                        len(p06["trace"]) > 14 and len(p07["trace"]) > 14
                        and before["budget_remaining"] == 10
                        and before["tools"]["C"]["state"] == "COMPENSATED"
                        and _action(p06, index)[1:] == ordinary == ("B", "primary")
                        and _action(p07, index)[1:] == tight == ("B", "alternate")
                        and _first_difference(p06, p07) == 14
                    )
            finish(probe, {"q3_exact_14_prefix": prefix_ok, "q3_budget_10_branch": branch_ok}, {"first_difference": _first_difference(p06, p07)})
            continue
        if probe in ("P08", "P09"):
            base, other = row("P00", "Q4"), row(probe, "Q4")
            index = _first_difference(base, other)
            ok = False
            if index is not None:
                before = _before(base, index)
                available = _available(probe_typed_genomes()["P00"].to_d090(), before)
                prior = base["trace"][:index]
                last_dispatch = max((i for i, event in enumerate(prior) if event["action"][0] == "COMPENSATE"), default=None)
                elapsed = 0 if last_dispatch is None else sum(event["action"][0] == "WAIT" for event in prior[last_dispatch + 1:])
                no_pending_verify = True if last_dispatch is None else not any(event["action"][0] == "VERIFY" and event["observation"] == "PENDING" for event in prior[last_dispatch + 1:])
                pending = any(route["pending"] for tool in before["tools"].values() for route in tool["routes"])
                if probe == "P08":
                    expected = elapsed == 0 and _action(base, index) == ("WAIT",) and _action(other, index)[0] == "VERIFY"
                else:
                    expected = elapsed == 1 and _action(base, index)[0] == "VERIFY" and _action(other, index) == ("WAIT",)
                ok = (
                    _same_before(base, other, index)
                    and pending and not available and no_pending_verify and expected
                )
            finish(probe, {"q4_delay_probe_cadence": ok}, {"first_difference": index})
    return result


def _episode_hashes(report: Dict[str, Any]) -> Dict[str, str]:
    trace = sha256_hex(report["trace"])
    outcome_payload = {key: value for key, value in report.items() if key not in ("trace", "transition_records", "attempt_records", "adapter_events", "episode_reference")}
    outcome = sha256_hex(outcome_payload)
    joint = sha256_hex({"episode_reference": report["episode_reference"], "outcome": outcome, "trace": trace})
    return {"trace_sha256": trace, "outcome_sha256": outcome, "joint_sha256": joint}


def execute_probe(outdir: Path) -> Dict[str, Any]:
    outdir.mkdir(parents=True, exist_ok=True)
    lock, lock_sha = verify_execution_lock(outdir)
    manifest = load_train_manifest(MANIFEST_PATH)
    probes = probe_typed_genomes()
    reports: Dict[str, List[Dict[str, Any]]] = {name: [] for name in probes}
    episodes_path = outdir / "episodes.jsonl"
    started = time.perf_counter()
    episode_ordinal = 0
    try:
        with episodes_path.open("w", encoding="utf-8", newline="\n") as output:
            for probe_index, (probe, genome) in enumerate(probes.items()):
                for scenario in manifest["scenarios"]:
                    report = run_guarded_episode(
                        D090Policy(genome.to_d090()), scenario,
                        seed=PROBE_SEED, unique_ordinal=probe_index,
                        typed_genome_sha256=genome_sha256(genome),
                    )
                    item = {
                        "episode_ordinal": episode_ordinal,
                        "probe_id": probe,
                        "typed_genome": genome.to_dict(),
                        "genome_sha256": genome_sha256(genome),
                        "scenario_id": scenario["scenario_id"],
                        "episode_hashes": _episode_hashes(report),
                        "report": report,
                    }
                    output.write(json.dumps(item, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False) + "\n")
                    reports[probe].append(item)
                    episode_ordinal += 1
        criteria = evaluate_probe_criteria(reports)
    except Exception as error:
        failure = {
            "status": "INVALID",
            "error_type": type(error).__name__,
            "error": str(error),
            "completed_episodes": episode_ordinal,
            "execution_lock_sha256": lock_sha,
            "episodes_jsonl_sha256": hashlib.sha256(episodes_path.read_bytes()).hexdigest() if episodes_path.exists() else None,
        }
        (outdir / "failure.json").write_text(json.dumps(failure, ensure_ascii=False, sort_keys=True, indent=2) + "\n", encoding="utf-8")
        raise
    elapsed = time.perf_counter() - started
    all_pass = all(item["status"] == "PASS" for item in criteria.values())
    summary = {
        "protocol": "D092-R2.3",
        "status": "PASS" if all_pass else "HOLD",
        "overall_pass": all_pass,
        "seed": PROBE_SEED,
        "episode_count": episode_ordinal,
        "expected_episode_count": 960,
        "cache_hits": 0,
        "execution_lock_sha256": lock_sha,
        "execution_lock_created_utc": lock["created_utc"],
        "runtime": lock["runtime"],
        "criteria": criteria,
        "hard_constraints": {
            field: sum(item["report"].get(field, 0) for rows in reports.values() for item in rows)
            for field in ("invalid_action_count", "unauthorized_action_count", "illegal_state_transition_count", "pending_count", "duplicate_count", "runtime_abort_count")
        },
        "compensation_attempts": sum(len(item["report"]["attempt_records"]) for rows in reports.values() for item in rows),
        "elapsed_seconds": elapsed,
        "episodes_jsonl_sha256": hashlib.sha256(episodes_path.read_bytes()).hexdigest(),
        "episodes_jsonl_bytes": episodes_path.stat().st_size,
        "scientific_claim": "Probe checks mechanism identifiability only; not algorithm performance evidence",
    }
    (outdir / "probe_summary.json").write_text(json.dumps(summary, ensure_ascii=False, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    lines = [
        "# D-092 960 Probe result",
        "",
        f"Status: **{summary['status']}**; episodes={episode_ordinal}/960; seed=711; cache_hits=0.",
        "",
        "| Probe | Episodes | Status | Passed checks | Total checks |",
        "|---|---:|---|---:|---:|",
    ]
    for probe, item in criteria.items():
        passed = sum(item["checks"].values())
        lines.append(f"| {probe} | {item['episode_count']} | {item['status']} | {passed} | {len(item['checks'])} |")
    lines += ["", "Probe 只验证编码/行为可辨识性，不构成算法性能提升证据。", ""]
    (outdir / "probe_report.md").write_text("\n".join(lines), encoding="utf-8")
    return summary
