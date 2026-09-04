#!/usr/bin/env python3
"""Localiza precedentes sem promover inferências internas a regra oficial."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]
REGISTRY = BASE_DIR / "FONTES_PRECEDENTES.json"

for _stream in (sys.stdout, sys.stderr):
    if hasattr(_stream, "reconfigure"):
        _stream.reconfigure(encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("consulta")
    parser.add_argument("--limit", type=int, default=10)
    parser.add_argument("--diagnostico", action="store_true")
    args = parser.parse_args()
    registry = json.loads(REGISTRY.read_text(encoding="utf-8"))
    status = str(registry.get("status", "AUSENTE")).upper()
    if status != "LIBERADA" and not args.diagnostico:
        print(f"BLOQUEADO: corpus com status {status}. {registry.get('motivo', '')}", file=sys.stderr)
        return 2
    data_path = BASE_DIR / registry["arquivo"]
    records = json.loads(data_path.read_text(encoding="utf-8"))
    if isinstance(records, dict):
        records = records.get("casos", [])
    query = args.consulta.casefold().strip()
    matches = []
    for record in records:
        fields = ("tema", "texto_ressalva", "resposta_fpe", "orgao", "pcode", "arquivo_origem")
        haystack = " ".join(str(record.get(field, "")) for field in fields).casefold()
        if query in haystack:
            matches.append(record)
    label = "DIAGNÓSTICO — CORPUS NÃO LIBERADO" if status != "LIBERADA" else "CORPUS LIBERADO"
    print(f"[{label}] {len(matches)} resultado(s); exibindo {min(len(matches), max(args.limit, 0))}.")
    for index, record in enumerate(matches[: max(args.limit, 0)], 1):
        print(f"\n[{index}] {record.get('orgao', 'N/I')} | {record.get('pcode', 'N/I')} | {record.get('tema', 'N/I')}")
        print(f"Fonte declarada: {record.get('arquivo_origem', 'N/I')} | revisão {record.get('revisao_analise', 'N/I')}")
        print(f"ANALISTA (não verificado): {record.get('texto_ressalva', '')}")
        print(f"RESPOSTA FPE (não é regra do órgão): {record.get('resposta_fpe', '')}")
        print(f"INFERÊNCIA INTERNA (não oficial): {record.get('acao_auditor', '')}")
    return 0 if status == "LIBERADA" else 2


if __name__ == "__main__":
    raise SystemExit(main())
