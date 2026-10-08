"""Painel de aprendizagem: custos e disponibilidade de ativos fictícios."""

import json
from pathlib import Path

import pandas as pd
import streamlit as st

from offshore_demo.analytics import summarize

ROOT = Path(__file__).resolve().parent
CSV_PATH = ROOT / "data" / "processed" / "operations.csv"
REPORT_PATH = ROOT / "data" / "processed" / "quality_report.json"


def euros(value: float) -> str:
    return f"{value:,.0f}".replace(",", " ") + " €"


def percent(value: float | None) -> str:
    return "Sem base de cálculo" if value is None else f"{value:.1f}".replace(".", ",") + "%"


st.set_page_config(page_title="Operações offshore | Portefólio", page_icon="🌊", layout="wide")
st.title("Custos e disponibilidade offshore")

if not CSV_PATH.exists():
    st.warning("Ainda faltam os dados preparados. Na pasta do projeto, executa o comando indicado abaixo e volta a abrir o painel.")
    st.code("python -m offshore_demo.pipeline", language="bash")
    st.stop()

# A leitura é feita a cada execução para refletir uma nova preparação dos dados.
data = pd.read_csv(CSV_PATH, dtype={"asset_id": str, "month": str})
report = json.loads(REPORT_PATH.read_text(encoding="utf-8")) if REPORT_PATH.exists() else {}
is_demo = report.get("source") == "synthetic_demo"
st.caption("Projeto de portefólio · " + ("Dados simulados" if is_demo else "CSV local"))
if is_demo:
    st.info("Os ativos e os valores são fictícios. Este projeto não representa operações nem dados da SBM Offshore.")
else:
    st.info("Dados de um CSV local. Confirma a origem e as definições dos indicadores antes de interpretar os resultados.")
if not data.empty:
    st.caption(f"Período dos dados: {data['month'].min()} a {data['month'].max()}")
with st.sidebar:
    st.header("Escolher dados")
    chosen_assets = st.multiselect("Unidades", sorted(data["asset_name"].unique()), default=sorted(data["asset_name"].unique()))
    chosen_months = st.multiselect("Meses", sorted(data["month"].unique()), default=sorted(data["month"].unique()))
    st.caption("Os indicadores e os gráficos usam apenas os dados selecionados.")

filtered = data[data["asset_name"].isin(chosen_assets) & data["month"].isin(chosen_months)]
if filtered.empty:
    st.warning("Seleciona pelo menos uma unidade e um mês com dados.")
    st.stop()

totals = summarize(filtered)
columns = st.columns(4)
columns[0].metric("Orçamento", euros(totals["budget_eur"]))
columns[1].metric("Despesa real", euros(totals["actual_eur"]))
columns[2].metric("Desvio ao orçamento", euros(totals["variance_eur"]), delta=percent(totals["variance_pct"]), delta_color="inverse")
columns[3].metric("Disponibilidade", percent(totals["availability_pct"]))
st.caption("Desvio positivo = despesa acima do orçamento. Disponibilidade = horas sem paragem / horas do período; inclui paragens planeadas e não planeadas.")

left, right = st.columns(2)
monthly = filtered.groupby("month")[["budget_eur", "actual_eur"]].sum()
with left:
    st.subheader("Despesas e orçamento por mês")
    st.line_chart(monthly.rename(columns={"budget_eur": "Orçamento (€)", "actual_eur": "Despesa real (€)"}))

asset_totals = filtered.groupby("asset_name")[["budget_eur", "actual_eur", "period_hours", "planned_downtime_hours", "unplanned_downtime_hours"]].sum()
asset_totals["Desvio (€)"] = asset_totals["actual_eur"] - asset_totals["budget_eur"]
asset_totals["Disponibilidade (%)"] = 100 * (1 - (asset_totals["planned_downtime_hours"] + asset_totals["unplanned_downtime_hours"]) / asset_totals["period_hours"])
with right:
    st.subheader("Desvio ao orçamento por unidade")
    st.bar_chart(asset_totals[["Desvio (€)"]])

st.subheader("Onde investigar primeiro")
largest = asset_totals["Desvio (€)"].idxmax()
lowest = asset_totals["Disponibilidade (%)"].idxmin()
if asset_totals.loc[largest, "Desvio (€)"] > 0:
    st.write(f"**{largest}** tem o maior desvio acima do orçamento: **{euros(asset_totals.loc[largest, 'Desvio (€)'])}**. Investiga as despesas e compara-as com o plano de manutenção.")
else:
    st.write("Nenhuma unidade ultrapassa o orçamento na seleção atual.")
st.write(f"**{lowest}** apresenta a menor disponibilidade: **{percent(asset_totals.loc[lowest, 'Disponibilidade (%)'])}**. Consulta as horas de paragem planeada e não planeada antes de propor ações.")
st.caption("Estes dados mensais ajudam a escolher o que investigar; não permitem atribuir uma causa às paragens nem calcular perdas de produção.")

st.dataframe(asset_totals.rename(columns={"budget_eur": "Orçamento (€)", "actual_eur": "Despesa real (€)", "period_hours": "Horas do período", "planned_downtime_hours": "Paragens planeadas (h)", "unplanned_downtime_hours": "Paragens não planeadas (h)"}), width="stretch")

with st.expander("Qualidade dos dados — antes dos filtros"):
    if REPORT_PATH.exists():
        st.write(f"Linhas de entrada: **{report['input_rows']}** · Linhas aceites: **{report['accepted_rows']}** · Linhas rejeitadas: **{report['rejected_rows']}** · Duplicados removidos: **{report['duplicate_rows_removed']}**")
        if is_demo:
            st.caption("Os erros foram introduzidos de propósito nos dados de demonstração, para praticar validação.")
        st.caption("O relatório cobre toda a origem, independentemente dos filtros.")
        st.json(report.get("issue_counts", {}))
    else:
        st.warning("O relatório de qualidade não está disponível. Volta a executar a preparação dos dados.")

with st.expander("Ver os dados selecionados"):
    st.dataframe(filtered, hide_index=True, width="stretch")

st.download_button("Descarregar a seleção em CSV", filtered.to_csv(index=False).encode("utf-8-sig"), file_name="operations_selection.csv", mime="text/csv")
st.caption("Para Power BI e SQL, usa os ficheiros completos em data/processed. As instruções estão no guia Windows.")
