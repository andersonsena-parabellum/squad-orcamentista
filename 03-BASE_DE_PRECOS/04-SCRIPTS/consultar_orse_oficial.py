#!/usr/bin/env python3
"""Busca e armazena, com proveniencia, composicoes oficiais ORSE/CEHOP."""

from __future__ import annotations

import argparse
import json
import re
import sys

from orse_oficial import fetch_composition, search_compositions

for _stream in (sys.stdout, sys.stderr):
    if hasattr(_stream, "reconfigure"):
        _stream.reconfigure(encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("consulta", help="codigo ORSE exato ou trecho da descricao")
    parser.add_argument("--pagina", type=int, default=1)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    try:
        if re.fullmatch(r"\d{1,5}(?:/ORSE)?", args.consulta.strip(), re.IGNORECASE):
            result = fetch_composition(args.consulta)
            if args.json:
                print(json.dumps(result, ensure_ascii=False, indent=2))
            else:
                print(f"[ORSE OFICIAL | SE {result['competencia']}] {result['codigo_exibicao']} — {result['descricao']}")
                print(f"Unidade: {result['unidade']} | Custo ORSE/SE: R$ {result['custo_total_orse_se']:.2f}")
                print(f"Auxiliares: {len(result['composicoes_auxiliares'])} | Insumos detalhados: {len(result['insumos_detalhados'])}")
                print(f"Fonte: {result['proveniencia']['url']}")
                print("LIBERADO COMO PARADIGMA. Preço direto fora de SE depende de autorização e justificativa expressas.")
        else:
            result = search_compositions(args.consulta, args.pagina)
            if args.json:
                print(json.dumps(result, ensure_ascii=False, indent=2))
            else:
                print(f"[ORSE OFICIAL | SE {result['competencia']}] {result['total']} resultado(s); página {result['pagina']}/{result['paginas']}")
                for item in result["resultados"]:
                    print(f"  {item['codigo'].zfill(5)}/ORSE | {item['unidade']} | R$ {item['custo_total_orse_se']:.2f} | {item['descricao']}")
                print("Consulte um código exato para gravar a composição analítica e sua evidência local.")
        return 0
    except Exception as exc:
        print(f"BLOQUEADO: falha na consulta ORSE oficial: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
