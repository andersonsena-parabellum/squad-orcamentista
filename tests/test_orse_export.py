"""Testes do adaptador de conexão usado apenas na conversão inicial do ORSE."""
import subprocess
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import exportar_orse_mssql


class OrseExportTests(unittest.TestCase):
    def test_auto_server_extracts_localdb_pipe_in_localized_output(self):
        responses = [
            subprocess.CompletedProcess([], 0, "", ""),
            subprocess.CompletedProcess(
                [],
                0,
                'Nome: "ORSE"\nNome do pipe da instância: np:\\\\.\\pipe\\LOCALDB#ABC\\tsql\\query\n',
                "",
            ),
        ]
        with patch.object(exportar_orse_mssql.subprocess, "run", side_effect=responses):
            self.assertEqual(
                exportar_orse_mssql.resolve_server("auto"),
                r"np:\\.\pipe\LOCALDB#ABC\tsql\query",
            )

    def test_auto_server_falls_back_to_sql_express(self):
        with patch.object(exportar_orse_mssql.subprocess, "run", side_effect=FileNotFoundError):
            self.assertEqual(exportar_orse_mssql.resolve_server("auto"), r"localhost\ORSE")


if __name__ == "__main__":
    unittest.main()
