"""Shared four-cell task-block baselines for the TCAIL estimator gate.

The stochastic methods are explicit paper-setting adaptations, not complete
original-paper reproductions.  They expose pair scores and states for a common
builder; this module does not build a FOS, run GOM, or execute an EC algorithm.
"""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import math
from typing import Any, Dict, Hashable, Iterable, List, Mapping, Optional, Tuple

import numpy as np


Pair = Tuple[int, int]
Context = Hashable
ObservationKey = Tuple[int, int, Context]

CELL_ORDER = ("00", "10", "01", "11")
CONTRAST_COEFFICIENTS = (1.0, -1.0, -1.0, 1.0)

LOCAL_RAW = "local_raw_absolute_contrast"
STANDARDIZED = "standardized_contrast"
CONTEXT_POOLED = "context_pooled_signed_global"
FBL_ABSOLUTE = "fbl_absolute_ratio_adaptation"
FBL_SIGNED_EQ7 = "fbl_signed_eq7_diagnostic"
CDLED_P3M = "cdled_p3m_paper_setting_adaptation"
CGOMEA = "cgomea_compatible_conditional_linkage_adaptation"
RANDOM = "random_linkage"
ORACLE = "oracle_linkage"
ALL_METHODS = (
    LOCAL_RAW,
    STANDARDIZED,
    CONTEXT_POOLED,
    FBL_ABSOLUTE,
    FBL_SIGNED_EQ7,
    CDLED_P3M,
    CGOMEA,
    RANDOM,
    ORACLE,
)

_ADAPTATION = "Bernoulli task-block paper-setting adaptation; not an original-paper reproduction"


@dataclass(frozen=True)
class BaselineSettings:
    min_complete_blocks: int = 2
    standard_error_epsilon: float = 0.015
    fbl_epsilon: float = 0.0
    fbl_zero_denominator_tolerance: float = 1e-12
    dled_epsilon: float = 0.0
    delta_local: float = 0.0

    def __post_init__(self) -> None:
        if (
            isinstance(self.min_complete_blocks, bool)
            or not isinstance(self.min_complete_blocks, (int, np.integer))
            or self.min_complete_blocks < 1
        ):
            raise ValueError("min_complete_blocks must be a positive integer")
        for name in (
            "standard_error_epsilon",
            "fbl_epsilon",
            "fbl_zero_denominator_tolerance",
            "dled_epsilon",
            "delta_local",
        ):
            value = getattr(self, name)
            if not np.isfinite(value) or value < 0:
                raise ValueError(f"{name} must be finite and nonnegative")
        if self.fbl_zero_denominator_tolerance == 0:
            raise ValueError("fbl_zero_denominator_tolerance must be positive")


@dataclass(frozen=True)
class FourCellTaskBlock:
    """Rows are matched task blocks with cells ordered as 00, 10, 01, 11.

    Values are Bernoulli outcomes; NaN denotes an unobserved cell.  Optional
    compatibility fields are annotations only and never trigger EC execution.
    """

    pair: Pair
    context: Context
    outcomes: np.ndarray
    budget_episode_equivalents: Optional[float] = None
    probe_link_state: Optional[str] = None
    structure_compatible: Optional[bool] = None
    donor_compatible: Optional[bool] = None

    def __post_init__(self) -> None:
        object.__setattr__(self, "pair", _validate_pair(self.pair))
        if self.context is None:
            raise ValueError("context cannot be None; None is reserved for pooled output")
        hash(self.context)
        object.__setattr__(self, "outcomes", _coerce_outcomes(self.outcomes))
        budget = self.budget_episode_equivalents
        if budget is not None:
            budget = float(budget)
            if not np.isfinite(budget) or budget < 0:
                raise ValueError("budget_episode_equivalents must be finite and nonnegative")
            object.__setattr__(self, "budget_episode_equivalents", budget)
        if self.probe_link_state is not None:
            state = str(self.probe_link_state).strip().upper()
            if state not in {"COMPATIBLE", "INCOMPATIBLE", "UNVERIFIED"}:
                raise ValueError("probe_link_state must be COMPATIBLE, INCOMPATIBLE, or UNVERIFIED")
            object.__setattr__(self, "probe_link_state", state)
        for name in ("structure_compatible", "donor_compatible"):
            value = getattr(self, name)
            if value is not None:
                if not isinstance(value, (bool, np.bool_)):
                    raise ValueError(f"{name} must be bool or None")
                object.__setattr__(self, name, bool(value))

    @property
    def key(self) -> ObservationKey:
        return self.pair[0], self.pair[1], self.context


@dataclass(frozen=True)
class BaselineEstimate:
    pair: Pair
    context: Optional[Context]
    method: str
    score: float
    state: str
    metadata: Dict[str, Any]

    @property
    def eligible_for_common_builder(self) -> bool:
        return self.state == "OK" and math.isfinite(self.score) and self.score >= 0

    def as_dict(self) -> Dict[str, Any]:
        return {
            "pair_i": self.pair[0],
            "pair_j": self.pair[1],
            "context": self.context,
            "method": self.method,
            "score": self.score,
            "state": self.state,
            "eligible_for_common_builder": self.eligible_for_common_builder,
            "metadata": dict(self.metadata),
        }


@dataclass(frozen=True)
class _FourCellSummary:
    state: str
    n_task_blocks: int
    n_complete_blocks: int
    n_observed_cells: int
    budget_episode_equivalents: float
    contrasts: np.ndarray
    delta_i_j0: np.ndarray
    delta_i_j1: np.ndarray


def _validate_pair(pair: Pair) -> Pair:
    if len(pair) != 2:
        raise ValueError("pair must contain exactly two variable indices")
    i, j = pair
    if any(isinstance(value, bool) or not isinstance(value, (int, np.integer)) for value in pair):
        raise ValueError("pair indices must be integers")
    if not 0 <= i < j:
        raise ValueError("pair must satisfy 0 <= i < j")
    return int(i), int(j)


def _coerce_outcomes(outcomes: np.ndarray) -> np.ndarray:
    try:
        values = np.array(outcomes, dtype=float, copy=True)
    except (TypeError, ValueError) as exc:
        raise ValueError("outcomes must be a numeric array") from exc
    if values.ndim != 2 or values.shape[1] != 4:
        raise ValueError("outcomes must have shape (n_task_blocks, 4)")
    finite = np.isfinite(values)
    if np.any(~finite & ~np.isnan(values)):
        raise ValueError("outcomes cannot contain infinities")
    observed = values[finite]
    if np.any((observed != 0) & (observed != 1)):
        raise ValueError("observed outcomes must be Bernoulli values 0 or 1; use NaN for missing")
    values.setflags(write=False)
    return values


def _summarize(block: FourCellTaskBlock, settings: BaselineSettings) -> _FourCellSummary:
    values = block.outcomes
    complete = values[np.all(np.isfinite(values), axis=1)]
    contrasts = complete @ np.asarray(CONTRAST_COEFFICIENTS)
    delta_i_j0 = complete[:, 1] - complete[:, 0]
    delta_i_j1 = complete[:, 3] - complete[:, 2]
    n_observed = int(np.isfinite(values).sum())
    n_complete = int(complete.shape[0])
    if n_observed == 0:
        state = "ABSTAIN_NO_OBSERVATIONS"
    elif n_complete == 0:
        state = "ABSTAIN_MISSING_CELL"
    elif n_complete < settings.min_complete_blocks:
        state = "ABSTAIN_LOW_SUPPORT"
    else:
        state = "OK"
    budget = block.budget_episode_equivalents
    if budget is None:
        budget = float(n_observed)
    return _FourCellSummary(
        state=state,
        n_task_blocks=int(values.shape[0]),
        n_complete_blocks=n_complete,
        n_observed_cells=n_observed,
        budget_episode_equivalents=float(budget),
        contrasts=contrasts,
        delta_i_j0=delta_i_j0,
        delta_i_j1=delta_i_j1,
    )


def _shared_metadata(summary: _FourCellSummary) -> Dict[str, Any]:
    return {
        "cell_order": CELL_ORDER,
        "contrast_coefficients": CONTRAST_COEFFICIENTS,
        "contrast_formula": "y00 - y10 - y01 + y11",
        "observation_state": summary.state,
        "n_task_blocks": summary.n_task_blocks,
        "n_complete_blocks": summary.n_complete_blocks,
        "n_incomplete_blocks": summary.n_task_blocks - summary.n_complete_blocks,
        "n_observed_cells": summary.n_observed_cells,
        "budget_episode_equivalents": summary.budget_episode_equivalents,
        "budget_scope": "supplied pair/context input; no global de-duplication is performed",
        "support_policy": "complete matched task blocks only; incomplete rows are not imputed",
        "observations_shared_across_methods": True,
    }


def _result(
    pair: Pair,
    context: Optional[Context],
    method: str,
    score: float,
    state: str,
    metadata: Dict[str, Any],
) -> BaselineEstimate:
    return BaselineEstimate(pair, context, method, float(score), state, metadata)


def _abstain(
    pair: Pair,
    context: Optional[Context],
    method: str,
    summary: _FourCellSummary,
    metadata: Dict[str, Any],
) -> BaselineEstimate:
    return _result(pair, context, method, np.nan, summary.state, metadata)


def _local_raw(
    block: FourCellTaskBlock, summary: _FourCellSummary
) -> BaselineEstimate:
    metadata = _shared_metadata(summary)
    if summary.state != "OK":
        return _abstain(block.pair, block.context, LOCAL_RAW, summary, metadata)
    signed = float(np.mean(summary.contrasts))
    metadata["signed_contrast"] = signed
    return _result(block.pair, block.context, LOCAL_RAW, abs(signed), "OK", metadata)


def _standardized(
    block: FourCellTaskBlock,
    summary: _FourCellSummary,
    settings: BaselineSettings,
) -> BaselineEstimate:
    metadata = _shared_metadata(summary)
    metadata["standard_error_epsilon"] = settings.standard_error_epsilon
    if summary.state != "OK":
        return _abstain(block.pair, block.context, STANDARDIZED, summary, metadata)
    signed = float(np.mean(summary.contrasts))
    metadata["signed_contrast"] = signed
    if summary.n_complete_blocks < 2:
        metadata["standard_error"] = np.nan
        return _result(
            block.pair,
            block.context,
            STANDARDIZED,
            np.nan,
            "ABSTAIN_UNDEFINED_STANDARD_ERROR",
            metadata,
        )
    standard_error = float(np.std(summary.contrasts, ddof=1) / math.sqrt(summary.n_complete_blocks))
    denominator = standard_error + settings.standard_error_epsilon
    metadata["standard_error"] = standard_error
    metadata["denominator"] = denominator
    if not math.isfinite(denominator) or denominator <= 0:
        return _result(
            block.pair,
            block.context,
            STANDARDIZED,
            np.nan,
            "ABSTAIN_ZERO_STANDARD_ERROR",
            metadata,
        )
    return _result(
        block.pair,
        block.context,
        STANDARDIZED,
        abs(signed) / denominator,
        "OK",
        metadata,
    )


def _fbl_absolute(
    block: FourCellTaskBlock,
    summary: _FourCellSummary,
    settings: BaselineSettings,
) -> BaselineEstimate:
    metadata = _shared_metadata(summary)
    metadata.update(
        {
            "adaptation": _ADAPTATION,
            "formula": "1 - min(|Delta_i|, |Delta_i,j|) / max(|Delta_i|, |Delta_i,j|)",
            "epsilon": settings.fbl_epsilon,
            "limitations": (
                "Binary task-block means replace deterministic real-valued fitness perturbations.",
                "The epsilon gate is an adaptation; epsilon=0 provides the no-positive-threshold diagnostic.",
            ),
        }
    )
    if summary.state != "OK":
        return _abstain(block.pair, block.context, FBL_ABSOLUTE, summary, metadata)
    delta_i = float(np.mean(summary.delta_i_j0))
    delta_ij = float(np.mean(summary.delta_i_j1))
    denominator = max(abs(delta_i), abs(delta_ij))
    zero_denominator = denominator < settings.fbl_zero_denominator_tolerance
    ungated = (
        0.0
        if zero_denominator
        else 1.0 - min(abs(delta_i), abs(delta_ij)) / denominator
    )
    gate_difference = abs(delta_i - delta_ij)
    gate_passed = gate_difference >= settings.fbl_epsilon
    metadata.update(
        {
            "delta_i_j0": delta_i,
            "delta_i_j1": delta_ij,
            "gate_difference": gate_difference,
            "gate_passed": bool(gate_passed),
            "ungated_score": float(ungated),
            "zero_denominator_convention": bool(zero_denominator),
        }
    )
    score = ungated if gate_passed else 0.0
    return _result(block.pair, block.context, FBL_ABSOLUTE, score, "OK", metadata)


def fbl_signed_eq7_value(delta_i: float, delta_ij: float) -> float:
    """Evaluate the signed FBL Eq.(7) ratio without hiding invalid outputs."""
    delta_i = float(delta_i)
    delta_ij = float(delta_ij)
    if not math.isfinite(delta_i) or not math.isfinite(delta_ij):
        return np.nan
    if delta_i == 0.0 and delta_ij == 0.0:
        return 0.0
    if delta_i >= delta_ij:
        if delta_i == 0.0:
            return np.nan
        return 1.0 - delta_ij / delta_i
    if delta_ij == 0.0:
        return np.nan
    return 1.0 - delta_i / delta_ij


def _fbl_signed(
    block: FourCellTaskBlock, summary: _FourCellSummary
) -> BaselineEstimate:
    metadata = _shared_metadata(summary)
    metadata.update(
        {
            "adaptation": _ADAPTATION,
            "formula": "signed FBL Eq.(7)",
            "valid_domain": "finite and 0 <= score < 1",
            "valid_only_diagnostic": True,
            "limitations": (
                "Signed Eq.(7) is evaluated on Bernoulli task-block mean differences.",
                "Undefined or out-of-range values are domain violations, not valid linkage scores.",
                "Valid-only metrics exclude violations and are not a complete fair baseline result.",
            ),
        }
    )
    if summary.state != "OK":
        return _abstain(block.pair, block.context, FBL_SIGNED_EQ7, summary, metadata)
    delta_i = float(np.mean(summary.delta_i_j0))
    delta_ij = float(np.mean(summary.delta_i_j1))
    raw_score = fbl_signed_eq7_value(delta_i, delta_ij)
    metadata.update(
        {
            "delta_i_j0": delta_i,
            "delta_i_j1": delta_ij,
            "raw_score": raw_score,
            "gate_difference": abs(delta_i - delta_ij),
        }
    )
    if not math.isfinite(raw_score):
        metadata["domain_violation"] = True
        metadata["domain_violation_reason"] = "UNDEFINED_RATIO"
        return _result(
            block.pair,
            block.context,
            FBL_SIGNED_EQ7,
            np.nan,
            "DOMAIN_VIOLATION_UNDEFINED",
            metadata,
        )
    if raw_score < 0.0 or raw_score >= 1.0:
        metadata["domain_violation"] = True
        metadata["domain_violation_reason"] = "OUTSIDE_[0,1)"
        return _result(
            block.pair,
            block.context,
            FBL_SIGNED_EQ7,
            np.nan,
            "DOMAIN_VIOLATION_OUT_OF_RANGE",
            metadata,
        )
    metadata["domain_violation"] = False
    return _result(block.pair, block.context, FBL_SIGNED_EQ7, raw_score, "OK", metadata)


def _cdled(
    block: FourCellTaskBlock,
    summary: _FourCellSummary,
    settings: BaselineSettings,
) -> BaselineEstimate:
    probe_state = block.probe_link_state or "UNVERIFIED_FROM_STATIC_FOUR_CELLS"
    incompatible = probe_state == "INCOMPATIBLE" or block.structure_compatible is False
    if incompatible:
        structure_state = "INCOMPATIBLE"
    elif probe_state == "COMPATIBLE" and block.structure_compatible is True:
        structure_state = "COMPATIBLE"
    else:
        structure_state = "UNVERIFIED_FROM_STATIC_FOUR_CELLS"
    metadata = _shared_metadata(summary)
    metadata.update(
        {
            "adaptation": _ADAPTATION,
            "probe_link_state": probe_state,
            "structure_compatibility_state": structure_state,
            "structure_compatible_annotation": block.structure_compatible,
            "native_sll_dsm_cluster_builder_run": False,
            "p3m_search_run": False,
            "donor_restricted_gom_run": False,
            "limitations": (
                "Only individual-local four-point DLED and a conditional eVIG entry are adapted.",
                "Static four cells cannot verify a probe link or P3M structure without explicit annotations.",
                "SLL-DSM clusters, native P3M search, and donor-restricted mating are not executed.",
            ),
        }
    )
    if summary.state != "OK":
        return _abstain(block.pair, block.context, CDLED_P3M, summary, metadata)
    signed = float(np.mean(summary.contrasts))
    magnitude = abs(signed)
    detected = magnitude > settings.dled_epsilon
    metadata["individual_local_dled"] = {
        "signed_four_point_contrast": signed,
        "absolute_contrast": magnitude,
        "epsilon": settings.dled_epsilon,
        "detected": bool(detected),
    }
    if incompatible:
        metadata["conditional_evig"] = {
            "pair": block.pair,
            "context": block.context,
            "score": np.nan,
            "state": "ABSTAIN_STRUCTURE_INCOMPATIBLE",
        }
        return _result(
            block.pair,
            block.context,
            CDLED_P3M,
            np.nan,
            "ABSTAIN_STRUCTURE_INCOMPATIBLE",
            metadata,
        )
    score = magnitude if detected else 0.0
    metadata["conditional_evig"] = {
        "pair": block.pair,
        "context": block.context,
        "score": score,
        "state": "OK",
    }
    return _result(block.pair, block.context, CDLED_P3M, score, "OK", metadata)


def _cgomea(
    block: FourCellTaskBlock, summary: _FourCellSummary
) -> BaselineEstimate:
    if block.donor_compatible is None:
        donor_state = "UNVERIFIED_STATIC_GATE"
    elif block.donor_compatible:
        donor_state = "COMPATIBLE"
    else:
        donor_state = "INCOMPATIBLE"
    metadata = _shared_metadata(summary)
    metadata.update(
        {
            "adaptation": _ADAPTATION,
            "mating_donor_compatibility": {
                "state": donor_state,
                "compatible_annotation": block.donor_compatible,
                "interface": "caller-supplied annotation; no donor search or mating is performed",
                "downstream_inputs_required": (
                    "parent",
                    "donor",
                    "conditional_dependency",
                    "mixing_subset",
                ),
            },
            "native_conditional_builder_run": False,
            "conditional_variation_run": False,
            "gom_run": False,
            "limitations": (
                "The static gate exposes conditional dependency and mating/donor compatibility interfaces only.",
                "This is not CGOMEA, a native conditional FOS builder, or a complete EC algorithm.",
            ),
        }
    )
    if summary.state != "OK":
        return _abstain(block.pair, block.context, CGOMEA, summary, metadata)
    signed = float(np.mean(summary.contrasts))
    score = abs(signed)
    metadata["conditional_dependency"] = {
        "pair": block.pair,
        "context": block.context,
        "signed_contrast": signed,
        "absolute_contrast": score,
        "state": "OK",
    }
    return _result(block.pair, block.context, CGOMEA, score, "OK", metadata)


def _random(block: FourCellTaskBlock, seed: int) -> BaselineEstimate:
    context_key = f"{type(block.context).__module__}.{type(block.context).__qualname__}:{block.context!r}"
    payload = f"{seed}|{block.pair[0]}|{block.pair[1]}|{context_key}".encode("utf-8")
    derived_seed = int.from_bytes(hashlib.blake2b(payload, digest_size=8).digest(), "little")
    score = float(np.random.default_rng(derived_seed).random())
    metadata = {
        "independent_preregistered_seed": seed,
        "derived_pair_context_seed": derived_seed,
        "distribution": "Uniform[0,1), deterministic per pair/context",
        "uses_observations_for_score": False,
        "uses_true_delta_for_score": False,
    }
    return _result(block.pair, block.context, RANDOM, score, "OK", metadata)


def _oracle(
    block: FourCellTaskBlock,
    true_delta: Optional[float],
    settings: BaselineSettings,
) -> BaselineEstimate:
    metadata = {
        "source": "passed probability-scale true_delta only",
        "probability_scale": True,
        "uses_observations_for_score": False,
        "uses_random_seed_for_score": False,
        "delta_local": settings.delta_local,
        "upper_bound_diagnostic": True,
    }
    if true_delta is None:
        return _result(
            block.pair,
            block.context,
            ORACLE,
            np.nan,
            "ABSTAIN_MISSING_TRUE_DELTA",
            metadata,
        )
    value = float(true_delta)
    metadata["signed_true_delta"] = value
    if math.isnan(value):
        return _result(
            block.pair,
            block.context,
            ORACLE,
            np.nan,
            "ABSTAIN_MISSING_TRUE_DELTA",
            metadata,
        )
    if not math.isfinite(value) or abs(value) > 2.0:
        metadata["domain_violation"] = True
        metadata["valid_domain"] = "finite probability-scale four-cell contrast in [-2, 2]"
        return _result(
            block.pair,
            block.context,
            ORACLE,
            np.nan,
            "DOMAIN_VIOLATION_TRUE_DELTA",
            metadata,
        )
    metadata["domain_violation"] = False
    metadata["practical_link"] = bool(abs(value) > settings.delta_local)
    return _result(block.pair, block.context, ORACLE, abs(value), "OK", metadata)


def _context_pooled(
    pair: Pair,
    members: List[Tuple[FourCellTaskBlock, _FourCellSummary]],
) -> BaselineEstimate:
    used = [(block, summary) for block, summary in members if summary.state == "OK"]
    excluded = [
        {
            "context": block.context,
            "state": summary.state,
            "n_complete_blocks": summary.n_complete_blocks,
        }
        for block, summary in members
        if summary.state != "OK"
    ]
    metadata: Dict[str, Any] = {
        "cell_order": CELL_ORDER,
        "contrast_coefficients": CONTRAST_COEFFICIENTS,
        "contrast_formula": "y00 - y10 - y01 + y11",
        "observations_shared_across_methods": True,
        "n_contexts_total": len(members),
        "n_contexts_used": len(used),
        "excluded_contexts": excluded,
        "input_budgets_episode_equivalents": {
            block.context: summary.budget_episode_equivalents for block, summary in members
        },
        "budget_scope": "input budgets are reported separately and not summed into a global cost",
        "score_definition": "absolute signed mean over all complete blocks from supported contexts",
        "global_rms_definition": "equal-context RMS of supported context-level signed mean contrasts",
    }
    if not used:
        return _result(
            pair,
            None,
            CONTEXT_POOLED,
            np.nan,
            "ABSTAIN_NO_SUPPORTED_CONTEXT",
            metadata,
        )
    contrasts = np.concatenate([summary.contrasts for _, summary in used])
    signed = float(np.mean(contrasts))
    context_means = {
        block.context: float(np.mean(summary.contrasts)) for block, summary in used
    }
    global_rms = float(np.sqrt(np.mean(np.square(list(context_means.values())))))
    metadata["pooled_signed_mean"] = signed
    metadata["context_signed_means"] = context_means
    metadata["global_rms"] = global_rms
    metadata["n_complete_blocks"] = int(contrasts.size)
    return _result(pair, None, CONTEXT_POOLED, abs(signed), "OK", metadata)


def estimate_baselines(
    blocks: Iterable[FourCellTaskBlock],
    *,
    random_seed: int,
    true_deltas: Optional[Mapping[ObservationKey, Optional[float]]] = None,
    settings: Optional[BaselineSettings] = None,
) -> List[BaselineEstimate]:
    """Estimate all baselines from the same observations and input budgets.

    Random linkage is keyed only by its independent preregistered seed and the
    pair/context.  Oracle linkage is keyed only by the separately supplied
    probability-scale true_delta.  Neither uses the other method's information.
    """
    if isinstance(random_seed, bool) or not isinstance(random_seed, (int, np.integer)):
        raise ValueError("random_seed must be a nonnegative integer")
    if random_seed < 0:
        raise ValueError("random_seed must be a nonnegative integer")
    settings = BaselineSettings() if settings is None else settings
    block_list = list(blocks)
    if not block_list:
        raise ValueError("at least one FourCellTaskBlock is required")
    if any(not isinstance(block, FourCellTaskBlock) for block in block_list):
        raise TypeError("blocks must contain only FourCellTaskBlock instances")
    keys = [block.key for block in block_list]
    if len(set(keys)) != len(keys):
        raise ValueError("each pair/context input must be unique")
    block_list.sort(key=lambda block: (block.pair, repr(block.context)))
    summaries = {block.key: _summarize(block, settings) for block in block_list}
    truth = {} if true_deltas is None else true_deltas

    estimates: List[BaselineEstimate] = []
    for block in block_list:
        summary = summaries[block.key]
        estimates.extend(
            (
                _local_raw(block, summary),
                _standardized(block, summary, settings),
                _fbl_absolute(block, summary, settings),
                _fbl_signed(block, summary),
                _cdled(block, summary, settings),
                _cgomea(block, summary),
            )
        )
        for estimate in (_random(block, int(random_seed)), _oracle(block, truth.get(block.key), settings)):
            metadata = _shared_metadata(summary)
            metadata.update(estimate.metadata)
            estimates.append(
                _result(
                    estimate.pair,
                    estimate.context,
                    estimate.method,
                    estimate.score,
                    estimate.state,
                    metadata,
                )
            )

    pairs = sorted({block.pair for block in block_list})
    for pair in pairs:
        members = [
            (block, summaries[block.key])
            for block in block_list
            if block.pair == pair
        ]
        estimates.append(_context_pooled(pair, members))
    return estimates


__all__ = [
    "ALL_METHODS",
    "BaselineEstimate",
    "BaselineSettings",
    "CDLED_P3M",
    "CGOMEA",
    "CONTRAST_COEFFICIENTS",
    "CONTEXT_POOLED",
    "CELL_ORDER",
    "FBL_ABSOLUTE",
    "FBL_SIGNED_EQ7",
    "FourCellTaskBlock",
    "LOCAL_RAW",
    "ORACLE",
    "RANDOM",
    "STANDARDIZED",
    "estimate_baselines",
    "fbl_signed_eq7_value",
]
