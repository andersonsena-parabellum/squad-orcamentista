#!/usr/bin/env python3
"""Consulta rastreável de composições e insumos por fonte e regime explícitos."""

from __future__ import annotations

import argparse
import json
import sqlite3
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]
DB_PATH = BASE_DIR / "base_precos.db"
REGISTRY_PATH = BASE_DIR / "FONTES_DADOS.json"

for _stream in (sys.stdout, sys.stderr):
    if hasattr(_stream, "reconfigure"):
        _stream.reconfigure(encoding="utf-8")


def brl(value: float | None) -> str:
    if value is None or value <= 0:
        return "SEM PREÇO — USO BLOQUEADO"
    return f"R$ {value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def source_record(source: str) -> dict:
    if not REGISTRY_PATH.exists():
        raise RuntimeError(f"registro de proveniência ausente: {REGISTRY_PATH}")
    data = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))
    record = data.get("fontes", {}).get(source)
    if not record:
        raise RuntimeError(f"fonte {source} sem registro de proveniência")
    return record


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("consulta", help="código exato ou trecho da descrição")
    parser.add_argument("--fonte", required=True, choices=("SINAPI", "ORSE"))
    parser.add_argument(
        "--regime", required=True, choices=("desonerado", "nao_desonerado")
    )
    parser.add_argument(
        "--diagnostico",
        action="store_true",
        help="permite apenas inspeção de fonte bloqueada; a saída não pode precificar",
    )
    args = parser.parse_args()

    record = source_record(args.fonte)
    status = str(record.get("status", "AUSENTE")).upper()
    if status != "LIBERADA" and not args.diagnostico:
        print(f"BLOQUEADO: fonte {args.fonte} com status {status}.", file=sys.stderr)
        print(record.get("motivo", "Sem justificativa registrada."), file=sys.stderr)
        return 2
    if not DB_PATH.exists():
        print(f"BLOQUEADO: banco ausente: {DB_PATH}", file=sys.stderr)
        return 2

    price_comp = "custo_deson" if args.regime == "desonerado" else "custo_nao_deson"
    price_input = "preco_deson" if args.regime == "desonerado" else "preco_nao_deson"
    provenance = f"UF {record.get('uf', 'N/D')} | competência {record.get('competencia', 'N/D')}"
    banner = "DIAGNÓSTICO — NÃO UTILIZAR EM ORÇAMENTO" if status != "LIBERADA" else "FONTE LIBERADA"

    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        comp = conn.execute(
            f"SELECT fonte,codigo,descricao,unidade,grupo,{price_comp} AS preco "
            "FROM composicoes WHERE fonte=? AND codigo=?",
            (args.fonte, args.consulta.strip()),
        ).fetchone()
        if comp:
            print(f"[{banner}] {comp['fonte']} {comp['codigo']} — {comp['descricao']}")
            print(f"{provenance} | Unidade: {comp['unidade']} | Grupo: {comp['grupo']} | {brl(comp['preco'])}")
            rows = conn.execute(
                "SELECT tipo_item,codigo_item,descricao,unidade,coeficiente "
                "FROM composicao_itens WHERE fonte=? AND codigo_composicao=?",
                (args.fonte, comp["codigo"]),
            ).fetchall()
            for row in rows:
                table = "insumos" if str(row["tipo_item"]).upper() == "INSUMO" else "composicoes"
                price_column = price_input if table == "insumos" else price_comp
                child = conn.execute(
                    f"SELECT {price_column} FROM {table} WHERE fonte=? AND codigo=?",
                    (args.fonte, row["codigo_item"]),
                ).fetchone()
                unit_price = child[0] if child else None
                print(
                    f"  {row['tipo_item']} {row['codigo_item']} | {row['unidade']} | "
                    f"coef. {row['coeficiente']} | {brl(unit_price)} | {row['descricao']}"
                )
            if status == "LIBERADA" and comp["preco"] is not None and comp["preco"] > 0:
                return 0
            print("BLOQUEADO: a composição não possui custo positivo para UF/competência/regime selecionados.", file=sys.stderr)
            return 2

        insumo = conn.execute(
            f"SELECT fonte,codigo,descricao,unidade,tipo,{price_input} AS preco "
            "FROM insumos WHERE fonte=? AND codigo=?",
            (args.fonte, args.consulta.strip()),
        ).fetchone()
        if insumo:
            print(f"[{banner}] {insumo['fonte']} {insumo['codigo']} — {insumo['descricao']}")
            print(f"{provenance} | Unidade: {insumo['unidade']} | Tipo: {insumo['tipo']} | {brl(insumo['preco'])}")
            if status == "LIBERADA" and insumo["preco"] is not None and insumo["preco"] > 0:
                return 0
            print("BLOQUEADO: o insumo não possui preço positivo para UF/competência/regime selecionados.", file=sys.stderr)
            return 2

        rows = conn.execute(
            f"SELECT fonte,codigo,descricao,unidade,{price_comp} AS preco FROM composicoes "
            "WHERE fonte=? AND descricao LIKE ? ORDER BY codigo LIMIT 20",
            (args.fonte, f"%{args.consulta.strip()}%"),
        ).fetchall()
        if not rows:
            print("Nenhum registro encontrado para a fonte informada.")
            return 1
        print(f"[{banner}] resultados em {args.fonte} | {provenance}:")
        for row in rows:
            print(f"  {row['codigo']} | {row['unidade']} | {brl(row['preco'])} | {row['descricao']}")
        return 0 if status == "LIBERADA" else 2


if __name__ == "__main__":
    raise SystemExit(main())
