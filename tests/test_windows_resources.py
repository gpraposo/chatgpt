"""Regressão de publicação do SQLite com ficheiros bloqueados no Windows.

O teste usa conexões SQLite reais e mantém referências fortes para que o
fecho não dependa da recolha de lixo nem das permissões de rename do Linux.
"""

from contextlib import closing
from pathlib import Path
import sqlite3
import tempfile
import unittest
from unittest.mock import patch

from offshore_demo.pipeline import run_pipeline


class WindowsResourceTests(unittest.TestCase):
    def test_database_is_closed_before_first_and_repeated_publication(self):
        real_connect = sqlite3.connect
        real_replace = Path.replace
        connections = []
        checked_publications = []

        def tracked_connect(*arguments, **options):
            connection = real_connect(*arguments, **options)
            connections.append(connection)
            return connection

        def replace_with_windows_lock_check(temporary, target):
            if temporary.name == "offshore.sqlite.tmp":
                self.assertTrue(connections, "A publicação deve ter criado uma conexão real.")
                for connection in connections:
                    try:
                        connection.execute("SELECT 1").fetchone()
                    except sqlite3.ProgrammingError as error:
                        self.assertIn("closed", str(error))
                    else:
                        error = PermissionError(
                            32,
                            "Simulação de WinError 32: SQLite ainda mantém o ficheiro aberto.",
                            str(temporary),
                        )
                        error.winerror = 32
                        raise error
                checked_publications.append(Path(target))
            # As escritas e substituições continuam a acontecer no filesystem real.
            return real_replace(temporary, target)

        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            try:
                with patch("offshore_demo.pipeline.sqlite3.connect", new=tracked_connect), \
                     patch.object(Path, "replace", new=replace_with_windows_lock_check):
                    first = run_pipeline(root)
                    second = run_pipeline(root)

                database = root / "data" / "processed" / "offshore.sqlite"
                self.assertEqual(checked_publications, [database, database])
                self.assertEqual(len(connections), 2)
                self.assertEqual(first, second)
                self.assertEqual(first["accepted_rows"], 18)
                self.assertFalse(database.with_suffix(".sqlite.tmp").exists())

                with closing(real_connect(database)) as connection:
                    self.assertEqual(connection.execute("PRAGMA integrity_check").fetchone(), ("ok",))
                    self.assertEqual(connection.execute("PRAGMA foreign_key_check").fetchall(), [])
                    self.assertEqual(connection.execute(
                        "SELECT COUNT(*) FROM fact_operations"
                    ).fetchone(), (18,))
                    budget, actual = connection.execute(
                        "SELECT SUM(budget_cents) / 100.0, SUM(actual_cents) / 100.0 FROM fact_operations"
                    ).fetchone()
                    self.assertEqual(budget, first["metrics"]["budget_eur"])
                    self.assertEqual(actual, first["metrics"]["actual_eur"])
            finally:
                # Também liberta os handles se o código anterior falhar na publicação.
                for connection in connections:
                    connection.close()


if __name__ == "__main__":
    unittest.main()
