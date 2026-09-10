"""O cache oficial deve funcionar sem rede e sem confiar nos numeros do JSON."""
import contextlib
import io
import sys
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


if __name__ == "__main__":
    unittest.main()
