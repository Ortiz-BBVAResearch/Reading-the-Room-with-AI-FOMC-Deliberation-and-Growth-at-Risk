#!/usr/bin/env python3

"""
Protocol B — Review15 closing signal-symmetry sealed TEST worker.

One invocation executes exactly ONE frozen model x tau job:
    70 TEST origins.

The worker:
- reads the frozen B4 contract;
- never selects lambda;
- never changes predictor eligibility;
- uses the frozen sealed estimation engine;
- stores predictions and realized values for later B6 evaluation;
- does NOT compute or display forecast loss/performance.

SUM -> MEAN fallback is handled only inside the frozen sealed engine.

NO lambda selection.
NO grid search.
NO model ranking.
NO TEST performance displayed.
"""

from pathlib import Path
import argparse
import hashlib
import json
import time

import numpy as np
import pandas as pd

from scenariolab.highdim.protocol_b_sealed_test import (
    fit_one_sealed_protocol_b_forecast,
)


CONTRACT = Path(
    "outputs/sa6/protocol_b/review15_closing/contract/"
    "ProtocolB_Review15_Closing_Contract.csv"
)

LAMBDAS = Path(
    "outputs/sa6/protocol_b/b2_validation/selection/"
    "ProtocolB_B2_Frozen_Block_Lambdas.csv"
)

FRED = Path(
    "outputs/sa4/data_audit/"
    "FREDMD_Quarterly_TRANSFORMED.csv"
)

GDP = Path(
    "data/raw/usa/macro/gdp_growth.csv"
)

QDISC = Path(
    "outputs/sa6/protocol_b/review15_closing/"
    "p0_qd_bridge/"
    "Review15_QD_Minutes_Conservative_Realtime_Bridge.csv"
)

VERBOSITY = Path(
    "outputs/sa6/protocol_b/review13_interaction/"
    "p0d_verbosity_placebo/"
    "Review13_Verbosity_Minutes_Conservative_Realtime_Bridge.csv"
)

NFCI = Path(
    "data/derived/usa/financial/e12/"
    "SA4_E12_NFCI_Quarterly_Realtime_Bridge.csv"
)

SEALED_ENGINE = Path(
    "src/scenariolab/highdim/"
    "protocol_b_sealed_test.py"
)

FOCAL_MODULE = Path(
    "src/scenariolab/highdim/"
    "protocol_b_focal.py"
)

SUM_MODULE = Path(
    "src/scenariolab/highdim/"
    "protocol_b_penalized_quantile.py"
)

MEAN_MODULE = Path(
    "src/scenariolab/highdim/"
    "protocol_b_penalized_quantile_mean_fallback.py"
)

OUTDIR = Path(
    "outputs/sa6/protocol_b/review15_closing/"
    "forecasts/checkpoints"
)

EXPECTED_CONTRACT_SHA = (
    "9deacb10e8ee3bb339d65540fd105dd8"
    "d90bd21dfbbf9f2286b14984f41e202e"
)

EXPECTED_QDISC_SHA = (
    "7603c59ca052c6c6138593f4c3c0cb81"
    "4793e29936eb3a407457921b9823208e"
)

EXPECTED_VERBOSITY_SHA = (
    "ad98cf109115130c91fac31f32555771e"
    "ef64ad5dcb68c587a27a16714540193"
)

EXPECTED_NFCI_SHA = (
    "71d8b8e92bffefd536b2c618c3906bba"
    "32fda3af99d2bb1508795815c47277d0"
)

EXPECTED_LAMBDA_SHA = (
    "81af45e41246bc9c6d2665764f9dbc90"
    "c0ec8f30f10a4db2d18326c8c8fd6183"
)

EXPECTED_SEALED_ENGINE_SHA = (
    "ae47f2a525e0e78e9899e417fb1d2a4e"
    "4b9fc1b63a4ca7dbe2bc09346363bd2b"
)

EXPECTED_FOCAL_SHA = (
    "c7d87a55d3a780eca0c866e24584913f"
    "911299c9170a67562f250dbef3411a6f"
)

EXPECTED_SUM_SHA = (
    "097d3350a11d7603acd26e4e4521af080"
    "71b1e3783a75c21e977982576fa347c"
)

EXPECTED_MEAN_SHA = (
    "96b800b92f36aff3ec408d45e5da82a30"
    "b192b3c331f5a49ef8335def35d6796"
)

INDEX = pd.period_range(
    "1973Q1",
    "2026Q1",
    freq="Q",
)

H = 4

MODELS = {
    "R15_PUBLIC_VERBOSITY",
    "R15_PUBLIC_QDISC",
    "R15_NFCI_QDISC",
}


def sha(path):
    h = hashlib.sha256()

    with path.open("rb") as f:
        for chunk in iter(
            lambda: f.read(1024 * 1024),
            b"",
        ):
            h.update(chunk)

    return h.hexdigest()


def tau_tag(tau):
    return (
        f"Q{int(round(float(tau) * 100)):02d}"
    )


def job_paths(model, tau):

    stem = (
        f"{model}_{tau_tag(tau)}"
    )

    return {
        "detail":
            OUTDIR / f"{stem}_sealed.csv",
        "meta":
            OUTDIR / f"{stem}_meta.json",
        "done":
            OUTDIR / f"{stem}.done",
    }


def load_focal(path, column):

    d = pd.read_csv(path)

    q = pd.PeriodIndex(
        d["origin_quarter"].astype(str),
        freq="Q",
    )

    if q.duplicated().any():
        raise RuntimeError(
            f"{column}: duplicate origin quarters."
        )

    return pd.Series(
        d[column].to_numpy(
            dtype=float
        ),
        index=q,
        name=column,
    )


def load_inputs():

    fd = pd.read_csv(FRED)

    fq = pd.PeriodIndex(
        fd["quarter"].astype(str),
        freq="Q",
    )

    Xf = (
        fd.drop(
            columns=["quarter"]
        )
        .astype(float)
    )

    Xf.index = fq

    Xf = Xf.reindex(
        INDEX
    )

    gd = pd.read_csv(GDP)

    gd["observation_date"] = (
        pd.to_datetime(
            gd["observation_date"]
        )
    )

    gd["quarter"] = (
        gd["observation_date"]
        .dt.to_period("Q")
    )

    y = (
        gd.set_index(
            "quarter"
        )[
            "A191RL1Q225SBEA"
        ]
        .astype(float)
        .reindex(INDEX)
    )

    if y.isna().any():
        raise RuntimeError(
            "GDP series contains missing values."
        )

    qdisc = load_focal(
        QDISC,
        "QD_MINUTES_AVAILABLE",
    )

    verbosity = load_focal(
        VERBOSITY,
        "VERBOSITY_MINUTES_AVAILABLE",
    )

    nfci = load_focal(
        NFCI,
        "NFCI_AVAILABLE",
    )

    return (
        Xf,
        y,
        qdisc,
        verbosity,
        nfci,
    )


def main():

    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--model",
        required=True,
        choices=sorted(MODELS),
    )

    parser.add_argument(
        "--tau",
        required=True,
        type=float,
    )

    args = parser.parse_args()

    model_name = str(
        args.model
    )

    tau = float(
        args.tau
    )

    allowed_taus = np.round(
        np.arange(
            0.05,
            1.00,
            0.05,
        ),
        2,
    )

    if not np.any(
        np.isclose(
            allowed_taus,
            tau,
            rtol=0.0,
            atol=1e-12,
        )
    ):
        raise RuntimeError(
            f"Invalid frozen tau={tau}"
        )

    # --------------------------------------------------
    # Provenance gates BEFORE any TEST fit.
    # --------------------------------------------------

    gates = {
        "contract":
            (
                CONTRACT,
                EXPECTED_CONTRACT_SHA,
            ),
        "lambda":
            (
                LAMBDAS,
                EXPECTED_LAMBDA_SHA,
            ),
        "sealed_engine":
            (
                SEALED_ENGINE,
                EXPECTED_SEALED_ENGINE_SHA,
            ),
        "focal":
            (
                FOCAL_MODULE,
                EXPECTED_FOCAL_SHA,
            ),
        "sum":
            (
                SUM_MODULE,
                EXPECTED_SUM_SHA,
            ),
        "mean":
            (
                MEAN_MODULE,
                EXPECTED_MEAN_SHA,
            ),
        "qdisc_bridge":
            (
                QDISC,
                EXPECTED_QDISC_SHA,
            ),
        "verbosity_bridge":
            (
                VERBOSITY,
                EXPECTED_VERBOSITY_SHA,
            ),
        "nfci_bridge":
            (
                NFCI,
                EXPECTED_NFCI_SHA,
            ),
    }

    for name, (
        path,
        expected,
    ) in gates.items():

        got = sha(path)

        if got != expected:
            raise RuntimeError(
                f"{name} SHA changed: {got}"
            )

    OUTDIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    p = job_paths(
        model_name,
        tau,
    )

    if p["done"].exists():
        print(
            f"[SKIP] {model_name} "
            f"{tau_tag(tau)}"
        )
        return

    # Never trust an incomplete prior artifact.
    for key in (
        "detail",
        "meta",
    ):
        if p[key].exists():
            p[key].unlink()

    contract = pd.read_csv(
        CONTRACT
    )

    job = (
        contract.loc[
            contract["model"].eq(
                model_name
            )
            &
            np.isclose(
                contract["tau"],
                tau,
                rtol=0.0,
                atol=1e-12,
            )
        ]
        .copy()
        .reset_index(drop=True)
    )

    if len(job) != 70:
        raise RuntimeError(
            f"Frozen job N={len(job)}, expected=70."
        )

    expected_origins = [
        str(x)
        for x in pd.period_range(
            "2007Q4",
            "2025Q1",
            freq="Q",
        )
    ]

    if (
        job["origin"]
        .astype(str)
        .tolist()
        != expected_origins
    ):
        raise RuntimeError(
            "Frozen origin clock changed."
        )

    if job[
        "lambda_mean"
    ].nunique() != 1:
        raise RuntimeError(
            "Job contains multiple lambdas."
        )

    Xf, y, qdisc, verbosity, nfci = (
        load_inputs()
    )

    rows = []
    fallback_count = 0

    started = time.time()

    for _, spec in (
        job.iterrows()
    ):

        origin = pd.Period(
            str(spec["origin"]),
            freq="Q",
        )

        target = pd.Period(
            str(spec["target"]),
            freq="Q",
        )

        t = INDEX.get_loc(
            origin
        )

        if INDEX[
            t + H
        ] != target:
            raise RuntimeError(
                "Contract target clock changed."
            )

        eligible = (
            str(
                spec[
                    "eligible_nuisance"
                ]
            )
            .split("|")
        )

        eligible = [
            x
            for x in eligible
            if x
        ]

        if len(eligible) != int(
            spec["n_nuisance"]
        ):
            raise RuntimeError(
                "Contract nuisance count mismatch."
            )

        missing = (
            set(eligible)
            - set(Xf.columns)
        )

        if missing:
            raise RuntimeError(
                "Contract nuisance missing "
                f"from FRED source: {sorted(missing)}"
            )

        X_public = (
            Xf[
                eligible
            ]
            .copy()
        )

        X_public[
            "GDP_GROWTH_CURRENT"
        ] = y

        focal_raw = {}

        use_nfci = bool(
            spec["use_nfci"]
        )

        use_verbosity = bool(
            spec["use_verbosity"]
        )

        use_qdisc = bool(
            spec["use_qdisc"]
        )

        if (
            int(use_verbosity)
            + int(use_qdisc)
            != 1
        ):
            raise RuntimeError(
                "Review15 contract must activate "
                "exactly one new signal."
            )

        if model_name == "R15_PUBLIC_VERBOSITY":

            if use_nfci:
                raise RuntimeError(
                    "PUBLIC Verbosity unexpectedly "
                    "contains NFCI."
                )

            if not use_verbosity or use_qdisc:
                raise RuntimeError(
                    "PUBLIC Verbosity signal gate failed."
                )

            focal_raw[
                "VERBOSITY_PF1"
            ] = verbosity

        elif model_name == "R15_PUBLIC_QDISC":

            if use_nfci:
                raise RuntimeError(
                    "PUBLIC QDISC unexpectedly "
                    "contains NFCI."
                )

            if not use_qdisc or use_verbosity:
                raise RuntimeError(
                    "PUBLIC QDISC signal gate failed."
                )

            focal_raw[
                "QDISC_PF1"
            ] = qdisc

        elif model_name == "R15_NFCI_QDISC":

            if not use_nfci:
                raise RuntimeError(
                    "NFCI QDISC lost frozen NFCI."
                )

            if not use_qdisc or use_verbosity:
                raise RuntimeError(
                    "NFCI QDISC signal gate failed."
                )

            focal_raw[
                "NFCI_PF1"
            ] = nfci

            focal_raw[
                "QDISC_PF1"
            ] = qdisc

        else:
            raise RuntimeError(
                f"Unexpected Review15 model: {model_name}"
            )

        r = (
            fit_one_sealed_protocol_b_forecast(
                X_public,
                y,
                origin_position=t,
                horizon=H,
                tau=tau,
                lambda_mean=float(
                    spec[
                        "lambda_mean"
                    ]
                ),
                nuisance_predictors=(
                    eligible
                ),
                focal_raw=(
                    focal_raw
                    if focal_raw
                    else None
                ),
                focal_first_available=(
                    "1994Q2"
                ),
            )
        )

        if str(r.origin) != str(
            spec["origin"]
        ):
            raise RuntimeError(
                "Returned origin mismatch."
            )

        if str(r.target) != str(
            spec["target"]
        ):
            raise RuntimeError(
                "Returned target mismatch."
            )

        if r.n_nuisance != int(
            spec["n_nuisance"]
        ):
            raise RuntimeError(
                "Returned nuisance count mismatch."
            )

        if (
            r.solver_scale
            ==
            "MEAN_FALLBACK_AFTER_SUM_FAILURE"
        ):
            fallback_count += 1

        # Store realized y for later B6 evaluation.
        # No loss/performance is computed here.
        actual = float(
            y.loc[
                target
            ]
        )

        rows.append({
            "model":
                model_name,
            "horizon":
                H,
            "origin":
                str(origin),
            "target":
                str(target),
            "tau":
                tau,
            "block":
                str(spec["block"]),
            "lambda_mean":
                float(
                    spec[
                        "lambda_mean"
                    ]
                ),
            "n_train":
                int(r.n_train),
            "n_nuisance":
                int(r.n_nuisance),
            "prediction":
                float(r.prediction),
            "actual":
                actual,
            "solver_scale":
                r.solver_scale,
        })

    detail = pd.DataFrame(
        rows
    )

    if len(detail) != 70:
        raise RuntimeError(
            "Completed job does not contain 70 rows."
        )

    if not np.isfinite(
        detail[
            "prediction"
        ].to_numpy(float)
    ).all():
        raise RuntimeError(
            "Non-finite stored prediction."
        )

    if not np.isfinite(
        detail[
            "actual"
        ].to_numpy(float)
    ).all():
        raise RuntimeError(
            "Non-finite stored actual."
        )

    detail.to_csv(
        p["detail"],
        index=False,
    )

    elapsed = (
        time.time()
        - started
    )

    meta = {
        "status":
            "SEALED_COMPLETE",
        "model":
            model_name,
        "tau":
            tau,
        "n_origins":
            70,
        "n_mean_fallback":
            fallback_count,
        "contract_sha256":
            EXPECTED_CONTRACT_SHA,
        "lambda_vector_sha256":
            EXPECTED_LAMBDA_SHA,
        "sealed_engine_sha256":
            EXPECTED_SEALED_ENGINE_SHA,
        "focal_module_sha256":
            EXPECTED_FOCAL_SHA,
        "sum_module_sha256":
            EXPECTED_SUM_SHA,
        "mean_module_sha256":
            EXPECTED_MEAN_SHA,
        "detail_sha256":
            sha(
                p["detail"]
            ),
        "elapsed_seconds":
            elapsed,
        "loss_computed":
            False,
        "model_ranking":
            False,
        "lambda_selection":
            False,
    }

    p["meta"].write_text(
        json.dumps(
            meta,
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )

    # Completion marker is always written last.
    p["done"].write_text(
        "SEALED_COMPLETE\n",
        encoding="utf-8",
    )

    print(
        f"[COMPLETE] "
        f"{model_name} "
        f"{tau_tag(tau)} "
        f"N=70 "
        f"fallback={fallback_count} "
        f"elapsed={elapsed/60:.1f}m"
    )

    print(
        "NO TEST PERFORMANCE DISPLAYED "
        "| NO LAMBDA SELECTION"
    )


if __name__ == "__main__":
    main()
