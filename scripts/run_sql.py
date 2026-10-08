"""Executar as consultas de exemplo sem instalar um cliente SQL separado."""

from pathlib import Path
from contextlib import closing
import sqlite3

ROOT = Path(__file__).resolve().parents[1]
DATABASE = ROOT / "data" / "processed" / "offshore.sqlite"
QUERY_FILE = ROOT / "sql" / "analysis.sql"


def main() -> None:
    if not DATABASE.exists():
        raise SystemExit("Prepara primeiro os dados com: python -m offshore_demo.pipeline")
    # Abrimos em modo de leitura; as consultas de aprendizagem não alteram dados.
    with closing(sqlite3.connect(DATABASE.as_uri() + "?mode=ro", uri=True)) as connection:
        statement = ""
        query_number = 0
        for line in QUERY_FILE.read_text(encoding="utf-8").splitlines(keepends=True):
            statement += line
            if sqlite3.complete_statement(statement):
                query_number += 1
                cursor = connection.execute(statement)
                print(f"\nConsulta {query_number}")
                print(" | ".join(column[0] for column in cursor.description))
                for row in cursor.fetchall():
                    print(" | ".join("—" if value is None else str(value) for value in row))
                statement = ""
        if statement.strip():
            raise SystemExit("A última consulta está incompleta; termina-a com ponto e vírgula.")


if __name__ == "__main__":
    main()
