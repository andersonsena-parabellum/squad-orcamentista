#!/usr/bin/env python3
"""Exporta a base oficial ORSE do SQL Server para o SQLite portavel do Squad.

O aplicativo ORSE e seu SQL Server sao usados somente como conversor do
formato proprietario .ORSE. O runtime do Squad consulta o SQLite e nao depende
do portal nem de uma instalacao local do ORSE.
"""

from __future__ import annotations

import argparse
import getpass
import json
import os
import subprocess
import shutil
import sqlite3
import sys
import tempfile
import unicodedata
from collections import defaultdict, deque
from contextlib import closing
from dataclasses import dataclass
from decimal import Decimal
from pathlib import Path
from typing import Any, Iterable

from squad_common import PRICE_DB, SOURCE_REGISTRY, atomic_write_json, exclusive_lock, load_json, sha256_file, utc_now


DEFAULT_SOURCE = SOURCE_REGISTRY.parent / "00-FONTES_OFICIAIS" / "ORSE-2026-06.ORSE"
DEFAULT_URL = "https://orse.cehop.se.gov.br/downloads/20260601-00.ORSE"
DEFAULT_SHA256 = "f1384a72398fb571b31de0fe0b0db918c90914c4362c3b75faa88170cb3bba90"


@dataclass(frozen=True)
class Period:
    year: int
    month: int
    order: int


def portable_code(source: str, code: Any) -> str:
    """Mantem codigos ORSE simples e qualifica auxiliares de outras fontes."""
    source = str(source or "ORSE").strip().upper()
    code_text = str(int(code)) if isinstance(code, (int, float, Decimal)) else str(code).strip().lstrip("0") or "0"
    return code_text if source == "ORSE" else f"{source}:{code_text}"


def number(value: Any) -> float | None:
    if value is None:
        return None
    return float(value)


def folded(value: Any) -> str:
    return "".join(
        character
        for character in unicodedata.normalize("NFKD", str(value or "").lower())
        if not unicodedata.combining(character)
    )


def rows(cursor: Any, sql: str, params: Iterable[Any]) -> list[dict[str, Any]]:
    cursor.execute(sql, tuple(params))
    names = [column[0] for column in cursor.description]
    return [dict(zip(names, row)) for row in cursor.fetchall()]


def assert_schema(cursor: Any) -> None:
    required = {"tb_servico", "tb_servico_preco", "tb_insumo", "tb_insumo_preco", "tb_composicao", "tb_periodo"}
    found = {
        row[0].lower()
        for row in cursor.execute(
            "SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_TYPE='BASE TABLE'"
        ).fetchall()
    }
    missing = sorted(required - found)
    if missing:
        raise RuntimeError(f"Banco ORSE nao inicializado; tabelas ausentes: {missing}")


def extract(cursor: Any, period: Period, min_compositions: int, min_inputs: int) -> dict[str, Any]:
    assert_schema(cursor)
    period_params = (period.year, period.month, period.order)
    services = rows(
        cursor,
        """
        SELECT s.font_sg_fonte AS fonte, s.serv_nr_codigo AS codigo,
               s.serv_tx_descricao AS descricao, s.serv_sg_unidade AS unidade,
               s.gpsv_nr_codigo AS grupo, p.svpr_vl_unitario AS preco
          FROM tb_servico s
          JOIN tb_servico_preco p
            ON p.font_sg_fonte=s.font_sg_fonte AND p.serv_nr_codigo=s.serv_nr_codigo
         WHERE p.peri_nr_ano=? AND p.peri_nr_mes=? AND p.peri_nr_ordem=?
        """,
        period_params,
    )
    inputs = rows(
        cursor,
        """
        SELECT i.font_sg_fonte AS fonte, i.insu_nr_codigo AS codigo,
               i.insu_tx_descricao AS descricao, i.insu_sg_unidade AS unidade,
               i.gpin_nr_codigo AS grupo, p.inpr_vl_adotado AS preco
          FROM tb_insumo i
          JOIN tb_insumo_preco p
            ON p.font_sg_fonte=i.font_sg_fonte AND p.insu_nr_codigo=i.insu_nr_codigo
         WHERE p.peri_nr_ano=? AND p.peri_nr_mes=? AND p.peri_nr_ordem=?
        """,
        period_params,
    )
    items = rows(
        cursor,
        """
        SELECT c.font_sg_fonte AS fonte_pai, c.serv_nr_codigo AS codigo_pai,
               c.comp_in_insumo AS indicador_insumo, c.comp_sg_fonte AS fonte_item,
               c.comp_nr_codigo AS codigo_item, c.comp_qn_quantidade AS coeficiente
          FROM tb_composicao c
         WHERE c.peri_nr_ano=? AND c.peri_nr_mes=? AND c.peri_nr_ordem=?
        """,
        period_params,
    )

    service_by_key = {(str(row["fonte"]).upper(), str(int(row["codigo"]))): row for row in services}
    input_by_key = {(str(row["fonte"]).upper(), str(int(row["codigo"]))): row for row in inputs}
    items_by_parent: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    for item in items:
        key = (str(item["fonte_pai"]).upper(), str(int(item["codigo_pai"])))
        items_by_parent[key].append(item)

    roots = {key for key in service_by_key if key[0] == "ORSE"}
    root_inputs = {key for key in input_by_key if key[0] == "ORSE"}
    if len(roots) < min_compositions or len(root_inputs) < min_inputs:
        raise RuntimeError(
            "Carga ORSE recusada por volume incompativel com a publicacao oficial: "
            f"composicoes={len(roots)} (minimo {min_compositions}); "
            f"insumos={len(root_inputs)} (minimo {min_inputs})"
        )

    generic = sum(
        1
        for key in roots
        if "especificacao analitica" in folded(service_by_key[key]["descricao"])
        and "execucao tecnica especializada" in folded(service_by_key[key]["descricao"])
    )
    if generic:
        raise RuntimeError(f"Carga ORSE recusada: {generic} descricoes sinteticas detectadas")

    closure = set(roots)
    queue = deque(roots)
    referenced_inputs = set(root_inputs)
    missing_references: list[str] = []
    while queue:
        parent = queue.popleft()
        for item in items_by_parent.get(parent, []):
            child = (str(item["fonte_item"] or "ORSE").upper(), str(int(item["codigo_item"])))
            is_input = str(item["indicador_insumo"] or "").strip().upper() == "S"
            if is_input:
                referenced_inputs.add(child)
                if child not in input_by_key:
                    missing_references.append(f"INSUMO {child[0]}/{child[1]}")
            elif child not in closure:
                if child not in service_by_key:
                    missing_references.append(f"COMPOSICAO {child[0]}/{child[1]}")
                else:
                    closure.add(child)
                    queue.append(child)
    if missing_references:
        raise RuntimeError(f"Carga ORSE possui referencias sem cadastro: {missing_references[:20]}")

    composition_rows = []
    for key in sorted(closure):
        row = service_by_key[key]
        composition_rows.append(
            (
                portable_code(*key),
                str(row["descricao"] or "").strip(),
                str(row["unidade"] or "").strip(),
                f"{key[0]}|{row['grupo']}",
                number(row["preco"]),
                number(row["preco"]),
            )
        )

    input_rows = []
    for key in sorted(referenced_inputs):
        row = input_by_key[key]
        input_rows.append(
            (
                portable_code(*key),
                str(row["descricao"] or "").strip(),
                str(row["unidade"] or "").strip(),
                f"{key[0]}|{row['grupo']}",
                number(row["preco"]),
                number(row["preco"]),
            )
        )

    analytical_rows = []
    for parent in sorted(closure):
        for item in items_by_parent.get(parent, []):
            child = (str(item["fonte_item"] or "ORSE").upper(), str(int(item["codigo_item"])))
            is_input = str(item["indicador_insumo"] or "").strip().upper() == "S"
            detail = input_by_key[child] if is_input else service_by_key[child]
            coefficient = number(item["coeficiente"])
            if coefficient is None or coefficient < 0:
                raise RuntimeError(f"Coeficiente invalido em {parent}: {child}={coefficient}")
            analytical_rows.append(
                (
                    "ORSE",
                    portable_code(*parent),
                    "INSUMO" if is_input else "COMPOSICAO",
                    portable_code(*child),
                    str(detail["descricao"] or "").strip(),
                    str(detail["unidade"] or "").strip(),
                    coefficient,
                )
            )
    return {
        "composicoes": composition_rows,
        "insumos": input_rows,
        "itens": analytical_rows,
        "contagens": {
            "composicoes_orse": len(roots),
            "composicoes_auxiliares_outras_fontes": len(closure - roots),
            "insumos_orse": len(root_inputs),
            "insumos_auxiliares_outras_fontes": len(referenced_inputs - root_inputs),
            "itens_analiticos": len(analytical_rows),
        },
    }


def import_database(data: dict[str, Any], period: Period, source_hash: str) -> None:
    fd, temp_name = tempfile.mkstemp(prefix=".base_precos.", suffix=".db", dir=PRICE_DB.parent)
    os.close(fd)
    temp_db = Path(temp_name)
    try:
        shutil.copy2(PRICE_DB, temp_db)
        with closing(sqlite3.connect(temp_db)) as connection:
            connection.execute("BEGIN IMMEDIATE")
            connection.execute("DELETE FROM composicao_itens WHERE fonte='ORSE'")
            connection.execute("DELETE FROM composicoes WHERE fonte='ORSE'")
            connection.execute("DELETE FROM insumos WHERE fonte='ORSE'")
            connection.executemany(
                "INSERT INTO composicoes(fonte,codigo,descricao,unidade,grupo,custo_deson,custo_nao_deson) "
                "VALUES('ORSE',?,?,?,?,?,?)",
                data["composicoes"],
            )
            connection.executemany(
                "INSERT INTO insumos(fonte,codigo,descricao,unidade,tipo,preco_deson,preco_nao_deson) "
                "VALUES('ORSE',?,?,?,?,?,?)",
                data["insumos"],
            )
            connection.executemany(
                "INSERT INTO composicao_itens(fonte,codigo_composicao,tipo_item,codigo_item,descricao,unidade,coeficiente) "
                "VALUES(?,?,?,?,?,?,?)",
                data["itens"],
            )
            metadata = {
                "orse_offline_competencia": f"{period.year:04d}-{period.month:02d}",
                "orse_offline_ordem": str(period.order),
                "orse_sha256_origem": source_hash,
                "orse_exported_at": utc_now(),
            }
            connection.executemany("INSERT OR REPLACE INTO metadata(chave,valor) VALUES(?,?)", metadata.items())
            connection.commit()
            if connection.execute("PRAGMA integrity_check").fetchone()[0] != "ok":
                raise RuntimeError("SQLite nao passou no integrity_check")
        os.replace(temp_db, PRICE_DB)
    finally:
        if temp_db.exists():
            temp_db.unlink()


def update_registry(source: Path, source_hash: str, url: str, period: Period, data: dict[str, Any]) -> None:
    registry = load_json(SOURCE_REGISTRY)
    record = registry["fontes"]["ORSE"]
    record.update(
        {
            "status": "LIBERADA",
            "competencia": f"{period.year:04d}-{period.month:02d}",
            "ordem_periodo": period.order,
            "arquivo_origem": source.resolve().relative_to(SOURCE_REGISTRY.parent.resolve()).as_posix(),
            "url_oficial": url,
            "sha256_origem": source_hash,
            "modo_consulta": "SQLITE_LOCAL_PRIMARIO; PORTAL_OFICIAL_CONTINGENCIA",
            "exportado_em": utc_now(),
            "contagens": data["contagens"],
            "motivo": (
                "Publicacao mensal oficial importada no ORSE local e exportada integralmente para SQLite. "
                "Consulta local e deterministica; portal oficial apenas para atualizacao, conferencia e contingencia."
            ),
        }
    )
    registry["database"]["sha256"] = sha256_file(PRICE_DB)
    registry["database"]["observacao"] = (
        "SINAPI e ORSE oficiais em SQLite portavel; ORSE legado sintetico permanece em quarentena."
    )
    atomic_write_json(SOURCE_REGISTRY, registry)


def resolve_server(server: str) -> str:
    if server.lower() == "auto":
        try:
            subprocess.run(
                ["sqllocaldb", "start", "ORSE"],
                check=True,
                capture_output=True,
                text=True,
            )
            info = subprocess.run(
                ["sqllocaldb", "info", "ORSE"],
                check=True,
                capture_output=True,
                text=True,
            ).stdout
            pipe_line = next(line for line in info.splitlines() if "np:\\" in line.lower())
            server = pipe_line[pipe_line.lower().index("np:\\") :].strip()
        except (FileNotFoundError, subprocess.CalledProcessError, StopIteration):
            server = r"localhost\ORSE"
    return server


def connect(args: argparse.Namespace, password: str | None = None) -> Any:
    try:
        import pyodbc
    except ImportError as exc:
        raise RuntimeError("Instale pyodbc para executar a conversao inicial: python -m pip install pyodbc") from exc
    if args.connection_string:
        return pyodbc.connect(args.connection_string, timeout=30)
    driver = args.driver
    if not driver:
        installed = set(pyodbc.drivers())
        driver = next(
            (
                candidate
                for candidate in (
                    "ODBC Driver 18 for SQL Server",
                    "ODBC Driver 17 for SQL Server",
                    "SQL Server Native Client 11.0",
                    "SQL Server",
                )
                if candidate in installed
            ),
            None,
        )
        if not driver:
            raise RuntimeError(f"Driver ODBC SQL Server ausente; drivers encontrados: {sorted(installed)}")
    server = resolve_server(args.server)
    password = password if password is not None else os.environ.get(args.password_env, "")
    auth = f"UID={args.user};PWD={password};" if args.user else "Trusted_Connection=yes;"
    try:
        return pyodbc.connect(
            f"DRIVER={{{driver}}};SERVER={server};DATABASE={args.database};"
            f"{auth}TrustServerCertificate=yes;",
            timeout=30,
        )
    except pyodbc.Error as exc:
        raise RuntimeError(f"Falha ao conectar ao banco ORSE em {server}: {exc}") from exc


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--arquivo", type=Path, default=DEFAULT_SOURCE)
    parser.add_argument("--sha256-esperado", default=DEFAULT_SHA256)
    parser.add_argument("--url", default=DEFAULT_URL)
    parser.add_argument("--competencia", default="2026-06")
    parser.add_argument("--ordem", type=int, default=1)
    parser.add_argument(
        "--server",
        default="auto",
        help="auto detecta LocalDB ORSE e recua para localhost\\ORSE",
    )
    parser.add_argument("--database", default="ORSE")
    parser.add_argument("--driver", default="", help="vazio seleciona automaticamente um driver SQL Server instalado")
    parser.add_argument("--user", default="", help="vazio usa autenticacao integrada; informe sa apenas no SQL Express")
    parser.add_argument("--password-env", default="ORSE_SQL_PASSWORD")
    parser.add_argument("--ask-password", action="store_true", help="solicita a senha sem exibi-la nem grava-la no historico")
    parser.add_argument("--connection-string", default=os.environ.get("ORSE_SQL_CONNECTION"))
    parser.add_argument("--diagnostico", action="store_true", help="valida conexão, esquema, competência e volumes sem alterar o SQLite")
    parser.add_argument("--min-composicoes", type=int, default=15000)
    parser.add_argument("--min-insumos", type=int, default=12000)
    args = parser.parse_args()

    source = args.arquivo.resolve()
    if not source.is_file():
        raise FileNotFoundError(source)
    source_hash = sha256_file(source)
    if source_hash.lower() != args.sha256_esperado.lower():
        raise RuntimeError(f"Hash divergente: esperado={args.sha256_esperado}; obtido={source_hash}")
    year, month = (int(part) for part in args.competencia.split("-"))
    period = Period(year, month, args.ordem)
    password = None
    if args.user and not (args.connection_string or os.environ.get(args.password_env) or args.ask_password):
        raise RuntimeError(f"Defina a senha somente na variavel de ambiente {args.password_env}")
    if args.user and args.ask_password and not args.connection_string:
        password = getpass.getpass(f"Senha SQL de {args.user}: ")

    connection = connect(args, password)
    try:
        data = extract(connection.cursor(), period, args.min_composicoes, args.min_insumos)
    finally:
        connection.close()
    if args.diagnostico:
        print(
            json.dumps(
                {
                    "status": "PRONTO_PARA_EXPORTAR",
                    "fonte": "ORSE",
                    "competencia": args.competencia,
                    **data["contagens"],
                    "sha256_origem": source_hash,
                },
                ensure_ascii=False,
                indent=2,
            )
        )
        return 0
    with exclusive_lock(PRICE_DB.with_suffix(".import.lock"), "exportar_orse_mssql"):
        import_database(data, period, source_hash)
        update_registry(source, source_hash, args.url, period, data)
    print(
        json.dumps(
            {
                "status": "LIBERADA",
                "fonte": "ORSE",
                "competencia": args.competencia,
                **data["contagens"],
                "sha256_origem": source_hash,
                "sha256_database": sha256_file(PRICE_DB),
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"BLOQUEADO: exportação ORSE não executada: {exc}", file=sys.stderr)
        raise SystemExit(2)
