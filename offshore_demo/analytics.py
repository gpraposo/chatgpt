"""Definições comuns dos indicadores mostrados no painel."""

import pandas as pd


def summarize(data: pd.DataFrame) -> dict:
    """Agrega custos e horas; não calcula médias de percentagens mensais."""
    budget = float(data["budget_eur"].sum())
    actual = float(data["actual_eur"].sum())
    hours = float(data["period_hours"].sum())
    downtime = float(data["planned_downtime_hours"].sum() + data["unplanned_downtime_hours"].sum())
    return {
        "budget_eur": budget,
        "actual_eur": actual,
        "variance_eur": actual - budget,
        "variance_pct": 100 * (actual - budget) / budget if budget else None,
        "availability_pct": 100 * (1 - downtime / hours) if hours else None,
    }
