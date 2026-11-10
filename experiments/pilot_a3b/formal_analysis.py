"""R4 formal family-level primary analysis.

This module consumes an explicit frozen primary roster and an episode
ledger. It is intentionally independent of the historical D-064-B diagnostic
builder, which remains a six-family diagnostic re-analysis.

The production confirmatory unit is the task family. For each expected
scenario and optimizer seed, AB and NSGA-II are paired; seeds are averaged
within scenario, scenarios within composition, compositions within family,
and family means receive equal weight.

Only synthetic fixtures are used while this module is being developed. The
real locked Test payload must not be opened before the separately approved
one-time final-evaluation gate.
"""
from __future__ import annotations

from collections import defaultdict
from statistics import fmean

from power_hierarchical import student_t_summary

ANALYSIS_VERSION = "d064-r4-family-primary-v1"
PRIMARY_METHODS = ("AB", "nsga2")
PRIMARY_LABELS = frozenset(("R1", "R2"))
DEFAULT_MIN_FAMILIES = 34
DEFAULT_COMPOSITIONS_PER_FAMILY = 5


def _nonempty_text(value, field):
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field} must be a non-empty string")
    return value


def _validate_roster(expected_roster, analysis_split, compositions_per_family):
    if not isinstance(expected_roster, (list, tuple)) or not expected_roster:
        raise ValueError("frozen expected roster must be a non-empty sequence")

    scenario_meta = {}
    family_compositions = defaultdict(set)
    composition_scenarios = defaultdict(list)

    for item in expected_roster:
        sid = _nonempty_text(item.get("scenario_id"), "scenario_id")
        family = _nonempty_text(item.get("family_id"), "family_id")
        composition = _nonempty_text(item.get("composition_id"), "composition_id")
        label = item.get("label")
        split = item.get("split")
        if label not in PRIMARY_LABELS:
            raise ValueError(f"primary roster contains non-primary label for {sid}")
        if split != analysis_split:
            raise ValueError(f"roster split mismatch for {sid}")
        if sid in scenario_meta:
            raise ValueError(f"duplicate scenario in frozen roster: {sid}")
        scenario_meta[sid] = (family, composition, label)
        family_compositions[family].add(composition)
        composition_scenarios[(family, composition)].append(sid)

    for family, compositions in family_compositions.items():
        if len(compositions) != compositions_per_family:
            raise ValueError(
                f"family {family} must have exactly {compositions_per_family} "
                "primary compositions in frozen roster"
            )

    return scenario_meta, family_compositions, composition_scenarios


def analyze_primary_endpoint(
    run_rows,
    expected_roster,
    expected_optimizer_seeds,
    technical_missing=None,
    *,
    analysis_split="test",
    min_families=DEFAULT_MIN_FAMILIES,
    compositions_per_family=DEFAULT_COMPOSITIONS_PER_FAMILY,
    method_a="AB",
    method_b="nsga2",
):
    """Validate a paired episode ledger and compute family-equal paired effect.

    expected_roster contains one record per scenario with scenario_id,
    family_id, composition_id, label, and split. The five primary compositions
    per family must be frozen before outcomes are observed.

    technical_missing may contain only explicit infrastructure failures with
    method/seed/scenario_id/category/reason. Missing rows without such a
    record fail closed. A composition with any missing paired run is invalid;
    no seed or composition is replaced. A family with fewer than the frozen
    five complete compositions is recorded as lost.

    For fewer than min_families complete families, descriptive family means
    are returned but confirmatory Student-t inference is withheld.
    """
    if min_families < 2:
        raise ValueError("min_families must be at least two")
    if compositions_per_family < 1:
        raise ValueError("compositions_per_family must be positive")

    seeds = tuple(expected_optimizer_seeds)
    if not seeds or len(set(seeds)) != len(seeds):
        raise ValueError("expected optimizer seeds must be non-empty and unique")

    scenario_meta, family_compositions, composition_scenarios = _validate_roster(
        expected_roster, analysis_split, compositions_per_family
    )
    families = sorted(family_compositions)
    if not method_a or not method_b or method_a == method_b:
        raise ValueError("contrast requires two distinct method names")
    pair_methods = (method_a, method_b)
    expected_keys = {
        (method, seed, sid)
        for method in pair_methods
        for seed in seeds
        for sid in scenario_meta
    }

    observed = {}
    behavioural_failure_count = 0
    for row in run_rows:
        if not isinstance(row, dict):
            raise ValueError("run ledger rows must be objects")
        sid = row.get("scenario_id")
        if sid not in scenario_meta:
            raise ValueError(f"run row outside frozen roster: {sid}")
        if row.get("split") != analysis_split:
            raise ValueError(f"run split mismatch for {sid}")
        method = row.get("method")
        if method not in pair_methods:
            continue
        seed = row.get("seed")
        if seed not in seeds:
            raise ValueError(f"unexpected optimizer seed for {sid}: {seed}")
        if "family_id" in row and row["family_id"] != scenario_meta[sid][0]:
            raise ValueError(f"family metadata mismatch for {sid}")
        if "composition_id" in row and row["composition_id"] != scenario_meta[sid][1]:
            raise ValueError(f"composition metadata mismatch for {sid}")

        key = (method, seed, sid)
        if key in observed:
            raise ValueError(f"duplicate run: {key}")
        value = row.get("class_success")
        if value is None:
            raise ValueError(f"labelled null class_success for {key}")
        if value not in (0, 1, 0.0, 1.0, False, True):
            raise ValueError(f"class_success must be binary for {key}")
        value = float(value)
        is_behavioural_failure = bool(
            row.get("behavioral_failure")
            or row.get("outcome_status") == "behavioral_failure"
        )
        if is_behavioural_failure and value != 0.0:
            raise ValueError(f"behavioral failure must score zero for {key}")
        behavioural_failure_count += int(is_behavioural_failure)
        observed[key] = value

    technical_keys = set()
    technical_records = list(technical_missing or ())
    for item in technical_records:
        if not isinstance(item, dict):
            raise ValueError("technical missing record must be an object")
        try:
            key = (item["method"], item["seed"], item["scenario_id"])
        except KeyError as exc:
            raise ValueError("technical missing record lacks run identity") from exc
        if key[0] not in pair_methods:
            continue
        if key not in expected_keys:
            raise ValueError(f"technical missing record outside frozen roster: {key}")
        if item.get("category") != "infrastructure" or not str(item.get("reason", "")).strip():
            raise ValueError("technical missing record requires infrastructure category and reason")
        if key in technical_keys or key in observed:
            raise ValueError(f"duplicate or contradictory technical missing record: {key}")
        technical_keys.add(key)

    missing_keys = expected_keys - set(observed)
    unexplained = missing_keys - technical_keys
    if unexplained:
        sample = sorted(unexplained, key=str)[:3]
        raise ValueError(f"unexplained missing run(s): {sample}")

    # Build paired scenario means. A missing run invalidates its whole
    # composition; it is counted, not silently replaced or imputed.
    scenario_diffs = {}
    incomplete_compositions = set()
    paired_run_count = 0
    for (family, composition), scenario_ids in composition_scenarios.items():
        for sid in scenario_ids:
            diffs = []
            for seed in seeds:
                key_a = (method_a, seed, sid)
                key_b = (method_b, seed, sid)
                if key_a in technical_keys or key_b in technical_keys:
                    incomplete_compositions.add((family, composition))
                    continue
                if key_a not in observed or key_b not in observed:
                    raise ValueError(f"unpaired {method_a}/{method_b} run for {sid}, seed={seed}")
                diffs.append(observed[key_a] - observed[key_b])
                paired_run_count += 1
            if len(diffs) != len(seeds):
                incomplete_compositions.add((family, composition))
            else:
                scenario_diffs[sid] = fmean(diffs)

    composition_means = {}
    for key, scenario_ids in composition_scenarios.items():
        if key in incomplete_compositions:
            continue
        if not scenario_ids or any(sid not in scenario_diffs for sid in scenario_ids):
            incomplete_compositions.add(key)
            continue
        composition_means[key] = fmean(scenario_diffs[sid] for sid in scenario_ids)

    family_means = {}
    family_loss = []
    family_loss_reasons = {}
    for family in families:
        comps = sorted(family_compositions[family])
        valid = [composition_means[(family, comp)]
                 for comp in comps if (family, comp) in composition_means]
        if len(valid) != compositions_per_family:
            family_loss.append(family)
            failed = sorted(comp for comp in comps
                            if (family, comp) not in composition_means)
            family_loss_reasons[family] = {
                "valid_compositions": len(valid),
                "required_compositions": compositions_per_family,
                "incomplete_compositions": failed,
            }
            continue
        family_means[family] = fmean(valid)

    n_families = len(family_means)
    design_deviation = n_families < min_families
    confirmatory_status = (
        "NOT_ELIGIBLE_UNDERPOWERED" if design_deviation else "ELIGIBLE"
    )
    effect = fmean(family_means.values()) if family_means else None
    student = None
    if not design_deviation and n_families >= 2:
        student = student_t_summary(list(family_means.values()))

    return {
        "analysis_version": ANALYSIS_VERSION,
        "analysis_split": analysis_split,
        "primary_contrast": f"{method_a} - {method_b}",
        "primary_endpoint": "CondRecSucc (R1+R2 class_success)",
        "n_expected_families": len(families),
        "n_families": n_families,
        "family_equal_weight_effect": effect,
        "family_means": family_means,
        "composition_means": {
            f"{family}|{composition}": value
            for (family, composition), value in sorted(composition_means.items())
        },
        "family_composition_counts": {
            family: len(family_compositions[family])
            for family in family_means
        },
        "family_loss": sorted(family_loss),
        "family_loss_reasons": family_loss_reasons,
        "technical_missing_runs": len(technical_keys),
        "technical_missing_records": technical_records,
        "behavioural_failure_count": behavioural_failure_count,
        "paired_run_count": paired_run_count,
        "n_expected_run_keys": len(expected_keys),
        "n_observed_run_keys": len(observed),
        "n_missing_run_keys": len(missing_keys),
        "design_deviation": design_deviation,
        "confirmatory_status": confirmatory_status,
        "student_t": student,
    }


SECONDARY_COMPARISONS = {
    "H2": ("AB", "A"),
    "H3": ("AwaitSLA", "A"),
    "H4": ("AwaitSLA", "AwaitFixed"),
    "H5": ("AB", "AwaitSLA"),
}


def holm_adjust(p_values):
    """Holm step-down adjusted p-values, preserving input order."""
    values = [float(p) for p in p_values]
    if len(values) != 4:
        raise ValueError("R4 secondary family must contain exactly four p-values")
    if any(not 0.0 <= p <= 1.0 for p in values):
        raise ValueError("p-values must be finite values in [0,1]")
    order = sorted(range(len(values)), key=lambda i: values[i])
    adjusted = [0.0] * len(values)
    running = 0.0
    m = len(values)
    for rank, idx in enumerate(order):
        candidate = min(1.0, (m - rank) * values[idx])
        running = max(running, candidate)
        adjusted[idx] = running
    return adjusted


def analyze_secondary_endpoints(
    run_rows,
    expected_roster,
    expected_optimizer_seeds,
    technical_missing=None,
    *,
    analysis_split="test",
    min_families=DEFAULT_MIN_FAMILIES,
    compositions_per_family=DEFAULT_COMPOSITIONS_PER_FAMILY,
):
    """Execute H2-H5 through the same paired family-level analysis path.

    No secondary endpoint is confirmatory in R4 because null/partial-null
    family-wise Type-I calibration has not yet been completed. Holm is still
    applied to the complete four-comparison exploratory family.
    """
    results = {}
    raw_p = {}
    for hypothesis, (method_a, method_b) in SECONDARY_COMPARISONS.items():
        result = analyze_primary_endpoint(
            run_rows,
            expected_roster,
            expected_optimizer_seeds,
            technical_missing,
            analysis_split=analysis_split,
            min_families=min_families,
            compositions_per_family=compositions_per_family,
            method_a=method_a,
            method_b=method_b,
        )
        result["hypothesis"] = hypothesis
        result["classification"] = "exploratory"
        result["confirmatory"] = False
        result["exploratory_reason"] = (
            "H2-H5 remain exploratory pending null/partial-null Type-I calibration"
        )
        p = result["student_t"]["p_two_sided"] if result["student_t"] else None
        raw_p[hypothesis] = p
        results[hypothesis] = result

    all_eligible = all(value is not None for value in raw_p.values())
    adjusted = (
        holm_adjust([raw_p[h] for h in SECONDARY_COMPARISONS])
        if all_eligible else [None] * 4
    )
    for hypothesis, adjusted_p in zip(SECONDARY_COMPARISONS, adjusted):
        results[hypothesis]["p_raw"] = raw_p[hypothesis]
        results[hypothesis]["p_holm_adjusted"] = adjusted_p

    return {
        "analysis_version": ANALYSIS_VERSION,
        "secondary_family": "H2-H5",
        "hypothesis_count": 4,
        "holm_method": "Holm step-down" if all_eligible else None,
        "status": "COMPLETE" if all_eligible else "NOT_ELIGIBLE",
        "all_exploratory": True,
        "results": results,
    }
