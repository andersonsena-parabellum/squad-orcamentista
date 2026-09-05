#!/usr/bin/env python3
"""Isola a particao ORSE sintetica sem apagar os registros historicos."""

from __future__ import annotations

import os
import sqlite3
import tempfile
from pathlib import Path

from squad_common import PRICE_DB, SOURCE_REGISTRY, atomic_write_json, load_json, sha256_file, utc_now


QUARANTINE_SOURCE = "ORSE_LEGADO_QUARENTENA"


def main() -> int:
    if not PRICE_DB.is_file():
        raise FileNotFoundError(PRICE_DB)
    fd, temp_name = tempfile.mkstemp(prefix=".base_precos-orse-", suffix=".db", dir=PRICE_DB.parent)
    os.close(fd)
    temp_path = Path(temp_name)
    try:
        source = sqlite3.connect(f"file:{PRICE_DB.as_posix()}?mode=ro", uri=True)
        target = sqlite3.connect(temp_path)
        try:
            source.backup(target)
            target.execute("BEGIN IMMEDIATE")
            counts = {}
            for table in ("composicoes", "insumos", "composicao_itens"):
                counts[table] = target.execute(f"SELECT count(*) FROM {table} WHERE fonte='ORSE'").fetchone()[0]
                target.execute(f"UPDATE {table} SET fonte=? WHERE fonte='ORSE'", (QUARANTINE_SOURCE,))
            target.execute(
                "INSERT OR REPLACE INTO metadata(chave,valor) VALUES(?,?)",
                ("orse_legado_quarentenado_em", utc_now()),
            )
            target.commit()
            if target.execute("PRAGMA integrity_check").fetchone()[0] != "ok":
                raise RuntimeError("falha de integridade apos migracao")
        finally:
            target.close()
            source.close()
        os.replace(temp_path, PRICE_DB)
        registry = load_json(SOURCE_REGISTRY)
        registry["database"]["sha256"] = sha256_file(PRICE_DB)
        registry["database"]["observacao"] = "Partição ORSE sintética preservada sob ORSE_LEGADO_QUARENTENA; consultas ORSE usam somente o portal oficial/cache verificável."
        atomic_write_json(SOURCE_REGISTRY, registry)
        print(f"ORSE legada isolada como {QUARANTINE_SOURCE}: {counts}")
        return 0
    finally:
        if temp_path.exists():
            temp_path.unlink()


if __name__ == "__main__":
    raise SystemExit(main())
