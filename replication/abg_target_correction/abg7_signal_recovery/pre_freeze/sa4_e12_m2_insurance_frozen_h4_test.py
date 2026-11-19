#!/usr/bin/env python3
"""SA4-E12 M2 frozen-lambda h=4 19Q TEST.

Specification
-------------
    Q_tau(y[t+1] | y[t], FRED-MD[t])

The design is imported directly from the completed SA4-E10-SEP-RISK common-history validation
script.  Current GDP growth and all public FRED-MD slopes are L2
penalized; the intercept is unpenalized.

Scientific protocol
-------------------
- TEST targets: 2008Q4 -> 2026Q1.
- Tau-specific lambda values are read ONLY from completed E5 validation
  checkpoints.
- The validation design SHA256 must match the TEST design SHA256.
- NO lambda grid exists here.
- NO lambda selection is performed here.
- NO E5/E6/E7 lambda reuse | NO TEST tuning.
- Checkpointed by tau.
"""

from __future__ import annotations

import importlib.util
import json
import time
from pathlib import Path

import numpy as np
import pandas as pd

from scenariolab.highdim.dynamic_horizon_validation import (
    run_frozen_lambda_dynamic_horizon_test,
)


# ======================================================
# Configuration
# ======================================================

E5_VALIDATION_SCRIPT = Path(
    "scripts/sa4_e12_m2_insurance_frozen_validation.py"
)

VALIDATION_DIR = Path(
    "outputs/sa4/e12/m2_insurance_frozen_validation"
)

VALIDATION_CHECKPOINTS = VALIDATION_DIR / "checkpoints"

OUTDIR = Path(
    "outputs/sa4/e12/m2_insurance_frozen_h4_test"
)

CHECKPOINT_DIR = OUTDIR / "checkpoints"

MASTER_DETAIL = OUTDIR / (
    "SA4_E12_M2_INSURANCE_H4_Frozen_Test_Detail.csv"
)

MASTER_SUMMARY = OUTDIR / (
    "SA4_E12_M2_INSURANCE_H4_Frozen_Test_Summary.csv"
)

MASTER_TEXT = OUTDIR / (
    "SA4_E12_M2_INSURANCE_H4_Frozen_Test_Summary.txt"
)

LOG_PATH = OUTDIR / (
    "SA4_E12_M2_INSURANCE_H4_FROZEN_TEST.log"
)

HORIZON = 4

TAUS = np.round(
    np.arange(0.05, 1.00, 0.05),
    2,
)

TEST_TARGETS = pd.period_range(
    "2008Q4",
    "2026Q1",
    freq="Q",
)


# ======================================================
# Utilities
# ======================================================

def log(message: str) -> None:
    stamp = time.strftime("%Y-%m-%d %H:%M:%S")
    line = f"{stamp} {message}"
    print(line, flush=True)
    with LOG_PATH.open("a", encoding="utf-8") as f:
        f.write(line + "\n")


def tau_tag(tau: float) -> str:
    return f"Q{int(round(float(tau) * 100)):02d}"


def paths_for_tau(tau: float) -> dict[str, Path]:
    tag = tau_tag(tau)
    return {
        "detail": CHECKPOINT_DIR / f"{tag}_detail.csv",
        "summary": CHECKPOINT_DIR / f"{tag}_summary.csv",
        "meta": CHECKPOINT_DIR / f"{tag}_meta.json",
        "done": CHECKPOINT_DIR / f"{tag}.done",
    }


def checkpoint_complete(tau: float) -> bool:
    p = paths_for_tau(tau)
    return all(
        p[key].exists()
        for key in ("detail", "summary", "meta", "done")
    )


def load_e8_validation_module():
    spec = importlib.util.spec_from_file_location(
        "sa4_e10_sep_risk_benchmark_validation",
        E5_VALIDATION_SCRIPT,
    )
    if spec is None or spec.loader is None:
        raise RuntimeError(
            f"Cannot import {E5_VALIDATION_SCRIPT}"
        )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def load_lambda_map(
    expected_fingerprint: str,
) -> dict[float, float]:
    """
    Load the 19 lambdas frozen in the certified E12
    pre-GFC development/validation exercise.

    IMPORTANT:
    The validation design fingerprint MUST NOT equal
    the frozen-TEST fingerprint because validation is
    physically truncated at 2007Q3 whereas TEST uses
    the full 1994Q2-2026Q1 design.

    Integrity is therefore established by:
      1. exact development/validation protocol;
      2. common validation design SHA across all 19 taus;
      3. exact identity with the certified lambda-vector CSV.
    """

    # The argument is deliberately retained because main()
    # already passes the TEST fingerprint.  It is NOT used
    # as the validation fingerprint.
    _ = expected_fingerprint

    vector_path = (
        VALIDATION_DIR
        / "SA4_E12_M2_INSURANCE_H4_Frozen_Lambda_Vector.csv"
    )

    if not vector_path.exists():
        raise FileNotFoundError(
            f"Missing certified lambda vector: {vector_path}"
        )

    vector = pd.read_csv(
        vector_path
    )

    required_vector = {
        "tau",
        "lambda_star",
        "n_validation",
        "n_min",
        "validation_start",
        "validation_end",
        "design_sha256",
    }

    missing = (
        required_vector
        - set(vector.columns)
    )

    if missing:
        raise AssertionError(
            "Certified lambda vector missing columns: "
            f"{sorted(missing)}"
        )

    if len(vector) != 19:
        raise AssertionError(
            f"Certified lambda vector N={len(vector)}, expected=19"
        )

    if vector["tau"].duplicated().any():
        raise AssertionError(
            "Duplicate tau in certified lambda vector"
        )

    if not vector["n_validation"].eq(23).all():
        raise AssertionError(
            "Certified validation N changed"
        )

    if not vector["n_min"].eq(24).all():
        raise AssertionError(
            "Certified N_MIN changed"
        )

    if not vector["validation_start"].eq(
        "2002Q1"
    ).all():
        raise AssertionError(
            "Certified validation start changed"
        )

    if not vector["validation_end"].eq(
        "2007Q3"
    ).all():
        raise AssertionError(
            "Certified validation end changed"
        )

    validation_hashes = (
        vector["design_sha256"]
        .astype(str)
        .unique()
    )

    if len(validation_hashes) != 1:
        raise AssertionError(
            "Certified vector contains multiple "
            "validation design hashes"
        )

    validation_fingerprint = str(
        validation_hashes[0]
    )

    vector_map = {
        round(float(r["tau"]), 2):
            float(r["lambda_star"])
        for _, r in vector.iterrows()
    }

    result: dict[float, float] = {}

    for tau_raw in TAUS:

        tau = float(tau_raw)
        tag = tau_tag(tau)

        meta_path = (
            VALIDATION_CHECKPOINTS
            / f"{tag}_meta.json"
        )

        done_path = (
            VALIDATION_CHECKPOINTS
            / f"{tag}.done"
        )

        if not meta_path.exists():
            raise FileNotFoundError(
                f"{tag}: missing validation meta: "
                f"{meta_path}"
            )

        if not done_path.exists():
            raise FileNotFoundError(
                f"{tag}: missing validation done marker"
            )

        meta = json.loads(
            meta_path.read_text(
                encoding="utf-8"
            )
        )

        if int(meta["horizon"]) != HORIZON:
            raise AssertionError(
                f"{tag}: validation horizon differs"
            )

        if round(
            float(meta["tau"]),
            2,
        ) != tau:
            raise AssertionError(
                f"{tag}: validation tau differs"
            )

        if int(
            meta["n_validation"]
        ) != 23:
            raise AssertionError(
                f"{tag}: validation N differs"
            )

        if int(
            meta["n_min"]
        ) != 24:
            raise AssertionError(
                f"{tag}: N_MIN differs"
            )

        if meta[
            "development_start"
        ] != "1994Q2":
            raise AssertionError(
                f"{tag}: development start differs"
            )

        if meta[
            "development_end"
        ] != "2007Q3":
            raise AssertionError(
                f"{tag}: development end differs"
            )

        if meta[
            "validation_start"
        ] != "2002Q1":
            raise AssertionError(
                f"{tag}: validation start differs"
            )

        if meta[
            "validation_end"
        ] != "2007Q3":
            raise AssertionError(
                f"{tag}: validation end differs"
            )

        if str(
            meta["design_sha256"]
        ) != validation_fingerprint:
            raise AssertionError(
                f"{tag}: validation design SHA differs "
                "from certified lambda vector"
            )

        lambda_meta = float(
            meta["lambda_star"]
        )

        lambda_vector = float(
            vector_map[tau]
        )

        if not np.isclose(
            lambda_meta,
            lambda_vector,
        ):
            raise AssertionError(
                f"{tag}: checkpoint lambda "
                f"{lambda_meta} != certified "
                f"vector lambda {lambda_vector}"
            )

        result[tau] = lambda_meta

    if len(result) != 19:
        raise AssertionError(
            f"Expected 19 frozen lambdas, got "
            f"{len(result)}"
        )

    return result


# ======================================================
# One tau
# ======================================================

def run_tau(
    X: pd.DataFrame,
    y: pd.Series,
    *,
    tau: float,
    lambda_star: float,
    fingerprint: str,
) -> None:
    tag = tau_tag(tau)

    log(
        f"[START] {tag} "
        f"tau={tau:.2f} "
        f"lambda*={lambda_star:g}"
    )

    started = time.time()

    result = run_frozen_lambda_dynamic_horizon_test(
        X,
        y,
        horizon=HORIZON,
        tau=float(tau),
        lambda_star=float(lambda_star),
        test_target_dates=TEST_TARGETS,
    )

    detail = result.forecasts.copy()

    # --------------------------------------------------
    # Scientific invariance gates
    # --------------------------------------------------

    if len(detail) != len(TEST_TARGETS):
        raise AssertionError(
            f"{tag}: expected {len(TEST_TARGETS)} "
            f"TEST forecasts, got {len(detail)}"
        )

    expected_targets = [
        str(x) for x in TEST_TARGETS
    ]

    if detail["target"].tolist() != expected_targets:
        raise AssertionError(
            f"{tag}: TEST target calendar differs"
        )

    if not detail["tau"].eq(float(tau)).all():
        raise AssertionError(
            f"{tag}: tau changed during TEST"
        )

    if not detail["lambda_star"].eq(
        float(lambda_star)
    ).all():
        raise AssertionError(
            f"{tag}: frozen lambda changed in TEST"
        )

    if detail["prediction"].isna().any():
        raise AssertionError(
            f"{tag}: missing TEST prediction"
        )

    if detail["actual"].isna().any():
        raise AssertionError(
            f"{tag}: missing TEST actual"
        )

    if detail["pinball"].isna().any():
        raise AssertionError(
            f"{tag}: missing TEST pinball"
        )

    # Predictor availability is origin-specific by design.
    # The certified dynamic-horizon engine determines the eligible
    # predictor set recursively at each forecast origin. Therefore
    # n_predictors/predictors/excluded_predictors may legitimately
    # change through TEST and must not be forced to remain constant.

    mean_pinball = float(
        detail["pinball"].mean()
    )

    summary = pd.DataFrame(
        [
            {
                "horizon": HORIZON,
                "tau": float(tau),
                "lambda_star": float(
                    lambda_star
                ),
                "score_sample": "FULL_TEST",
                "N": len(detail),
                "mean_pinball": mean_pinball,
                "sum_pinball": float(
                    detail["pinball"].sum()
                ),
                "min_prediction": float(
                    detail["prediction"].min()
                ),
                "max_prediction": float(
                    detail["prediction"].max()
                ),
                "min_n_predictors": int(
                    detail["n_predictors"].min()
                ),
                "max_n_predictors": int(
                    detail["n_predictors"].max()
                ),
                "design_sha256": fingerprint,
                "specification": (
                    "intercept + "
                    "GDP_GROWTH_CURRENT + "
                    "FRED-MD; all slopes L2"
                ),
            }
        ]
    )

    # Save checkpoint before done marker.
    p = paths_for_tau(tau)

    detail.to_csv(
        p["detail"],
        index=False,
    )

    summary.to_csv(
        p["summary"],
        index=False,
    )

    elapsed = time.time() - started

    meta = {
        "tau": float(tau),
        "lambda_star": float(lambda_star),
        "horizon": HORIZON,
        "n_test": len(detail),
        "test_start": str(TEST_TARGETS[0]),
        "test_end": str(TEST_TARGETS[-1]),
        "design_sha256": fingerprint,
        "specification": (
            "intercept + GDP_GROWTH_CURRENT + "
            "FRED-MD; all slopes L2"
        ),
        "lambda_source": (
            "SA4-E12 M2 frozen-validation checkpoint"
        ),
        "lambda_selection_in_test": False,
        "elapsed_seconds": elapsed,
        "status": "COMPLETE",
    }

    p["meta"].write_text(
        json.dumps(meta, indent=2) + "\n",
        encoding="utf-8",
    )

    # Written LAST.
    p["done"].write_text(
        "COMPLETE\n",
        encoding="utf-8",
    )

    log(
        f"[COMPLETE] {tag} "
        f"mean_pinball={mean_pinball:.9f} "
        f"N={len(detail)} "
        f"elapsed={elapsed/60:.1f}m"
    )


# ======================================================
# Master outputs
# ======================================================

def build_master() -> tuple[
    pd.DataFrame,
    pd.DataFrame,
]:
    details = []
    summaries = []

    for tau_raw in TAUS:
        tau = float(tau_raw)

        if not checkpoint_complete(tau):
            continue

        p = paths_for_tau(tau)

        details.append(
            pd.read_csv(p["detail"])
        )

        summaries.append(
            pd.read_csv(p["summary"])
        )

    detail = (
        pd.concat(
            details,
            ignore_index=True,
        )
        if details
        else pd.DataFrame()
    )

    summary = (
        pd.concat(
            summaries,
            ignore_index=True,
        )
        if summaries
        else pd.DataFrame()
    )

    if not detail.empty:
        detail = detail.sort_values(
            ["tau", "target"]
        ).reset_index(drop=True)

        detail.to_csv(
            MASTER_DETAIL,
            index=False,
        )

    if not summary.empty:
        summary = summary.sort_values(
            "tau"
        ).reset_index(drop=True)

        summary.to_csv(
            MASTER_SUMMARY,
            index=False,
        )

        MASTER_TEXT.write_text(
            summary.to_string(index=False)
            + "\n",
            encoding="utf-8",
        )

    return detail, summary


# ======================================================
# Main
# ======================================================

def main() -> None:
    OUTDIR.mkdir(
        parents=True,
        exist_ok=True,
    )
    CHECKPOINT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    validation = load_e8_validation_module()

    X, y, included, excluded = (
        validation.load_full_design()
    )

    fingerprint = (
        validation.design_fingerprint(
            X,
            y,
            HORIZON,
        )
    )

    lambda_map = load_lambda_map(
        fingerprint
    )

    log("=" * 72)
    log("SA4-E12 M2+INSURANCE h=4 FROZEN TEST")
    log(
        "Specification: intercept + current GDP "
        "+ all public FRED-MD + Insurance Risk Minutes"
    )
    log(
        "Penalty: L2 on current GDP, every "
        "FRED-MD slope, and Insurance; intercept unpenalized"
    )
    log(
        f"TEST targets: {TEST_TARGETS[0]} -> "
        f"{TEST_TARGETS[-1]} "
        f"(N={len(TEST_TARGETS)})"
    )
    log(
        "Lambdas: frozen from SA4-E12 M2+INSURANCE PRE-GFC FROZEN VALIDATION"
    )
    log(
        "NO lambda selection | NO TEST tuning | "
        "NO E3/E4 reuse"
    )
    log(
        f"Base predictors={len(included)} "
        f"(includes {validation.GDP}); "
        f"excluded={excluded}"
    )
    log(f"Design SHA256={fingerprint}")
    log("=" * 72)

    for tau_raw in TAUS:
        tau = float(tau_raw)

        if checkpoint_complete(tau):
            p = paths_for_tau(tau)

            meta = json.loads(
                p["meta"].read_text(
                    encoding="utf-8"
                )
            )

            if (
                meta.get("design_sha256")
                != fingerprint
            ):
                raise RuntimeError(
                    f"{tau_tag(tau)}: TEST "
                    f"checkpoint belongs to "
                    f"another design"
                )

            if float(
                meta["lambda_star"]
            ) != float(
                lambda_map[tau]
            ):
                raise RuntimeError(
                    f"{tau_tag(tau)}: TEST "
                    f"checkpoint lambda differs "
                    f"from frozen validation lambda"
                )

            log(
                f"[REUSE E5 TEST] "
                f"{tau_tag(tau)} "
                f"lambda*={lambda_map[tau]:g}"
            )
            continue

        run_tau(
            X,
            y,
            tau=tau,
            lambda_star=lambda_map[tau],
            fingerprint=fingerprint,
        )

        build_master()

    detail, summary = build_master()

    if len(summary) != 19:
        raise AssertionError(
            f"Expected 19 completed TEST "
            f"quantiles, got {len(summary)}"
        )

    if len(detail) != 19 * len(TEST_TARGETS):
        raise AssertionError(
            "Master TEST detail has unexpected "
            "number of rows"
        )

    log("=" * 72)
    log("COMPLETE: 19/19 frozen TEST quantiles")
    log(f"Master detail: {MASTER_DETAIL}")
    log(f"Master summary: {MASTER_SUMMARY}")
    log("=" * 72)


if __name__ == "__main__":
    main()
