#!/usr/bin/env python3
"""Valida 100% dos codigos/precos oficiais e seleciona a Faixa A sem BDI.

O script e intencionalmente fail-closed: fonte sem proveniencia, formula sem
cache, codigo/unidade/descricao divergente ou preco zero bloqueiam o gate.
"""

from __future__ import annotations

import argparse
import json
import math
import re
import sqlite3
import sys
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any

import openpyxl

from squad_common import PRICE_DB, money, normalize_text, normalize_unit, sha256_file, source_is_releasable, utc_now


PROCESS_NOTE_RE = re.compile(
    r"\b(REVISAR|CONFIRMAR|PENDENTE|VER\s+MEMORIAL|VER\s+RELAT[OÓ]RIO|"
    r"N[AÃ]O\s+QUANTIFIC|EST[AÁ]\s+FALTANDO|D[UÚ]VIDA\s+INTERNA)\b",
    re.IGNORECASE,
)


def _header_map(ws: Any) -> tuple[int | None, dict[str, int]]:
    expected = {
        "item": ("ITEM",),
        "codigo": ("CÓDIGO", "CODIGO"),
        "banco": ("BANCO", "FONTE"),
        "descricao": ("DESCRIÇÃO", "DESCRICAO"),
        "unidade": ("UND", "UNIDADE", "UN"),
        "quantidade": ("QUANT.", "QUANTIDADE", "QTD"),
        "valor_unit": ("VALOR UNIT", "CUSTO UNIT", "PREÇO UNIT", "PRECO UNIT"),
        "total": ("TOTAL",),
    }
    for row in range(1, min(ws.max_row, 30) + 1):
        values = [normalize_text(ws.cell(row, col).value) for col in range(1, min(ws.max_column, 20) + 1)]
        if not any(v == "ITEM" for v in values) or not any("DESCRI" in v for v in values):
            continue
        mapping: dict[str, int] = {}
        for key, aliases in expected.items():
            for col, value in enumerate(values, 1):
                if key == "valor_unit" and "BDI" in value:
                    continue
                if any(value == alias or value.startswith(alias + " ") for alias in aliases):
                    mapping[key] = col
                    break
        return row, mapping
    return None, {}


def _database_lookup(cur: sqlite3.Cursor, source: str, code: str, regime: str) -> dict[str, Any] | None:
    cost_column = "custo_deson" if regime == "DESONERADO" else "custo_nao_deson"
    cur.execute(
        f"SELECT fonte, codigo, descricao, unidade, {cost_column} FROM composicoes WHERE fonte=? AND codigo=?",
        (source, code),
    )
    row = cur.fetchone()
    if row:
        return {"tipo": "COMPOSICAO", "fonte": row[0], "codigo": row[1], "descricao": row[2], "unidade": row[3], "preco": row[4]}
    price_column = "preco_deson" if regime == "DESONERADO" else "preco_nao_deson"
    cur.execute(
        f"SELECT fonte, codigo, descricao, unidade, {price_column} FROM insumos WHERE fonte=? AND codigo=?",
        (source, code),
    )
    row = cur.fetchone()
    if row:
        return {"tipo": "INSUMO", "fonte": row[0], "codigo": row[1], "descricao": row[2], "unidade": row[3], "preco": row[4]}
    return None


def audit_workbook(path: Path, regime: str, federal_transfer: bool = False) -> dict[str, Any]:
    result: dict[str, Any] = {
        "schema_version": "1.0.0",
        "generated_at": utc_now(),
        "arquivo": str(path.resolve()),
        "sha256": sha256_file(path),
        "regime": regime,
        "falhas": [],
        "itens": [],
        "faixa_a": [],
    }
    if not PRICE_DB.exists():
        result["falhas"].append({"tipo": "BASE_AUSENTE", "mensagem": str(PRICE_DB)})
        result["gate"] = "BLOQUEADO"
        return result

    wb_formula = openpyxl.load_workbook(path, data_only=False, read_only=False)
    wb_value = openpyxl.load_workbook(path, data_only=True, read_only=False)
    ws_formula = wb_formula.active
    ws_value = wb_value[ws_formula.title]
    header_row, columns = _header_map(ws_formula)
    required = {"item", "codigo", "banco", "descricao", "unidade", "quantidade", "valor_unit", "total"}
    missing = sorted(required - set(columns))
    if header_row is None or missing:
        result["falhas"].append({"tipo": "LAYOUT_INVALIDO", "mensagem": f"Colunas ausentes: {missing}"})
        result["gate"] = "BLOQUEADO"
        return result

    conn = sqlite3.connect(f"file:{PRICE_DB.as_posix()}?mode=ro", uri=True)
    try:
        cur = conn.cursor()
        for row in range(header_row + 1, ws_formula.max_row + 1):
            code = str(ws_value.cell(row, columns["codigo"]).value or "").strip()
            source = normalize_text(ws_value.cell(row, columns["banco"]).value)
            description = str(ws_value.cell(row, columns["descricao"]).value or "").strip()
            if not code:
                continue
            item = {
                "linha": row,
                "item": str(ws_value.cell(row, columns["item"]).value or "").strip(),
                "codigo": code,
                "banco": source,
                "descricao": description,
                "unidade": normalize_unit(ws_value.cell(row, columns["unidade"]).value),
                "falhas": [],
            }
            if PROCESS_NOTE_RE.search(description):
                item["falhas"].append("DESCRICAO_CONTAMINADA")

            if source in {"SINAPI", "ORSE"}:
                releasable, reason = source_is_releasable(source)
                if not releasable:
                    item["falhas"].append(f"FONTE_NAO_LIBERADA: {reason}")
                official = _database_lookup(cur, source, code, regime)
                if not official:
                    item["falhas"].append("CODIGO_INEXISTENTE_NA_FONTE")
                else:
                    if normalize_text(description) != normalize_text(official["descricao"]):
                        item["falhas"].append("DESCRICAO_DIVERGENTE")
                    if item["unidade"] != normalize_unit(official["unidade"]):
                        item["falhas"].append("UNIDADE_DIVERGENTE")
                    try:
                        official_price = money(official["preco"])
                        sheet_price = money(ws_value.cell(row, columns["valor_unit"]).value)
                        if official_price <= 0:
                            item["falhas"].append("PRECO_OFICIAL_ZERO_OU_AUSENTE")
                        elif abs(official_price - sheet_price) > Decimal("0.01"):
                            item["falhas"].append(f"PRECO_DIVERGENTE: base={official_price} planilha={sheet_price}")
                    except InvalidOperation:
                        item["falhas"].append("PRECO_INVALIDO")

            for numeric_key in ("quantidade", "valor_unit", "total"):
                formula_cell = ws_formula.cell(row, columns[numeric_key])
                value_cell = ws_value.cell(row, columns[numeric_key])
                if isinstance(formula_cell.value, str) and formula_cell.value.startswith("=") and value_cell.value is None:
                    item["falhas"].append(f"FORMULA_SEM_CACHE:{numeric_key}")
            try:
                quantity = Decimal(str(ws_value.cell(row, columns["quantidade"]).value))
                unit_price = money(ws_value.cell(row, columns["valor_unit"]).value)
                direct_total = (quantity * unit_price).quantize(Decimal("0.01"))
                if quantity < 0:
                    item["falhas"].append("QUANTIDADE_NEGATIVA")
            except (InvalidOperation, TypeError):
                direct_total = Decimal("0")
                item["falhas"].append("VALOR_NUMERICO_INVALIDO")
            item["custo_direto"] = str(direct_total)
            result["itens"].append(item)
            for failure in item["falhas"]:
                result["falhas"].append({"tipo": failure, "linha": row, "item": item["item"], "codigo": code})
    finally:
        conn.close()

    ranked = sorted(result["itens"], key=lambda entry: Decimal(entry["custo_direto"]), reverse=True)
    direct_sum = sum((Decimal(entry["custo_direto"]) for entry in ranked), Decimal("0"))
    accumulated = Decimal("0")
    faixa_a: list[dict[str, Any]] = []
    min_count = math.ceil(len(ranked) * 0.10) if federal_transfer else 0
    for entry in ranked:
        if direct_sum <= 0:
            break
        if accumulated < direct_sum * Decimal("0.80") or len(faixa_a) < min_count:
            faixa_a.append(entry)
            accumulated += Decimal(entry["custo_direto"])
        else:
            break
    result["custo_direto_total"] = str(direct_sum)
    result["faixa_a"] = faixa_a
    result["cobertura_faixa_a_pct"] = str((accumulated / direct_sum * 100).quantize(Decimal("0.01"))) if direct_sum else "0.00"
    result["gate"] = "LIBERADO" if result["itens"] and not result["falhas"] else "BLOQUEADO"
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("planilha", type=Path)
    parser.add_argument("--regime", required=True, choices=["DESONERADO", "NAO_DESONERADO"])
    parser.add_argument("--federal-transfer", action="store_true")
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()
    if not args.planilha.is_file():
        print(f"[ERRO] Planilha nao encontrada: {args.planilha}", file=sys.stderr)
        return 2
    report = audit_workbook(args.planilha, args.regime, args.federal_transfer)
    payload = json.dumps(report, ensure_ascii=False, indent=2)
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(payload + "\n", encoding="utf-8")
    print(payload)
    return 0 if report["gate"] == "LIBERADO" else 2


if __name__ == "__main__":
    raise SystemExit(main())
