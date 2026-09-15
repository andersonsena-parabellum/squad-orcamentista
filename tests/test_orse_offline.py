"""O cache oficial deve funcionar sem rede e sem confiar nos numeros do JSON."""
import contextlib
import io
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "03-BASE_DE_PRECOS" / "04-SCRIPTS"))
import consultar_orse_oficial as cli
import orse_oficial


class OfflineTests(unittest.TestCase):
    def test_exact_cache_never_requires_network(self):
        with patch.object(cli, "_local_connection", return_value=None), patch.object(
            cli, "fetch_composition", side_effect=AssertionError("rede indevida")
        ), patch.object(sys, "argv", ["consulta", "05970", "--somente-local"]), contextlib.redirect_stdout(io.StringIO()) as output:
            self.assertEqual(cli.main(), 0)
        self.assertIn("CACHE_LOCAL", output.getvalue())

    def test_cache_rebuilds_price_from_raw_evidence(self):
        original = orse_oficial.json.loads
        def changed(text):
            data = original(text)
            if data.get("codigo") == "5970":
                data["custo_total_orse_se"] = 1
            return data
        with patch.object(orse_oficial.json, "loads", side_effect=changed):
            result = orse_oficial.load_cached_composition("05970")
        self.assertEqual(result["custo_total_orse_se"], 1508.83)

    def test_description_search_uses_verified_cache_without_network(self):
        with patch.object(cli, "_local_connection", return_value=None), patch.object(
            cli, "search_compositions", side_effect=AssertionError("rede indevida")
        ), patch.object(
            sys, "argv", ["consulta", "drenagem", "--somente-local"]
        ), contextlib.redirect_stdout(io.StringIO()) as output:
            self.assertEqual(cli.main(), 0)
        self.assertIn("CACHE_LOCAL", output.getvalue())
        self.assertIn("05970/ORSE", output.getvalue())

    def test_source_registry_is_fail_closed(self):
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            raw = base / "source.ORSE"
            raw.write_bytes(b"official")
            registry = base / "FONTES_DADOS.json"
            registry.write_text(
                '{"fontes":{"ORSE":{"status":"QUARENTENADA","capacidades":{"consulta":"LIBERADA"},'
                '"arquivo_origem":"source.ORSE","sha256_origem":"x"}}}',
                encoding="utf-8",
            )
            with patch.object(orse_oficial, "BASE_DIR", base), patch.object(
                orse_oficial, "REGISTRY_PATH", registry
            ):
                with self.assertRaisesRegex(ValueError, "capacidade de consulta"):
                    orse_oficial.validate_source()


if __name__ == "__main__":
    unittest.main()
