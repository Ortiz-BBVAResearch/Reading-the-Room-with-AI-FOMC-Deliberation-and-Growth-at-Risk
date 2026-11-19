"""Record the lambda schedules and training clocks of Review 37e families.

Only the `lambda_mean`, `origin`, `n_train`, `solver_scale` columns and JSON
metadata are read. Forecasts, realizations, and losses are never loaded.
"""

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "outputs/sa6/preenvio_jme/penalties_by_family.csv"
TAUS = [5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55, 60, 65, 70, 75, 80, 85, 90, 95]
BLOCK_TAUS = {
    "LOWER": TAUS[:5],
    "CENTER": TAUS[5:14],
    "UPPER": TAUS[14:],
}
TRAINING_SCALE = (
    "SUM_PRIMARY: L1 lambda multiplies the summed pinball objective; no lambda/N rescaling. "
    "The sealed engine can use MEAN_FALLBACK_AFTER_SUM_FAILURE at a failed origin."
)


def read_bank(folder: str, prefix: str, tau: int) -> dict[str, object] | None:
    directory = ROOT / folder
    tag = f"Q{tau:02d}"
    csv_path = directory / f"{prefix}_{tag}_sealed.csv"
    meta_path = directory / f"{prefix}_{tag}_meta.json"
    if not csv_path.exists():
        return None
    frame = pd.read_csv(csv_path, usecols=["origin", "n_train", "lambda_mean", "solver_scale"])
    if frame.empty or frame["lambda_mean"].nunique(dropna=False) != 1:
        raise ValueError(f"Nonconstant lambda or empty bank: {csv_path}")
    meta = json.loads(meta_path.read_text()) if meta_path.exists() else {}
    first = frame.iloc[0]
    return {
        "lambda": float(first["lambda_mean"]),
        "origin": str(first["origin"]),
        "n_train": int(first["n_train"]),
        "solver_scale": str(first["solver_scale"]),
        "csv_path": str(csv_path.relative_to(ROOT)),
        "meta_path": str(meta_path.relative_to(ROOT)) if meta_path.exists() else "",
        "meta_lambda_hash": str(meta.get("lambda_vector_sha256", "")),
        "meta_history_start": str(meta.get("common_history_start", "")),
        "meta_n_origins": str(meta.get("n_origins", "")),
    }


def collect(specs: list[dict[str, object]]) -> tuple[dict[int, float], list[dict[str, object]]]:
    lambdas: dict[int, float] = {}
    records: list[dict[str, object]] = []
    for spec in specs:
        taus = spec.get("taus", TAUS)
        for prefix in spec["prefixes"]:
            for tau in taus:
                result = read_bank(spec["folder"], prefix, tau)
                if result is None:
                    continue
                if tau in lambdas and not np.isclose(lambdas[tau], result["lambda"], rtol=0, atol=1e-12):
                    raise ValueError(f"Base/HD lambda mismatch at Q{tau:02d}")
                lambdas[tau] = result["lambda"]
                records.append(result)
    return lambdas, records


def fmt_block(lambdas: dict[int, float], block: str) -> str:
    present = [(tau, lambdas[tau]) for tau in BLOCK_TAUS[block] if tau in lambdas]
    if not present:
        return "not banked in this universe"
    vals = {round(value, 6) for _, value in present}
    if len(present) == len(BLOCK_TAUS[block]) and len(vals) == 1:
        return f"{present[0][1]:.6f}"
    return ";".join(f"Q{tau:02d}={value:.6f}" for tau, value in present)


def canonical_hash(lambdas: dict[int, float]) -> str:
    if set(lambdas) != set(TAUS):
        return "not computable: fewer than 19 quantile banks in this universe"
    vector = ",".join(f"{lambdas[tau]:.6f}" for tau in TAUS)
    return hashlib.sha256(vector.encode("utf-8")).hexdigest()


def main() -> None:
    families = [
        (1, "A1 principal — M2 y M2+HD", "Tablas 2 y 3", "M2 / M2+HD",
         [{"folder": "outputs/sa6/abg_target_correction/abg4_sealed_test/checkpoints",
           "prefixes": ["R2", "R2_HD"]}], "1973Q1"),
        (2, "A1 principal — M3 y M3+HD", "Tabla 3", "M3 / M3+HD",
         [{"folder": "outputs/sa6/abg_target_correction/abg4_sealed_test/checkpoints",
           "prefixes": ["R2_NFCI", "R2_NFCI_HD"]}], "1973Q1"),
        (3, "Historia común — M2_CH y M2_CH+HD", "Benchmark de historia común", "M2_CH / M2_CH+HD",
         [{"folder": "outputs/sa6/construct_validation/review34/a4b_panel_spf/checkpoints",
           "prefixes": ["M2_CH", "M2_CH_HD"]}], "1974Q4"),
        (4, "Historia común — M3_CH y M3_CH+HD", "Benchmark de historia común", "M3_CH / M3_CH+HD",
         [{"folder": "outputs/sa6/construct_validation/review34/m3_common_history_lower/checkpoints",
           "prefixes": ["M3_CH", "M3_CH_HD"], "taus": TAUS[:5]}], "1974Q4"),
        (5, "C1 — A4B_M2_SEP y +HD", "Tabla 9", "A4B_M2_SEP / +HD",
         [
             {"folder": "outputs/sa6/construct_validation/review34/a4b_panel_spf/checkpoints",
              "prefixes": ["A4B_M2_SEP", "A4B_M2_SEP_HD"], "taus": TAUS[:5] + TAUS[14:]},
             {"folder": "outputs/sa6/construct_validation/review37b_sep_long/forecasting/ct_m2/checkpoints",
              "prefixes": ["A4B_M2_SEP", "A4B_M2_SEP_HD"], "taus": TAUS[5:14]},
         ], "1974Q4"),
        (6, "C3 — M2+DISP_long y +HD, centro", "Tabla 9", "M2_DISP_LONG70 / +HD — CENTER",
         [{"folder": "outputs/sa6/construct_validation/review37c/forecasting/c3_disp_m2/checkpoints",
           "prefixes": ["M2_DISP_LONG70", "M2_DISP_LONG70_HD"], "taus": TAUS[5:14]}], "1974Q4"),
        (7, "C2 — M3+DISP_long y +HD, inferior", "Tabla 9", "M3_DISP_LONG45 / +HD — LOWER",
         [{"folder": "outputs/sa6/construct_validation/review37b_sep_long/forecasting/disp_m3/checkpoints",
           "prefixes": ["M3_DISP_LONG45", "M3_DISP_LONG45_HD"], "taus": TAUS[:5]}], "1974Q4"),
        (8, "C4 — M3+CT_long y +HD, inferior", "Tabla 9", "M3_CT_LONG70 / +HD — LOWER",
         [{"folder": "outputs/sa6/construct_validation/review37c/forecasting/c4_ct_m3/checkpoints",
           "prefixes": ["M3_CT_LONG70", "M3_CT_LONG70_HD"], "taus": TAUS[:5]}], "1974Q4"),
        (9, "M2+DISP_long — primera ejecución inferior/superior", "Review 37e, sección 3", "M2_DISP_LONG70 / +HD — LOWER + UPPER primera ejecución",
         [{"folder": "outputs/sa6/construct_validation/review37e/forecasting/disp_m2_completion/checkpoints",
           "prefixes": ["M2_DISP_LONG70", "M2_DISP_LONG70_HD"], "taus": TAUS[:5] + TAUS[14:]}], "1974Q4"),
        (10, "M2+DISP_long — rama UPPER100", "Review 37e, sección 3", "M2_DISP_LONG70 / +HD — UPPER100",
         [{"folder": "outputs/sa6/construct_validation/review37e/forecasting/disp_m2_upper100/checkpoints",
           "prefixes": ["M2_DISP_LONG70", "M2_DISP_LONG70_HD"], "taus": TAUS[14:]}], "1974Q4"),
        (11, "Tiempo real — Tabla 4", "Tabla 4", "M2 realtime / M2 realtime+HD",
         [{"folder": "outputs/sa6/realtime_fredmd/rt1_sealed_test/checkpoints",
           "prefixes": ["REALTIME_MATCHED_PUBLIC", "REALTIME_MATCHED_HD"]}], "1973Q1"),
        (11, "Tiempo real — Tabla 5", "Tabla 5", "M3 realtime / M3 realtime+HD",
         [{"folder": "outputs/sa6/realtime_fredmd/rtm3_sealed_test/checkpoints",
           "prefixes": ["REALTIME_MATCHED_NFCI", "REALTIME_MATCHED_NFCI_HD"]}], "1973Q1"),
    ]

    output_rows = []
    for family_no, family, use, universe, specs, training_start in families:
        lambdas, records = collect(specs)
        if not records:
            raise ValueError(f"No bank metadata found for {universe}")
        first_origin = {str(r["origin"]) for r in records}
        first_n = {int(r["n_train"]) for r in records}
        scales = {str(r["solver_scale"]) for r in records}
        if len(first_origin) != 1 or len(first_n) != 1:
            raise ValueError(f"Base/HD training clock mismatch in {universe}: {first_origin}, {first_n}")
        folders = sorted({str(r["csv_path"]).rsplit("/", 1)[0] for r in records})
        prefixes = sorted({str(r["csv_path"]).rsplit("/", 1)[-1].split("_Q")[0] for r in records})
        meta_paths = sorted({str(r["meta_path"]) for r in records})
        meta_hashes = sorted({str(r["meta_lambda_hash"]) for r in records if r["meta_lambda_hash"]})
        history_starts = sorted({str(r["meta_history_start"]) for r in records if r["meta_history_start"]})
        n_origins = sorted({str(r["meta_n_origins"]) for r in records if r["meta_n_origins"]})
        missing_taus = [tau for tau in TAUS if tau not in lambdas]
        metadata_note = (
            f"lambda_mean per tau from sealed CSV; metadata lambda_vector_sha256={';'.join(meta_hashes)}"
            if meta_hashes else "lambda_mean per tau from sealed CSV; lambda_vector_sha256 absent in metadata"
        )
        if history_starts:
            metadata_note += f"; common_history_start={','.join(history_starts)}"
        if n_origins:
            metadata_note += f"; n_origins={','.join(n_origins)}"
        if missing_taus:
            metadata_note += "; missing tau banks=" + ",".join(f"Q{x:02d}" for x in missing_taus)

        output_rows.append({
            "family_no": family_no,
            "family": family,
            "paper_use": use,
            "model_universe": universe,
            "lambda_lower_Q05_Q25": fmt_block(lambdas, "LOWER"),
            "lambda_center_Q30_Q70": fmt_block(lambdas, "CENTER"),
            "lambda_upper_Q75_Q95": fmt_block(lambdas, "UPPER"),
            "lambda_vector_19_Q05_to_Q95": ",".join(f"{lambdas[t]:.6f}" if t in lambdas else "NA" for t in TAUS),
            "first_training_row": training_start,
            "first_origin": next(iter(first_origin)),
            "n_train_at_first_origin": next(iter(first_n)),
            "lambda_scale": TRAINING_SCALE,
            "bank_path_and_prefixes": " ; ".join(folders + ["prefixes=" + ",".join(prefixes)]),
            "bank_lambda_field": "lambda_mean (per tau; sealed forecast CSV; only metadata columns read)",
            "metadata_field_read": "lambda_vector_sha256; common_history_start; n_origins (when present)",
            "metadata_paths": " ; ".join(meta_paths),
            "metadata_values": metadata_note,
            "sha256_lambda_vector_19_six_decimals": canonical_hash(lambdas),
            "solver_scale_values_at_first_origin": ";".join(sorted(scales)),
        })

    OUT.parent.mkdir(parents=True, exist_ok=True)
    with OUT.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(output_rows[0]))
        writer.writeheader()
        writer.writerows(output_rows)


if __name__ == "__main__":
    main()
