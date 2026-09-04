#!/usr/bin/env python3
"""Migra o SQLite para chaves compostas fonte+código, de forma transacional."""

from __future__ import annotations

import sqlite3
import sys

from squad_common import PRICE_DB, utc_now


def primary_key_columns(conn: sqlite3.Connection, table: str) -> list[str]:
    rows = conn.execute(f"PRAGMA table_info({table})").fetchall()
    return [row[1] for row in sorted((row for row in rows if row[5]), key=lambda row: row[5])]


def main() -> int:
    if not PRICE_DB.is_file():
        print(f"BLOQUEADO: banco ausente: {PRICE_DB}", file=sys.stderr)
        return 2
    with sqlite3.connect(PRICE_DB) as conn:
        if primary_key_columns(conn, "composicoes") == ["fonte", "codigo"]:
            print("[OK] Schema já está na versão 2.0.0.")
            return 0
        nulls = conn.execute("SELECT count(*) FROM composicoes WHERE fonte IS NULL OR codigo IS NULL").fetchone()[0]
        duplicates = conn.execute(
            "SELECT count(*) FROM (SELECT fonte,codigo,count(*) n FROM composicoes GROUP BY fonte,codigo HAVING n>1)"
        ).fetchone()[0]
        if nulls or duplicates:
            print(f"BLOQUEADO: nulls={nulls}, duplicidades={duplicates}", file=sys.stderr)
            return 2
        try:
            conn.execute("BEGIN IMMEDIATE")
            conn.execute("ALTER TABLE composicoes RENAME TO composicoes_legacy_v1")
            conn.execute(
                "CREATE TABLE composicoes ("
                "fonte TEXT NOT NULL, codigo TEXT NOT NULL, descricao TEXT, unidade TEXT, grupo TEXT, "
                "custo_deson REAL, custo_nao_deson REAL, PRIMARY KEY (fonte,codigo))"
            )
            conn.execute(
                "INSERT INTO composicoes(fonte,codigo,descricao,unidade,grupo,custo_deson,custo_nao_deson) "
                "SELECT fonte,codigo,descricao,unidade,grupo,custo_deson,custo_nao_deson FROM composicoes_legacy_v1"
            )
            conn.execute("DROP TABLE composicoes_legacy_v1")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_composicoes_descricao ON composicoes(fonte,descricao)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_itens_comp ON composicao_itens(fonte,codigo_composicao)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_itens_codigo ON composicao_itens(fonte,codigo_item)")
            conn.execute("CREATE TABLE IF NOT EXISTS metadata (chave TEXT PRIMARY KEY, valor TEXT NOT NULL)")
            conn.execute("INSERT OR REPLACE INTO metadata(chave,valor) VALUES('schema_version','2.0.0')")
            conn.execute("INSERT OR REPLACE INTO metadata(chave,valor) VALUES('migrated_at',?)", (utc_now(),))
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        integrity = conn.execute("PRAGMA integrity_check").fetchone()[0]
        if integrity != "ok":
            print(f"BLOQUEADO: integrity_check={integrity}", file=sys.stderr)
            return 2
    print("[OK] Migração transacional concluída: schema 2.0.0, chave (fonte,codigo).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
