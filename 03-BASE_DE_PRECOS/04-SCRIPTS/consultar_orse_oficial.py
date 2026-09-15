#!/usr/bin/env python3
"""Busca e armazena, com proveniencia, composicoes oficiais ORSE/CEHOP."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
import sqlite3
import sys
from pathlib import Path

from orse_oficial import (
    fetch_composition,
    load_cached_composition,
    search_cached_compositions,
    search_compositions,
    validate_source,
)


BASE_DIR = Path(__file__).resolve().parents[1]
DB_PATH = BASE_DIR / "base_precos.db"
REGISTRY_PATH = BASE_DIR / "FONTES_DADOS.json"

for _stream in (sys.stdout, sys.stderr):
    if hasattr(_stream, "reconfigure"):
        _stream.reconfigure(encoding="utf-8")


def _registry() -> tuple[dict, dict]:
    data = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))
    return data, data["fontes"]["ORSE"]


def _local_connection() -> sqlite3.Connection | None:
    if not DB_PATH.is_file():
        return None
    registry, source = _registry()
    expected_db_hash = registry.get("database", {}).get("sha256")
    if expected_db_hash and hashlib.sha256(DB_PATH.read_bytes()).hexdigest() != expected_db_hash:
        return None
    connection = sqlite3.connect(f"file:{DB_PATH.as_posix()}?mode=ro", uri=True)
    connection.row_factory = sqlite3.Row
    metadata = dict(connection.execute("SELECT chave,valor FROM metadata WHERE chave LIKE 'orse_%'"))
    if metadata.get("orse_offline_competencia") != source.get("competencia"):
        connection.close()
        return None
    if metadata.get("orse_sha256_origem") != source.get("sha256_origem"):
        connection.close()
        return None
    if connection.execute("SELECT count(*) FROM composicoes WHERE fonte='ORSE'").fetchone()[0] == 0:
        connection.close()
        return None
    return connection


def _local_exact(connection: sqlite3.Connection, code: str) -> dict | None:
    normalized = str(int(code.split("/", 1)[0]))
    composition = connection.execute(
        "SELECT codigo,descricao,unidade,grupo,custo_nao_deson preco FROM composicoes "
        "WHERE fonte='ORSE' AND codigo=?",
        (normalized,),
    ).fetchone()
    if not composition:
        return None
    registry, source = _registry()
    auxiliary = []
    detailed = []
    for item in connection.execute(
        "SELECT tipo_item,codigo_item,descricao,unidade,coeficiente FROM composicao_itens "
        "WHERE fonte='ORSE' AND codigo_composicao=? ORDER BY rowid",
        (normalized,),
    ):
        is_input = str(item["tipo_item"]).upper() == "INSUMO"
        table = "insumos" if is_input else "composicoes"
        price_column = "preco_nao_deson" if is_input else "custo_nao_deson"
        price = connection.execute(
            f"SELECT {price_column} FROM {table} WHERE fonte='ORSE' AND codigo=?",
            (item["codigo_item"],),
        ).fetchone()
        payload = {
            "tipo": "INSUMO" if is_input else "COMPOSICAO_AUXILIAR",
            "codigo": item["codigo_item"],
            "fonte": item["codigo_item"].split(":", 1)[0] if ":" in item["codigo_item"] else "ORSE",
            "descricao": item["descricao"],
            "unidade": item["unidade"],
            "coeficiente": item["coeficiente"],
            "custo_unitario_orse_se": price[0] if price else None,
        }
        (detailed if is_input else auxiliary).append(payload)
    return {
        "schema_version": "1.1.0",
        "fonte": "ORSE",
        "uf": source.get("uf", "SE"),
        "competencia": source["competencia"],
        "codigo": composition["codigo"],
        "codigo_exibicao": f"{int(composition['codigo']):05d}/ORSE",
        "descricao": composition["descricao"],
        "unidade": composition["unidade"],
        "grupo": composition["grupo"],
        "custo_total_orse_se": composition["preco"],
        "composicoes_auxiliares": auxiliary,
        "insumos_detalhados": detailed,
        "proveniencia": {
            "modo": "SQLITE_LOCAL",
            "arquivo_origem": source["arquivo_origem"],
            "sha256_origem": source["sha256_origem"],
            "sha256_database": registry["database"]["sha256"],
        },
    }


def _local_search(connection: sqlite3.Connection, description: str, page: int) -> dict:
    if page < 1:
        raise ValueError("pagina deve ser maior ou igual a 1")
    source = _registry()[1]
    pattern = f"%{description.strip()}%"
    total = connection.execute(
        "SELECT count(*) FROM composicoes WHERE fonte='ORSE' AND codigo NOT LIKE '%:%' AND descricao LIKE ?",
        (pattern,),
    ).fetchone()[0]
    result = connection.execute(
        "SELECT codigo,descricao,unidade,custo_nao_deson preco FROM composicoes "
        "WHERE fonte='ORSE' AND codigo NOT LIKE '%:%' AND descricao LIKE ? "
        "ORDER BY CAST(codigo AS INTEGER) LIMIT 20 OFFSET ?",
        (pattern, (page - 1) * 20),
    ).fetchall()
    return {
        "fonte": "ORSE",
        "uf": source.get("uf", "SE"),
        "competencia": source["competencia"],
        "consulta": description,
        "pagina": page,
        "total": total,
        "paginas": max(1, math.ceil(total / 20)),
        "modo": "SQLITE_LOCAL",
        "resultados": [
            {
                "codigo": row["codigo"],
                "descricao": row["descricao"],
                "unidade": row["unidade"],
                "custo_total_orse_se": row["preco"],
            }
            for row in result
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("consulta", help="codigo ORSE exato ou trecho da descricao")
    parser.add_argument("--pagina", type=int, default=1)
    parser.add_argument("--json", action="store_true")
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--web", action="store_true", help="forca consulta ao portal oficial")
    mode.add_argument(
        "--somente-local",
        action="store_true",
        help="usa SQLite/cache verificado e bloqueia quando nao houver evidencia local",
    )
    args = parser.parse_args()
    try:
        source = validate_source()
        exact = bool(re.fullmatch(r"\d{1,5}(?:/ORSE)?", args.consulta.strip(), re.IGNORECASE))
        connection = None if args.web else _local_connection()
        result = None
        if connection:
            try:
                result = _local_exact(connection, args.consulta) if exact else _local_search(connection, args.consulta, args.pagina)
            finally:
                connection.close()
        if result is None and exact and not args.web:
            result = load_cached_composition(args.consulta, source)
        if result is None and not exact and not args.web:
            result = search_cached_compositions(args.consulta, args.pagina, source)
        if result is None and args.somente_local:
            raise RuntimeError("base ORSE local ausente, desatualizada ou sem o codigo solicitado")
        if result is None:
            result = fetch_composition(args.consulta) if exact else search_compositions(args.consulta, args.pagina)

        if exact:
            if args.json:
                print(json.dumps(result, ensure_ascii=False, indent=2))
            else:
                mode_label = result.get("proveniencia", {}).get("modo", "WEB")
                print(f"[ORSE OFICIAL {mode_label} | SE {result['competencia']}] {result['codigo_exibicao']} — {result['descricao']}")
                print(f"Unidade: {result['unidade']} | Custo ORSE/SE: R$ {result['custo_total_orse_se']:.2f}")
                print(f"Auxiliares: {len(result['composicoes_auxiliares'])} | Insumos detalhados: {len(result['insumos_detalhados'])}")
                if result["proveniencia"].get("url"):
                    print(f"Fonte: {result['proveniencia']['url']}")
                else:
                    print(f"Fonte local: {result['proveniencia']['arquivo_origem']} | SHA-256 {result['proveniencia']['sha256_origem']}")
                print("LIBERADO COMO PARADIGMA. Preço direto fora de SE depende de autorização e justificativa expressas.")
        else:
            if args.json:
                print(json.dumps(result, ensure_ascii=False, indent=2))
            else:
                mode_label = result.get("modo", "WEB")
                print(f"[ORSE OFICIAL {mode_label} | SE {result['competencia']}] {result['total']} resultado(s); página {result['pagina']}/{result['paginas']}")
                for item in result["resultados"]:
                    print(f"  {item['codigo'].zfill(5)}/ORSE | {item['unidade']} | R$ {item['custo_total_orse_se']:.2f} | {item['descricao']}")
                if mode_label == "WEB":
                    print("Consulte um código exato para gravar a composição analítica e sua evidência local.")
        return 0
    except Exception as exc:
        print(f"BLOQUEADO: falha na consulta ORSE oficial: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
