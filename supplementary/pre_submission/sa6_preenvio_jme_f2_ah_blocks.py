"""Compute the pre-specified AH-added-to-M2 block rows from sealed forecasts.

This reads only sealed prediction CSVs. It does not fit models or write to the
source forecast archives.
"""

from __future__ import annotations

import csv
import json
from pathlib import Path
from math import sqrt

import numpy as np
import pandas as pd
from scipy.stats import t as student_t


ROOT = Path(__file__).resolve().parents[1]
BASE_LOWER = ROOT / "outputs/sa6/abg_target_correction/abg4_sealed_test/checkpoints"
BASE_MIN = ROOT / "outputs/sa6/construct_validation/review34/a1_r1_min_validation_lambda/checkpoints"
AH_MAIN_LOWER = ROOT / "outputs/sa6/construct_validation/review25/c1b2a_ah_sealed_forecasts/checkpoints"
AH_MIN = ROOT / "outputs/sa6/construct_validation/review34/ah_m2_minlambda/checkpoints"
OUT = ROOT / "outputs/sa6/preenvio_jme/f2_ah_m2_blocks.csv"

TAUS = np.round(np.arange(0.05, 1.00, 0.05), 2)
BLOCKS = {
    "LOWER": TAUS[:5],
    "CENTER": TAUS[5:14],
    "UPPER": TAUS[14:],
}
H = 4
HAC_LAG = 3


def read_bank(path: Path, tau: float) -> pd.DataFrame:
    frame = pd.read_csv(path)
    expected = pd.period_range("2007Q4", "2025Q1", freq="Q")
    if len(frame) != 70:
        raise ValueError(f"{path}: expected 70 forecasts, got {len(frame)}")
    if not pd.PeriodIndex(frame["origin"], freq="Q").equals(expected):
        raise ValueError(f"{path}: origin clock mismatch")
    if frame["tau"].nunique() != 1 or not np.isclose(frame["tau"].iloc[0], tau):
        raise ValueError(f"{path}: quantile mismatch")
    if not np.isfinite(frame[["prediction", "actual"]].to_numpy(float)).all():
        raise ValueError(f"{path}: non-finite forecast or actual")
    return frame


def load_losses() -> dict[str, pd.DataFrame]:
    collected: dict[str, list[pd.DataFrame]] = {"M2": [], "AH": []}
    for tau in TAUS:
        tag = f"Q{int(round(tau * 100)):02d}"
        if tau <= 0.25:
            base_path = BASE_LOWER / f"R2_{tag}_sealed.csv"
            ah_path = AH_MAIN_LOWER / f"R2_AH_{tag}_sealed.csv"
        else:
            base_path = BASE_MIN / f"R2_{tag}_sealed.csv"
            ah_path = AH_MIN / f"R2_AH_MINLAMBDA_{tag}_sealed.csv"
        base = read_bank(base_path, tau)
        ah = read_bank(ah_path, tau)
        if not np.array_equal(base["target"].to_numpy(), ah["target"].to_numpy()):
            raise ValueError(f"{tag}: target clock differs between M2 and AH")
        for label, frame in (("M2", base), ("AH", ah)):
            error = frame["actual"].to_numpy(float) - frame["prediction"].to_numpy(float)
            pinball = np.where(error >= 0, tau * error, (tau - 1) * error)
            collected[label].append(
                pd.DataFrame({"origin": frame["origin"], "target": frame["target"], "tau": tau, "loss": pinball})
            )
    return {key: pd.concat(parts, ignore_index=True) for key, parts in collected.items()}


def hac_hln(d: np.ndarray) -> tuple[float, float, float]:
    n = len(d)
    centered = d - d.mean()
    lrv = float(np.dot(centered, centered) / n)
    for lag in range(1, HAC_LAG + 1):
        gamma = float(np.dot(centered[lag:], centered[:-lag]) / n)
        lrv += 2 * (1 - lag / (HAC_LAG + 1)) * gamma
    if not np.isfinite(lrv) or lrv <= 0:
        raise ValueError(f"invalid HAC long-run variance: {lrv}")
    se = sqrt(lrv / n)
    hln_factor = sqrt((n + 1 - 2 * H + H * (H - 1) / n) / n)
    statistic = hln_factor * float(d.mean()) / se
    p_two = min(1.0, 2 * min(student_t.cdf(statistic, n - 1), student_t.sf(statistic, n - 1)))
    return se, statistic, float(p_two)


def calculate() -> pd.DataFrame:
    losses = load_losses()
    rows = []
    for block, taus in BLOCKS.items():
        means: dict[str, pd.Series] = {}
        for model, frame in losses.items():
            means[model] = (
                frame[frame["tau"].isin(taus)]
                .groupby("target", sort=False)["loss"]
                .mean()
            )
        if not means["M2"].index.equals(means["AH"].index):
            raise ValueError(f"{block}: target clock mismatch")
        d = (means["AH"] - means["M2"]).to_numpy(float)
        se, statistic, p_two = hac_hln(d)
        benchmark = float(means["M2"].mean())
        challenger = float(means["AH"].mean())
        rows.append(
            {
                "block": block,
                "n": len(d),
                "benchmark_mean_loss": benchmark,
                "ah_mean_loss": challenger,
                "gain_percent": 100 * (benchmark - challenger) / benchmark,
                "mean_d": float(d.mean()),
                "p_two_sided_HLN": p_two,
                "HAC_lag": HAC_LAG,
                "HAC_SE": se,
                "DM_HLN_stat": statistic,
                "HAC_CI95_low": float(d.mean() - 1.96 * se),
                "HAC_CI95_high": float(d.mean() + 1.96 * se),
                "benchmark_forecast_sources": "abg4 Q05-Q25; review34/a1_r1_min_validation_lambda Q30-Q95",
                "ah_forecast_sources": "review25/c1b2a Q05-Q25; review34/ah_m2_minlambda Q30-Q95",
            }
        )
    return pd.DataFrame(rows)


def main() -> None:
    result = calculate()
    OUT.parent.mkdir(parents=True, exist_ok=True)
    result.to_csv(OUT, index=False, float_format="%.12g")
    print(result.to_string(index=False))
    print(f"wrote {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
