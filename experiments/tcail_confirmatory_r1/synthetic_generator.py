"""Full-factorial local-module generator for the TCAIL estimator gate."""
from __future__ import annotations

from dataclasses import dataclass
from itertools import combinations, product
import math
from typing import Any, Dict, Mapping, Optional, Sequence, Tuple

import numpy as np
import pandas as pd
from scipy.special import expit


N_VARIABLES = 40
MODULES = tuple(tuple(range(start, start + 4)) for start in range(0, 40, 4))
SCENARIOS = (
    "additive_null",
    "sparse_pairwise",
    "parent_sign_flip",
    "overlapping_higher_order",
    "low_support_drift",
)
SPLITS = ("train", "validation", "held_out")
SPLIT_SEEDS = {
    "train": tuple(range(40)),
    "validation": tuple(range(40, 60)),
    "held_out": tuple(range(60, 100)),
}
SUPPORT_BLOCK_COUNTS = (8, 16, 32, 128)
LOCAL_CONFIGS = tuple(product((-1, 1), repeat=4))
LOCAL_CONFIG_INDEX = {bits: index for index, bits in enumerate(LOCAL_CONFIGS)}
CELL_BITS = ((0, 0), (1, 0), (0, 1), (1, 1))
CELL_ORDER = ("00", "10", "01", "11")
CELL_CONTRAST = np.array([1.0, -1.0, -1.0, 1.0])
EFFECT_SCALES = {"weak": 0.25, "medium": 0.8, "strong": 1.4}
_SCENARIO_CODES = {scenario: index + 1 for index, scenario in enumerate(SCENARIOS)}
_SPLIT_CODES = {split: index + 1 for index, split in enumerate(SPLITS)}


@dataclass(frozen=True)
class GeneratorConfig:
    n_tasks: int = 4
    n_blocks: int = 32
    delta_local: float = 0.08
    effect_strength: str = "medium"
    base_intercept_mean: float = -0.25
    base_intercept_sd: float = 0.35
    main_effect_sd: float = 0.4
    task_intercept_sd: float = 0.35
    block_intercept_sd: float = 0.25
    task_slope_sd: float = 0.0
    block_slope_sd: float = 0.0
    block_overdispersion_sd: float = 0.0
    task_drift: float = 0.0
    missing_cell_probability: float = 0.0
    min_support_blocks: int = 16
    quadrature_order: int = 21

    def __post_init__(self):
        if not isinstance(self.n_tasks, int) or self.n_tasks < 2:
            raise ValueError("n_tasks must be an integer >= 2")
        if self.n_blocks not in SUPPORT_BLOCK_COUNTS:
            raise ValueError("n_blocks must be one of 8, 16, 32, 128")
        if self.effect_strength not in EFFECT_SCALES:
            raise ValueError("unknown effect_strength")
        for name in (
            "delta_local", "base_intercept_sd", "main_effect_sd",
            "task_intercept_sd", "block_intercept_sd", "task_slope_sd",
            "block_slope_sd", "block_overdispersion_sd",
        ):
            value = getattr(self, name)
            if not np.isfinite(value) or value < 0:
                raise ValueError(f"{name} must be finite and nonnegative")
        if not np.isfinite(self.base_intercept_mean) or not np.isfinite(self.task_drift):
            raise ValueError("intercepts and drift must be finite")
        if not 0 <= self.missing_cell_probability < 1:
            raise ValueError("missing_cell_probability must be in [0,1)")
        if self.min_support_blocks < 1 or self.quadrature_order < 3:
            raise ValueError("invalid support or quadrature setting")


@dataclass
class SyntheticData:
    scenario: str
    split: str
    seeds: Tuple[int, ...]
    config: GeneratorConfig
    observations: pd.DataFrame
    pair_truth: pd.DataFrame
    fixed_effects: pd.DataFrame
    task_parameters: pd.DataFrame
    block_parameters: pd.DataFrame
    metadata: Dict[str, Any]

    @property
    def raw_observations(self):
        return self.observations

    @property
    def truth(self):
        return self.pair_truth


def default_config(scenario: str, **overrides: Any) -> GeneratorConfig:
    if scenario not in SCENARIOS:
        raise ValueError("unknown scenario")
    values: Dict[str, Any] = {}
    if scenario == "additive_null":
        values = {
            "task_intercept_sd": 0.0,
            "block_intercept_sd": 0.0,
            "task_slope_sd": 0.0,
            "block_slope_sd": 0.0,
            "block_overdispersion_sd": 0.0,
            "main_effect_sd": 0.4,
        }
    if scenario == "low_support_drift":
        values = {
            "n_blocks": 8,
            "task_slope_sd": 0.08,
            "block_overdispersion_sd": 0.15,
            "task_drift": 0.18,
            "missing_cell_probability": 0.15,
        }
    values.update(overrides)
    return GeneratorConfig(**values)


def module_for_seed(seed: int) -> Tuple[int, ...]:
    return MODULES[seed % len(MODULES)]


def _effect(rng: np.random.Generator, strength: str) -> float:
    return float(EFFECT_SCALES[strength] * rng.uniform(0.85, 1.15)
                 * rng.choice(np.array([-1.0, 1.0])))


def _fixed_parameters(scenario, config, rng, module):
    coefficients = {(): float(rng.normal(config.base_intercept_mean,
                                         config.base_intercept_sd))}
    if scenario != "additive_null":
        for variable in module:
            coefficients[(variable,)] = float(rng.normal(0.0, config.main_effect_sd))
    roles = {pair: "main_only" for pair in combinations(module, 2)}
    if scenario in ("sparse_pairwise", "low_support_drift"):
        count = 2 if scenario == "low_support_drift" else 3
        selected = rng.choice(len(roles), size=count, replace=False)
        for index in selected:
            pair = tuple(combinations(module, 2))[int(index)]
            coefficients[pair] = _effect(rng, config.effect_strength)
            roles[pair] = "sparse_pairwise"
    elif scenario == "parent_sign_flip":
        for pair in list(combinations(module, 2))[:2]:
            switch = next(variable for variable in module if variable not in pair)
            coefficients[tuple(sorted(pair + (switch,)))] = _effect(
                rng, config.effect_strength)
            roles[pair] = "parent_sign_flip"
    elif scenario == "overlapping_higher_order":
        for triple in list(combinations(module, 3))[:3]:
            coefficients[triple] = _effect(rng, config.effect_strength)
            for pair in combinations(triple, 2):
                roles[pair] = "overlapping_higher_order"
    return coefficients, roles


def _local_eta(coefficients, module, configs):
    eta = np.full(len(configs), coefficients[()], dtype=float)
    for term, coefficient in coefficients.items():
        if term:
            local = [module.index(variable) for variable in term]
            eta += coefficient * np.prod(configs[:, local], axis=1)
    return eta


def _target_probabilities(fixed_eta, config):
    variance = (
        config.task_intercept_sd**2 + config.block_intercept_sd**2
        + config.block_overdispersion_sd**2
        + 4 * (config.task_slope_sd**2 + config.block_slope_sd**2)
    )
    random_sd = math.sqrt(variance)
    target_shift = config.task_drift * (config.n_tasks - 1)
    if random_sd == 0:
        probabilities = expit(fixed_eta + target_shift)
    else:
        nodes, weights = np.polynomial.hermite.hermgauss(config.quadrature_order)
        probabilities = expit(
            fixed_eta[:, None] + target_shift
            + math.sqrt(2) * random_sd * nodes[None, :]
        ) @ (weights / math.sqrt(math.pi))
    if not np.all(np.isfinite(probabilities)):
        raise FloatingPointError("nonfinite target probabilities")
    return probabilities, random_sd


def generate_seed(scenario: str, seed: int, split: str,
                  config: Optional[GeneratorConfig] = None) -> SyntheticData:
    if scenario not in SCENARIOS or split not in SPLITS:
        raise ValueError("unknown scenario or split")
    if not isinstance(seed, int) or seed < 0:
        raise ValueError("seed must be nonnegative")
    config = default_config(scenario) if config is None else config
    module = module_for_seed(seed)
    streams = np.random.SeedSequence(
        [seed, _SCENARIO_CODES[scenario], _SPLIT_CODES[split]]).spawn(7)
    parameter_rng, task_rng, block_rng, over_rng, obs_rng, missing_rng, slope_rng = (
        np.random.default_rng(stream) for stream in streams)
    coefficients, roles = _fixed_parameters(scenario, config, parameter_rng, module)
    module_configs = np.asarray(LOCAL_CONFIGS, dtype=np.int8)
    fixed_eta = _local_eta(coefficients, module, module_configs)
    probabilities_true, random_sd = _target_probabilities(fixed_eta, config)

    n_tasks, n_blocks, n_configs = config.n_tasks, config.n_blocks, len(LOCAL_CONFIGS)
    task_intercepts = task_rng.normal(0, config.task_intercept_sd, n_tasks)
    task_slopes = task_rng.normal(
        0, config.task_slope_sd, (n_tasks, 4)
    ) if config.task_slope_sd else np.zeros((n_tasks, 4))
    block_intercepts = block_rng.normal(
        0, config.block_intercept_sd, (n_tasks, n_blocks))
    block_slopes = block_rng.normal(
        0, config.block_slope_sd, (n_tasks, n_blocks, 4)
    ) if config.block_slope_sd else np.zeros((n_tasks, n_blocks, 4))
    drift = config.task_drift * np.arange(n_tasks)
    eta = (fixed_eta[None, None, :]
           + (task_intercepts + drift)[:, None, None]
           + block_intercepts[:, :, None])
    if config.task_slope_sd:
        eta += np.einsum("ta,ca->tc", task_slopes, module_configs)[:, None, :]
    if config.block_slope_sd:
        eta += np.einsum("tba,ca->tbc", block_slopes, module_configs)
    if config.block_overdispersion_sd:
        eta += over_rng.normal(0, config.block_overdispersion_sd, eta.shape)
    observation_probabilities = expit(eta)
    y = (obs_rng.random(eta.shape) < observation_probabilities).astype(np.int8)
    observed = missing_rng.random(eta.shape) >= config.missing_cell_probability
    if not np.all(observed.any(axis=(0, 1))):
        raise RuntimeError("a local configuration has no observations")

    task_ids = [f"{split}:{scenario}:seed_{seed}:task_{t}" for t in range(n_tasks)]
    block_ids = [
        [f"{task_ids[t]}:block_{b}" for b in range(n_blocks)]
        for t in range(n_tasks)
    ]
    task_rows, block_rows = [], []
    for t in range(n_tasks):
        row = {
            "split": split, "scenario": scenario, "seed": seed,
            "task_id": task_ids[t], "task_index": t,
            "task_intercept": task_intercepts[t], "drift_offset": drift[t],
        }
        for local, variable in enumerate(module):
            row[f"task_slope_x_{variable}"] = task_slopes[t, local]
        task_rows.append(row)
    for t in range(n_tasks):
        for b in range(n_blocks):
            row = {
                "split": split, "scenario": scenario, "seed": seed,
                "task_id": task_ids[t], "task_index": t,
                "block_id": block_ids[t][b], "block_index": b,
                "block_intercept": block_intercepts[t, b],
            }
            for local, variable in enumerate(module):
                row[f"block_slope_x_{variable}"] = block_slopes[t, b, local]
            block_rows.append(row)

    t_index, b_index, c_index = np.indices(observed.shape)
    keep = observed
    data = {
        "split": split, "scenario": scenario, "seed": seed, "module_id": seed % 10,
        "task_id": np.asarray(task_ids, dtype=object)[t_index[keep]],
        "task_index": t_index[keep], "block_index": b_index[keep],
        "block_id": np.asarray(
            [block_ids[t][b] for t in range(n_tasks) for b in range(n_blocks)],
            dtype=object,
        ).reshape(n_tasks, n_blocks)[t_index[keep], b_index[keep]],
        "config_index": c_index[keep],
        "config_id": np.asarray(
            [f"cfg_{''.join(map(str, bits))}" for bits in LOCAL_CONFIGS],
            dtype=object,
        )[c_index[keep]],
        "y": y[keep],
    }
    x_all = np.full((keep.sum(), N_VARIABLES), -1, dtype=np.int8)
    x_all[:, list(module)] = module_configs[c_index[keep]]
    for variable in range(N_VARIABLES):
        data[f"x_{variable}"] = x_all[:, variable]
    observations = pd.DataFrame(data)

    pair_rows = []
    local_pairs = list(combinations(range(4), 2))
    for local_i, local_j in local_pairs:
        pair = (module[local_i], module[local_j])
        others = [index for index in range(4) if index not in (local_i, local_j)]
        for context, parent_value in enumerate((-1, 1)):
            config_indices = []
            for bit_i, bit_j in CELL_BITS:
                bits = [-1, -1, -1, -1]
                bits[local_i], bits[local_j] = 2 * bit_i - 1, 2 * bit_j - 1
                for index in others:
                    bits[index] = parent_value
                config_indices.append(LOCAL_CONFIG_INDEX[tuple(bits)])
            probabilities_cells = probabilities_true[np.asarray(config_indices)]
            true_delta = float(CELL_CONTRAST @ probabilities_cells)
            complete = observed[:, :, config_indices].all(axis=-1)
            n_complete = int(complete.sum())
            n_task = int(np.unique(np.where(complete)[0]).size) if n_complete else 0
            cell_total = observed[:, :, config_indices].sum(axis=(0, 1))
            unsupported = bool(np.any(cell_total == 0))
            low_support = n_complete < config.min_support_blocks
            support_status = (
                "unsupported" if unsupported else
                "low_support" if low_support else "supported"
            )
            row = {
                "split": split, "scenario": scenario, "seed": seed,
                "module_id": seed % 10, "module_variables": str(module),
                "pair_i": pair[0], "pair_j": pair[1],
                "local_i": local_i, "local_j": local_j,
                "parent_id": f"parent_{context}",
                "parent_context": f"other_two_{parent_value:+d}",
                "target_task_drift_shift": config.task_drift * (config.n_tasks - 1),
                "true_delta": true_delta, "delta_threshold": config.delta_local,
                "label": int(abs(true_delta) > config.delta_local),
                "direction": "positive" if true_delta > 0 else
                             "negative" if true_delta < 0 else "zero",
                "design_role": roles[pair],
                "support_status": support_status,
                "supported": support_status == "supported",
                "n_tasks": config.n_tasks, "n_blocks": config.n_blocks,
                "n_block_complete": n_complete, "n_task_complete": n_task,
                "integration_method": "gauss_hermite_target_marginal",
                "integrated_random_sd": random_sd,
                "config_indices": ";".join(map(str, config_indices)),
            }
            for cell, config_index in zip(CELL_ORDER, config_indices):
                row[f"p_{cell}"] = float(probabilities_true[config_index])
                row[f"cell_{cell}_n"] = int(observed[:, :, config_index].sum())
            pair_rows.append(row)
    pair_truth = pd.DataFrame(pair_rows)
    fixed_effects = pd.DataFrame([
        {
            "split": split, "scenario": scenario, "seed": seed,
            "term": "intercept" if not term else "*".join(map(str, term)),
            "term_order": len(term), "coefficient": coefficient,
        }
        for term, coefficient in coefficients.items()
    ])
    return SyntheticData(
        scenario=scenario, split=split, seeds=(seed,), config=config,
        observations=observations, pair_truth=pair_truth,
        fixed_effects=fixed_effects,
        task_parameters=pd.DataFrame(task_rows),
        block_parameters=pd.DataFrame(block_rows),
        metadata={
            "n_variables": N_VARIABLES, "modules": MODULES,
            "module_variables": module, "local_configs": LOCAL_CONFIGS,
            "cell_order": CELL_ORDER, "cell_bits": CELL_BITS,
            "delta_formula": "p_00-p_10-p_01+p_11",
            "label_rule": "abs(true_delta)>delta_local",
            "split_role": split, "seed": seed,
            "coding": "full 2^4 local module, other variables fixed at -1",
        },
    )


def generate_split(scenario, split, config=None, seeds=None):
    selected = SPLIT_SEEDS[split] if seeds is None else tuple(seeds)
    if not selected or len(set(selected)) != len(selected):
        raise ValueError("seeds must be nonempty and unique")
    datasets = [generate_seed(scenario, seed, split, config) for seed in selected]
    return SyntheticData(
        scenario=scenario, split=split, seeds=selected,
        config=datasets[0].config,
        observations=pd.concat([d.observations for d in datasets], ignore_index=True),
        pair_truth=pd.concat([d.pair_truth for d in datasets], ignore_index=True),
        fixed_effects=pd.concat([d.fixed_effects for d in datasets], ignore_index=True),
        task_parameters=pd.concat([d.task_parameters for d in datasets], ignore_index=True),
        block_parameters=pd.concat([d.block_parameters for d in datasets], ignore_index=True),
        metadata={**datasets[0].metadata, "seeds": selected},
    )


def extract_module_estimator_data(observations, module):
    module = tuple(module)
    columns = ["task_id", "block_id", "y"] + [f"x_{variable}" for variable in module]
    frame = observations.loc[:, columns].copy()
    frame.columns = ["task_id", "block_id", "y"] + [
        f"x_{local}" for local in range(len(module))
    ]
    return frame


def extract_four_cells(observations, pair, parent_id="parent_0", module=None):
    frame = observations.loc[observations["parent_id"] == parent_id].copy() if "parent_id" in observations else observations.copy()
    if "module_id" in observations:
        seed = int(frame["seed"].iloc[0])
        module = module_for_seed(seed)
    if module is None:
        raise ValueError("module is required when observations lack module_id")
    local_i, local_j = module.index(pair[0]), module.index(pair[1])
    others = [index for index in range(4) if index not in (local_i, local_j)]
    parent_value = -1 if parent_id.endswith("0") else 1
    configs = []
    for bit_i, bit_j in CELL_BITS:
        bits = [-1] * 4
        bits[local_i], bits[local_j] = 2 * bit_i - 1, 2 * bit_j - 1
        for index in others:
            bits[index] = parent_value
        configs.append(bits)
    all_bits = observations.loc[:, [f"x_{variable}" for variable in module]].to_numpy()
    mask = np.zeros(len(observations), dtype=bool)
    for bits in configs:
        mask |= np.all(all_bits == np.asarray(bits), axis=1)
    subset = observations.loc[mask, ["task_id", "block_id", "config_index", "y"]].copy()
    mapping = {index: cell for index, cell in zip(
        [LOCAL_CONFIG_INDEX[tuple(bits)] for bits in configs], CELL_ORDER)}
    subset["cell_id"] = subset["config_index"].map(mapping)
    return subset


__all__ = [
    "N_VARIABLES", "MODULES", "SCENARIOS", "SPLITS", "SPLIT_SEEDS",
    "SUPPORT_BLOCK_COUNTS", "LOCAL_CONFIGS", "CELL_ORDER", "CELL_BITS",
    "CELL_CONTRAST", "EFFECT_SCALES", "GeneratorConfig", "SyntheticData",
    "default_config", "module_for_seed", "generate_seed", "generate_split",
    "extract_module_estimator_data", "extract_four_cells",
]
