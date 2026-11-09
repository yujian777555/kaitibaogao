"""D-064-B: CondRecSucc power re-analysis with task-family hierarchical
correlation and ICC sensitivity.

Analysis variable: cluster-level paired difference
    d_fj = CondRecSucc_AB(fj) - CondRecSucc_nsga2(fj)
with f = task family, j = fault-composition cluster (R1/R2 primary-eligible
only). Seeds are nested repeats inside scenarios; never treated as families.

Everything is recomputed from raw diagnostic3 rows -- no hardcoded summary
statistics. See 67_D064B_POWER_AND_HIERARCHICAL_SENSITIVITY_EXECUTION.md.
"""
from __future__ import annotations

import csv
import hashlib
import itertools
import json
import math
import random
import subprocess
from collections import defaultdict
from pathlib import Path

import numpy as np

HERE = Path(__file__).parent
MC_KEY = 10000       # MC reps for reported key cells
MC_SWEEP = 2000      # MC reps for the broad sample-size sweep
BOOT_REPS = 4000
SEED = 20261112
ALPHA = 0.05
MDE_GRID = (0.05, 0.08, 0.10, 0.1173, 0.15)
ICC_GRID = (0.0, 0.05, 0.10, 0.20)
FAM_GRID = (6, 8, 10, 12, 15, 17, 19, 22, 25, 30, 40)
COMP_GRID = (6, 7, 8, 9)
CL_ATTR = (0.0, 0.10, 0.15, 0.20)
FAM_ATTR = (0.0, 0.10, 0.15, 0.20)


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def git_sha():
    try:
        return subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True,
                              text=True, cwd=str(HERE)).stdout.strip()
    except Exception:
        return "unknown"


# ---------------------------------------------------------------------------
# Task A: hierarchical data rebuild from raw rows
# ---------------------------------------------------------------------------
def build_hierarchy(input_path):
    raw = Path(input_path).read_bytes()
    data = json.loads(raw)
    input_sha = hashlib.sha256(raw).hexdigest()

    problems = []
    seen = set()
    # scenario -> method -> seed -> cs   (R1/R2 only)
    prim = defaultdict(lambda: defaultdict(dict))
    meta = {}
    for run in data["runs"]:
        m, s = run["method"], run["seed"]
        for row in run["rows"]:
            key = (m, s, row["scenario_id"])
            if key in seen:
                problems.append(f"duplicate episode {key}")
            seen.add(key)
            sid = row["scenario_id"]
            meta[sid] = (row["task"], row["composition"], row["label"])
            if row["label"] in ("R1", "R2") and row["class_success"] is not None:
                prim[sid][m][s] = row["class_success"]

    # per-scenario paired seed-mean diffs -> cluster diffs
    cluster_scen = defaultdict(list)
    cluster_denom = defaultdict(int)
    for sid, per in prim.items():
        a, b = per.get("AB", {}), per.get("nsga2", {})
        common = set(a) & set(b)
        if set(a) != set(b):
            problems.append(f"unpaired seeds at {sid}")
        vals = [a[k] - b[k] for k in sorted(common)]
        if not vals:
            continue
        fam, comp, _lab = meta[sid]
        cluster_scen[(fam, comp)].append(sum(vals) / len(vals))
        cluster_denom[(fam, comp)] += 1

    all_clusters = {(t, c) for (t, c, _l) in meta.values()}
    zero_denom = sorted(all_clusters - set(cluster_scen))

    families = defaultdict(dict)
    for (fam, comp), diffs in cluster_scen.items():
        families[fam][comp] = {
            "mean_diff": sum(diffs) / len(diffs),
            "n_r12_scenarios": len(diffs),
        }

    fam_sizes = {f: len(c) for f, c in families.items()}
    if len(families) != 6:
        problems.append(f"expected 6 families, got {len(families)}")
    if len(cluster_scen) != 42:
        problems.append(f"expected 42 eligible clusters, got {len(cluster_scen)}")
    for f, n in fam_sizes.items():
        if n != 7:
            problems.append(f"family {f} has {n} eligible compositions, expected 7")
    if len(zero_denom) != 12:
        problems.append(f"expected 12 zero-denom clusters, got {len(zero_denom)}")

    # variance decomposition
    fam_means = {f: float(np.mean([c["mean_diff"] for c in comps.values()]))
                 for f, comps in families.items()}
    all_vals = np.array([c["mean_diff"] for comps in families.values()
                         for c in comps.values()], dtype=float)
    grand = float(all_vals.mean())
    ss_between = sum(fam_sizes[f] * (fam_means[f] - grand) ** 2 for f in families)
    ss_within = sum((c["mean_diff"] - fam_means[f]) ** 2
                    for f, comps in families.items() for c in comps.values())
    df_b, df_w = len(families) - 1, len(all_vals) - len(families)
    ms_b = ss_between / df_b if df_b else float("nan")
    ms_w = ss_within / df_w if df_w else float("nan")
    m0 = len(all_vals) / len(families)  # balanced 7
    between_var = (ms_b - ms_w) / m0 if m0 else float("nan")
    within_var = ms_w

    rows_csv = []
    for f in sorted(families):
        for c in sorted(families[f]):
            d = families[f][c]
            rows_csv.append({
                "family_id": f, "composition_id": c,
                "cluster_id": f"{f}|{c}",
                "n_r12_scenarios": d["n_r12_scenarios"],
                "paired_diff": round(d["mean_diff"], 6),
            })
        rows_csv.append({
            "family_id": f, "composition_id": "__FAMILY_MEAN__",
            "cluster_id": f"{f}|__MEAN__",
            "n_r12_scenarios": sum(d["n_r12_scenarios"] for d in families[f].values()),
            "paired_diff": round(fam_means[f], 6),
        })

    return {
        "input_sha256": input_sha,
        "problems": problems,
        "families": families,
        "fam_means": fam_means,
        "fam_sizes": fam_sizes,
        "zero_denom_clusters": [f"{t}|{c}" for t, c in zero_denom],
        "grand_mean": grand,
        "total_sd": float(all_vals.std(ddof=1)),
        "between_var_mom": float(between_var),
        "within_var_mom": float(within_var),
        "ms_between": float(ms_b),
        "ms_within": float(ms_w),
        "m_per_family": m0,
        "rows_csv": rows_csv,
        "n_episode_rows": len(seen),
    }


# ---------------------------------------------------------------------------
# Task B: ICC estimation
# ---------------------------------------------------------------------------
def icc_anova(h):
    """Balanced one-way random-effects ANOVA / method-of-moments ICC."""
    ms_b, ms_w, m0 = h["ms_between"], h["ms_within"], h["m_per_family"]
    denom = ms_b + (m0 - 1) * ms_w
    icc = (ms_b - ms_w) / denom if denom > 0 else float("nan")
    return {
        "method": "balanced one-way ANOVA / method-of-moments",
        "icc_raw": float(icc),
        "icc_constrained": float(max(0.0, icc)),
        "between_var": h.get("between_var_mom", float("nan")),
        "within_var": h.get("within_var_mom", float("nan")),
        "ms_between": ms_b,
        "ms_within": ms_w,
        "m_per_family": m0,
    }


def icc_reml(h):
    """Random-intercept REML for the balanced one-way model via numerical
    maximisation of the profile restricted log-likelihood over lambda =
    sigma_u^2 / sigma_e^2, lambda >= 0 (boundary-constrained).

    Analytic note: for balanced one-way random effects the unconstrained REML
    estimate equals the ANOVA estimator; when MSB < MSW the constrained REML
    sits on the boundary lambda = 0. Both values are reported.
    """
    fams = h["families"]
    fam_names = sorted(fams)
    F = len(fam_names)
    m = h["m_per_family"]
    vals = np.array([c["mean_diff"] for f in fam_names for c in fams[f].values()], dtype=float)
    grand = float(vals.mean())
    sse = float(sum((c["mean_diff"] - h["fam_means"][f]) ** 2
                    for f in fam_names for c in fams[f].values()))
    ssb = float(sum(m * (h["fam_means"][f] - grand) ** 2 for f in fam_names))
    se2 = sse / (len(vals) - F)

    def neg_reml(lam):
        sv = se2 * (1 + m * lam)
        return 0.5 * ((F - 1) * math.log(sv) + ssb / sv)

    a, b = 0.0, 1e3
    phi = (math.sqrt(5) - 1) / 2
    c, d = b - phi * (b - a), a + phi * (b - a)
    fc, fd = neg_reml(c), neg_reml(d)
    for _ in range(80):
        if fc < fd:
            b, d, fd = d, c, fc
            c = b - phi * (b - a)
            fc = neg_reml(c)
        else:
            a, c, fc = c, d, fd
            d = a + phi * (b - a)
            fd = neg_reml(d)
    lam_c = (a + b) / 2
    ms_b = ssb / (F - 1) if F > 1 else float("nan")
    ms_w = sse / (len(vals) - F) if len(vals) > F else float("nan")
    lam_raw = (ms_b / ms_w - 1.0) / m if (ms_w and ms_w == ms_w and ms_w > 0) else float("nan")
    icc_raw = lam_raw / (1 + lam_raw) if lam_raw == lam_raw and lam_raw > -1 else float("nan")
    return {
        "method": "random-intercept REML (profile restricted likelihood, lambda>=0)",
        "icc_raw": float(icc_raw),
        "icc_constrained": float(lam_c / (1 + lam_c)),
        "lambda_constrained": float(lam_c),
        "note": ("balanced one-way: unconstrained REML == ANOVA estimator; "
                 "constrained REML at boundary 0 when MSB < MSW"),
    }


def icc_bootstrap_ci(h, reps=BOOT_REPS, seed=SEED):
    """Family-block bootstrap percentile CI for the ANOVA ICC (only 6
    families: CI is expected to be wide / unstable)."""
    fams = sorted(h["families"])
    rng = random.Random(seed)
    iccs = []
    for _ in range(reps):
        chosen = [rng.choice(fams) for _ in fams]
        vals = [c["mean_diff"] for f in chosen for c in h["families"][f].values()]
        ms_b = ms_w = None
        F, m = len(chosen), h["m_per_family"]
        grand = sum(vals) / len(vals)
        ssb = sum(m * (np.mean([c["mean_diff"] for c in h["families"][f].values()]) - grand) ** 2
                  for f in chosen)
        ssw = sum((c["mean_diff"] - np.mean([c["mean_diff"] for c in h["families"][f].values()])) ** 2
                  for f in chosen for c in h["families"][f].values())
        df_b, df_w = F - 1, len(vals) - F
        if df_b <= 0 or df_w <= 0:
            continue
        ms_b, msw = ssb / df_b, ssw / df_w
        denom = ms_b + (m - 1) * msw
        if denom > 0:
            iccs.append((ms_b - msw) / denom)
    iccs.sort()
    return {
        "reps": reps, "seed": seed,
        "ci95_raw": [round(iccs[int(0.025 * (len(iccs) - 1))], 4),
                     round(iccs[int(0.975 * (len(iccs) - 1))], 4)] if iccs else None,
        "note": "family-block bootstrap percentile; 6 families -> unstable, wide interval expected",
    }


# ---------------------------------------------------------------------------
# Task E: hierarchical inference on the observed data
# ---------------------------------------------------------------------------
def family_level_tests(h, seed=SEED):
    fam_means = np.array([h["fam_means"][f] for f in sorted(h["fam_means"])], dtype=float)
    F = len(fam_means)
    mean = float(fam_means.mean())
    sd = float(fam_means.std(ddof=1))
    # Student-t
    tval = mean / (sd / math.sqrt(F)) if sd > 0 else float("inf")
    # two-sided p via survival function of t(F-1); use scipy-free integration:
    p_t = _t_sf(abs(tval), F - 1) * 2
    # exact sign-flip (2^F enumeration)
    obs = abs(mean)
    extreme = 0
    total = 2 ** F
    for signs in itertools.product((1, -1), repeat=F):
        s = sum(s * v for s, v in zip(signs, fam_means)) / F
        if abs(s) >= obs - 1e-12:
            extreme += 1
    p_sf = extreme / total
    # family-block bootstrap CI (percentile, resample F families)
    rng = random.Random(seed)
    boots = []
    for _ in range(BOOT_REPS):
        sample = [fam_means[rng.randrange(F)] for _ in range(F)]
        boots.append(sum(sample) / F)
    boots.sort()
    ci = [round(boots[int(0.025 * (len(boots) - 1))], 6),
          round(boots[int(0.975 * (len(boots) - 1))], 6)]
    return {
        "n_families": F,
        "family_means": {f: round(h["fam_means"][f], 6) for f in sorted(h["fam_means"])},
        "mean": round(mean, 6),
        "family_mean_sd": round(sd, 6),
        "student_t": {"t": round(tval, 4), "df": F - 1, "p_two_sided": round(p_t, 6)},
        "signflip_exact": {"p": round(p_sf, 6), "enumeration": total},
        "block_bootstrap_ci95": ci,
    }


def _t_sf(t, df):
    """Two-sided tail of Student-t via the regularized incomplete beta."""
    x = df / (df + t * t)
    return 0.5 * _betainc(df / 2.0, 0.5, x)


def _betainc(a, b, x):
    """Regularized incomplete beta I_x(a,b) (continued fraction)."""
    if x <= 0:
        return 0.0
    if x >= 1:
        return 1.0
    lbeta = math.lgamma(a) + math.lgamma(b) - math.lgamma(a + b)
    front = math.exp(math.log(x) * a + math.log(1 - x) * b - lbeta) / a
    # Lentz continued fraction
    f, c, d = 1.0, 1.0, 0.0
    for i in range(0, 200):
        m = i // 2
        if i == 0:
            num = 1.0
        elif i % 2 == 0:
            num = (m * (b - m) * x) / ((a + 2 * m - 1) * (a + 2 * m))
        else:
            num = -((a + m) * (a + b + m) * x) / ((a + 2 * m) * (a + 2 * m + 1))
        d = 1.0 + num * d
        if abs(d) < 1e-30:
            d = 1e-30
        d = 1.0 / d
        c = 1.0 + num / c
        if abs(c) < 1e-30:
            c = 1e-30
        f *= c * d
        if abs(1 - c * d) < 1e-10:
            break
    return front * (f - 1.0)


# ---------------------------------------------------------------------------
# Task C: power simulation (numpy-vectorised)
# ---------------------------------------------------------------------------
def gen_family_means_hier(rng, reps, n_fam, m_eff, icc, mu, total_var, eps_pool):
    """Mechanism 2: d_fj = mu + u_f + eps_fj; empirical eps resampled in-family,
    ICC-controlled variance split. Returns (reps, n_fam) family means and the
    out-of-[-1,1] rate of individual cluster draws."""
    var_u = icc * total_var
    var_e = (1 - icc) * total_var
    eps_sd = float(np.std(eps_pool, ddof=1)) or 1e-9
    scale = math.sqrt(var_e) / eps_sd
    idx = rng.integers(0, len(eps_pool), size=(reps, n_fam, int(m_eff)))
    eps = eps_pool[idx] * scale
    u = rng.normal(0.0, math.sqrt(var_u), size=(reps, n_fam, 1))
    clusters = mu + u + eps
    overflow = float(np.mean(np.abs(clusters) > 1.0))
    return clusters.mean(axis=2), float(overflow)


def gen_family_means_block(rng, reps, n_fam, fam_blocks, mu_shift):
    """Mechanism 1: whole family-block resampling (composition clusters kept
    intact). Only 6 empirical blocks -> limited distributional estimate."""
    idx = rng.integers(0, len(fam_blocks), size=(reps, n_fam))
    out = np.empty((reps, n_fam))
    for i in range(reps):
        for j in range(n_fam):
            out[i, j] = fam_blocks[idx[i, j]].mean() + mu_shift
    return out, 0.0


def _pvals_student_t(means):
    """Vectorised two-sided one-sample Student-t p-values per row."""
    F = means.shape[1]
    m = means.mean(axis=1)
    s = means.std(axis=1, ddof=1)
    s = np.where(s <= 0, 1e-12, s)
    tval = np.abs(m / (s / math.sqrt(F)))
    # vectorised t survival via the same continued fraction per element
    return np.array([min(1.0, _t_sf(float(t), F - 1) * 2) for t in tval])


def _pvals_signflip(means, rng, inner=999):
    """Vectorised Monte Carlo sign-flip p-values (true sign flips, not z)."""
    reps, F = means.shape
    if F <= 12:
        out = np.empty(reps)
        sign_mat = np.array(list(itertools.product((1.0, -1.0), repeat=F)))
        obs = np.abs(means.mean(axis=1))
        for i in range(reps):
            stats = np.abs((sign_mat * means[i]).mean(axis=1))
            out[i] = np.mean(stats >= obs[i] - 1e-12)
        return out
    obs = np.abs(means.mean(axis=1))
    counts = np.zeros(reps)
    batch = 200
    for start in range(0, reps, batch):
        b = min(batch, reps - start)
        signs = rng.choice(np.array([1.0, -1.0]), size=(b, inner, F))
        stats = np.abs((signs * means[start:start + b][:, None, :]).mean(axis=2))
        counts[start:start + b] = (stats >= obs[start:start + b][:, None] - 1e-12).sum(axis=1)
    return (counts + 1.0) / (inner + 1.0)


def _pvals_bootstrap_reject(means, rng, inner=999):
    """Family-block bootstrap percentile-CI rejection indicator per row."""
    reps, F = means.shape
    out = np.zeros(reps, dtype=bool)
    batch = 200
    for start in range(0, reps, batch):
        b = min(batch, reps - start)
        idx = rng.integers(0, F, size=(b, inner, F))
        base = np.broadcast_to(means[start:start + b][:, None, :], (b, inner, F))
        boots = np.take_along_axis(base, idx, axis=2).mean(axis=2)
        lo = np.percentile(boots, 2.5, axis=1)
        hi = np.percentile(boots, 97.5, axis=1)
        out[start:start + b] = (lo > 0) | (hi < 0)
    return out.astype(float)


def mc_power_at(mu, n_fam, m_eff, icc, total_var, eps_pool, fam_blocks,
                mechanism, reps, seed, tests="t"):
    """Monte Carlo power / Type-I for family-level tests.

    tests: 't' -> Student-t only (broad sweep);
           'all' -> Student-t + exact/MC sign-flip + family-block bootstrap.
    """
    if n_fam < 2 or int(m_eff) < 1 or total_var < 0:
        raise ValueError("illegal power-simulation parameters")
    rng = np.random.default_rng(seed)
    if mechanism == "hierarchical":
        means, overflow = gen_family_means_hier(rng, reps, n_fam, m_eff, icc,
                                                mu, total_var, eps_pool)
    else:
        means, overflow = gen_family_means_block(rng, reps, n_fam, fam_blocks, mu)
    p_t = _pvals_student_t(means)
    rej_t = float(np.mean(p_t < ALPHA))
    out = {
        "power_student_t": round(rej_t, 4),
        "mcse_student_t": round(math.sqrt(max(rej_t * (1 - rej_t), 1e-12) / reps), 4),
        "ci95_student_t": [round(max(0.0, rej_t - 1.96 * math.sqrt(rej_t * (1 - rej_t) / reps)), 4),
                           round(min(1.0, rej_t + 1.96 * math.sqrt(rej_t * (1 - rej_t) / reps)), 4)],
        "out_of_range_rate": round(float(overflow), 6),
    }
    if tests == "all":
        prng = random.Random(seed + 1)
        np_rng = np.random.default_rng(seed + 2)
        p_sf = _pvals_signflip(means, np_rng)
        rej_sf = float(np.mean(p_sf < ALPHA))
        brng = np.random.default_rng(seed + 3)
        rej_bt = float(np.mean(_pvals_bootstrap_reject(means, brng) == 1.0))
        out.update({
            "power_signflip": round(rej_sf, 4),
            "mcse_signflip": round(math.sqrt(max(rej_sf * (1 - rej_sf), 1e-12) / reps), 4),
            "power_block_bootstrap": round(rej_bt, 4),
            "mcse_block_bootstrap": round(math.sqrt(max(rej_bt * (1 - rej_bt), 1e-12) / reps), 4),
        })
        del prng
    return out


# ---------------------------------------------------------------------------
# Main pipeline
# ---------------------------------------------------------------------------
def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", default="diagnostic3_results.json")
    ap.add_argument("--outdir", default=".")
    ap.add_argument("--quick", action="store_true", help="reduced MC for smoke")
    args = ap.parse_args()
    outdir = Path(args.outdir)
    mc_key = 500 if args.quick else MC_KEY
    mc_sweep = 200 if args.quick else MC_SWEEP

    h = build_hierarchy(args.input)
    icc_a = icc_anova(h)
    icc_r = icc_reml(h)
    icc_ci = icc_bootstrap_ci(h, reps=BOOT_REPS if not args.quick else 500)
    infer = family_level_tests(h)

    # empirical pieces for simulation
    fam_blocks_raw = [np.array([c["mean_diff"] for c in comps.values()], dtype=float)
                      for comps in h["families"].values()]
    # centred blocks for mechanism 1 so that mu_shift is the true grand mean
    fam_blocks = [blk - h["grand_mean"] for blk in fam_blocks_raw]
    eps_pool = np.array([c["mean_diff"] - h["fam_means"][f]
                         for f, comps in h["families"].items()
                         for c in comps.values()], dtype=float)
    total_var = float(np.var([c["mean_diff"] for comps in h["families"].values()
                              for c in comps.values()], ddof=1))

    # ---- null calibration + key power cells (all three tests) ----------
    key_cells = []
    for icc in ICC_GRID:
        for mde in (0.0, 0.10):
            for n_fam in (6, 17):
                res = mc_power_at(mde, n_fam, 7, icc, total_var, eps_pool,
                                  fam_blocks, "hierarchical", mc_key,
                                  SEED + int(icc * 1000) + n_fam + int(mde * 100),
                                  tests="all")
                key_cells.append({"mechanism": "hierarchical", "icc": icc, "mde": mde,
                                  "n_families": n_fam, "m_eff": 7, "mc_reps": mc_key, **res})
    mech1 = []
    for n_fam in (6, 17):
        for mde in (0.0, 0.10):
            res = mc_power_at(mde, n_fam, 7, 0, total_var, eps_pool,
                              fam_blocks, "block_resample", mc_key,
                              SEED + 9000 + n_fam + int(mde * 100), tests="all")
            mech1.append({"mechanism": "family_block_resample", "mde": mde,
                          "n_families": n_fam, "m_eff": 7, "mc_reps": mc_key, **res})

    # ---- sample-size sweep (Task D) ------------------------------------
    sweep = []
    for icc in ICC_GRID:
        for m in COMP_GRID:
            for fam in FAM_GRID:
                for mde in MDE_GRID:
                    for cl_at, fm_at in ((0.0, 0.0), (0.15, 0.15)):
                        f_eff = max(3, int(math.floor(fam * (1 - fm_at))))
                        m_eff = max(2, int(math.floor(m * (1 - cl_at))))
                        res = mc_power_at(mde, f_eff, m_eff, icc, total_var,
                                          eps_pool, fam_blocks, "hierarchical",
                                          mc_sweep, SEED + f_eff * 7 + m_eff + int(mde * 1000) + int(icc * 10000))
                        sweep.append({
                            "icc": icc, "compositions_per_family": m,
                            "n_families_design": fam, "family_attrition": fm_at,
                            "cluster_attrition": cl_at,
                            "n_families_effective": f_eff,
                            "primary_eligible_clusters_design": fam * m,
                            "primary_eligible_clusters_eff": f_eff * m_eff,
                            "mde": mde, "mc_reps": mc_sweep,
                            "power_student_t": res["power_student_t"],
                            "power_signflip": res.get("power_signflip"),
                            "ci95_student_t": res["ci95_student_t"],
                            "de_formula": round(1 + (m_eff - 1) * icc, 3),
                        })

    # required families for 80/90% per ICC/MDE (m=7, no attrition & 15% both)
    req = []
    for icc in ICC_GRID:
        for mde in MDE_GRID:
            for target in (0.80, 0.90):
                for cl_at, fm_at in ((0.0, 0.0), (0.15, 0.15)):
                    hits = [s for s in sweep
                            if s["icc"] == icc and s["mde"] == mde
                            and s["compositions_per_family"] == 7
                            and s["family_attrition"] == fm_at
                            and s["cluster_attrition"] == cl_at
                            and s["power_student_t"] >= target]
                    req.append({
                        "icc": icc, "mde": mde, "target_power": target,
                        "family_attrition": fm_at, "cluster_attrition": cl_at,
                        "n_families_design_required":
                            min((s["n_families_design"] for s in hits), default=None),
                    })

    out = {
        "kind": "D064B_HIERARCHICAL_POWER_AND_ICC_SENSITIVITY",
        "input_file": args.input,
        "input_sha256": h["input_sha256"],
        "program_version": "power_hierarchical.py v1 (D-064-B)",
        "git_commit": git_sha(),
        "random_seed": SEED,
        "mc_reps_key_cells": mc_key,
        "mc_reps_sweep": mc_sweep,
        "alpha": ALPHA,
        "sided": "two-sided",
        "hierarchy": {
            "n_families": len(h["families"]),
            "fam_sizes": h["fam_sizes"],
            "n_eligible_clusters": sum(h["fam_sizes"].values()),
            "zero_denom_clusters": h["zero_denom_clusters"],
            "grand_mean": round(h["grand_mean"], 6),
            "total_sd": round(h["total_sd"], 6),
            "between_var_mom": round(h["between_var_mom"], 6),
            "within_var_mom": round(h["within_var_mom"], 6),
            "family_means": {f: round(v, 6) for f, v in h["fam_means"].items()},
            "problems": h["problems"],
        },
        "icc_anova": icc_a,
        "icc_reml": icc_r,
        "icc_family_bootstrap_ci": icc_ci,
        "observed_inference": infer,
        "key_cells": key_cells,
        "mechanism1_block_resample": mech1,
        "sample_size_sweep": sweep,
        "required_families": req,
        "mde_grid_note": ("0.1173 = historical observed effect (sensitivity only); "
                          "+<diagnostic observed effect> = NOT an MDE (see 66 report); "
                          "MDE needs independent scientific justification"),
    }
    (outdir / "power_hierarchical.json").write_text(
        json.dumps(out, indent=2, ensure_ascii=False), encoding="utf-8")

    with (outdir / "family_cluster_diagnostics.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["family_id", "composition_id", "cluster_id",
                                          "n_r12_scenarios", "paired_diff"])
        w.writeheader()
        w.writerows(h["rows_csv"])

    _write_report(out, outdir)
    print("hierarchy problems:", h["problems"] or "none")
    print("ICC anova:", icc_a["icc_raw"], "reml:", icc_r["icc_raw"], "CI:", icc_ci["ci95_raw"])
    print("observed inference:", json.dumps(infer, indent=1)[:600])
    print("wrote power_hierarchical.{json,report.md} + family_cluster_diagnostics.csv")


def _write_report(out, outdir):
    hi = out["hierarchy"]
    inf = out["observed_inference"]
    lines = [
        "# D-064-B — CondRecSucc 层级功效与 ICC 敏感性报告", "",
        f"- 输入 SHA-256：`{out['input_sha256']}`；程序 {out['program_version']}；git `{out['git_commit']}`",
        f"- MC：key cells {out['mc_reps_key_cells']} 次、sweep {out['mc_reps_sweep']} 次；seed {out['random_seed']}；α={out['alpha']} 双侧", "",
        "## 1. 层级数据复核（Task A）",
        f"- 6 families × 7 eligible compositions = **42 clusters**；零分母 12；问题：{hi['problems'] or '无'}",
        f"- 总均值 Δ={hi['grand_mean']}，总 SD={hi['total_sd']}；family 均值：{hi['family_means']}",
        f"- within var={hi['within_var_mom']}；between var(MoM)={hi['between_var_mom']}", "",
        "## 2. ICC（Task B）",
        f"- ANOVA/MoM：**ICC={out['icc_anova']['icc_raw']:.4f}**（约束 {out['icc_anova']['icc_constrained']:.4f}）",
        f"- REML：ICC={out['icc_reml']['icc_raw']:.4f}（平衡设计下应与 MoM 一致）",
        f"- family-block bootstrap CI：{out['icc_family_bootstrap_ci']['ci95_raw']}（6 families，不稳定——**不解释为独立性证明**）", "",
        "## 3. 层级推断（Task E：D-064-A 重评估）",
        f"- family-level t：t={inf['student_t']['t']} df={inf['student_t']['df']} p=**{inf['student_t']['p_two_sided']}**",
        f"- family-level exact sign-flip（2^6 枚举）：p=**{inf['signflip_exact']['p']}**",
        f"- family-block bootstrap CI：{inf['block_bootstrap_ci95']}",
        f"- 对照 D-064-A 42-cluster 独立分析结果（CI/p 见 66 号报告与 condrec_diagnostic3.json）", "",
        "## 4. Type-I 校准与关键功效（Task C）",
        "| ICC | MDE | n_fam | t 功效 (MCSE) | sign-flip | bootstrap |",
        "|---|---|---|---|---|---|",
    ]
    for c in out["key_cells"]:
        lines.append(f"| {c['icc']} | {c['mde']} | {c['n_families']} | "
                     f"{c['power_student_t']} ({c['mcse_student_t']}) | "
                     f"{c['power_signflip']} | {c['power_block_bootstrap']} |")
    lines += ["", "## 5. 所需 family 数（m=7，t 检验）", "",
              "| ICC | MDE | 80% 无损耗 | 80% 双 15% 损耗 | 90% 无损耗 | 90% 双 15% 损耗 |",
              "|---|---|---|---|---|---|"]
    by = defaultdict(dict)
    for r in out["required_families"]:
        key = (r["icc"], r["mde"])
        by[key][(r["target_power"], r["family_attrition"])] = r["n_families_design_required"]
    for (icc, mde), d in sorted(by.items()):
        lines.append(f"| {icc} | {mde} | {d.get((0.8, 0.0))} | {d.get((0.8, 0.15))} | "
                     f"{d.get((0.9, 0.0))} | {d.get((0.9, 0.15))} |")
    lines += ["", "## 6. 17-family 评估与结论见 power_hierarchical.json 与 68 号报告。", ""]
    lines.append(f"备注：{out['mde_grid_note']}")
    (outdir / "power_hierarchical_report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
