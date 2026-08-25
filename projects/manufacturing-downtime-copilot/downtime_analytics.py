"""Pure analytics logic for the Manufacturing Downtime Copilot."""

from __future__ import annotations

from difflib import get_close_matches
from pathlib import Path
import re

import pandas as pd


REQUIRED_COLUMNS = {
    "Batch",
    "Description",
    "Downtime_Minutes",
    "Product",
    "Operator",
    "Shift",
    "Operator_Error",
}


def _clean_column_name(value: str) -> str:
    return re.sub(r"[^A-Za-z0-9]+", "_", value.strip()).strip("_")


def load_data(path: str | Path) -> pd.DataFrame:
    """Load, standardize, and validate the public downtime dataset."""
    df = pd.read_csv(path, encoding="utf-8-sig")
    df.columns = [_clean_column_name(column) for column in df.columns]
    df = df.rename(columns={"Sum_of_Downtime_Minutes": "Downtime_Minutes"})

    missing = REQUIRED_COLUMNS - set(df.columns)
    if missing:
        raise ValueError(f"Missing required columns: {', '.join(sorted(missing))}")

    if "Date" not in df.columns and {"Year", "Month", "Day"}.issubset(df.columns):
        df["Date"] = pd.to_datetime(
            df["Year"].astype(str) + "-" + df["Month"].astype(str) + "-" + df["Day"].astype(str),
            format="%Y-%B-%d",
            errors="coerce",
        )
    elif "Date" in df.columns:
        df["Date"] = pd.to_datetime(df["Date"], errors="coerce")

    df["Batch"] = pd.to_numeric(df["Batch"], errors="coerce").astype("Int64")
    df["Downtime_Minutes"] = pd.to_numeric(df["Downtime_Minutes"], errors="coerce")
    text_columns = ["Description", "Product", "Operator", "Shift", "Operator_Error"]
    for column in text_columns:
        df[column] = df[column].astype("string").str.strip()

    df = df.dropna(subset=["Batch", "Downtime_Minutes", *text_columns])
    df = df[df["Downtime_Minutes"] > 0]
    df = df.drop_duplicates().sort_values(["Date", "Batch", "Description"], na_position="last")
    return df.reset_index(drop=True)


def filter_data(
    df: pd.DataFrame,
    *,
    products: list[str] | None = None,
    shifts: list[str] | None = None,
    operators: list[str] | None = None,
    start_date=None,
    end_date=None,
) -> pd.DataFrame:
    """Return rows matching the selected dashboard filters."""
    result = df.copy()
    if products:
        result = result[result["Product"].isin(products)]
    if shifts:
        result = result[result["Shift"].isin(shifts)]
    if operators:
        result = result[result["Operator"].isin(operators)]
    if start_date is not None and "Date" in result:
        result = result[result["Date"].dt.date >= start_date]
    if end_date is not None and "Date" in result:
        result = result[result["Date"].dt.date <= end_date]
    return result


def breakdown(df: pd.DataFrame, column: str) -> pd.DataFrame:
    """Aggregate downtime minutes and event counts by one category."""
    if column not in df.columns:
        raise KeyError(f"Unknown breakdown column: {column}")
    return (
        df.groupby(column, dropna=False)
        .agg(Downtime_Minutes=("Downtime_Minutes", "sum"), Events=("Batch", "size"))
        .reset_index()
        .sort_values(["Downtime_Minutes", column], ascending=[False, True])
        .reset_index(drop=True)
    )


def kpis(df: pd.DataFrame) -> dict[str, int | float | str]:
    """Compute the executive KPIs used by both the app and tests."""
    if df.empty:
        return {
            "total_minutes": 0,
            "events": 0,
            "affected_batches": 0,
            "top_reason": "No data",
            "top_reason_minutes": 0,
            "operator_error_share": 0.0,
        }
    reason = breakdown(df, "Description").iloc[0]
    operator_error_minutes = df.loc[
        df["Operator_Error"].str.casefold().eq("yes"), "Downtime_Minutes"
    ].sum()
    total = float(df["Downtime_Minutes"].sum())
    return {
        "total_minutes": int(total),
        "events": int(len(df)),
        "affected_batches": int(df["Batch"].nunique()),
        "top_reason": str(reason["Description"]),
        "top_reason_minutes": int(reason["Downtime_Minutes"]),
        "operator_error_share": float(operator_error_minutes / total) if total else 0.0,
    }


def _match_value(question: str, values: list[str], cutoff: float = 0.84) -> str | None:
    normalized_question = question.casefold()
    for value in values:
        if value.casefold() in normalized_question:
            return value
    tokens = re.findall(r"[a-z0-9-]+", normalized_question)
    candidates = set(tokens)
    candidates.update(" ".join(tokens[index:index + 2]) for index in range(len(tokens) - 1))
    normalized_values = {value.casefold(): value for value in values}
    for candidate in candidates:
        match = get_close_matches(candidate, normalized_values, n=1, cutoff=cutoff)
        if match:
            return normalized_values[match[0]]
    return None


def answer_question(df: pd.DataFrame, question: str) -> str:
    """Answer common, auditable questions using deterministic aggregations."""
    q = question.casefold().strip()
    if not q:
        return "Ask a question about a downtime reason, product, shift, or operator-error share."

    filtered = df.copy()
    for column, cutoff in (("Product", 0.82), ("Shift", 0.82), ("Operator", 0.9)):
        values = sorted(filtered[column].dropna().astype(str).unique())
        match = _match_value(q, values, cutoff=cutoff)
        if match:
            filtered = filtered[filtered[column].eq(match)]

    if filtered.empty:
        return "No rows match those filters. Try a product code, Shift A/B/C, or a broader question."

    stats = kpis(filtered)
    if "operator error" in q or "human error" in q:
        minutes = int(filtered.loc[filtered["Operator_Error"].str.casefold().eq("yes"), "Downtime_Minutes"].sum())
        share = minutes / stats["total_minutes"] if stats["total_minutes"] else 0
        return f"Operator-attributed events account for {minutes:,} minutes ({share:.1%}) in the selected data."
    if any(word in q for word in ("summary", "summarize", "overview", "explain")):
        return (
            f"The selected data contains {stats['total_minutes']:,} downtime minutes across "
            f"{stats['events']} events and {stats['affected_batches']} batches. "
            f"The leading reason is {stats['top_reason']} ({stats['top_reason_minutes']:,} minutes); "
            f"operator-attributed events represent {stats['operator_error_share']:.1%} of downtime."
        )
    if any(word in q for word in ("reason", "cause", "driver", "issue")):
        top = breakdown(filtered, "Description").iloc[0]
        return f"The leading downtime reason is {top['Description']} at {int(top['Downtime_Minutes']):,} minutes across {int(top['Events'])} events."
    if "product" in q:
        top = breakdown(filtered, "Product").iloc[0]
        return f"{top['Product']} has the most downtime at {int(top['Downtime_Minutes']):,} minutes."
    if "shift" in q or "shfit" in q:
        top = breakdown(filtered, "Shift").iloc[0]
        return f"{top['Shift']} has the most downtime at {int(top['Downtime_Minutes']):,} minutes."
    if "operator" in q:
        top = breakdown(filtered, "Operator").iloc[0]
        return f"{top['Operator']} has the most associated downtime at {int(top['Downtime_Minutes']):,} minutes. This is an association, not a causal conclusion."
    return "Try: ‘What is the top downtime reason?’, ‘Summarize Shift B’, or ‘What is the operator error share?’"
