#!/usr/bin/env python3
"""Run the frozen TCAIL estimator gate; no held-out tuning is performed."""
from __future__ import annotations

import argparse
from concurrent.futures import ProcessPoolExecutor
from dataclasses import replace
import json
import os
from pathlib import Path
import time

import numpy as np
import pandas as pd
from scipy.special import expit

from experiments.tcail_confirmatory_r1.analysis_metrics import (
    calibration_summary,
    macro_auprc_by_seed,
    paired_bootstrap_ci,
    select_strongest_baseline,
)
from experiments.tcail_confirmatory_r1.fos_metrics import (
    average_linkage_fos,
    linkage_partition,
    pair_cocluster_metrics,
    variation_of_information,
)
from experiments.tcail_confirmatory_r1.linkage_baselines import (
    CDLED_P3M,
    CGOMEA,
    CONTEXT_POOLED,
    FBL_ABSOLUTE,
    FBL_SIGNED_EQ7,
    LOCAL_RAW,
    ORACLE,
    RANDOM,
    STANDARDIZED,
    BaselineSettings,
    FourCellTaskBlock,
    estimate_baselines,
)
from experiments.tcail_confirmatory_r1.synthetic_generator import (
    SCENARIOS,
    CELL_ORDER,
    default_config,
    extract_module_estimator_data,
    generate_seed,
    module_for_seed,
)
from experiments.tcail_confirmatory_r1.tcail_bernoulli import (
    BernoulliPrior,
    LaplaceSettings,
    PredictiveSettings,
    fit_tcail_bernoulli,
    walsh_design,
)


BASELINE_NAMES = {
    LOCAL_RAW: "local_raw",
    STANDARDIZED: "standardized",
    CONTEXT_POOLED: "context_pooled",
    FBL_ABSOLUTE: "fbl_abs",
    FBL_SIGNED_EQ7: "fbl_signed",
    CDLED_P3M: "cdled",
    CGOMEA: "cgomea",
    RANDOM: "random",
    ORACLE: "oracle",
}
ALL_SCORE_COLUMNS = ["tcail_q", "tcail_w"] + list(BASELINE_NAMES.values())


def load_config(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def calibrate_null_threshold(scores, target_false_link=0.05):
    values = np.asarray(scores, dtype=float)
    values = values[np.isfinite(values)]
    if len(values) == 0:
        return float("nan")
    return float(np.quantile(values, 1.0 - target_false_link, method="higher"))


def combine_tcail_models(result_2, result_3, delta):
    left = result_2.pair_results.set_index(["pair_i", "pair_j"])
    right = result_3.pair_results.set_index(["pair_i", "pair_j"])
    if set(left.index) != set(right.index):
        raise ValueError("M2 and M3 pair sets differ")
    rows = []
    for pair in sorted(left.index):
        a, b = left.loc[pair], right.loc[pair]
        abstain = bool(a["abstain"] or b["abstain"])
        reason = ";".join(filter(None, [str(a["abstain_reason"]), str(b["abstain_reason"])]))
        q = min(float(a["q"]), float(b["q"]))
        w = min(float(a["w"]), float(b["w"]))
        opposite = (
            (a["p_positive"] >= 0.9 and b["p_negative"] >= 0.9)
            or (a["p_negative"] >= 0.9 and b["p_positive"] >= 0.9)
        )
        if opposite:
            abstain = True
            reason = ";".join(filter(None, [reason, "MODEL_ORDER_SIGN_CONFLICT"]))
        rows.append({
            "pair_i": int(pair[0]), "pair_j": int(pair[1]),
            "tcail_q": q, "tcail_w": w,
            "q_m2": float(a["q"]), "q_m3": float(b["q"]),
            "w_m2": float(a["w"]), "w_m3": float(b["w"]),
            "delta_mean_m2": float(a["delta_mean"]),
            "delta_mean_m3": float(b["delta_mean"]),
            "ci_lower": min(float(a["ci_lower"]), float(b["ci_lower"])),
            "ci_upper": max(float(a["ci_upper"]), float(b["ci_upper"])),
            "p_positive": min(float(a["p_positive"]), float(b["p_positive"])),
            "p_negative": min(float(a["p_negative"]), float(b["p_negative"])),
            "n_task": min(int(a["n_task"]), int(b["n_task"])),
            "n_block": min(int(a["n_block"]), int(b["n_block"])),
            "tcail_abstain": abstain,
            "tcail_abstain_reason": reason,
            "delta_threshold": float(delta),
        })
    return pd.DataFrame(rows)


def build_baseline_blocks(observations, truth):
    blocks, true_deltas = [], {}
    for _, row in truth.iterrows():
        config_indices = [int(value) for value in str(row["config_indices"]).split(";")]
        subset = observations.loc[observations["config_index"].isin(config_indices)]
        pivot = subset.pivot_table(
            index="block_id", columns="config_index", values="y", aggfunc="first"
        ).reindex(columns=config_indices)
        outcomes = pivot.to_numpy(dtype=float)
        block = FourCellTaskBlock(
            pair=(int(row["pair_i"]), int(row["pair_j"])),
            context=str(row["parent_id"]),
            outcomes=outcomes,
            budget_episode_equivalents=float(np.isfinite(outcomes).sum()),
        )
        blocks.append(block)
        true_deltas[block.key] = float(row["true_delta"])
    return blocks, true_deltas


def baseline_long_frame(estimates):
    rows = []
    for estimate in estimates:
        base = estimate.as_dict()
        contexts = ([str(estimate.context)] if estimate.context is not None
                    else ["parent_0", "parent_1"])
        for context in contexts:
            rows.append({
                "pair_i": base["pair_i"], "pair_j": base["pair_j"],
                "parent_id": context,
                "method": BASELINE_NAMES[base["method"]],
                "score": base["score"], "state": base["state"],
                "eligible": bool(base["eligible_for_common_builder"]),
            })
    return pd.DataFrame(rows)


def posterior_predictive_pvalue(fit, data, max_draws=50, seed=17):
    if not fit.fit_ok:
        return float("nan")
    task_codes, _ = pd.factorize(data["task_id"], sort=True)
    block_codes, _ = pd.factorize(data["block_id"], sort=True)
    x = data.loc[:, fit.x_columns].to_numpy(dtype=float)
    design = walsh_design(x, fit.terms)
    y = data["y"].to_numpy(dtype=int)
    draws = fit.posterior_draws[:max_draws]
    p = fit.n_fixed
    beta = draws[:, :p]
    u = draws[:, p:p + fit.n_tasks]
    v = draws[:, p + fit.n_tasks:p + fit.n_tasks + fit.n_blocks]
    eta = design @ beta.T + u[:, task_codes].T + v[:, block_codes].T
    probabilities = expit(eta)
    rng = np.random.default_rng(seed)
    simulated = (rng.random(probabilities.shape) < probabilities).sum(axis=0)
    observed = int(y.sum())
    low = np.mean(simulated <= observed)
    high = np.mean(simulated >= observed)
    return float(min(1.0, 2.0 * min(low, high)))


def fit_graph(seed, scenario, split, config):
    generator_config = default_config(scenario)
    if scenario != "low_support_drift":
        block_count = config["support_blocks"][seed % len(config["support_blocks"])]
        generator_config = replace(generator_config, n_blocks=block_count)
    data = generate_seed(scenario, seed, split, generator_config)
    module = module_for_seed(seed)
    estimator_data = extract_module_estimator_data(data.observations, module)
    prior_values = config["estimator"]["fixed_effect_sd_by_order"]
    prior = BernoulliPrior(
        intercept_scale=prior_values["intercept"],
        main_scale=prior_values["main"],
        pair_scale=prior_values["pairwise"],
        three_way_scale=prior_values["three_way"],
        task_log_sigma_mean=config["estimator"]["log_random_effect_sd_prior"]["mean"],
        block_log_sigma_mean=config["estimator"]["log_random_effect_sd_prior"]["mean"],
        task_log_sigma_sd=config["estimator"]["log_random_effect_sd_prior"]["sd"],
        block_log_sigma_sd=config["estimator"]["log_random_effect_sd_prior"]["sd"],
    )
    laplace = LaplaceSettings(
        n_draws=config["estimator"]["posterior_draws"], seed=seed * 17 + 1,
        maxiter=config["estimator"]["optimizer_max_iterations"],
    )
    predictive = PredictiveSettings(
        n_draws=config["estimator"]["anchor_tasks"], seed=seed * 31 + 7,
    )
    tcail_rows, diagnostics = [], []
    for context_index, parent_values in enumerate((-1, 1)):
        parent_id = f"parent_{context_index}"
        fits = {}
        for model_order in (2, 3):
            started = time.time()
            result = fit_tcail_bernoulli(
                estimator_data, parent=[parent_values] * 4,
                model_order=model_order, delta=config["delta_local"],
                prior=prior, laplace=laplace, predictive=predictive,
                min_task_support=2, min_block_support=config["estimator"]["minimum_support_candidates"][0],
            )
            fits[model_order] = result
            diag = result.fit.diagnostics
            diagnostics.append({
                "scenario": scenario, "split": split, "seed": seed,
                "module_id": seed % 10, "parent_id": parent_id,
                "model_order": model_order,
                "fit_ok": result.fit.fit_ok,
                "converged": diag.converged,
                "gradient_max_abs": diag.gradient_max_abs,
                "hessian_rank": diag.hessian_rank,
                "hessian_dimension": diag.hessian_dimension,
                "condition_number": diag.condition_number,
                "failure_reason": diag.failure_reason,
                "ppc_p_value": posterior_predictive_pvalue(result.fit, estimator_data)
                    if model_order == 2 else np.nan,
                "fit_seconds": time.time() - started,
            })
        combined = combine_tcail_models(fits[2], fits[3], config["delta_local"])
        local_to_global = {
            (int(row.local_i), int(row.local_j)): (int(row.pair_i), int(row.pair_j))
            for _, row in data.pair_truth.iterrows()
        }
        combined["parent_id"] = parent_id
        mapped = [local_to_global[(int(i), int(j))]
                  for i, j in zip(combined["pair_i"], combined["pair_j"])]
        combined["pair_i"] = [pair[0] for pair in mapped]
        combined["pair_j"] = [pair[1] for pair in mapped]
        tcail_rows.append(combined)
    tcail = pd.concat(tcail_rows, ignore_index=True)

    blocks, true_deltas = build_baseline_blocks(data.observations, data.pair_truth)
    estimates = estimate_baselines(
        blocks, random_seed=seed,
        true_deltas=true_deltas,
        settings=BaselineSettings(
            min_complete_blocks=config["estimator"]["minimum_support_candidates"][0],
            fbl_epsilon=0.0, dled_epsilon=0.0,
            delta_local=config["delta_local"],
        ),
    )
    baseline = baseline_long_frame(estimates)
    baseline_wide = baseline.pivot(
        index=["pair_i", "pair_j", "parent_id"], columns="method",
        values=["score", "eligible"],
    )
    baseline_wide.columns = [
        f"{method}_{'score' if field == 'score' else 'abstain'}"
        for field, method in baseline_wide.columns
    ]
    baseline_wide = baseline_wide.reset_index()
    for name in BASELINE_NAMES.values():
        baseline_wide[f"{name}_score"] = pd.to_numeric(
            baseline_wide[f"{name}_score"], errors="coerce")
        baseline_wide[f"{name}_abstain"] = ~(
            baseline_wide[f"{name}_abstain"].astype("boolean").fillna(False).astype(bool))
    evaluation = data.pair_truth.merge(
        baseline_wide, on=["pair_i", "pair_j", "parent_id"], how="left",
        validate="many_to_one",
    )
    evaluation = evaluation.merge(
        tcail, on=["pair_i", "pair_j", "parent_id"], how="left",
        validate="one_to_one",
    )
    return data, evaluation, pd.DataFrame(diagnostics)


def apply_thresholds(evaluation, thresholds):
    output = evaluation.copy()
    for method in ALL_SCORE_COLUMNS:
        score = pd.to_numeric(
            output[f"{method}_score"] if method in BASELINE_NAMES.values()
            else output[method], errors="coerce")
        abstain = (output[f"{method}_abstain"] if method in BASELINE_NAMES.values()
                   else output["tcail_abstain"])
        threshold = thresholds.get(method, float("nan"))
        eligible = (~abstain.astype("boolean").fillna(True).astype(bool)) & np.isfinite(score)
        output[f"{method}_evaluable"] = eligible
        output[f"{method}_rank_score"] = np.where(eligible, score, -1.0)
        output[f"{method}_selected"] = eligible & (score > threshold)
    return output


def method_macro(evaluation, method):
    frame = evaluation.loc[evaluation["support_status"] != "unsupported"].copy()
    frame["score_for_metric"] = frame[f"{method}_rank_score"]
    detail, macro = macro_auprc_by_seed(frame, "score_for_metric")
    return pd.DataFrame(detail), pd.DataFrame(macro)


def fos_recovery(evaluation, thresholds):
    frame = evaluation.loc[evaluation["support_status"] != "unsupported"].copy()
    rows = []
    for (seed, scenario, parent_id), group in frame.groupby(
            ["seed", "scenario", "parent_id"], sort=True):
        truth_edges = []
        local_pairs = {}
        for _, row in group.iterrows():
            local_pairs[(int(row.pair_i), int(row.pair_j))] = (
                int(row.local_i), int(row.local_j))
            if int(row.label) == 1:
                truth_edges.append({"i": int(row.local_i), "j": int(row.local_j)})
        true_fos = average_linkage_fos(4, [
            {**edge, "weight": 1.0, "selected": True, "supported": True}
            for edge in truth_edges
        ])
        for method in ALL_SCORE_COLUMNS:
            predicted_edges = []
            for _, row in group.iterrows():
                if row[f"{method}_selected"]:
                    local_i, local_j = local_pairs[(int(row.pair_i), int(row.pair_j))]
                    score_value = (row[f"{method}_score"]
                                   if method in BASELINE_NAMES.values()
                                   else row[method])
                    predicted_edges.append({
                        "i": local_i, "j": local_j,
                        "weight": float(max(score_value, 1e-12)),
                        "selected": True, "supported": True,
                    })
            predicted_fos = average_linkage_fos(4, predicted_edges)
            pair_metrics = pair_cocluster_metrics(true_fos, predicted_fos, 4)
            true_labels = linkage_partition(4, truth_edges)
            pred_labels = linkage_partition(4, predicted_edges)
            pair_metrics["variation_of_information"] = variation_of_information(
                true_labels, pred_labels)
            pair_metrics.update({
                "seed": seed, "scenario": scenario, "parent_id": parent_id,
                "method": method,
            })
            rows.append(pair_metrics)
    return pd.DataFrame(rows)


def _fit_one(task):
    split, scenario, seed, config = task
    data, evaluation, diag = fit_graph(seed, scenario, split, config)
    observed = data.observations.copy()
    observed["module_variables"] = str(data.metadata["module_variables"])
    return (evaluation, diag, observed, data.pair_truth, data.fixed_effects,
            data.task_parameters, data.block_parameters)


def loop_split(split, seeds, config, jobs=1):
    tasks = [(split, scenario, seed, config)
             for scenario in SCENARIOS for seed in seeds]
    if jobs > 1:
        chunksize = max(1, len(tasks) // (jobs * 4))
        with ProcessPoolExecutor(max_workers=jobs) as pool:
            results = list(pool.map(_fit_one, tasks, chunksize=chunksize))
        for (_, scenario, seed, _), result in zip(tasks, results):
            print(split, scenario, seed, len(result[0]), flush=True)
    else:
        results = []
        for task in tasks:
            result = _fit_one(task)
            results.append(result)
            print(split, task[1], task[2], len(result[0]), flush=True)
    evaluations = [result[0] for result in results]
    diagnostics = [result[1] for result in results]
    observed_parts = [result[2] for result in results]
    truth_parts = [result[3] for result in results]
    fixed_parts = [result[4] for result in results]
    task_parts = [result[5] for result in results]
    block_parts = [result[6] for result in results]
    return (
        pd.concat(evaluations, ignore_index=True),
        pd.concat(diagnostics, ignore_index=True),
        pd.concat(observed_parts, ignore_index=True),
        pd.concat(truth_parts, ignore_index=True),
        pd.concat(fixed_parts, ignore_index=True),
        pd.concat(task_parts, ignore_index=True),
        pd.concat(block_parts, ignore_index=True),
    )


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=Path,
                        default=Path("experiments/tcail_confirmatory_r1/experiment_config.json"))
    parser.add_argument("--output", type=Path,
                        default=Path("experiments/tcail_confirmatory_r1/results"))
    parser.add_argument("--smoke-seeds", type=int, default=0)
    parser.add_argument("--jobs", type=int, default=1)
    args = parser.parse_args()
    config = load_config(args.config)
    if args.jobs > 1:
        for variable in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS",
                         "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS"):
            os.environ.setdefault(variable, "1")
    if args.smoke_seeds:
        split_seeds = {
            "train": tuple(range(args.smoke_seeds)),
            "validation": tuple(range(40, 40 + args.smoke_seeds)),
            "held_out": tuple(range(60, 60 + args.smoke_seeds)),
        }
    else:
        split_seeds = {
            "train": tuple(range(40)),
            "validation": tuple(range(40, 60)),
            "held_out": tuple(range(3000, 3040)),
        }
    args.output.mkdir(parents=True, exist_ok=True)
    raw_dir = args.output / "raw"
    raw_dir.mkdir(exist_ok=True)

    evaluations = {}
    diagnostics = {}
    for split in ("train", "validation", "held_out"):
        evaluation, diag, observed, truth, fixed, tasks, blocks = loop_split(
            split, split_seeds[split], config, jobs=args.jobs)
        evaluations[split] = evaluation
        diagnostics[split] = diag
        evaluation.to_csv(args.output / f"{split}_evaluation_raw.csv", index=False)
        diag.to_csv(args.output / f"{split}_fit_diagnostics.csv", index=False)
        observed.to_csv(
            raw_dir / f"{split}_observations.csv.gz", index=False, compression="gzip")
        truth.to_csv(raw_dir / f"{split}_pair_truth.csv", index=False)
        fixed.to_csv(raw_dir / f"{split}_fixed_effects.csv", index=False)
        tasks.to_csv(raw_dir / f"{split}_task_parameters.csv", index=False)
        blocks.to_csv(raw_dir / f"{split}_block_parameters.csv", index=False)

    train_null = evaluations["train"].loc[
        (evaluations["train"]["scenario"] == "additive_null")
        & (evaluations["train"]["support_status"] != "unsupported")
    ]
    thresholds = {}
    for method in ALL_SCORE_COLUMNS:
        if method.startswith("tcail"):
            eligible = ~train_null["tcail_abstain"].astype(
                "boolean").fillna(True).astype(bool)
            values = pd.to_numeric(train_null.loc[eligible, method], errors="coerce")
        else:
            eligible = ~train_null[f"{method}_abstain"].astype(
                "boolean").fillna(True).astype(bool)
            values = pd.to_numeric(
                train_null.loc[eligible, f"{method}_score"], errors="coerce")
        thresholds[method] = calibrate_null_threshold(
            values, config["estimator"]["null_false_link_target"])

    train = apply_thresholds(evaluations["train"], thresholds)
    validation = apply_thresholds(evaluations["validation"], thresholds)
    test = apply_thresholds(evaluations["held_out"], thresholds)

    validation_macro = {}
    validation_detail = {}
    for method in ALL_SCORE_COLUMNS:
        detail, macro = method_macro(validation, method)
        validation_detail[method] = detail
        validation_macro[method] = macro.set_index("seed")["macro_auprc"]
    validation_evaluable = validation.loc[
        validation["support_status"] != "unsupported"]
    baseline_candidates = {
        method: validation_macro[method]
        for method in BASELINE_NAMES.values()
        if method not in ("oracle", "fbl_signed", "random")
        and np.mean(validation_evaluable[method + "_evaluable"]) >= 0.99
    }
    baseline_selection = select_strongest_baseline(baseline_candidates)
    strongest = baseline_selection["method"]

    test_macro, test_detail = {}, {}
    for method in ALL_SCORE_COLUMNS:
        detail, macro = method_macro(test, method)
        test_detail[method] = detail
        test_macro[method] = macro.set_index("seed")["macro_auprc"]
    seeds = sorted(test_macro["tcail_q"].index)
    overall_differences = [
        test_macro["tcail_q"][seed] - test_macro[strongest][seed] for seed in seeds
    ]
    overall_ci = paired_bootstrap_ci(
        overall_differences,
        seed=config["statistics"]["paired_bootstrap_seed"],
        draws=config["statistics"]["paired_bootstrap_draws"],
    )
    scenario_summary = {}
    key_scenarios = ("sparse_pairwise", "parent_sign_flip")
    not_worse = True
    for scenario in SCENARIOS:
        differences = []
        for seed in seeds:
            t = test_detail["tcail_q"].query(
                "seed == @seed and scenario == @scenario")["auprc"].iloc[0]
            b = test_detail[strongest].query(
                "seed == @seed and scenario == @scenario")["auprc"].iloc[0]
            differences.append(t - b)
        ci = paired_bootstrap_ci(
            differences, seed=config["statistics"]["paired_bootstrap_seed"] + 1,
            draws=config["statistics"]["paired_bootstrap_draws"])
        scenario_summary[scenario] = {
            "mean_difference": float(np.mean(differences)), "ci": ci,
        }
        if scenario in key_scenarios and ci[1] < 0:
            not_worse = False

    gate_pass = bool(overall_ci[0] > 0 and not_worse)
    t_test = test.loc[
        (test["support_status"] != "unsupported") & ~test["tcail_abstain"].fillna(True)]
    calibration = calibration_summary(
        t_test["label"].to_numpy(), t_test["tcail_q"].to_numpy())
    null_rows = test.loc[test["scenario"] == "additive_null"]
    null_false_link = {}
    for method in ALL_SCORE_COLUMNS:
        selected = null_rows[method + "_selected"] & (
            null_rows["support_status"] != "unsupported")
        null_false_link[method] = float(selected.mean())
    sign_rows = t_test.loc[
        (t_test["scenario"] == "parent_sign_flip") & t_test["tcail_q_selected"]]
    predicted = np.where(sign_rows["p_positive"] >= sign_rows["p_negative"],
                         "positive", "negative")
    sign_accuracy = float(np.mean(predicted == sign_rows["direction"])) \
        if len(sign_rows) else float("nan")
    fos = fos_recovery(test, thresholds)
    fos_summary = fos.groupby("method").agg(
        precision=("precision", "mean"), recall=("recall", "mean"),
        f1=("f1", "mean"), false_merge_rate=("false_merge_rate", "mean"),
        variation_of_information=("variation_of_information", "mean"),
    ).reset_index().to_dict("records")
    fit_quality = diagnostics["held_out"].groupby("model_order").agg(
        fit_ok=("fit_ok", "mean"), ppc_extreme_rate=("ppc_p_value", lambda x: np.mean(x < 0.05)),
        mean_seconds=("fit_seconds", "mean"),
    ).reset_index().to_dict("records")

    summary = {
        "baseline_selection": baseline_selection,
        "strongest_baseline": strongest,
        "thresholds": thresholds,
        "seed_counts": {k: len(v) for k, v in split_seeds.items()},
        "estimator_gate": {
            "overall_mean_difference": float(np.mean(overall_differences)),
            "overall_paired_bootstrap_95pct_ci": overall_ci,
            "scenario_results": scenario_summary,
            "key_scenarios_not_significantly_worse": not_worse,
            "PASS": gate_pass,
        },
        "calibration": calibration,
        "null_false_link": null_false_link,
        "sign_flip_accuracy": sign_accuracy,
        "FOS_recovery": fos_summary,
        "fit_quality": fit_quality,
        "status": "ESTIMATOR_GATE_PASS" if gate_pass else "ESTIMATOR_GATE_FAIL",
        "gom_gate": "NOT_RUN" if not gate_pass else "ELIGIBLE",
        "limitations": [
            "Laplace posterior approximation, not exact MCMC.",
            "cDLED-P3M and CGOMEA are explicit static-data adaptations, not full original reproductions.",
            "FBL signed Eq.(7) domain violations are reported separately and excluded from valid-only metrics.",
            "Test metrics were computed only after thresholds and strongest baseline were frozen.",
        ],
    }
    args.output.joinpath("summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    fos.to_csv(args.output / "held_out_fos_recovery.csv", index=False)
    for method, detail in test_detail.items():
        detail.to_csv(args.output / f"held_out_macro_{method}.csv", index=False)
    stage_summary = {
        "scenario_auprc": {
            method: test_detail[method].groupby("scenario")["auprc"].mean().to_dict()
            for method in ALL_SCORE_COLUMNS
        },
        "overall_macro_auprc": {
            method: float(test_macro[method].mean()) for method in ALL_SCORE_COLUMNS
        },
        "fos_recovery": fos_summary,
    }
    (args.output / "stage_summary.json").write_text(
        json.dumps(stage_summary, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
