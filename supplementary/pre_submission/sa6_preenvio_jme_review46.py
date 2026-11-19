"""Reproduce Review 46 first-stage and Board-vacancy checks.

The author-provided speaker-score CSV is read directly from Downloads and is
never copied. Outputs contain aggregate regression results and pseudonymous
person fixed effects only; no source row, speaker name, or row-level score is
written.
"""

from __future__ import annotations

import hashlib
import json
import re
import unicodedata
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.formula.api as smf


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "outputs/sa6/preenvio_jme"
PRIVATE = Path.home() / "Downloads/pred_score_for_voting_and_non_voting_members.csv"
REVIEW45 = ROOT / "outputs/sa6/review45"
ACCESS_DATE = "2026-10-27"
FED_BOARD_URL = "https://www.federalreserve.gov/aboutthefed/bios/board/boardmembership.htm"

MAIN_START = pd.Timestamp("1976-01-01")
MAIN_END = pd.Timestamp("2018-12-31")
FIRST_STAGE_START = pd.Timestamp("1994-01-01")
FIRST_STAGE_END = pd.Timestamp("2018-12-31")
VACANCY_END = pd.Timestamp("2025-12-31")


def key(value: object) -> str:
    normalized = unicodedata.normalize("NFKD", str(value)).encode("ascii", "ignore").decode()
    return "".join(ch for ch in normalized.lower() if ch.isalpha())


def quarter_label(period: pd.Period) -> str:
    return f"{period.year}Q{period.quarter}"


def load_roster() -> pd.DataFrame:
    governors = pd.read_csv(REVIEW45 / "phase0/roster/governors.csv")
    presidents = pd.read_csv(REVIEW45 / "phase0/roster/presidents.csv")
    roster = pd.concat([governors, presidents], ignore_index=True)
    roster["start"] = pd.to_datetime(roster["start"])
    roster["end"] = pd.to_datetime(roster["end"], errors="coerce")
    roster.loc[roster["end"].dt.year.eq(2099), "end"] = pd.NaT
    roster["kind"] = np.where(roster["institution"].eq("Board of Governors"), "governor", "president")
    return roster


def load_private(roster: pd.DataFrame) -> tuple[pd.DataFrame, str]:
    if not PRIVATE.exists():
        raise FileNotFoundError(f"Private input not found at {PRIVATE}")
    source_hash = hashlib.sha256(PRIVATE.read_bytes()).hexdigest()
    raw = pd.read_csv(PRIVATE)
    required = {"meeting", "name", "pred", "voting_member"}
    missing = required.difference(raw.columns)
    if missing:
        raise ValueError(f"Private input is missing required columns: {sorted(missing)}")

    raw["date"] = pd.to_datetime(raw["meeting"].str[4:12], format="%Y%m%d", errors="coerce")
    raw["meeting_type"] = raw["meeting"].str[12:].str.lower()
    raw["person_key_internal"] = raw["name"].map(key)
    raw["pred"] = pd.to_numeric(raw["pred"], errors="coerce")
    raw["voting_member"] = pd.to_numeric(raw["voting_member"], errors="coerce").fillna(0).astype(int)

    # Match the Review 45 roster by active tenure. Names remain internal.
    intervals: dict[str, list[tuple[pd.Timestamp, pd.Timestamp | pd.NaT, str, str, str]]] = {}
    for row in roster.itertuples(index=False):
        end = row.end if pd.notna(row.end) else pd.Timestamp("2099-12-31")
        intervals.setdefault(row.key, []).append((row.start, end, row.kind, row.institution, row.full_name))

    kinds, institutions, official_names = [], [], []
    for surname, date in zip(raw["person_key_internal"], raw["date"]):
        matches = [x for x in intervals.get(surname, []) if pd.notna(date) and x[0] <= date <= x[1]]
        if len(matches) == 1:
            kinds.append(matches[0][2]); institutions.append(matches[0][3]); official_names.append(matches[0][4])
        elif len(matches) > 1:
            # Tenure overlaps for a surname are ambiguous; do not guess.
            kinds.append(""); institutions.append(""); official_names.append("")
        else:
            kinds.append(""); institutions.append(""); official_names.append("")
    raw["roster_kind"] = kinds
    raw["roster_institution"] = institutions
    raw["official_roster_name_internal"] = official_names
    raw["participant"] = raw["roster_kind"].isin(["governor", "president"])
    raw["person_meeting_key"] = raw["person_key_internal"] + "|" + raw["meeting"]

    sample = raw[
        raw["meeting_type"].eq("meeting")
        & raw["participant"]
        & raw["date"].between(MAIN_START, MAIN_END)
        & raw["pred"].notna()
    ].copy()
    if sample.empty:
        raise ValueError("No eligible participant speaker-meeting rows in 1976–2018")
    if sample.duplicated(["person_key_internal", "meeting"]).any():
        raise ValueError("More than one score row exists for a participant-meeting pair")
    return sample, source_hash


def estimate_person_fe(sample: pd.DataFrame) -> tuple[pd.DataFrame, dict[str, float]]:
    # Numeric category IDs prevent names or source identifiers entering formulas.
    persons = sorted(sample["person_key_internal"].unique())
    meetings = sorted(sample["meeting"].unique())
    person_codes = {name: f"P{i:04d}" for i, name in enumerate(persons, start=1)}
    work = sample[["pred", "person_key_internal", "meeting"]].copy()
    work["person_code"] = work["person_key_internal"].map(person_codes)
    work["meeting_code"] = pd.Categorical(work["meeting"], categories=meetings)
    fit = smf.ols("pred ~ C(person_code) + C(meeting_code)", data=work).fit()

    effects = {code: 0.0 for code in person_codes.values()}
    for term, value in fit.params.items():
        match = re.fullmatch(r"C\(person_code\)\[T\.(P\d+)\]", term)
        if match:
            effects[match.group(1)] = float(value)
    counts = work["person_code"].value_counts().to_dict()
    weighted_mean = sum(effects[p] * counts[p] for p in effects) / sum(counts.values())
    effects = {p: value - weighted_mean for p, value in effects.items()}
    name_to_id = {name: person_codes[name] for name in persons}
    rows = pd.DataFrame(
        [{"person_id": person_codes[name], "person_fe": effects[person_codes[name]]} for name in persons]
    )
    fe_map = {name: effects[name_to_id[name]] for name in persons}
    return rows, fe_map


def build_board_roster() -> pd.DataFrame:
    source = pd.read_csv(REVIEW45 / "phase0/roster/governors.csv")
    source["start"] = pd.to_datetime(source["start"])
    source["end"] = pd.to_datetime(source["end"], errors="coerce")
    source.loc[source["end"].dt.year.eq(2099), "end"] = pd.NaT
    additions = [
        ("Waller", "Christopher J. Waller", "2020-12-18", ""),
        ("Cook", "Lisa D. Cook", "2022-05-23", ""),
        ("Jefferson", "Philip N. Jefferson", "2022-05-23", ""),
        ("Barr", "Michael S. Barr", "2022-07-19", ""),
        ("Kugler", "Adriana D. Kugler", "2023-09-13", "2025-08-08"),
        ("Miran", "Stephen I. Miran", "2025-09-16", ""),
    ]
    extra = pd.DataFrame(
        [{"key": k, "full_name": n, "role": "Governor", "institution": "Board of Governors",
          "start": pd.Timestamp(s), "end": pd.Timestamp(e) if e else pd.NaT, "source": FED_BOARD_URL}
         for k, n, s, e in additions]
    )
    source = pd.concat([source, extra], ignore_index=True)
    source = source[source["start"].le(VACANCY_END) & (source["end"].isna() | source["end"].ge(FIRST_STAGE_START))]
    source = source.sort_values(["start", "full_name"]).reset_index(drop=True)
    source["analysis_window"] = "1994-01-01/2025-12-31"
    source["source"] = source["source"].fillna(FED_BOARD_URL)
    source["source_as_of"] = ACCESS_DATE
    source["start"] = source["start"].dt.strftime("%Y-%m-%d")
    source["end"] = source["end"].dt.strftime("%Y-%m-%d")
    return source[["full_name", "start", "end", "analysis_window", "source", "source_as_of"]]


def macro_controls() -> pd.DataFrame:
    ext = REVIEW45 / "phase0/ext"
    gdp = pd.read_csv(ext / "GDPC1.csv", parse_dates=[0]).set_index("observation_date")["GDPC1"]
    g = 100 * ((gdp / gdp.shift(1)) ** 4 - 1)
    g.index = g.index.to_period("Q")
    nfci = pd.read_csv(ext / "NFCI.csv", parse_dates=[0]).set_index("observation_date")["NFCI"]
    nfci = nfci.groupby(nfci.index.to_period("Q")).mean()
    frame = pd.concat([g.rename("g"), nfci.rename("nfci")], axis=1)
    frame.index.name = "quarter"
    return frame


def chair_category(date: pd.Timestamp) -> str:
    if date < pd.Timestamp("2006-02-01"):
        return "Greenspan"
    if date < pd.Timestamp("2014-02-03"):
        return "Bernanke"
    if date < pd.Timestamp("2018-02-05"):
        return "Yellen"
    return "Powell"


def clustered_result(frame: pd.DataFrame, dependent: str, regressor: str,
                     include_controls: bool, sample_name: str, frequency: str) -> dict[str, object]:
    controls = ["g", "nfci", "chair_Bernanke", "chair_Yellen", "chair_Powell"] if include_controls else []
    frame = frame.dropna(subset=[dependent, regressor, "year"] + controls).copy()
    model = smf.ols(f"{dependent} ~ {regressor}" + (" + " + " + ".join(controls) if controls else ""), data=frame)
    groups = frame["year"].to_numpy()
    fit = model.fit(cov_type="cluster", cov_kwds={"groups": groups, "use_correction": True}, use_t=True)
    beta = float(fit.params[regressor])
    se = float(fit.bse[regressor])
    return {
        "sample": sample_name,
        "frequency": frequency,
        "regressor": regressor,
        "controls": "g;NFCI;Fed-chair dummies" if include_controls else "none",
        "n": int(fit.nobs),
        "n_clusters_year": int(pd.Series(groups).nunique()),
        "beta": beta,
        "se_cluster_year": se,
        "f_effective_single_instrument": beta * beta / (se * se),
        "p_cluster": float(fit.pvalues[regressor]),
    }


def construct_instruments(sample: pd.DataFrame, fe_map: dict[str, float], roster: pd.DataFrame) -> pd.DataFrame:
    members = sample.copy()
    members["person_fe"] = members["person_key_internal"].map(fe_map)
    voters = members[members["voting_member"].eq(1)].copy()
    if voters.empty:
        raise ValueError("No voter rows to build composition instruments")
    voters["year"] = voters["date"].dt.year
    annual_rows = []
    for year, group in voters.groupby("year"):
        if not FIRST_STAGE_START.year <= year <= FIRST_STAGE_END.year:
            continue
        unique_voters = group.drop_duplicates("person_key_internal")
        rotating = group[
            group["roster_kind"].eq("president")
            & ~group["roster_institution"].str.contains("New York", case=False, na=False)
        ]
        bank_support = rotating.groupby("roster_institution")["meeting"].nunique().sort_values(ascending=False)
        if len(bank_support) < 4 or (len(bank_support) >= 5 and bank_support.iloc[3] == bank_support.iloc[4]):
            raise ValueError(f"Cannot identify four rotating Reserve Banks in {year}")
        four_banks = bank_support.iloc[:4].index
        # Average people within each of the four rotating districts first. This
        # preserves four bank seats if a district changes president midyear.
        bank_effects = (
            rotating[rotating["roster_institution"].isin(four_banks)]
            .drop_duplicates(["roster_institution", "person_key_internal"])
            .groupby("roster_institution")["person_fe"].mean()
        )
        if bank_effects.size != 4:
            raise ValueError(f"Incomplete rotating-bank FE coverage in {year}")
        annual_rows.append({
            "year": int(year),
            "composition": float(unique_voters["person_fe"].mean()),
            "n_voters_year": int(len(unique_voters)),
            "rotation_composition": float(bank_effects.mean()),
            "n_rotating_voters": 4,
        })
    annual = pd.DataFrame(annual_rows)
    meetings = sample[["meeting", "date"]].drop_duplicates("meeting").copy()
    meetings["year"] = meetings["date"].dt.year
    meetings = meetings.merge(annual, on="year", how="left", validate="many_to_one")
    return meetings[meetings["date"].between(FIRST_STAGE_START, FIRST_STAGE_END)].copy()


def build_minutes_panel(instruments: pd.DataFrame, controls: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    minutes = pd.read_csv(REVIEW45 / "data_paper/hd_meetings_minutes_index.csv", parse_dates=["meeting_date"])
    minutes = minutes.rename(columns={"meeting_date": "date", "hd_minutes": "hd_minutes"})
    panel = instruments.merge(minutes, on="date", how="inner", validate="one_to_one")
    panel["quarter"] = panel["date"].dt.to_period("Q")
    panel["year"] = panel["date"].dt.year
    panel["chair"] = panel["date"].map(chair_category)
    for chair in ["Bernanke", "Yellen", "Powell"]:
        panel[f"chair_{chair}"] = panel["chair"].eq(chair).astype(int)
    panel = panel.merge(controls, left_on="quarter", right_index=True, how="left", validate="many_to_one")
    panel = panel[panel["date"].between(FIRST_STAGE_START, FIRST_STAGE_END)].copy()
    panel = panel.dropna(subset=["hd_minutes", "composition", "g", "nfci"])

    quarter = panel.groupby("quarter", as_index=False).agg(
        hd_minutes=("hd_minutes", "mean"),
        composition=("composition", "mean"),
        rotation_composition=("rotation_composition", "mean"),
        g=("g", "first"), nfci=("nfci", "first"),
        chair_Bernanke=("chair_Bernanke", "mean"),
        chair_Yellen=("chair_Yellen", "mean"),
        chair_Powell=("chair_Powell", "mean"),
        n_meetings=("meeting", "size"),
        n_rotation_meetings=("rotation_composition", "count"),
    )
    quarter["year"] = quarter["quarter"].map(lambda q: q.year)
    panel["quarter"] = panel["quarter"].map(quarter_label)
    quarter["quarter"] = quarter["quarter"].map(quarter_label)
    return panel, quarter


def vacancy_regressions(minutes: pd.DataFrame, board: pd.DataFrame, controls: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    raw = minutes.copy()
    raw["quarter"] = raw["date"].dt.to_period("Q")
    start = pd.to_datetime(board["start"])
    end = pd.to_datetime(board["end"], errors="coerce")
    raw["vacancies"] = [
        max(0, 7 - int(((start <= date) & (end.isna() | (end >= date))).sum())) for date in raw["date"]
    ]
    raw["chair"] = raw["date"].map(chair_category)
    for chair in ["Bernanke", "Yellen", "Powell"]:
        raw[f"chair_{chair}"] = raw["chair"].eq(chair).astype(int)
    raw = raw.merge(controls, left_on="quarter", right_index=True, how="left", validate="many_to_one")
    q = raw.groupby("quarter", as_index=False).agg(
        hd_minutes=("hd_minutes", "mean"), vacancies_mean=("vacancies", "mean"),
        g=("g", "first"), nfci=("nfci", "first"),
        chair_Bernanke=("chair_Bernanke", "mean"),
        chair_Yellen=("chair_Yellen", "mean"),
        chair_Powell=("chair_Powell", "mean"),
        n_meetings=("date", "size"),
    )
    q = q.dropna(subset=["hd_minutes", "vacancies_mean", "g", "nfci"]).copy()
    q["year"] = q["quarter"].map(lambda x: x.year)
    specs = [
        ("1994-2025", pd.Period("1994Q1", freq="Q"), pd.Period("2025Q4", freq="Q")),
        ("1994-2007", pd.Period("1994Q1", freq="Q"), pd.Period("2007Q4", freq="Q")),
        ("2008-2025", pd.Period("2008Q1", freq="Q"), pd.Period("2025Q4", freq="Q")),
    ]
    rows = []
    for label, lo, hi in specs:
        sub = q[q["quarter"].between(lo, hi)].copy()
        if sub.empty:
            continue
        sub = sub.rename(columns={"vacancies_mean": "vacancies"})
        rows.append(clustered_result(sub, "hd_minutes", "vacancies", True, label, "quarter"))
    q["quarter"] = q["quarter"].map(quarter_label)
    return q, pd.DataFrame(rows)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    roster = load_roster()
    sample, private_hash = load_private(roster)
    fe_rows, fe_map = estimate_person_fe(sample)
    # Deliberately omit names and source records from this aggregate output.
    fe_rows.to_csv(OUT / "person_fe.csv", index=False, float_format="%.12g")

    instruments = construct_instruments(sample, fe_map, roster)
    controls = macro_controls()
    meeting_panel, quarter_panel = build_minutes_panel(instruments, controls)
    fs_rows = []
    for frequency, frame in [("meeting", meeting_panel), ("quarterly", quarter_panel)]:
        for instrument in ["composition", "rotation_composition"]:
            for with_controls in [False, True]:
                fs_rows.append(clustered_result(
                    frame, "hd_minutes", instrument, with_controls,
                    "1994Q1-2018Q4", frequency
                ))
    fs = pd.DataFrame(fs_rows)
    for frequency, name in [("meeting", "first_stage_meeting.csv"), ("quarterly", "first_stage_quarterly.csv")]:
        fs[fs["frequency"].eq(frequency)].to_csv(OUT / name, index=False, float_format="%.12g")

    board = build_board_roster()
    board.to_csv(OUT / "board_roster.csv", index=False)
    minutes = pd.read_csv(REVIEW45 / "data_paper/hd_meetings_minutes_index.csv", parse_dates=["meeting_date"])
    minutes = minutes.rename(columns={"meeting_date": "date", "hd_minutes": "hd_minutes"})
    vacancy_panel, vacancy = vacancy_regressions(minutes, board, controls)
    vacancy_panel.to_csv(OUT / "vacancies_quarterly.csv", index=False, float_format="%.12g")

    summary = {
        "private_source_sha256": private_hash,
        "private_source_location": "~/Downloads/pred_score_for_voting_and_non_voting_members.csv (read in place; not copied)",
        "fe_speaker_meeting_rows": int(len(sample)),
        "fe_person_count": int(len(fe_rows)),
        "first_stage_meeting_n": int(len(meeting_panel)),
        "first_stage_quarter_n": int(len(quarter_panel)),
        "first_stage_results": fs.to_dict("records"),
        "vacancy_results": vacancy.to_dict("records"),
        "rotating_complete_meetings": int(meeting_panel["rotation_composition"].notna().sum()),
        "rotating_meeting_count": int(len(meeting_panel)),
        "rotating_complete_quarters": int(quarter_panel["rotation_composition"].notna().sum()),
        "quarter_count": int(len(quarter_panel)),
        "privacy": "No raw speaker row, score, or name written to outputs; person FE output uses pseudonymous IDs.",
        "board_source": FED_BOARD_URL,
        "board_source_as_of": ACCESS_DATE,
    }
    (OUT / "_review46_run_summary.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n")


if __name__ == "__main__":
    main()
