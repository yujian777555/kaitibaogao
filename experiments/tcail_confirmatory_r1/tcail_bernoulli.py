"""Joint Laplace approximation for the TCAIL Bernoulli task/block model.

This is a small/medium-design research prototype, not exact MCMC and not a
calibrated confirmatory analysis.  The Laplace approximation is over fixed
effects, observed task/block latent intercepts, and log variance components
jointly.  Parent-local contrasts use new-task/new-block predictive random
effects and are computed on the probability scale for every posterior draw.
"""

from __future__ import annotations

from dataclasses import dataclass
from itertools import combinations
import math
import re
from typing import Dict, Mapping, Optional, Sequence, Tuple

import numpy as np
import pandas as pd
from scipy import optimize
from scipy.special import expit, gammaln


Pair = Tuple[int, int]
_CELL_LABELS = ("++", "+-", "-+", "--")
_CELL_VALUES = ((1, 1), (1, -1), (-1, 1), (-1, -1))
_CELL_CONTRAST = np.array([1.0, -1.0, -1.0, 1.0])


@dataclass(frozen=True)
class BernoulliPrior:
    """Model-order Normal priors and explicit variance-component priors.

    The default independent Normal priors are directly on log sigma.  Setting
    ``sigma_prior='half_student_t'`` instead puts Half-Student-t priors on
    sigma and includes the log-coordinate Jacobian.  The latter can make a
    joint-latent MAP degenerate as sigma approaches zero; such fits abstain.
    Defaults are computational starting points, not calibrated values.
    """

    intercept_scale: float = 5.0
    main_scale: float = 2.5
    pair_scale: float = 1.0
    three_way_scale: float = 1.0
    sigma_prior: str = "normal"
    task_log_sigma_mean: float = -1.0
    task_log_sigma_sd: float = 0.5
    block_log_sigma_mean: float = -1.0
    block_log_sigma_sd: float = 0.5
    task_sigma_df: float = 3.0
    task_sigma_scale: float = 2.5
    block_sigma_df: float = 3.0
    block_sigma_scale: float = 2.5

    def __post_init__(self) -> None:
        if self.sigma_prior not in ("normal", "half_student_t"):
            raise ValueError("sigma_prior must be 'normal' or 'half_student_t'")
        for name in ("task_log_sigma_mean", "block_log_sigma_mean"):
            if not np.isfinite(getattr(self, name)):
                raise ValueError(f"{name} must be finite")
        for name in (
            "intercept_scale",
            "main_scale",
            "pair_scale",
            "three_way_scale",
            "task_log_sigma_sd",
            "block_log_sigma_sd",
            "task_sigma_df",
            "task_sigma_scale",
            "block_sigma_df",
            "block_sigma_scale",
        ):
            value = getattr(self, name)
            if not np.isfinite(value) or value <= 0:
                raise ValueError(f"{name} must be finite and positive")

    def fixed_effect_scales(self, terms: Sequence[Tuple[int, ...]]) -> np.ndarray:
        by_order = {
            0: self.intercept_scale,
            1: self.main_scale,
            2: self.pair_scale,
            3: self.three_way_scale,
        }
        return np.array([by_order[len(term)] for term in terms], dtype=float)


@dataclass(frozen=True)
class LaplaceSettings:
    n_draws: int = 400
    seed: int = 0
    maxiter: int = 1000
    initial_sigma: float = 0.5
    optimizer_gtol: float = 1e-6
    gradient_tol: float = 1e-4
    eigen_tol: float = 1e-9
    max_condition: float = 1e12

    def __post_init__(self) -> None:
        if self.n_draws < 1 or self.maxiter < 1:
            raise ValueError("n_draws and maxiter must be positive integers")
        if self.seed < 0:
            raise ValueError("seed must be nonnegative")
        for name in (
            "initial_sigma",
            "optimizer_gtol",
            "gradient_tol",
            "eigen_tol",
            "max_condition",
        ):
            value = getattr(self, name)
            if not np.isfinite(value) or value <= 0:
                raise ValueError(f"{name} must be finite and positive")


@dataclass(frozen=True)
class PredictiveSettings:
    """Random-intercept MC integration for the frozen anchor task distribution."""

    n_draws: int = 64
    seed: int = 1
    antithetic: bool = True

    def __post_init__(self) -> None:
        if self.n_draws < 1:
            raise ValueError("n_draws must be a positive integer")
        if self.seed < 0:
            raise ValueError("seed must be nonnegative")


@dataclass
class LaplaceDiagnostics:
    optimizer_success: bool
    converged: bool
    status: int
    message: str
    n_iterations: int
    n_function_evaluations: int
    objective: float
    gradient_max_abs: float
    gradient_norm: float
    hessian_rank: int
    hessian_dimension: int
    hessian_min_eigenvalue: float
    hessian_max_eigenvalue: float
    condition_number: float
    failure_reason: str = ""

    @property
    def fit_ok(self) -> bool:
        return self.converged and not self.failure_reason


@dataclass
class LaplaceFit:
    model_order: int
    x_columns: Tuple[str, ...]
    terms: Tuple[Tuple[int, ...], ...]
    parameter_names: Tuple[str, ...]
    mode: np.ndarray
    covariance: Optional[np.ndarray]
    posterior_draws: Optional[np.ndarray]
    diagnostics: LaplaceDiagnostics
    n_tasks: int
    n_blocks: int

    @property
    def n_fixed(self) -> int:
        return len(self.terms)

    @property
    def fit_ok(self) -> bool:
        return self.diagnostics.fit_ok and self.posterior_draws is not None


@dataclass
class TcailBernoulliResult:
    model_order: int
    parent: Dict[str, int]
    fit: LaplaceFit
    pair_results: pd.DataFrame
    delta_draws: Dict[Pair, np.ndarray]
    predictive_settings: PredictiveSettings


def bernoulli_log_likelihood(y: np.ndarray, eta: np.ndarray) -> float:
    """Stable row-wise Bernoulli log likelihood evaluated at linear predictors."""
    y = np.asarray(y, dtype=float)
    eta = np.asarray(eta, dtype=float)
    if y.shape != eta.shape:
        raise ValueError("y and eta must have identical shapes")
    if not np.all(np.isfinite(y)) or not np.all((y == 0) | (y == 1)):
        raise ValueError("y must contain only finite binary values")
    if not np.all(np.isfinite(eta)):
        raise ValueError("eta must be finite")
    return float(np.sum(y * eta - np.logaddexp(0.0, eta)))


def walsh_terms(n_variables: int, model_order: int) -> Tuple[Tuple[int, ...], ...]:
    """Intercept, every main/pair term, and (for M3) every three-way term."""
    if n_variables < 2:
        raise ValueError("at least two binary variables are required")
    if model_order not in (2, 3):
        raise ValueError("model_order must be 2 or 3")
    if model_order == 3 and n_variables < 3:
        raise ValueError("M3 requires at least three variables")
    terms = [()]
    for order in range(1, model_order + 1):
        terms.extend(combinations(range(n_variables), order))
    return tuple(terms)


def walsh_design(
    x: np.ndarray, terms: Sequence[Tuple[int, ...]]
) -> np.ndarray:
    x = np.asarray(x, dtype=float)
    if x.ndim != 2 or not np.all(np.isfinite(x)) or not np.all(np.abs(x) == 1):
        raise ValueError("x must be a finite two-dimensional array in {-1,+1}")
    columns = []
    for term in terms:
        if not term:
            columns.append(np.ones(x.shape[0]))
        elif max(term) >= x.shape[1] or min(term) < 0:
            raise ValueError("term index is outside x")
        else:
            columns.append(np.prod(x[:, term], axis=1))
    if not columns:
        raise ValueError("terms cannot be empty")
    return np.column_stack(columns)


def walsh_design_matrix(
    x: np.ndarray, model_order: int
) -> Tuple[np.ndarray, Tuple[str, ...]]:
    terms = walsh_terms(x.shape[1], model_order)
    names = tuple(
        "intercept" if not term else "*".join(f"x_{i}" for i in term)
        for term in terms
    )
    return walsh_design(x, terms), names


def _half_t_log_sigma_logpdf(log_sigma: float, df: float, scale: float) -> float:
    log_normalizer = (
        math.log(2.0)
        + float(gammaln((df + 1.0) / 2.0) - gammaln(df / 2.0))
        - 0.5 * math.log(df * math.pi)
        - math.log(scale)
    )
    log_quadratic = 2.0 * log_sigma - math.log(df * scale * scale)
    log_density_sigma = log_normalizer - 0.5 * (df + 1.0) * float(
        np.logaddexp(0.0, log_quadratic)
    )
    return log_density_sigma + log_sigma


class _JointPosterior:
    def __init__(
        self,
        x: np.ndarray,
        z_task: np.ndarray,
        z_block: np.ndarray,
        y: np.ndarray,
        fixed_scales: np.ndarray,
        prior: BernoulliPrior,
    ) -> None:
        self.a = np.column_stack((x, z_task, z_block))
        self.y = y
        self.n_fixed = x.shape[1]
        self.n_tasks = z_task.shape[1]
        self.n_blocks = z_block.shape[1]
        self.n_latent = self.a.shape[1]
        self.fixed_scales = fixed_scales
        self.prior = prior
        self.fixed_precision = fixed_scales**-2

    def objective_gradient(self, theta: np.ndarray) -> Tuple[float, np.ndarray]:
        p = self.n_fixed
        t = self.n_tasks
        b = self.n_blocks
        u = theta[p : p + t]
        v = theta[p + t : p + t + b]
        log_sigma_t = theta[-2]
        log_sigma_b = theta[-1]
        precision_t = math.exp(-2.0 * log_sigma_t)
        precision_b = math.exp(-2.0 * log_sigma_b)
        eta = self.a @ theta[: self.n_latent]
        ll = bernoulli_log_likelihood(self.y, eta)

        beta = theta[:p]
        objective = -ll + float(
            np.sum(
                0.5 * (beta / self.fixed_scales) ** 2
                + np.log(self.fixed_scales)
                + 0.5 * math.log(2.0 * math.pi)
            )
        )
        objective += (
            0.5 * precision_t * float(u @ u)
            + t * log_sigma_t
            + 0.5 * t * math.log(2.0 * math.pi)
            + 0.5 * precision_b * float(v @ v)
            + b * log_sigma_b
            + 0.5 * b * math.log(2.0 * math.pi)
        )
        if self.prior.sigma_prior == "normal":
            objective += (
                0.5 * ((log_sigma_t - self.prior.task_log_sigma_mean) / self.prior.task_log_sigma_sd) ** 2
                + math.log(self.prior.task_log_sigma_sd)
                + 0.5 * ((log_sigma_b - self.prior.block_log_sigma_mean) / self.prior.block_log_sigma_sd) ** 2
                + math.log(self.prior.block_log_sigma_sd)
                + math.log(2.0 * math.pi)
            )
        else:
            objective -= _half_t_log_sigma_logpdf(
                log_sigma_t, self.prior.task_sigma_df, self.prior.task_sigma_scale
            )
            objective -= _half_t_log_sigma_logpdf(
                log_sigma_b, self.prior.block_sigma_df, self.prior.block_sigma_scale
            )

        gradient = np.zeros_like(theta)
        residual = expit(eta) - self.y
        gradient[: self.n_latent] = self.a.T @ residual
        gradient[:p] += self.fixed_precision * beta
        gradient[p : p + t] += precision_t * u
        gradient[p + t : p + t + b] += precision_b * v

        for index, values, precision, count, mean, sd, df, scale in (
            (-2, u, precision_t, t, self.prior.task_log_sigma_mean, self.prior.task_log_sigma_sd, self.prior.task_sigma_df, self.prior.task_sigma_scale),
            (-1, v, precision_b, b, self.prior.block_log_sigma_mean, self.prior.block_log_sigma_sd, self.prior.block_sigma_df, self.prior.block_sigma_scale),
        ):
            base = count - precision * float(values @ values)
            if self.prior.sigma_prior == "normal":
                gradient[index] = base + (theta[index] - mean) / sd**2
            else:
                fraction = float(expit(2.0 * theta[index] - math.log(df * scale * scale)))
                gradient[index] = base - 1.0 + (df + 1.0) * fraction
        return float(objective), gradient

    def hessian(self, theta: np.ndarray) -> np.ndarray:
        p = self.n_fixed
        t = self.n_tasks
        b = self.n_blocks
        u = theta[p : p + t]
        v = theta[p + t : p + t + b]
        eta = self.a @ theta[: self.n_latent]
        probabilities = expit(eta)
        weights = probabilities * (1.0 - probabilities)
        dimension = theta.size
        hessian = np.zeros((dimension, dimension))
        hessian[: self.n_latent, : self.n_latent] = self.a.T @ (
            weights[:, None] * self.a
        )
        diagonal = np.zeros(dimension)
        diagonal[:p] = self.fixed_precision
        precision_t = math.exp(-2.0 * theta[-2])
        precision_b = math.exp(-2.0 * theta[-1])
        diagonal[p : p + t] = precision_t
        diagonal[p + t : p + t + b] = precision_b
        hessian += np.diag(diagonal)

        for index, start, values, precision, sd, df, scale in (
            (-2, p, u, precision_t, self.prior.task_log_sigma_sd, self.prior.task_sigma_df, self.prior.task_sigma_scale),
            (-1, p + t, v, precision_b, self.prior.block_log_sigma_sd, self.prior.block_sigma_df, self.prior.block_sigma_scale),
        ):
            cross = -2.0 * precision * values
            hessian[index, start : start + values.size] = cross
            hessian[start : start + values.size, index] = cross
            latent_curvature = 2.0 * precision * float(values @ values)
            if self.prior.sigma_prior == "normal":
                hessian[index, index] = sd**-2 + latent_curvature
            else:
                fraction = float(expit(2.0 * theta[index] - math.log(df * scale * scale)))
                hessian[index, index] = (
                    2.0 * (df + 1.0) * fraction * (1.0 - fraction)
                    + latent_curvature
                )
        return hessian


class _NoncenteredJointPosterior:
    """Equivalent joint posterior with z=u/sigma, avoiding the variance funnel."""

    def __init__(self, x, z_task, z_block, y, fixed_scales, prior):
        self.x = x
        self.z_task = z_task
        self.z_block = z_block
        self.y = y
        self.n_fixed = x.shape[1]
        self.n_tasks = z_task.shape[1]
        self.n_blocks = z_block.shape[1]
        self.n_latent = self.n_fixed + self.n_tasks + self.n_blocks
        self.fixed_scales = np.asarray(fixed_scales, dtype=float)
        self.prior = prior

    def _components(self, theta):
        p, t = self.n_fixed, self.n_tasks
        beta = theta[:p]
        z_t = theta[p:p + t]
        z_b = theta[p + t:p + t + self.n_blocks]
        log_sigma_t, log_sigma_b = theta[-2], theta[-1]
        sigma_t, sigma_b = math.exp(log_sigma_t), math.exp(log_sigma_b)
        eta = (self.x @ beta
               + sigma_t * (self.z_task @ z_t)
               + sigma_b * (self.z_block @ z_b))
        design = np.column_stack((
            self.x,
            sigma_t * self.z_task,
            sigma_b * self.z_block,
            sigma_t * (self.z_task @ z_t),
            sigma_b * (self.z_block @ z_b),
        ))
        return eta, design, beta, z_t, z_b, log_sigma_t, log_sigma_b, sigma_t, sigma_b

    def _sigma_prior(self, theta, index):
        if self.prior.sigma_prior == "normal":
            if index == -2:
                mean, sd = self.prior.task_log_sigma_mean, self.prior.task_log_sigma_sd
            else:
                mean, sd = self.prior.block_log_sigma_mean, self.prior.block_log_sigma_sd
            return (theta[index] - mean) / sd**2, sd**-2
        df = self.prior.task_sigma_df if index == -2 else self.prior.block_sigma_df
        scale = (self.prior.task_sigma_scale if index == -2
                 else self.prior.block_sigma_scale)
        fraction = float(expit(2 * theta[index] - math.log(df * scale * scale)))
        gradient = -1.0 + (df + 1.0) * fraction
        hessian = 2.0 * (df + 1.0) * fraction * (1.0 - fraction)
        return gradient, hessian

    def objective_gradient(self, theta):
        p, t = self.n_fixed, self.n_tasks
        eta, design, beta, z_t, z_b, _, _, _, _ = self._components(theta)
        objective = -bernoulli_log_likelihood(self.y, eta)
        objective += float(np.sum(
            0.5 * (beta / self.fixed_scales) ** 2
            + np.log(self.fixed_scales) + 0.5 * math.log(2 * math.pi)))
        objective += 0.5 * float(z_t @ z_t) + 0.5 * float(z_b @ z_b)
        if self.prior.sigma_prior == "normal":
            for index, mean, sd in (
                (-2, self.prior.task_log_sigma_mean, self.prior.task_log_sigma_sd),
                (-1, self.prior.block_log_sigma_mean, self.prior.block_log_sigma_sd),
            ):
                objective += (0.5 * ((theta[index] - mean) / sd) ** 2
                              + math.log(sd) + 0.5 * math.log(2 * math.pi))
        else:
            objective -= _half_t_log_sigma_logpdf(
                theta[-2], self.prior.task_sigma_df, self.prior.task_sigma_scale)
            objective -= _half_t_log_sigma_logpdf(
                theta[-1], self.prior.block_sigma_df, self.prior.block_sigma_scale)
        residual = expit(eta) - self.y
        gradient = design.T @ residual
        gradient[:p] += beta / self.fixed_scales**2
        gradient[p:p + t] += z_t
        gradient[p + t:p + t + self.n_blocks] += z_b
        for index in (-2, -1):
            gradient[index] += self._sigma_prior(theta, index)[0]
        return float(objective), gradient

    def hessian(self, theta):
        p, t = self.n_fixed, self.n_tasks
        eta, design, _, z_t, z_b, _, _, sigma_t, sigma_b = self._components(theta)
        probabilities = expit(eta)
        weights = probabilities * (1 - probabilities)
        hessian = design.T @ (weights[:, None] * design)
        diagonal = np.zeros(theta.size)
        diagonal[:p] = self.fixed_scales**-2
        diagonal[p:p + t] = 1.0
        diagonal[p + t:p + t + self.n_blocks] = 1.0
        hessian += np.diag(diagonal)
        residual = probabilities - self.y
        extra_t = sigma_t * (self.z_task.T @ residual)
        extra_b = sigma_b * (self.z_block.T @ residual)
        hessian[p:p + t, -2] += extra_t
        hessian[-2, p:p + t] += extra_t
        hessian[p + t:p + t + self.n_blocks, -1] += extra_b
        hessian[-1, p + t:p + t + self.n_blocks] += extra_b
        hessian[-2, -2] += float(sigma_t * z_t @ (self.z_task.T @ residual))
        hessian[-1, -1] += float(sigma_b * z_b @ (self.z_block.T @ residual))
        for index in (-2, -1):
            hessian[index, index] += self._sigma_prior(theta, index)[1]
        return hessian

    def transform_original(self, theta):
        p, t = self.n_fixed, self.n_tasks
        transformed = np.array(theta, copy=True)
        log_sigma_t, log_sigma_b = theta[-2], theta[-1]
        sigma_t, sigma_b = math.exp(log_sigma_t), math.exp(log_sigma_b)
        transformed[p:p + t] = sigma_t * theta[p:p + t]
        transformed[p + t:p + t + self.n_blocks] = (
            sigma_b * theta[p + t:p + t + self.n_blocks])
        jacobian = np.eye(theta.size)
        jacobian[p:p + t, p:p + t] = sigma_t * np.eye(t)
        jacobian[p:p + t, -2] = transformed[p:p + t]
        jacobian[p + t:p + t + self.n_blocks,
                 p + t:p + t + self.n_blocks] = sigma_b * np.eye(self.n_blocks)
        jacobian[p + t:p + t + self.n_blocks, -1] = (
            transformed[p + t:p + t + self.n_blocks])
        return transformed, jacobian


def _prepare_data(
    data: pd.DataFrame,
) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray, Tuple[str, ...], np.ndarray, np.ndarray]:
    if not isinstance(data, pd.DataFrame) or data.empty:
        raise ValueError("data must be a nonempty pandas DataFrame")
    indexed_columns = []
    for column in data.columns:
        match = re.fullmatch(r"x_(\d+)", str(column))
        if match:
            indexed_columns.append((int(match.group(1)), str(column)))
    indexed_columns.sort()
    if not indexed_columns or [i for i, _ in indexed_columns] != list(
        range(len(indexed_columns))
    ):
        raise ValueError("design columns must be contiguous x_0,...,x_{m-1}")
    x_columns = tuple(column for _, column in indexed_columns)
    required = ("task_id", "block_id", "y") + x_columns
    missing = [column for column in required if column not in data.columns]
    if missing:
        raise ValueError(f"missing required columns: {missing}")
    if data[["task_id", "block_id"]].isna().any().any():
        raise ValueError("task_id and block_id cannot be missing")
    try:
        x = data.loc[:, x_columns].to_numpy(dtype=float)
        y = data["y"].to_numpy(dtype=float)
    except (TypeError, ValueError) as exc:
        raise ValueError("x and y columns must be numeric") from exc
    if not np.all(np.isfinite(x)) or not np.all(np.abs(x) == 1):
        raise ValueError("every design value must be -1 or +1")
    if not np.all(np.isfinite(y)) or not np.all((y == 0) | (y == 1)):
        raise ValueError("y must contain only 0 or 1")

    task_codes, task_levels = pd.factorize(data["task_id"], sort=True)
    block_codes, block_levels = pd.factorize(data["block_id"], sort=True)
    block_task = np.full(len(block_levels), -1, dtype=int)
    for task_code, block_code in zip(task_codes, block_codes):
        if block_task[block_code] < 0:
            block_task[block_code] = task_code
        elif block_task[block_code] != task_code:
            raise ValueError("each block_id must be nested within exactly one task_id")
    z_task = np.eye(len(task_levels))[task_codes]
    z_block = np.eye(len(block_levels))[block_codes]
    return (
        x,
        z_task,
        z_block,
        y,
        task_codes,
        x_columns,
        np.asarray(task_levels, dtype=object),
        np.asarray(block_levels, dtype=object),
    )


def _failed_diagnostics(message: str, dimension: int) -> LaplaceDiagnostics:
    return LaplaceDiagnostics(
        optimizer_success=False,
        converged=False,
        status=-1,
        message=message,
        n_iterations=0,
        n_function_evaluations=0,
        objective=np.nan,
        gradient_max_abs=np.nan,
        gradient_norm=np.nan,
        hessian_rank=0,
        hessian_dimension=dimension,
        hessian_min_eigenvalue=np.nan,
        hessian_max_eigenvalue=np.nan,
        condition_number=np.inf,
        failure_reason="NUMERICAL_FAILURE",
    )


def fit_bernoulli_laplace(
    data: pd.DataFrame,
    model_order: int = 2,
    prior: Optional[BernoulliPrior] = None,
    settings: Optional[LaplaceSettings] = None,
) -> LaplaceFit:
    """Fit one M2/M3 joint MAP and its explicit Laplace approximation."""
    prior = BernoulliPrior() if prior is None else prior
    settings = LaplaceSettings() if settings is None else settings
    (
        x,
        z_task,
        z_block,
        y,
        _,
        x_columns,
        task_levels,
        block_levels,
    ) = _prepare_data(data)
    terms = walsh_terms(x.shape[1], model_order)
    design = walsh_design(x, terms)
    coefficient_names = tuple(
        "intercept" if not term else "*".join(f"x_{i}" for i in term)
        for term in terms
    )
    parameter_names = (
        tuple(f"beta[{name}]" for name in coefficient_names)
        + tuple(f"u[{task}]" for task in task_levels)
        + tuple(f"v[{block}]" for block in block_levels)
        + ("log_sigma_task", "log_sigma_block")
    )
    posterior = _NoncenteredJointPosterior(
        design,
        z_task,
        z_block,
        y,
        prior.fixed_effect_scales(terms),
        prior,
    )
    n_fixed = len(terms)
    dimension = n_fixed + z_task.shape[1] + z_block.shape[1] + 2
    initial = np.zeros(dimension)
    mean_y = float(np.clip(np.mean(y), 1e-6, 1.0 - 1e-6))
    initial[0] = math.log(mean_y / (1.0 - mean_y))
    initial[-2:] = math.log(settings.initial_sigma)

    try:
        result = optimize.minimize(
            posterior.objective_gradient,
            initial,
            method="L-BFGS-B",
            jac=True,
            options={
                "maxiter": settings.maxiter,
                "gtol": settings.optimizer_gtol,
                "ftol": 1e-14,
                "maxls": 50,
            },
        )
        mode_noncentered = np.asarray(result.x, dtype=float)
        mode, transform_jacobian = posterior.transform_original(mode_noncentered)
        _, gradient = posterior.objective_gradient(mode_noncentered)
        objective = float(result.fun)
        diagnostics = LaplaceDiagnostics(
            optimizer_success=bool(result.success),
            converged=bool(result.success),
            status=int(result.status),
            message=str(result.message),
            n_iterations=int(result.nit),
            n_function_evaluations=int(result.nfev),
            objective=objective,
            gradient_max_abs=float(np.max(np.abs(gradient))),
            gradient_norm=float(np.linalg.norm(gradient)),
            hessian_rank=0,
            hessian_dimension=dimension,
            hessian_min_eigenvalue=np.nan,
            hessian_max_eigenvalue=np.nan,
            condition_number=np.inf,
        )
    except (ArithmeticError, FloatingPointError, ValueError) as exc:
        diagnostics = _failed_diagnostics(str(exc), dimension)
        return LaplaceFit(
            model_order,
            x_columns,
            terms,
            parameter_names,
            initial,
            None,
            None,
            diagnostics,
            z_task.shape[1],
            z_block.shape[1],
        )

    if not np.all(np.isfinite(mode)) or not np.isfinite(objective):
        diagnostics.failure_reason = "NUMERICAL_FAILURE"
    if not result.success:
        diagnostics.failure_reason = "NONCONVERGENCE"
    elif diagnostics.gradient_max_abs > settings.gradient_tol:
        diagnostics.failure_reason = "GRADIENT_TOLERANCE"

    covariance = None
    draws = None
    try:
        hessian = posterior.hessian(mode_noncentered)
        if not np.all(np.isfinite(hessian)):
            raise ValueError("nonfinite Hessian")
        eigenvalues, eigenvectors = np.linalg.eigh(hessian)
        largest = float(np.max(eigenvalues))
        smallest = float(np.min(eigenvalues))
        threshold = settings.eigen_tol * max(1.0, largest)
        rank = int(np.sum(eigenvalues > threshold))
        diagnostics.hessian_rank = rank
        diagnostics.hessian_min_eigenvalue = smallest
        diagnostics.hessian_max_eigenvalue = largest
        diagnostics.condition_number = (
            float(largest / smallest) if smallest > 0 else np.inf
        )
        if not diagnostics.failure_reason:
            if rank != dimension or smallest <= threshold:
                diagnostics.failure_reason = "HESSIAN_RANK_DEFICIENT"
            elif diagnostics.condition_number > settings.max_condition:
                diagnostics.failure_reason = "HESSIAN_ILL_CONDITIONED"
        if diagnostics.fit_ok:
            covariance_noncentered = (eigenvectors / eigenvalues) @ eigenvectors.T
            covariance = (transform_jacobian @ covariance_noncentered
                          @ transform_jacobian.T)
            covariance = 0.5 * (covariance + covariance.T)
            rng = np.random.default_rng(settings.seed)
            standard = rng.standard_normal((settings.n_draws, dimension))
            draws_noncentered = (
                mode_noncentered
                + (standard / np.sqrt(eigenvalues)) @ eigenvectors.T)
            draws = mode + (draws_noncentered - mode_noncentered) @ transform_jacobian.T
            if not np.all(np.isfinite(draws)) or not np.all(np.isfinite(covariance)):
                diagnostics.failure_reason = "POSTERIOR_DRAW_NUMERICAL_FAILURE"
                draws = None
    except (ArithmeticError, FloatingPointError, ValueError, np.linalg.LinAlgError) as exc:
        diagnostics.message += f"; Hessian/Laplace failure: {exc}"
        if not diagnostics.failure_reason:
            diagnostics.failure_reason = "NUMERICAL_FAILURE"

    return LaplaceFit(
        model_order,
        x_columns,
        terms,
        parameter_names,
        mode,
        covariance,
        draws,
        diagnostics,
        z_task.shape[1],
        z_block.shape[1],
    )


def _normalize_parent(
    parent: Mapping[object, int] | Sequence[int], x_columns: Sequence[str]
) -> Dict[str, int]:
    if isinstance(parent, Mapping):
        normalized: Dict[str, int] = {}
        for key, value in parent.items():
            column = f"x_{key}" if isinstance(key, (int, np.integer)) else str(key)
            if column in normalized:
                raise ValueError("parent contains duplicate design columns")
            normalized[column] = value
        if set(normalized) != set(x_columns):
            raise ValueError("parent must specify every design column exactly once")
    else:
        values = list(parent)
        if len(values) != len(x_columns):
            raise ValueError("parent sequence length must equal the number of variables")
        normalized = dict(zip(x_columns, values))
    try:
        valid = all(
            np.isfinite(value) and value in (-1, 1)
            for value in normalized.values()
        )
    except TypeError as exc:
        raise ValueError("parent values must be numeric -1 or +1") from exc
    if not valid:
        raise ValueError("parent values must be -1 or +1")
    return {column: int(normalized[column]) for column in x_columns}


def _parent_cells(parent: Mapping[str, int], x_columns: Sequence[str], pair: Pair) -> np.ndarray:
    i, j = pair
    if not (0 <= i < j < len(x_columns)):
        raise ValueError("pair must satisfy 0 <= i < j < n_variables")
    cells = []
    for value_i, value_j in _CELL_VALUES:
        row = [parent[column] for column in x_columns]
        row[i] = value_i
        row[j] = value_j
        cells.append(row)
    return np.asarray(cells, dtype=float)


def _draw_pair_predictive(
    fit: LaplaceFit,
    parent: Mapping[str, int],
    pair: Pair,
    settings: PredictiveSettings,
) -> Tuple[np.ndarray, float]:
    if not fit.fit_ok:
        raise RuntimeError("predictive draws require a valid Laplace fit")
    draws = fit.posterior_draws
    assert draws is not None
    cells = _parent_cells(parent, fit.x_columns, pair)
    design = walsh_design(cells, fit.terms)
    beta = draws[:, : fit.n_fixed]
    log_sigma_t = draws[:, -2]
    log_sigma_b = draws[:, -1]
    rng = np.random.default_rng(settings.seed)
    n_standard = (settings.n_draws + 1) // 2 if settings.antithetic else settings.n_draws
    z_task = rng.standard_normal((draws.shape[0], n_standard))
    z_block = rng.standard_normal((draws.shape[0], n_standard))
    if settings.antithetic:
        z_task = np.concatenate((z_task, -z_task), axis=1)[:, : settings.n_draws]
        z_block = np.concatenate((z_block, -z_block), axis=1)[:, : settings.n_draws]
    random_intercepts = (
        np.exp(log_sigma_t)[:, None] * z_task
        + np.exp(log_sigma_b)[:, None] * z_block
    )
    fixed_eta = design @ beta.T
    probabilities = expit(fixed_eta[:, :, None] + random_intercepts[None, :, :])
    if not np.all(np.isfinite(probabilities)):
        raise FloatingPointError("nonfinite predictive probabilities")
    draw_cell_deltas = np.einsum("c,csr->sr", _CELL_CONTRAST, probabilities)
    delta = np.mean(draw_cell_deltas, axis=1)
    if settings.n_draws > 1:
        per_draw_variance = np.var(draw_cell_deltas, axis=1, ddof=1)
        integration_mcse = float(
            np.sqrt(np.mean(per_draw_variance / settings.n_draws))
        )
    else:
        integration_mcse = np.nan
    return delta, integration_mcse


def draw_parent_pair_delta(
    fit: LaplaceFit,
    parent: Mapping[object, int] | Sequence[int],
    pair: Pair,
    settings: Optional[PredictiveSettings] = None,
) -> np.ndarray:
    """Draw objective-scale four-cell contrasts, integrating random effects."""
    settings = PredictiveSettings() if settings is None else settings
    normalized = _normalize_parent(parent, fit.x_columns)
    delta, _ = _draw_pair_predictive(fit, normalized, pair, settings)
    return delta


def _mcse(values: np.ndarray) -> float:
    if values.size < 2:
        return np.nan
    return float(np.std(values, ddof=1) / math.sqrt(values.size))


def _empty_pair_draw_summary() -> Dict[str, float]:
    return {
        "q": np.nan,
        "w": np.nan,
        "delta_mean": np.nan,
        "delta_median": np.nan,
        "ci_lower": np.nan,
        "ci_upper": np.nan,
        "p_positive": np.nan,
        "p_negative": np.nan,
        "mean_abs": np.nan,
        "q_mcse": np.nan,
        "w_mcse": np.nan,
        "delta_mcse": np.nan,
        "predictive_delta_mcse": np.nan,
    }


def fit_tcail_bernoulli(
    data: pd.DataFrame,
    parent: Mapping[object, int] | Sequence[int],
    model_order: int = 2,
    delta: float = 0.05,
    prior: Optional[BernoulliPrior] = None,
    laplace: Optional[LaplaceSettings] = None,
    predictive: Optional[PredictiveSettings] = None,
    pairs: Optional[Sequence[Pair]] = None,
    min_task_support: int = 2,
    min_block_support: int = 2,
) -> TcailBernoulliResult:
    """Fit M2 or M3 and summarize parent-local pair posterior functionals.

    ``n_task``/``n_block`` count independent tasks/blocks having all four
    cells matched within the same block.  Missing cells, insufficient matched
    support, optimizer failure, rank failure, and numerical failure produce
    abstentions with NA posterior summaries rather than forced edges.
    """
    if not np.isfinite(delta) or delta < 0:
        raise ValueError("delta must be finite and nonnegative")
    if min_task_support < 1 or min_block_support < 1:
        raise ValueError("support thresholds must be positive integers")
    laplace = LaplaceSettings() if laplace is None else laplace
    predictive = PredictiveSettings() if predictive is None else predictive
    fit = fit_bernoulli_laplace(data, model_order, prior, laplace)
    normalized = _normalize_parent(parent, fit.x_columns)
    if pairs is None:
        pair_list = list(combinations(range(len(fit.x_columns)), 2))
    else:
        pair_list = [tuple(pair) for pair in pairs]
        if not pair_list or len(set(pair_list)) != len(pair_list):
            raise ValueError("pairs must be nonempty and unique")
        for pair in pair_list:
            if len(pair) != 2 or not (0 <= pair[0] < pair[1] < len(fit.x_columns)):
                raise ValueError("each pair must satisfy 0 <= i < j < n_variables")

    x = data.loc[:, fit.x_columns].to_numpy(dtype=float)
    task_codes, _ = pd.factorize(data["task_id"], sort=True)
    block_codes, block_levels = pd.factorize(data["block_id"], sort=True)
    block_task = np.empty(len(block_levels), dtype=int)
    for task_code, block_code in zip(task_codes, block_codes):
        block_task[block_code] = task_code

    rows = []
    delta_draws: Dict[Pair, np.ndarray] = {}
    for pair in pair_list:
        cells = _parent_cells(normalized, fit.x_columns, pair)
        masks = [np.all(x == cell, axis=1) for cell in cells]
        cell_counts = [int(np.sum(mask)) for mask in masks]
        any_mask = np.logical_or.reduce(masks)
        complete_blocks = None
        for mask in masks:
            observed_blocks = set(block_codes[mask].tolist())
            complete_blocks = (
                observed_blocks
                if complete_blocks is None
                else complete_blocks & observed_blocks
            )
        assert complete_blocks is not None
        complete_block_codes = np.array(sorted(complete_blocks), dtype=int)
        n_block = len(complete_blocks)
        n_task = (
            int(np.unique(block_task[complete_block_codes]).size)
            if n_block
            else 0
        )
        reasons = []
        if any(count == 0 for count in cell_counts):
            reasons.append("MISSING_CELL")
        if n_task < min_task_support or n_block < min_block_support:
            reasons.append("LOW_SUPPORT")
        if not fit.fit_ok:
            reasons.append(fit.diagnostics.failure_reason or "NONCONVERGENCE")
        reasons = list(dict.fromkeys(reasons))

        row = {
            "pair_i": pair[0],
            "pair_j": pair[1],
            "model_order": model_order,
            "delta_threshold": delta,
            "n_task": n_task,
            "n_block": n_block,
            "n_task_any": int(np.unique(task_codes[any_mask]).size),
            "n_block_any": int(np.unique(block_codes[any_mask]).size),
            "cell_pp": cell_counts[0],
            "cell_pm": cell_counts[1],
            "cell_mp": cell_counts[2],
            "cell_mm": cell_counts[3],
            "n_posterior_draws": 0,
            "n_predictive_draws": predictive.n_draws,
            "credible_level": 0.95,
        }
        row.update(_empty_pair_draw_summary())
        if not reasons:
            try:
                pair_delta, integration_mcse = _draw_pair_predictive(
                    fit, normalized, pair, predictive
                )
                if not np.all(np.isfinite(pair_delta)):
                    raise FloatingPointError("nonfinite Delta draws")
                delta_draws[pair] = pair_delta
                absolute = np.abs(pair_delta)
                excess = np.maximum(absolute - delta, 0.0)
                interval = np.quantile(pair_delta, [0.025, 0.975])
                row.update(
                    {
                        "q": float(np.mean(absolute > delta)),
                        "w": float(np.mean(excess)),
                        "delta_mean": float(np.mean(pair_delta)),
                        "delta_median": float(np.median(pair_delta)),
                        "ci_lower": float(interval[0]),
                        "ci_upper": float(interval[1]),
                        "p_positive": float(np.mean(pair_delta > 0)),
                        "p_negative": float(np.mean(pair_delta < 0)),
                        "mean_abs": float(np.mean(absolute)),
                        "q_mcse": _mcse((absolute > delta).astype(float)),
                        "w_mcse": _mcse(excess),
                        "delta_mcse": _mcse(pair_delta),
                        "predictive_delta_mcse": integration_mcse,
                        "n_posterior_draws": pair_delta.size,
                    }
                )
            except (ArithmeticError, FloatingPointError, ValueError) as exc:
                reasons.append("PREDICTIVE_NUMERICAL_FAILURE")
                row["predictive_error"] = str(exc)
        row["abstain"] = bool(reasons)
        row["abstain_reason"] = ";".join(reasons)
        rows.append(row)

    return TcailBernoulliResult(
        model_order=model_order,
        parent=normalized,
        fit=fit,
        pair_results=pd.DataFrame(rows),
        delta_draws=delta_draws,
        predictive_settings=predictive,
    )


__all__ = [
    "BernoulliPrior",
    "LaplaceSettings",
    "PredictiveSettings",
    "LaplaceDiagnostics",
    "LaplaceFit",
    "TcailBernoulliResult",
    "bernoulli_log_likelihood",
    "walsh_terms",
    "walsh_design",
    "walsh_design_matrix",
    "fit_bernoulli_laplace",
    "draw_parent_pair_delta",
    "fit_tcail_bernoulli",
]
