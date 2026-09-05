#!/usr/bin/env python3
"""Regenera índices Markdown somente a partir de fontes liberadas e identificadas."""

from __future__ import annotations

import argparse
import json
import sqlite3
import sys
from collections import defaultdict
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]
DB_PATH = BASE_DIR / "base_precos.db"
REGISTRY_PATH = BASE_DIR / "FONTES_DADOS.json"
OUT_DIR = BASE_DIR / "01-DISCIPLINAS_MARKDOWN"

for _stream in (sys.stdout, sys.stderr):
    if hasattr(_stream, "reconfigure"):
        _stream.reconfigure(encoding="utf-8")

DISCIPLINES = {
    1: ("SERVIÇOS PRELIMINARES", ("demoli", "remoção", "canteiro", "locação")),
    2: ("INFRAESTRUTURA E FUNDAÇÕES", ("fundação", "estaca", "sapata", "escavação", "reaterro")),
    3: ("ESTRUTURAS", ("armação", "concreto", "estrutura metálica", "laje", "forma")),
    4: ("PAREDES E PAINÉIS", ("alvenaria", "drywall", "divisória", "verga", "contraverga")),
    5: ("ESQUADRIAS E VIDROS", ("porta", "janela", "esquadria", "vidro", "brise")),
    6: ("COBERTURAS", ("cobertura", "telha", "trama", "rufo", "calha")),
    7: ("IMPERMEABILIZAÇÕES", ("impermeabil", "manta asfáltica", "hidrofugante")),
    8: ("REVESTIMENTOS", ("chapisco", "emboço", "reboco", "revestimento cerâmico", "forro")),
    9: ("PAVIMENTAÇÕES E PISOS", ("contrapiso", "piso", "intertravado", "pavimentação")),
    10: ("HIDROSSANITÁRIO", ("água fria", "esgoto", "hidrául", "sanitár", "caixa sifonada")),
    11: ("ELÉTRICA E TELECOM", ("elétric", "eletroduto", "cabo", "quadro", "luminária", "telecom")),
    12: ("SPDA E INCÊNDIO", ("spda", "descarga atmosférica", "hidrante", "extintor", "incêndio")),
    13: ("PINTURAS", ("pintura", "tinta", "selador", "verniz")),
    14: ("PAISAGISMO E COMPLEMENTARES", ("paisag", "grama", "plantio", "alambrado", "mobiliário")),
    15: ("URBANIZAÇÃO E VIAS", ("asfalto", "sarjeta", "meio-fio", "bueiro", "sinalização viária")),
}


def classify(group: str, description: str) -> int:
    haystack = f"{group} {description}".casefold()
    scores = {key: sum(term.casefold() in haystack for term in terms) for key, (_, terms) in DISCIPLINES.items()}
    best = max(scores, key=scores.get)
    return best if scores[best] else 1


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--fonte", required=True, choices=("SINAPI", "ORSE"))
    args = parser.parse_args()
    registry = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))
    record = registry.get("fontes", {}).get(args.fonte, {})
    if str(record.get("status", "")).upper() != "LIBERADA":
        print(f"BLOQUEADO: {args.fonte} não está LIBERADA.", file=sys.stderr)
        return 2
    price_capability = record.get("capacidades", {}).get("preco_direto")
    price_status = price_capability.get("status") if isinstance(price_capability, dict) else price_capability
    if str(price_status).upper() != "LIBERADA":
        print(f"BLOQUEADO: {args.fonte} não está liberada para índice de preço direto.", file=sys.stderr)
        if args.fonte == "ORSE":
            print("Use consultar_orse_oficial.py para paradigma e referência SE.", file=sys.stderr)
        return 2

    buckets: dict[int, list[sqlite3.Row]] = defaultdict(list)
    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        rows = conn.execute(
            "SELECT fonte,codigo,descricao,unidade,grupo,custo_deson,custo_nao_deson "
            "FROM composicoes WHERE fonte=? ORDER BY codigo",
            (args.fonte,),
        ).fetchall()
    for row in rows:
        buckets[classify(row["grupo"] or "", row["descricao"] or "")].append(row)

    source_out = OUT_DIR / args.fonte
    source_out.mkdir(parents=True, exist_ok=True)
    generated = []
    for number, (title, _) in DISCIPLINES.items():
        path = source_out / f"{number:02d}_{title.replace(' ', '_').replace('/', '_')}.md"
        lines = [f"# {number:02d} — {title}", "", f"Fonte: `{args.fonte}` | Competência: `{record.get('competencia')}`", "", "| Código | Descrição | Un | Deson. | Não deson. |", "|---|---|---:|---:|---:|"]
        for row in buckets[number]:
            lines.append(f"| `{row['codigo']}` | {row['descricao']} | {row['unidade']} | {row['custo_deson']} | {row['custo_nao_deson']} |")
        path.write_text("\n".join(lines) + "\n", encoding="utf-8")
        generated.append(path.name)
    (source_out / "MAPA_COMPOSICOES.md").write_text(
        "# Mapa de composições\n\n" + "\n".join(f"- [{name}]({name})" for name in generated) + "\n",
        encoding="utf-8",
    )
    print(f"Gerados {len(generated)} índices de {args.fonte} em {source_out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
