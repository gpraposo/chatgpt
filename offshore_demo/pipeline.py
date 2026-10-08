"""Recolher, validar e preparar dados para o painel e para consultas SQL.

Executar, a partir da pasta do projeto: ``python -m offshore_demo.pipeline``.
Todos os montantes representam euros e são tratados com Decimal antes de
serem guardados como cêntimos inteiros no SQLite. A disponibilidade inclui
paragens planeadas e não planeadas: horas disponíveis / horas do período.
É um indicador educativo; não é a definição contratual da SBM Offshore.

O ficheiro de entrada existente nunca é substituído. As exportações na pasta
processed são resultados reproduzíveis e podem ser novamente geradas.
"""

from __future__ import annotations

import argparse
import calendar
import csv
import hashlib
import json
import random
import re
import sqlite3
from collections import Counter, defaultdict
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from pathlib import Path
from typing import Any


RAW_COLUMNS = (
    "asset_id", "asset_name", "month", "budget_eur", "actual_eur",
    "period_hours", "planned_downtime_hours", "unplanned_downtime_hours",
)
PROCESSED_COLUMNS = RAW_COLUMNS + (
    "variance_eur", "variance_pct", "availability_pct",
)
ISSUE_COLUMNS = ("row_number", "asset_id", "month", "status", "code", "field", "message")
CENT = Decimal("0.01")
HUNDRED = Decimal(100)


@dataclass(frozen=True)
class Operation:
    """Uma linha válida: uma unidade num único mês de calendário."""

    asset_id: str
    asset_name: str
    month: str
    budget_eur: Decimal
    actual_eur: Decimal
    period_hours: Decimal
    planned_downtime_hours: Decimal
    unplanned_downtime_hours: Decimal

    @property
    def variance_eur(self) -> Decimal:
        return self.actual_eur - self.budget_eur

    @property
    def variance_pct(self) -> Decimal | None:
        if self.budget_eur == 0:
            return None  # Um orçamento zero não permite calcular uma percentagem.
        return self.variance_eur / self.budget_eur * HUNDRED

    @property
    def availability_pct(self) -> Decimal:
        downtime = self.planned_downtime_hours + self.unplanned_downtime_hours
        return (self.period_hours - downtime) / self.period_hours * HUNDRED

    def csv_record(self) -> dict[str, str]:
        record = {
            column: str(getattr(self, column)) for column in RAW_COLUMNS
        }
        for column in ("budget_eur", "actual_eur", "variance_eur"):
            record[column] = format(getattr(self, column), ".2f")
        for column in ("variance_pct", "availability_pct"):
            value = getattr(self, column)
            record[column] = "" if value is None else format(value, ".4f")
        return record


def _digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _write_csv(path: Path, columns: tuple[str, ...], rows: list[dict[str, Any]]) -> None:
    temporary = path.with_suffix(path.suffix + ".tmp")
    with temporary.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns)
        writer.writeheader()
        writer.writerows(rows)
    temporary.replace(path)


def _write_json(path: Path, value: dict[str, Any]) -> None:
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(
        json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    temporary.replace(path)


def generate_demo_csv(path: Path) -> None:
    """Criar 18 observações fictícias e três erros de qualidade intencionais.

    A mesma seed produz os mesmos dados. O modo 'x' protege um ficheiro
    existente, mesmo que seja criado entre a verificação e esta escrita.
    """
    generator = random.Random(42)
    assets = (
        ("FPSO-A", "Unidade Aurora", 980_000),
        ("FPSO-B", "Unidade Boreal", 1_050_000),
        ("FPSO-C", "Unidade Coral", 880_000),
    )
    rows: list[dict[str, Any]] = []
    for asset_id, name, budget in assets:
        for month in range(1, 7):
            planned = generator.randint(8, 24)
            unplanned = generator.randint(3, 15)
            cost = budget + generator.randint(-25_000, 35_000)
            # Tendência construída para praticar investigação; não prova causalidade.
            if asset_id == "FPSO-C" and month >= 4:
                unplanned += (month - 3) * 24
                cost += (month - 3) * 65_000
            rows.append({
                "asset_id": asset_id,
                "asset_name": name,
                "month": f"2025-{month:02d}",
                "budget_eur": f"{budget:.2f}",
                "actual_eur": f"{cost:.2f}",
                "period_hours": calendar.monthrange(2025, month)[1] * 24,
                "planned_downtime_hours": planned,
                "unplanned_downtime_hours": unplanned,
            })
    rows.append(dict(rows[0]))  # Repetição exata: eliminar e registar.
    rows.append({**rows[1], "actual_eur": ""})  # Falta uma despesa.
    rows.append({**rows[2], "actual_eur": "-120.00"})  # Despesa inválida.
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=RAW_COLUMNS)
        writer.writeheader()
        writer.writerows(rows)
    _write_json(path.with_suffix(".source.json"), {
        "kind": "synthetic_demo",
        "description": "Dados fictícios para aprendizagem; sem dados da SBM Offshore.",
        "seed": 42,
        "sha256": _digest(path),
    })


def _source_details(path: Path) -> dict[str, Any]:
    metadata_file = path.with_suffix(".source.json")
    if metadata_file.exists():
        try:
            metadata = json.loads(metadata_file.read_text(encoding="utf-8"))
            if metadata.get("kind") == "synthetic_demo" and metadata.get("sha256") == _digest(path):
                return {
                    "source": "synthetic_demo",
                    "dataset_description": metadata["description"],
                    "seed": metadata["seed"],
                }
        except (OSError, ValueError, KeyError, AttributeError):
            pass
    return {
        "source": "local_csv",
        "dataset_description": "CSV local fornecido ou alterado pelo utilizador; confirmar a origem.",
    }


def validate_rows(rows: list[dict[str, Any]]) -> tuple[list[Operation], list[dict[str, Any]], int]:
    """Validar sem preencher valores ausentes nem escolher entre conflitos.

    As linhas inválidas são rejeitadas antes de comparar observações válidas.
    Duplicados exatos são removidos. Para valores válidos em conflito na mesma
    unidade/mês, todas as linhas desse grupo são rejeitadas para revisão.
    Retorna observações aceites, problemas encontrados e duplicados removidos.
    """
    issues: list[dict[str, Any]] = []
    candidates: list[tuple[int, Operation, tuple[str, ...]]] = []

    def issue(number: int, row: dict[str, Any], code: str, field: str, message: str,
              status: str = "rejected") -> None:
        issues.append({
            "row_number": number,
            "asset_id": row.get("asset_id") or "",
            "month": row.get("month") or "",
            "status": status,
            "code": code,
            "field": field,
            "message": message,
        })

    for number, row in enumerate(rows, start=2):
        before = len(issues)
        text_fields: dict[str, str] = {}
        for column in ("asset_id", "asset_name", "month"):
            value = str(row.get(column) or "").strip()
            text_fields[column] = value
            if not value:
                issue(number, row, "missing_value", column, "Valor obrigatório em falta.")
            elif any(ord(character) < 32 for character in value):
                issue(number, row, "invalid_text", column, "O texto contém caracteres de controlo.")
        month_hours: int | None = None
        month_text = text_fields["month"]
        if month_text:
            if not re.fullmatch(r"[0-9]{4}-[0-9]{2}", month_text):
                issue(number, row, "invalid_month", "month", "Usar o formato AAAA-MM.")
            else:
                year, month = map(int, month_text.split("-"))
                if year < 1 or not 1 <= month <= 12:
                    issue(number, row, "invalid_month", "month", "Mês de calendário inválido.")
                else:
                    month_hours = calendar.monthrange(year, month)[1] * 24

        numbers: dict[str, Decimal] = {}
        for column in RAW_COLUMNS[3:]:
            raw_value = str(row.get(column) or "").strip()
            if not raw_value:
                issue(number, row, "missing_value", column, "Valor obrigatório em falta.")
                continue
            try:
                value = Decimal(raw_value)
            except InvalidOperation:
                issue(number, row, "invalid_number", column, "Número inválido; usar ponto decimal.")
                continue
            if not value.is_finite():
                issue(number, row, "invalid_number", column, "O número deve ser finito.")
                continue
            if value < 0:
                issue(number, row, "negative_value", column, "Não são permitidos valores negativos.")
                continue
            if column in ("budget_eur", "actual_eur"):
                try:
                    cents = value.quantize(CENT)
                except InvalidOperation:
                    issue(number, row, "invalid_number", column, "Montante demasiado grande.")
                    continue
                if cents != value:
                    issue(number, row, "currency_precision", column, "Usar no máximo duas casas decimais.")
                    continue
                # O SQLite usa inteiros de 64 bits para os montantes em cêntimos.
                if value > Decimal(2**63 - 1) / 100:
                    issue(number, row, "invalid_number", column, "Montante excede a capacidade do modelo.")
                    continue
                value = cents
            numbers[column] = value
        period = numbers.get("period_hours")
        if period is not None and month_hours is not None and period != month_hours:
            issue(number, row, "calendar_hours_mismatch", "period_hours",
                  f"O mês indicado tem {month_hours} horas; cada registo cobre o mês completo.")
        planned = numbers.get("planned_downtime_hours")
        unplanned = numbers.get("unplanned_downtime_hours")
        if period is not None and planned is not None and unplanned is not None:
            if planned + unplanned > period:
                issue(number, row, "downtime_exceeds_period", "downtime_hours",
                      "A soma das paragens ultrapassa as horas do período.")
        if len(issues) == before:
            operation = Operation(**text_fields, **numbers)
            # Apenas repetições exatas dos oito campos de origem são eliminadas.
            signature = tuple(str(row.get(column) or "") for column in RAW_COLUMNS)
            candidates.append((number, operation, signature))

    seen: set[tuple[str, ...]] = set()
    unique: list[tuple[int, Operation]] = []
    duplicates = 0
    for number, operation, signature in candidates:
        if signature in seen:
            duplicates += 1
            issue(number, operation.csv_record(), "duplicate_exact", "asset_id,month",
                  "Repetição exata eliminada; a primeira ocorrência segue para validação de conflitos.",
                  status="removed")
        else:
            seen.add(signature)
            unique.append((number, operation))

    names_by_id: dict[str, set[str]] = defaultdict(set)
    ids_by_name: dict[str, set[str]] = defaultdict(set)
    by_grain: dict[tuple[str, str], list[int]] = defaultdict(list)
    for number, operation in unique:
        names_by_id[operation.asset_id].add(operation.asset_name)
        ids_by_name[operation.asset_name].add(operation.asset_id)
        by_grain[(operation.asset_id, operation.month)].append(number)
    accepted: list[Operation] = []
    for number, operation in unique:
        before = len(issues)
        record = operation.csv_record()
        if len(names_by_id[operation.asset_id]) > 1 or len(ids_by_name[operation.asset_name]) > 1:
            issue(number, record, "inconsistent_asset", "asset_id,asset_name",
                  "O identificador e o nome devem representar sempre a mesma unidade.")
        if len(by_grain[(operation.asset_id, operation.month)]) > 1:
            issue(number, record, "conflicting_duplicate", "asset_id,month",
                  "Existem observações diferentes para a mesma unidade/mês; todas foram rejeitadas.")
        if len(issues) == before:
            accepted.append(operation)
    accepted.sort(key=lambda operation: (operation.asset_id, operation.month))
    issues.sort(key=lambda record: (record["row_number"], record["code"], record["field"]))
    return accepted, issues, duplicates


def summarize(operations: list[Operation]) -> dict[str, float | None]:
    """Somar antes de dividir: disponibilidade ponderada pelas horas do período."""
    budget = sum((operation.budget_eur for operation in operations), Decimal(0))
    actual = sum((operation.actual_eur for operation in operations), Decimal(0))
    period = sum((operation.period_hours for operation in operations), Decimal(0))
    downtime = sum((operation.planned_downtime_hours + operation.unplanned_downtime_hours
                    for operation in operations), Decimal(0))

    def number(value: Decimal, places: str = "0.01") -> float:
        return float(value.quantize(Decimal(places), rounding=ROUND_HALF_UP))

    return {
        "budget_eur": number(budget),
        "actual_eur": number(actual),
        "variance_eur": number(actual - budget),
        "variance_pct": number((actual - budget) / budget * HUNDRED, "0.0001") if budget else None,
        "availability_pct": number((period - downtime) / period * HUNDRED, "0.0001") if period else None,
        "total_period_hours": number(period),
        "total_downtime_hours": number(downtime),
    }


def _write_database(path: Path, operations: list[Operation]) -> None:
    temporary = path.with_suffix(path.suffix + ".tmp")
    if temporary.exists():
        temporary.unlink()
    with sqlite3.connect(temporary) as connection:
        connection.execute("PRAGMA foreign_keys = ON")
        connection.executescript("""
            CREATE TABLE dim_asset (
                asset_id TEXT PRIMARY KEY,
                asset_name TEXT NOT NULL UNIQUE
            );
            CREATE TABLE dim_month (
                month TEXT PRIMARY KEY,
                year INTEGER NOT NULL,
                month_number INTEGER NOT NULL CHECK(month_number BETWEEN 1 AND 12),
                calendar_hours INTEGER NOT NULL CHECK(calendar_hours > 0)
            );
            CREATE TABLE fact_operations (
                asset_id TEXT NOT NULL REFERENCES dim_asset(asset_id),
                month TEXT NOT NULL REFERENCES dim_month(month),
                budget_cents INTEGER NOT NULL CHECK(budget_cents >= 0),
                actual_cents INTEGER NOT NULL CHECK(actual_cents >= 0),
                period_hours REAL NOT NULL CHECK(period_hours > 0),
                planned_downtime_hours REAL NOT NULL CHECK(planned_downtime_hours >= 0),
                unplanned_downtime_hours REAL NOT NULL CHECK(unplanned_downtime_hours >= 0),
                PRIMARY KEY(asset_id, month),
                CHECK(planned_downtime_hours + unplanned_downtime_hours <= period_hours)
            );
        """)
        assets = sorted({(operation.asset_id, operation.asset_name) for operation in operations})
        months = sorted({operation.month for operation in operations})
        connection.executemany("INSERT INTO dim_asset VALUES (?, ?)", assets)
        connection.executemany("INSERT INTO dim_month VALUES (?, ?, ?, ?)", [
            (month, int(month[:4]), int(month[5:]),
             calendar.monthrange(int(month[:4]), int(month[5:]))[1] * 24)
            for month in months
        ])
        connection.executemany("INSERT INTO fact_operations VALUES (?, ?, ?, ?, ?, ?, ?)", [
            (operation.asset_id, operation.month,
             int(operation.budget_eur * 100), int(operation.actual_eur * 100),
             float(operation.period_hours), float(operation.planned_downtime_hours),
             float(operation.unplanned_downtime_hours))
            for operation in operations
        ])
    temporary.replace(path)


def run_pipeline(project_root: Path | None = None) -> dict[str, Any]:
    """Gerar a demonstração se necessário e publicar apenas dados validados.

    Paths no relatório são relativos à raiz do projeto. Um cabeçalho incompleto
    causa uma falha explícita antes de substituir os resultados anteriores.
    """
    root = Path(project_root) if project_root is not None else Path(__file__).resolve().parent.parent
    raw_path = root / "data" / "raw" / "operations.csv"
    processed_dir = root / "data" / "processed"
    if not raw_path.exists():
        generate_demo_csv(raw_path)
    with raw_path.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        missing = set(RAW_COLUMNS) - set(reader.fieldnames or [])
        if missing:
            raise ValueError("Faltam colunas obrigatórias no CSV: " + ", ".join(sorted(missing)))
        rows = list(reader)
    accepted, issues, duplicate_count = validate_rows(rows)
    rejected = {record["row_number"] for record in issues if record["status"] == "rejected"}
    report: dict[str, Any] = {
        "schema_version": 1,
        **_source_details(raw_path),
        "raw_file": "data/raw/operations.csv",
        "processed_file": "data/processed/operations.csv",
        "database_file": "data/processed/offshore.sqlite",
        "issues_file": "data/processed/quality_issues.csv",
        "input_rows": len(rows),
        "accepted_rows": len(accepted),
        "rejected_rows": len(rejected),
        "duplicate_rows_removed": duplicate_count,
        "issues_count": len(issues),
        "issue_counts": dict(sorted(Counter(record["code"] for record in issues).items())),
        "metrics": summarize(accepted),
        "definitions": {
            "grain": "Uma observação por unidade e mês completo de calendário.",
            "variance_eur": "Despesa real menos orçamento; positivo significa acima do orçamento.",
            "variance_pct": "100 × (despesa real − orçamento) / orçamento; null quando o orçamento é zero.",
            "availability_pct": "100 × (Σ horas do período − Σ paragens planeadas − Σ paragens não planeadas) / Σ horas do período.",
            "calendar_assumption": "Dias de calendário × 24; sem ajustes por fuso horário ou mudança da hora.",
            "null_percentages": "Percentagens sem denominador são null no JSON e vazias no CSV.",
            "quality_policy": "Não preencher ausências; eliminar duplicados exatos; rejeitar valores inválidos e todas as observações válidas em conflito.",
        },
    }
    processed_dir.mkdir(parents=True, exist_ok=True)
    _write_csv(processed_dir / "operations.csv", PROCESSED_COLUMNS,
               [operation.csv_record() for operation in accepted])
    _write_csv(processed_dir / "quality_issues.csv", ISSUE_COLUMNS, issues)
    _write_database(processed_dir / "offshore.sqlite", accepted)
    _write_json(processed_dir / "quality_report.json", report)
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description="Preparar dados fictícios ou validar um CSV local.")
    parser.add_argument("--project-root", type=Path, default=None, help="Pasta raiz do projeto.")
    arguments = parser.parse_args()
    report = run_pipeline(arguments.project_root)
    print(f"Origem: {report['dataset_description']}")
    print(f"Linhas recebidas: {report['input_rows']} | aceites: {report['accepted_rows']} | "
          f"rejeitadas: {report['rejected_rows']} | duplicados removidos: {report['duplicate_rows_removed']}")
    print("Relatório: data/processed/quality_report.json")
    print(f"Detalhes dos problemas: {report['issues_file']}")
    if report["accepted_rows"] == 0:
        parser.exit(1, "Não existem observações válidas. Rever o relatório de qualidade.\n")


if __name__ == "__main__":
    main()
