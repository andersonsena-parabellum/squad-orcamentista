#!/usr/bin/env python3
"""Gate PRE-ENVIO SUPAT/SAEB com verificacoes mecanicas e evidencias humanas.

O script nunca converte ausencia de evidencia em conformidade. Os itens que
dependem de julgamento de engenharia exigem um JSON de evidencias assinado.
"""

from __future__ import annotations

import argparse
import json
import re
import statistics
import sys
from datetime import date, datetime
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any

import openpyxl

from amostrar_codigos import audit_workbook
from squad_common import load_json, money, normalize_text, sha256_file, utc_now


DC_RE = {number: re.compile(rf"DC[-_ ]?00{number}(?!\d)", re.IGNORECASE) for number in range(1, 8)}
REQUIRED_HUMAN_ITEMS = {f"ITEM {number:02d}" for number in range(1, 11)}


def valid_cnpj(value: Any) -> bool:
    digits = re.sub(r"\D", "", str(value or ""))
    if len(digits) != 14 or digits == digits[0] * 14:
        return False
    numbers = [int(char) for char in digits]
    for length, weights in ((12, [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]), (13, [6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2])):
        remainder = sum(numbers[index] * weights[index] for index in range(length)) % 11
        digit = 0 if remainder < 2 else 11 - remainder
        if numbers[length] != digit:
            return False
    return True


def discover_pieces(target: Path) -> tuple[dict[str, Path | None], list[dict[str, Any]]]:
    pieces: dict[str, Path | None] = {}
    findings: list[dict[str, Any]] = []
    candidates = [path for path in target.rglob("*.xlsx") if not path.name.startswith("~$") and "ENVIO" not in {part.upper() for part in path.parts}]
    for number, pattern in DC_RE.items():
        key = f"DC-00{number}"
        matches = [path for path in candidates if pattern.search(path.name)]
        if len(matches) == 1:
            pieces[key] = matches[0]
        elif not matches:
            pieces[key] = None
            findings.append({"item": key, "tipo": "PECA_AUSENTE", "mensagem": f"{key} XLSX nao localizado"})
        else:
            pieces[key] = None
            findings.append({"item": key, "tipo": "PECA_AMBIGUA", "mensagem": f"{len(matches)} candidatos: {[str(p) for p in matches]}"})
    return pieces, findings


def _header_map(ws: Any, aliases: dict[str, tuple[str, ...]]) -> tuple[int | None, dict[str, int]]:
    for row in range(1, min(ws.max_row, 30) + 1):
        values = [normalize_text(ws.cell(row, col).value) for col in range(1, min(ws.max_column, 30) + 1)]
        mapping: dict[str, int] = {}
        for key, names in aliases.items():
            for col, value in enumerate(values, 1):
                if any(name in value for name in names):
                    mapping[key] = col
                    break
        if len(mapping) == len(aliases):
            return row, mapping
    return None, {}


def budget_total(path: Path) -> tuple[Decimal | None, list[str]]:
    wb_formula = openpyxl.load_workbook(path, data_only=False)
    wb_value = openpyxl.load_workbook(path, data_only=True)
    ws_f, ws_v = wb_formula.active, wb_value[wb_formula.active.title]
    row, cols = _header_map(ws_f, {"codigo": ("CODIGO", "CÓDIGO"), "total": ("TOTAL",)})
    if not row:
        return None, ["Cabecalho Codigo/Total nao localizado no DC-001"]
    total = Decimal("0")
    failures = []
    service_rows = 0
    for index in range(row + 1, ws_f.max_row + 1):
        code = str(ws_v.cell(index, cols["codigo"]).value or "").strip()
        if not code:
            continue
        service_rows += 1
        formula = ws_f.cell(index, cols["total"]).value
        value = ws_v.cell(index, cols["total"]).value
        if isinstance(formula, str) and formula.startswith("=") and value is None:
            failures.append(f"Formula sem cache no total da linha {index}")
            continue
        try:
            total += money(value)
        except InvalidOperation:
            failures.append(f"Total invalido na linha {index}")
    if not service_rows:
        failures.append("Nenhuma linha de servico com codigo no DC-001")
    return total.quantize(Decimal("0.01")), failures


def schedule_total(path: Path) -> tuple[Decimal | None, list[str]]:
    wb_formula = openpyxl.load_workbook(path, data_only=False)
    wb_value = openpyxl.load_workbook(path, data_only=True)
    ws_f, ws_v = wb_formula.active, wb_value[wb_formula.active.title]
    labels = ("TOTAL GERAL", "TOTAL FINANCEIRO", "VALOR TOTAL")
    failures = []
    for row in range(1, ws_f.max_row + 1):
        for col in range(1, ws_f.max_column + 1):
            if not any(label in normalize_text(ws_v.cell(row, col).value) for label in labels):
                continue
            for candidate_col in range(col + 1, ws_f.max_column + 1):
                formula = ws_f.cell(row, candidate_col).value
                value = ws_v.cell(row, candidate_col).value
                if isinstance(formula, str) and formula.startswith("=") and value is None:
                    failures.append(f"Formula sem cache no cronograma: {ws_f.cell(row, candidate_col).coordinate}")
                    continue
                try:
                    candidate = money(value)
                except (InvalidOperation, TypeError):
                    continue
                if candidate > 0:
                    return candidate, failures
    failures.append("Total financeiro nao localizado ou igual a zero no DC-004")
    return None, failures


def audit_quotes(path: Path) -> list[dict[str, Any]]:
    wb = openpyxl.load_workbook(path, data_only=True)
    ws = wb.active
    aliases = {
        "item": ("ITEM",),
        "spec": ("ESPECIFICACAO", "ESPECIFICAÇÃO", "SPEC ANCORA", "SPEC ÂNCORA"),
        "supplier": ("FORNECEDOR", "RAZAO SOCIAL", "RAZÃO SOCIAL"),
        "cnpj": ("CNPJ",),
        "date": ("DATA",),
        "price": ("PRECO FOB", "PREÇO FOB", "VALOR FOB"),
        "median": ("MEDIANA",),
    }
    row, cols = _header_map(ws, aliases)
    if not row:
        return [{"item": "ITEM 04", "tipo": "LAYOUT_DC007_INVALIDO", "mensagem": "As 7 colunas Item, Especificacao, Fornecedor, CNPJ, Data, Preco FOB e Mediana sao obrigatorias"}]
    groups: dict[str, list[dict[str, Any]]] = {}
    for index in range(row + 1, ws.max_row + 1):
        item = str(ws.cell(index, cols["item"]).value or "").strip()
        if not item:
            continue
        groups.setdefault(item, []).append({key: ws.cell(index, col).value for key, col in cols.items()})
    failures = []
    for item, rows in groups.items():
        cnpjs = {re.sub(r"\D", "", str(row_data["cnpj"] or "")) for row_data in rows}
        cnpjs.discard("")
        suppliers = {normalize_text(row_data["supplier"]) for row_data in rows if normalize_text(row_data["supplier"])}
        specs = {normalize_text(row_data["spec"]) for row_data in rows if normalize_text(row_data["spec"])}
        prices = []
        dates = []
        for row_data in rows:
            try:
                prices.append(money(row_data["price"]))
            except InvalidOperation:
                pass
            raw_date = row_data["date"]
            if isinstance(raw_date, datetime):
                dates.append(raw_date.date())
            elif isinstance(raw_date, date):
                dates.append(raw_date)
        if len(cnpjs) < 3 or len(suppliers) < 3 or len(prices) < 3:
            failures.append({"item": item, "tipo": "COTACOES_INSUFICIENTES", "mensagem": f"fornecedores={len(suppliers)}, CNPJs={len(cnpjs)}, precos={len(prices)}"})
            continue
        invalid_cnpjs = sorted(cnpj for cnpj in cnpjs if not valid_cnpj(cnpj))
        if invalid_cnpjs:
            failures.append({"item": item, "tipo": "CNPJ_INVALIDO", "mensagem": str(invalid_cnpjs)})
        if len(specs) != 1:
            failures.append({"item": item, "tipo": "ANCORA_TECNICA_DIVERGENTE", "mensagem": f"Especificacoes distintas={len(specs)}"})
        expected = Decimal(str(statistics.median(prices))).quantize(Decimal("0.01"))
        adopted_values = set()
        for row_data in rows:
            try:
                adopted_values.add(money(row_data["median"]))
            except InvalidOperation:
                pass
        if adopted_values != {expected}:
            failures.append({"item": item, "tipo": "MEDIANA_DIVERGENTE", "mensagem": f"Esperada={expected}; informadas={sorted(str(v) for v in adopted_values)}"})
        if len(dates) < 3 or any((date.today() - quote_date).days > 180 or quote_date > date.today() for quote_date in dates):
            failures.append({"item": item, "tipo": "DATA_COTACAO_INVALIDA", "mensagem": "Cotacoes devem estar entre hoje e 180 dias"})
    if not groups:
        failures.append({"item": "ITEM 04", "tipo": "DC007_SEM_ITENS", "mensagem": "Use folha N/A formal quando nao houver cotacao"})
    return failures


def human_checkpoints(evidence_path: Path | None) -> list[dict[str, Any]]:
    findings = []
    evidence = load_json(evidence_path) if evidence_path and evidence_path.exists() else {}
    checkpoints = evidence.get("checkpoints", {})
    for item in sorted(REQUIRED_HUMAN_ITEMS):
        checkpoint = checkpoints.get(item)
        if not checkpoint:
            findings.append({"item": item, "tipo": "EVIDENCIA_HUMANA_AUSENTE", "mensagem": "Checkpoint assinado nao informado"})
            continue
        status = normalize_text(checkpoint.get("status"))
        if status != "CONFORME":
            findings.append({"item": item, "tipo": "CHECKPOINT_NAO_CONFORME", "mensagem": status or "SEM STATUS"})
        if not checkpoint.get("responsavel") or not checkpoint.get("evidencias"):
            findings.append({"item": item, "tipo": "CHECKPOINT_SEM_RASTREABILIDADE", "mensagem": "Responsavel e evidencias sao obrigatorios"})
    return findings


def run(args: argparse.Namespace) -> dict[str, Any]:
    target = args.pasta.resolve()
    report: dict[str, Any] = {"schema_version": "1.0.0", "generated_at": utc_now(), "target": str(target), "findings": [], "pieces": {}, "checklist": []}
    pieces, discovery_findings = discover_pieces(target)
    report["findings"].extend(discovery_findings)
    report["pieces"] = {key: ({"path": str(path), "sha256": sha256_file(path)} if path else None) for key, path in pieces.items()}

    if pieces.get("DC-001"):
        code_audit = audit_workbook(pieces["DC-001"], args.regime, args.federal_transfer)
        report["code_audit"] = code_audit
        report["findings"].extend({"item": "ITEM 02", "tipo": failure["tipo"], "mensagem": f"Linha {failure.get('linha')}: {failure.get('codigo', '')}"} for failure in code_audit["falhas"])
        total_budget, failures = budget_total(pieces["DC-001"])
        report["total_orcamento"] = str(total_budget) if total_budget is not None else None
        report["findings"].extend({"item": "ITEM 01", "tipo": "DC001_INVALIDO", "mensagem": message} for message in failures)
    else:
        total_budget = None

    if pieces.get("DC-004"):
        total_schedule, failures = schedule_total(pieces["DC-004"])
        report["total_cronograma"] = str(total_schedule) if total_schedule is not None else None
        report["findings"].extend({"item": "ITEM 05", "tipo": "CRONOGRAMA_INVALIDO", "mensagem": message} for message in failures)
        if total_budget is None or total_schedule is None or total_budget != total_schedule:
            report["findings"].append({"item": "ITEM 05", "tipo": "ORCAMENTO_DIFERE_CRONOGRAMA", "mensagem": f"Orcamento={total_budget}; Cronograma={total_schedule}"})

    if pieces.get("DC-007"):
        report["findings"].extend(audit_quotes(pieces["DC-007"]))

    human_findings = human_checkpoints(args.evidencias)
    report["findings"].extend(human_findings)
    if report["findings"]:
        report["gate"] = "BLOQUEADO"
    else:
        report["gate"] = "PRE_LIBERADO"
    report["technical_conformity_pct"] = "100.00" if not report["findings"] else "0.00"
    return report


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("pasta", type=Path)
    parser.add_argument("--regime", required=True, choices=["DESONERADO", "NAO_DESONERADO"])
    parser.add_argument("--federal-transfer", action="store_true")
    parser.add_argument("--evidencias", type=Path, help="JSON com checkpoints humanos ITEM 02/03/06/08/09/10")
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--xlsx", type=Path)
    args = parser.parse_args()
    if not args.pasta.is_dir():
        print(f"[BLOQUEADO] Pasta nao encontrada: {args.pasta}", file=sys.stderr)
        return 2
    report = run(args)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if args.xlsx:
        from build_audit_workbook import build_workbook
        build_workbook(report, args.xlsx)
    print(json.dumps({"gate": report["gate"], "findings": len(report["findings"]), "out": str(args.out)}, ensure_ascii=False))
    return 0 if report["gate"] == "PRE_LIBERADO" else 2


if __name__ == "__main__":
    raise SystemExit(main())
