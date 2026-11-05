"""Pilot A-2: multi-tool, contract-aware recovery benchmark.

Run:
  python experiments/pilot_a2_multitool/pilot_a2.py --output-dir experiments/pilot_a2_multitool/results

The benchmark is deterministic for a fixed seed. Policies only receive Env.observe()
fields. The oracle is explicitly diagnostic and may inspect hidden simulator state.
"""
from __future__ import annotations
import argparse
import csv
import json
import random
from collections import defaultdict
from pathlib import Path

TOOLS = {
    "inventory": {"idempotency": "native", "compensable": True,
                  "consistency": "strong", "max_visibility_delay": 0},
    "order": {"idempotency": "keyed", "compensable": True,
              "consistency": "eventual", "max_visibility_delay": 3},
    "calendar": {"idempotency": "none", "compensable": True,
                 "consistency": "eventual", "max_visibility_delay": 5},
    "ledger": {"idempotency": "native", "compensable": False,
               "consistency": "strong", "max_visibility_delay": 0},
}
TASK_FAMILY = {
    "inventory": "reserve_stock",
    "order": "create_order",
    "calendar": "book_appointment",
    "ledger": "post_ledger_entry",
}
PROFILES = (
    "timeout_before", "timeout_after", "partial_commit",
    "delayed_commit_timeout", "timeout_rate_before", "timeout_rate_after",
    "partial_delayed_rate", "schema_before", "schema_rate_before",
    "permission_before", "permission_timeout_before",
    "partial_timeout_delayed", "partial_compensation_unavailable",
)
POLICIES = (
    "blind_retry", "verify_then_retry", "idempotency_only",
    "conservative_escalate", "contract_basic", "contract_bounded",
    "contract_optimized", "oracle_upper_bound",
)
SEEDS = range(100)
METRICS = (
    "task_success", "safe_resolution", "duplicate_side_effect",
    "invariant_violation", "unresolved", "escalated", "compensated",
    "tool_actions", "wait_units",
)

def _rng(tool: str, profile: str, seed: int) -> random.Random:
    ti = list(TOOLS).index(tool)
    pi = list(PROFILES).index(profile)
    return random.Random((seed + 1) * 1009 + ti * 101 + pi * 13)

def make_episode(tool: str, profile: str, seed: int) -> dict:
    rng = _rng(tool, profile, seed)
    contract = dict(TOOLS[tool])
    outcome, effects = "NONE", 0
    signals = []
    delay, retry_after = 0, 0
    schema_valid, permission = True, True
    compensation_available = True

    def visibility_delay() -> int:
        if contract["consistency"] != "eventual":
            return 0
        return rng.randint(1, contract["max_visibility_delay"])

    if profile == "timeout_before":
        signals = ["TIMEOUT"]
    elif profile == "timeout_after":
        signals, outcome, effects = ["TIMEOUT"], "COMMITTED", 1
    elif profile == "partial_commit":
        signals, outcome, effects = ["PARTIAL_RESPONSE"], "PARTIAL", 1
    elif profile == "delayed_commit_timeout":
        signals, outcome, effects, delay = ["TIMEOUT"], "COMMITTED", 1, visibility_delay()
    elif profile == "timeout_rate_before":
        signals, retry_after = ["TIMEOUT", "RATE_LIMIT"], rng.randint(1, 3)
    elif profile == "timeout_rate_after":
        signals, outcome, effects = ["TIMEOUT", "RATE_LIMIT"], "COMMITTED", 1
        retry_after, delay = rng.randint(1, 3), visibility_delay()
    elif profile == "partial_delayed_rate":
        signals, outcome, effects = ["PARTIAL_RESPONSE", "RATE_LIMIT"], "PARTIAL", 1
        retry_after, delay = rng.randint(1, 3), visibility_delay()
        compensation_available = rng.random() < 0.8
    elif profile == "schema_before":
        signals, schema_valid = ["SCHEMA_VALIDATION"], False
    elif profile == "schema_rate_before":
        signals, schema_valid = ["SCHEMA_VALIDATION", "RATE_LIMIT"], False
        retry_after = rng.randint(1, 3)
    elif profile == "permission_before":
        signals, permission = ["PERMISSION"], False
    elif profile == "permission_timeout_before":
        signals, permission = ["PERMISSION", "TIMEOUT"], False
    elif profile == "partial_timeout_delayed":
        signals, outcome, effects = ["TIMEOUT"], "PARTIAL", 1
        delay = visibility_delay()
    elif profile == "partial_compensation_unavailable":
        signals, outcome, effects = ["PARTIAL_RESPONSE"], "PARTIAL", 1
        compensation_available = False
    else:
        raise ValueError(profile)

    return {
        "tool": tool, "task_family": TASK_FAMILY[tool], "profile": profile,
        "seed": seed, "contract": contract, "signals": tuple(signals),
        "hidden_outcome": outcome, "effects": effects, "visibility_delay": delay,
        "retry_after": retry_after, "schema_valid": schema_valid,
        "permission": permission, "compensation_available": compensation_available,
    }

class Env:
    def __init__(self, spec: dict):
        self.spec = spec
        self.tick = 0
        self.hidden_outcome = spec["hidden_outcome"]
        self.effects = spec["effects"]
        self.violation = False
        self.escalated = False
        self.compensated = False
        self.actions = 0
        self.wait_units = 0

    def observe(self) -> dict:
        # Only public runtime observations and declared tool contracts.
        return {
            "tool": self.spec["tool"],
            "task_family": self.spec["task_family"],
            "contract": dict(self.spec["contract"]),
            "signals": tuple(self.spec["signals"]),
            "schema_valid": self.spec["schema_valid"],
            "permission": self.spec["permission"],
            "retry_after": self.spec["retry_after"],
        }

    def act(self, action: str, duration: int = 0) -> str:
        self.actions += 1
        s = self.spec
        if action == "WAIT":
            duration = max(0, int(duration))
            self.tick += duration
            self.wait_units += duration
            return "WAITED"
        if action == "VERIFY":
            if self.tick < s["visibility_delay"]:
                return "NOT_FOUND"
            return "NOT_FOUND" if self.hidden_outcome == "NONE" else self.hidden_outcome
        if action == "REPAIR_SCHEMA":
            s["schema_valid"] = True
            return "SCHEMA_REPAIRED"
        if action == "ESCALATE":
            self.escalated = True
            return "ESCALATED"
        if action == "COMPENSATE":
            if (self.hidden_outcome == "PARTIAL"
                    and s["contract"]["compensable"]
                    and s["compensation_available"]):
                self.hidden_outcome, self.effects = "NONE", 0
                self.compensated = True
                return "COMPENSATED"
            return "COMPENSATION_UNAVAILABLE"
        if action in ("RETRY", "RETRY_WITH_KEY"):
            if not s["permission"]:
                return "PERMISSION_DENIED"
            if not s["schema_valid"]:
                return "SCHEMA_REJECTED"
            if self.tick < s["retry_after"]:
                return "RATE_LIMITED"
            idem = s["contract"]["idempotency"]
            deduplicates = ((idem == "native" and action == "RETRY")
                            or (idem == "keyed" and action == "RETRY_WITH_KEY"))
            if self.effects > 0:
                if deduplicates:
                    return "ALREADY_COMMITTED" if self.hidden_outcome == "COMMITTED" else "ALREADY_PARTIAL"
                self.effects += 1
                self.violation = True
                return "DUPLICATE"
            self.hidden_outcome, self.effects = "COMMITTED", 1
            return "COMMITTED"
        raise ValueError(f"Unknown action: {action}")

    def result(self) -> dict:
        success = (self.hidden_outcome == "COMMITTED"
                   and self.effects == 1 and not self.violation)
        return {
            "task_success": int(success),
            "safe_resolution": int(success or self.escalated),
            "duplicate_side_effect": int(self.violation),
            "invariant_violation": int(self.violation),
            "unresolved": int(not success and not self.escalated),
            "escalated": int(self.escalated),
            "compensated": int(self.compensated),
            "tool_actions": self.actions,
            "wait_units": self.wait_units,
        }

def run_policy(spec: dict, policy: str) -> dict:
    env = Env(spec)
    obs = env.observe()
    signals = set(obs["signals"])
    contract = obs["contract"]

    def retry() -> str:
        action = "RETRY_WITH_KEY" if contract["idempotency"] == "keyed" else "RETRY"
        return env.act(action)

    def resolve_partial() -> None:
        status = env.act("VERIFY")
        if status == "PARTIAL":
            if contract["compensable"]:
                if env.act("COMPENSATE") == "COMPENSATED":
                    retry()
                else:
                    env.act("ESCALATE")
            else:
                env.act("ESCALATE")
        elif status == "NOT_FOUND":
            retry()

    if policy == "blind_retry":
        env.act("RETRY")
    elif policy == "verify_then_retry":
        status = env.act("VERIFY")
        if status == "NOT_FOUND":
            env.act("RETRY")
        elif status == "PARTIAL":
            if env.act("COMPENSATE") == "COMPENSATED":
                retry()
    elif policy == "idempotency_only":
        if contract["idempotency"] == "none":
            env.act("ESCALATE")
        else:
            retry()
    elif policy == "conservative_escalate":
        env.act("ESCALATE")
    elif policy in ("contract_basic", "contract_bounded", "contract_optimized"):
        if not obs["permission"]:
            env.act("ESCALATE")
        else:
            if not obs["schema_valid"]:
                env.act("REPAIR_SCHEMA")
            if "RATE_LIMIT" in signals:
                env.act("WAIT", obs["retry_after"])

            if policy == "contract_optimized" and "TIMEOUT" in signals:
                if contract["idempotency"] in ("native", "keyed"):
                    retry_result = retry()
                    # The idempotency service returns the prior operation outcome;
                    # this is a public action response, not a hidden simulator read.
                    if retry_result == "ALREADY_PARTIAL":
                        if contract["consistency"] == "eventual":
                            env.act("WAIT", contract["max_visibility_delay"])
                        resolve_partial()
                else:
                    if contract["consistency"] == "eventual":
                        env.act("WAIT", contract["max_visibility_delay"])
                    status = env.act("VERIFY")
                    if status == "PARTIAL":
                        if contract["compensable"] and env.act("COMPENSATE") == "COMPENSATED":
                            retry()
                        else:
                            env.act("ESCALATE")
                    elif status == "NOT_FOUND":
                        retry()
            elif "TIMEOUT" in signals or "PARTIAL_RESPONSE" in signals:
                if policy in ("contract_bounded", "contract_optimized"):
                    if contract["consistency"] == "eventual":
                        env.act("WAIT", contract["max_visibility_delay"])
                status = env.act("VERIFY")
                if status == "COMMITTED":
                    pass
                elif status == "PARTIAL":
                    if contract["compensable"]:
                        if env.act("COMPENSATE") == "COMPENSATED":
                            retry()
                        else:
                            env.act("ESCALATE")
                    else:
                        env.act("ESCALATE")
                elif status == "NOT_FOUND":
                    retry()
            else:
                retry()
    elif policy == "oracle_upper_bound":
        # Diagnostic upper bound only: hidden simulator state is available here.
        if not obs["permission"]:
            env.act("ESCALATE")
        else:
            if not obs["schema_valid"]:
                env.act("REPAIR_SCHEMA")
            if env.tick < obs["retry_after"]:
                env.act("WAIT", obs["retry_after"] - env.tick)
            if env.hidden_outcome == "COMMITTED":
                pass
            elif env.hidden_outcome == "PARTIAL":
                if contract["compensable"] and spec["compensation_available"]:
                    env.act("COMPENSATE")
                    retry()
                else:
                    env.act("ESCALATE")
            else:
                retry()
    else:
        raise ValueError(policy)

    return {
        "policy": policy, "tool": spec["tool"], "task_family": spec["task_family"],
        "fault_profile": spec["profile"], "seed": spec["seed"], **env.result(),
    }

def mean_metrics(rows: list[dict]) -> dict:
    return {m: round(sum(r[m] for r in rows) / len(rows), 6) for m in METRICS}

def bootstrap_paired(rows: list[dict], policy_a: str, policy_b: str,
                     metric: str, seeds: list[int], draws: int = 10000) -> dict:
    by = defaultdict(lambda: defaultdict(list))
    for row in rows:
        if row["seed"] in seeds:
            by[row["seed"]][row["policy"]].append(row[metric])
    diffs = []
    for seed in seeds:
        a = sum(by[seed][policy_a]) / len(by[seed][policy_a])
        b = sum(by[seed][policy_b]) / len(by[seed][policy_b])
        diffs.append(a - b)
    rng = random.Random(20261105 + len(metric) + len(policy_a))
    samples = []
    for _ in range(draws):
        sample = [diffs[rng.randrange(len(diffs))] for _ in diffs]
        samples.append(sum(sample) / len(sample))
    samples.sort()
    return {
        "mean_difference_A_minus_B": round(sum(diffs) / len(diffs), 6),
        "ci95": [round(samples[int(0.025 * draws)], 6),
                 round(samples[min(draws - 1, int(0.975 * draws))], 6)],
        "independent_unit": "seed; paired across policies",
        "n_seeds": len(seeds), "bootstrap_draws": draws,
    }

def run_experiment() -> tuple[list[dict], dict]:
    rows = [
        run_policy(make_episode(tool, profile, seed), policy)
        for policy in POLICIES
        for tool in TOOLS
        for profile in PROFILES
        for seed in SEEDS
    ]
    all_summary = {
        p: mean_metrics([r for r in rows if r["policy"] == p]) for p in POLICIES
    }
    train_seeds, validation_seeds, test_seeds = list(range(40)), list(range(40, 60)), list(range(60, 100))
    heldout_all = [r for r in rows if r["seed"] in test_seeds]
    heldout_tool = [r for r in rows if r["seed"] in test_seeds and r["tool"] == "ledger"]
    split_summary = {
        "train_seed_range": [0, 39], "validation_seed_range": [40, 59],
        "heldout_test_seed_range": [60, 99],
        "heldout_test_all_tools": {
            p: mean_metrics([r for r in heldout_all if r["policy"] == p]) for p in POLICIES
        },
        "heldout_test_ledger_tool": {
            p: mean_metrics([r for r in heldout_tool if r["policy"] == p]) for p in POLICIES
        },
    }
    stats = {
        "heldout_all_tools_success_contract_optimized_vs_contract_bounded":
            bootstrap_paired(heldout_all, "contract_optimized", "contract_bounded",
                             "task_success", test_seeds),
        "heldout_all_tools_actions_contract_optimized_vs_contract_bounded":
            bootstrap_paired(heldout_all, "contract_optimized", "contract_bounded",
                             "tool_actions", test_seeds),
        "heldout_all_tools_success_contract_optimized_vs_oracle":
            bootstrap_paired(heldout_all, "contract_optimized", "oracle_upper_bound",
                             "task_success", test_seeds),
        "heldout_all_tools_actions_contract_optimized_vs_oracle":
            bootstrap_paired(heldout_all, "contract_optimized", "oracle_upper_bound",
                             "tool_actions", test_seeds),
    }
    metadata = {
        "status": "EXPLORATORY_PILOT_A2",
        "total_policy_episodes": len(rows),
        "episodes_per_policy": len(TOOLS) * len(PROFILES) * len(list(SEEDS)),
        "tools": TOOLS, "task_families": TASK_FAMILY, "fault_profiles": list(PROFILES),
        "policies": list(POLICIES),
        "seeds": {"train": [0, 39], "validation": [40, 59], "heldout_test": [60, 99]},
        "heldout_tool": "ledger",
        "oracle_uses_hidden_state": True,
        "policy_observation_fields": [
            "tool", "task_family", "declared_contract", "public_failure_signals",
            "schema_valid", "permission", "retry_after",
        ],
        "no_llm_api": True, "no_a800_training": True, "no_evolutionary_search": True,
        "limitations": [
            "synthetic deterministic simulator; not a real production tool environment",
            "single-operation recovery episodes; no multi-step cross-tool transaction yet",
            "train/validation/test seed ranges are parameter splits, not learned-model splits",
            "ledger is a single held-out tool family; transfer evidence is preliminary",
            "oracle upper bound reads hidden simulator state and is not implementable",
        ],
    }
    summary = {
        "metadata": metadata, "all_episodes": all_summary,
        "split_summary": split_summary, "paired_bootstrap": stats,
    }
    return rows, summary

def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", default="experiments/pilot_a2_multitool/results")
    args = parser.parse_args()
    out = Path(args.output_dir)
    out.mkdir(parents=True, exist_ok=True)
    rows, summary = run_experiment()
    with (out / "summary.json").open("w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)
    with (out / "episodes.csv").open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    print(json.dumps(summary, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main()
