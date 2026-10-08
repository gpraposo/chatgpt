-- Projeto educativo: dados fictícios; não representam a SBM Offshore.
-- O modelo guarda euros como cêntimos inteiros para evitar erros monetários.
-- Granularidade de fact_operations: uma unidade e um mês completo.
-- Cada dimensão tem uma chave única; estes joins não multiplicam o orçamento.

-- 1. Visão global: somar antes de calcular percentagens.
-- A disponibilidade inclui AMBAS as paragens e é ponderada pelas horas.
SELECT
    SUM(budget_cents) / 100.0 AS budget_eur,
    SUM(actual_cents) / 100.0 AS actual_eur,
    SUM(actual_cents - budget_cents) / 100.0 AS variance_eur,
    100.0 * SUM(actual_cents - budget_cents)
        / NULLIF(SUM(budget_cents), 0) AS variance_pct,
    100.0 * SUM(period_hours - planned_downtime_hours - unplanned_downtime_hours)
        / NULLIF(SUM(period_hours), 0) AS availability_pct
FROM fact_operations;

-- 2. Por unidade: onde investigar despesas acima do orçamento e paragens?
SELECT
    a.asset_id,
    a.asset_name,
    SUM(f.budget_cents) / 100.0 AS budget_eur,
    SUM(f.actual_cents) / 100.0 AS actual_eur,
    SUM(f.actual_cents - f.budget_cents) / 100.0 AS variance_eur,
    100.0 * SUM(f.actual_cents - f.budget_cents)
        / NULLIF(SUM(f.budget_cents), 0) AS variance_pct,
    SUM(f.planned_downtime_hours) AS planned_downtime_hours,
    SUM(f.unplanned_downtime_hours) AS unplanned_downtime_hours,
    100.0 * SUM(f.period_hours - f.planned_downtime_hours - f.unplanned_downtime_hours)
        / NULLIF(SUM(f.period_hours), 0) AS availability_pct
FROM fact_operations AS f
JOIN dim_asset AS a ON a.asset_id = f.asset_id
GROUP BY a.asset_id, a.asset_name
ORDER BY variance_eur DESC;

-- 3. Por mês: acompanhar a evolução conjunta das unidades.
SELECT
    m.month,
    SUM(f.budget_cents) / 100.0 AS budget_eur,
    SUM(f.actual_cents) / 100.0 AS actual_eur,
    SUM(f.actual_cents - f.budget_cents) / 100.0 AS variance_eur,
    SUM(f.unplanned_downtime_hours) AS unplanned_downtime_hours,
    100.0 * SUM(f.period_hours - f.planned_downtime_hours - f.unplanned_downtime_hours)
        / NULLIF(SUM(f.period_hours), 0) AS availability_pct
FROM fact_operations AS f
JOIN dim_month AS m ON m.month = f.month
GROUP BY m.month
ORDER BY m.month;

-- 4. Exceções para revisão: associação entre custos e paragens não prova causa.
-- O limiar de 5% serve apenas para demonstrar um filtro; exige validação de negócio.
SELECT
    a.asset_name,
    f.month,
    (f.actual_cents - f.budget_cents) / 100.0 AS variance_eur,
    100.0 * (f.actual_cents - f.budget_cents)
        / NULLIF(f.budget_cents, 0) AS variance_pct,
    f.unplanned_downtime_hours
FROM fact_operations AS f
JOIN dim_asset AS a ON a.asset_id = f.asset_id
WHERE f.budget_cents > 0 AND f.actual_cents > f.budget_cents * 1.05
ORDER BY variance_eur DESC;
