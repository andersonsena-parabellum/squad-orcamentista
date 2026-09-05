#!/usr/bin/env python3
"""Consulta os modelos de CPU própria catalogados e suas ressalvas."""

from __future__ import annotations

import argparse
import json
import sys
import unicodedata
from pathlib import Path


CATALOG = Path(__file__).resolve().parents[1] / "03-CPU_PROPRIAS" / "CATALOGO_CPU_PROPRIAS.json"

for _stream in (sys.stdout, sys.stderr):
    if hasattr(_stream, "reconfigure"):
        _stream.reconfigure(encoding="utf-8")


def normalized(value: str) -> str:
    return "".join(char for char in unicodedata.normalize("NFKD", value).upper() if not unicodedata.combining(char))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("consulta", help="código exato ou trecho da descrição")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    if not CATALOG.is_file():
        print(f"BLOQUEADO: catálogo ausente: {CATALOG}", file=sys.stderr)
        return 2
    catalog = json.loads(CATALOG.read_text(encoding="utf-8"))
    needle = normalized(args.consulta)
    results = [cpu for cpu in catalog.get("composicoes", []) if normalized(cpu["codigo"]) == needle or needle in normalized(cpu["descricao"])]
    if args.json:
        print(json.dumps(results, ensure_ascii=False, indent=2))
    else:
        for cpu in results[:20]:
            print(f"[{cpu['uso_como_modelo']}] {cpu['codigo']} | {cpu['unidade']} | {cpu['descricao']}")
            print(f"  {len(cpu['itens'])} item(ns) | uso direto: {cpu['uso_direto']} | preço: {cpu['preco']}")
            for note in cpu["validacoes_pendentes"]:
                print(f"  - {note}")
        if len(results) > 20:
            print(f"... mais {len(results) - 20} resultado(s)")
    return 0 if results else 1


if __name__ == "__main__":
    raise SystemExit(main())
