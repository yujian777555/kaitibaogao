"""Independent Pilot A-3 recompute and pre-registered gate audit.

Reads the raw episode CSV (and optionally the simulator JSON for a parity
check), recomputes every reported metric from the episode rows alone, applies
the exact pre-registered gate from 47_PILOT_A3_PROTOCOL.md, and writes a
machine-readable audit report. This script does not import pilot_a3.py, so the
aggregation and gate logic are implemented independently of the simulator's
own summary code.

Usage:
    python experiments/pilot_a_recovery/recompute_a3_audit.py \
        --csv experiments/pilot_a_recovery/pilot_a3_episodes.csv \
        --json experiments/pilot_a_recovery/pilot_a3_results.json \
        --out experiments/pilot_a_recovery/a3_recompute_report.json
"""
import argparse
import csv
import hashlib
import json
import random
from collections import defaultdict
from pathlib import Path

EXPECTED_POLICIES = (
    "blind_retry",
    "verify_then_retry",
    "fixed_wait_verify",
    "conservative_escalation",
    "contract_aware",
    "saga_aware",
    "oracle_diagnostic",
)
EXPECTED_EPISODES_PER_POLICY = 954
EXPECTED_SPLIT_COUNTS = {"train": 144, "validation": 120, "heldout": 690}
HELDOUT_SLICES = ("heldout_task_shift", "heldout_fault_shift", "heldout_joint_shift")
BINARY_METRICS = (
    "task_success",
    "safe_resolution",
    "safe",
    "invariant_violation",
    "duplicate_side_effect",
    "unresolved",
    "escalated",
    "compensation_failure",
)
MEAN_METRICS = ("action_count", "active_effects", "steps_committed", "compensation_failures")


def sha256(path):
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def rate(rows, key):
    return round(sum(int(r[key]) for r in rows) / len(rows), 6) if rows else None


def mean(rows, key):
    return round(sum(float(r[key]) for r in rows) / len(rows), 6) if rows else None


def summarize(rows):
    out = {"episodes": len(rows)}
    for key in BINARY_METRICS:
        out[key] = rate(rows, key)
    for key in MEAN_METRICS:
        out["mean_" + key if not key.startswith("compensation_failures") else key] = mean(rows, key)
    return out


def heldout_split_of(row):
    return row["split"]


def paired_cluster_bootstrap(rows, policy_a, policy_b, metric="task_success", reps=2000, seed=20261105):
    """Paired cluster bootstrap over task-family x fault-composition clusters."""
    by_scenario = defaultdict(dict)
    scenario_meta = {}
    for row in rows:
        by_scenario[row["scenario_id"]][row["policy"]] = int(row[metric])
        scenario_meta[row["scenario_id"]] = (row["task_family"], row["fault_composition"])
    clusters = defaultdict(list)
    for scenario_id, values in by_scenario.items():
        if policy_a in values and policy_b in values:
            clusters[scenario_meta[scenario_id]].append(values[policy_a] - values[policy_b])
    keys = sorted(clusters)
    if not keys:
        return {"mean_difference": None, "ci95": [None, None], "clusters": 0}
    all_values = [v for key in keys for v in clusters[key]]
    mean_difference = sum(all_values) / len(all_values)
    rng = random.Random(seed)
    estimates = []
    for _ in range(reps):
        sampled_keys = [rng.choice(keys) for _ in keys]
        sample = [v for key in sampled_keys for v in clusters[key]]
        estimates.append(sum(sample) / len(sample))
    estimates.sort()
    low = estimates[int(0.025 * (len(estimates) - 1))]
    high = estimates[int(0.975 * (len(estimates) - 1))]
    return {
        "mean_difference": round(mean_difference, 6),
        "ci95": [round(low, 6), round(high, 6)],
        "clusters": len(keys),
        "cluster_sizes": {f"{k[0]}|{k[1]}": len(clusters[k]) for k in keys},
        "bootstrap_reps": reps,
        "seed": seed,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--csv", required=True)
    parser.add_argument("--json", default=None)
    parser.add_argument("--out", default=None)
    args = parser.parse_args()

    with open(args.csv, newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    for row in rows:
        for key in BINARY_METRICS:
            row[key] = int(row[key])
        for key in MEAN_METRICS:
            row[key] = float(row[key])

    report = {
        "source_csv": args.csv,
        "source_csv_sha256": sha256(args.csv),
        "total_rows": len(rows),
    }

    # --- structural checks -------------------------------------------------
    problems = []
    policies = sorted({r["policy"] for r in rows})
    if tuple(p for p in EXPECTED_POLICIES if p in policies) != EXPECTED_POLICIES or len(policies) != 7:
        problems.append(f"policy set mismatch: {policies}")
    counts = defaultdict(int)
    split_counts = defaultdict(lambda: defaultdict(int))
    keys_seen = set()
    dup_keys = []
    scenario_meta = defaultdict(dict)
    for row in rows:
        counts[row["policy"]] += 1
        if row["split"].startswith("validation"):
            fold = "validation"
        elif row["split"].startswith("heldout_"):
            fold = "heldout"
        else:
            fold = row["split"]
        split_counts[row["policy"]][fold] += 1
        key = (row["scenario_id"], row["policy"])
        if key in keys_seen:
            dup_keys.append(key)
        keys_seen.add(key)
        scenario_meta[row["scenario_id"]][row["policy"]] = (row["seed"], row["fault_vector"], row["tool_vector"])
    for policy in EXPECTED_POLICIES:
        if counts[policy] != EXPECTED_EPISODES_PER_POLICY:
            problems.append(f"{policy}: {counts[policy]} rows, expected {EXPECTED_EPISODES_PER_POLICY}")
        for split, expected in EXPECTED_SPLIT_COUNTS.items():
            if split_counts[policy][split] != expected:
                problems.append(f"{policy}/{split}: {split_counts[policy][split]} rows, expected {expected}")
    if dup_keys:
        problems.append(f"{len(dup_keys)} duplicate (scenario_id, policy) keys, e.g. {dup_keys[:3]}")

    paired = True
    for scenario_id, per_policy in scenario_meta.items():
        if set(per_policy) != set(EXPECTED_POLICIES):
            problems.append(f"scenario {scenario_id}: policies {sorted(per_policy)} != all 7")
            paired = False
            continue
        sigs = set(per_policy.values())
        if len(sigs) != 1:
            problems.append(f"scenario {scenario_id}: seed/fault/tool vector not identical across policies")
            paired = False

    report["structural_checks"] = {
        "rows_per_policy": dict(counts),
        "split_counts_per_policy": {p: dict(split_counts[p]) for p in sorted(split_counts)},
        "unique_scenario_ids": len(scenario_meta),
        "duplicate_policy_scenario_keys": len(dup_keys),
        "identical_seed_and_fault_realization_across_policies": paired,
        "problems": problems,
    }

    # --- independent metric recompute ------------------------------------
    by_policy = defaultdict(list)
    by_policy_split = defaultdict(list)
    for row in rows:
        by_policy[row["policy"]].append(row)
        by_policy_split[(row["policy"], row["split"])].append(row)
        if row["split"].startswith("validation"):
            by_policy_split[(row["policy"], "validation")].append(row)
        if row["split"].startswith("heldout_"):
            by_policy_split[(row["policy"], "heldout_all")].append(row)

    recomputed = {}
    split_keys = (
        "train",
        "validation",
        "validation_task_shift",
        "validation_fault_shift",
        "heldout_task_shift",
        "heldout_fault_shift",
        "heldout_joint_shift",
        "heldout_all",
    )
    for policy in EXPECTED_POLICIES:
        recomputed[policy] = {}
        for key in split_keys:
            group = by_policy_split.get((policy, key), [])
            if group:
                recomputed[policy][key] = summarize(group)

    # worst-group over held-out task-family x fault-composition
    worst = defaultdict(list)
    for row in rows:
        if row["split"].startswith("heldout_"):
            worst[(row["policy"], row["task_family"], row["fault_composition"])].append(row)
    worst_groups = {
        f"{p}|{t}|{c}": summarize(g) for (p, t, c), g in sorted(worst.items())
    }

    # paired cluster bootstrap oracle - saga on held-out
    heldout_rows = [r for r in rows if r["split"].startswith("heldout_")]
    bootstrap = paired_cluster_bootstrap(heldout_rows, "oracle_diagnostic", "saga_aware")
    bootstrap_seed42 = paired_cluster_bootstrap(
        heldout_rows, "oracle_diagnostic", "saga_aware", seed=42
    )

    report["recomputed"] = recomputed
    report["heldout_worst_groups"] = worst_groups
    report["paired_bootstrap_oracle_minus_saga_success"] = bootstrap
    report["paired_bootstrap_sensitivity_seed42"] = bootstrap_seed42

    # --- JSON parity ------------------------------------------------------
    parity = {"checked": False, "mismatches": []}
    if args.json:
        with open(args.json, encoding="utf-8") as handle:
            payload = json.load(handle)
        parity["checked"] = True
        parity["source_json_sha256"] = sha256(args.json)
        for policy in EXPECTED_POLICIES:
            for key, js_summary in payload.get("summary", {}).get(policy, {}).items():
                ours = recomputed.get(policy, {}).get(key)
                if ours is None:
                    parity["mismatches"].append(f"missing recomputed {policy}/{key}")
                    continue
                js_pairs = {
                    "task_success": js_summary.get("task_success"),
                    "safe_resolution": js_summary.get("safe_resolution"),
                    "safe": js_summary.get("safe"),
                    "invariant_violation": js_summary.get("invariant_violation"),
                    "duplicate_side_effect": js_summary.get("duplicate_side_effect"),
                    "unresolved": js_summary.get("unresolved"),
                    "escalated": js_summary.get("escalated"),
                    "compensation_failure": js_summary.get("compensation_failure"),
                    "mean_action_count": js_summary.get("mean_action_count"),
                    "episodes": js_summary.get("episodes"),
                }
                for name, js_value in js_pairs.items():
                    our_value = ours.get(name)
                    if name == "episodes":
                        if js_value != our_value:
                            parity["mismatches"].append(f"{policy}/{key}/{name}: json={js_value} recompute={our_value}")
                    else:
                        if js_value is None or abs(round(our_value, 4) - js_value) > 1e-9:
                            parity["mismatches"].append(
                                f"{policy}/{key}/{name}: json={js_value} recompute={round(our_value, 4)}"
                            )
        js_gate = payload.get("gate", {})
        parity["json_gate_decision"] = js_gate.get("decision")
    report["json_parity"] = parity

    # --- pre-registered gate (47_PILOT_A3_PROTOCOL.md, verbatim) -----------
    saga = recomputed["saga_aware"]
    oracle = recomputed["oracle_diagnostic"]
    slice_violations = {
        slice_name: saga[slice_name]["invariant_violation"] for slice_name in HELDOUT_SLICES
    }
    zero_violation_all_slices = all(v == 0 for v in slice_violations.values())
    success_gap = round(oracle["heldout_all"]["task_success"] - saga["heldout_all"]["task_success"], 6)
    oracle_actions = oracle["heldout_all"]["mean_action_count"]
    saga_actions = saga["heldout_all"]["mean_action_count"]
    action_gap = round((saga_actions - oracle_actions) / oracle_actions, 6) if oracle_actions else None
    ci_low = bootstrap["ci95"][0]

    if not zero_violation_all_slices:
        gate = "HOLD_SAFETY_FAILURE"
    elif success_gap >= 0.05 and ci_low is not None and ci_low > 0:
        gate = "CONDITIONAL_GO_PILOT_B"
    elif success_gap <= 0.02 and action_gap is not None and action_gap <= 0.10:
        gate = "NO_GO_INSUFFICIENT_OPTIMIZATION_HEADROOM"
    else:
        gate = "HOLD_REVIEW_FAILURE_BOUNDARIES"

    report["gate"] = {
        "protocol": "47_PILOT_A3_PROTOCOL.md section 6, applied verbatim",
        "saga_invariant_violation_per_heldout_slice": slice_violations,
        "saga_zero_violation_all_heldout_slices": zero_violation_all_slices,
        "oracle_minus_saga_heldout_task_success_gap": success_gap,
        "gap_threshold_for_go": 0.05,
        "no_go_gap_threshold": 0.02,
        "saga_minus_oracle_action_cost_relative": action_gap,
        "no_go_action_cost_threshold": 0.10,
        "bootstrap_ci95_lower_bound": ci_low,
        "bootstrap_ci95": bootstrap["ci95"],
        "decision": gate,
    }

    text = json.dumps(report, indent=2, ensure_ascii=False) + "\n"
    if args.out:
        Path(args.out).write_text(text, encoding="utf-8")
    print(text)


if __name__ == "__main__":
    main()
