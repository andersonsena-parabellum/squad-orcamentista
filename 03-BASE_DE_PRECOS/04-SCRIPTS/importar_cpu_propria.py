#!/usr/bin/env python3
"""Importa CPUs historicas como modelos estruturais, nunca como preco vigente."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


BASE_DIR = Path(__file__).resolve().parents[1]
CPU_DIR = BASE_DIR / "03-CPU_PROPRIAS"
ORIGINALS_DIR = CPU_DIR / "_ORIGINAIS"
CATALOG_PATH = CPU_DIR / "CATALOGO_CPU_PROPRIAS.json"
REGISTRY_PATH = BASE_DIR / "FONTES_DADOS.json"
PROCESS_RE = re.compile(r"\b(A COTAR|CÓDIGO A CRAVAR|NAO INVENTAR|NÃO INVENTAR|PENDENTE|MENOR PREÇO|3 FORNECEDORES)\b", re.IGNORECASE)

for _stream in (sys.stdout, sys.stderr):
    if hasattr(_stream, "reconfigure"):
        _stream.reconfigure(encoding="utf-8")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def canonical(item: dict[str, Any]) -> str:
    return json.dumps(item, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def validate_cpu(cpu: dict[str, Any]) -> list[str]:
    failures = []
    for field in ("code", "description", "unit", "items"):
        if not cpu.get(field):
            failures.append(f"CAMPO_AUSENTE:{field}")
    if not isinstance(cpu.get("items"), list):
        return failures
    for index, item in enumerate(cpu["items"], 1):
        for field in ("type", "code", "bank", "description", "unit", "coefficient"):
            if item.get(field) in (None, ""):
                failures.append(f"ITEM_{index}_CAMPO_AUSENTE:{field}")
        try:
            if float(item.get("coefficient", 0)) <= 0:
                failures.append(f"ITEM_{index}_COEFICIENTE_NAO_POSITIVO")
        except (TypeError, ValueError):
            failures.append(f"ITEM_{index}_COEFICIENTE_INVALIDO")
    return failures


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("arquivo", type=Path, help="JSON contendo uma lista de CPUs")
    parser.add_argument("--projeto", required=True, help="identificador legivel do projeto de origem")
    parser.add_argument("--revisao", required=True, help="revisao do artefato de origem")
    args = parser.parse_args()
    if not args.arquivo.is_file():
        print(f"BLOQUEADO: arquivo ausente: {args.arquivo}", file=sys.stderr)
        return 2
    raw = json.loads(args.arquivo.read_text(encoding="utf-8"))
    if not isinstance(raw, list):
        print("BLOQUEADO: o JSON deve conter uma lista de CPUs", file=sys.stderr)
        return 2

    by_code: dict[str, dict[str, Any]] = {}
    duplicates = 0
    for cpu in raw:
        if not isinstance(cpu, dict):
            print("BLOQUEADO: registro de CPU não é objeto", file=sys.stderr)
            return 2
        code = str(cpu.get("code", "")).strip()
        failures = validate_cpu(cpu)
        if failures:
            print(f"BLOQUEADO: CPU {code or '?'} inválida: {', '.join(failures)}", file=sys.stderr)
            return 2
        if code in by_code:
            if canonical(cpu) != canonical(by_code[code]):
                print(f"BLOQUEADO: código duplicado com conteúdo divergente: {code}", file=sys.stderr)
                return 2
            duplicates += 1
            continue
        by_code[code] = cpu

    source_hash = sha256(args.arquivo)
    ORIGINALS_DIR.mkdir(parents=True, exist_ok=True)
    destination = ORIGINALS_DIR / f"{source_hash[:12]}-{args.arquivo.name}"
    if not destination.exists():
        shutil.copy2(args.arquivo, destination)

    entries = []
    for code, cpu in sorted(by_code.items()):
        own_inputs = any(str(item.get("bank", "")).upper() in {"PRÓPRIO", "PROPRIO", "FPE", "COT"} for item in cpu["items"])
        notes = []
        if PROCESS_RE.search(str(cpu["description"])):
            notes.append("DESCRICAO_CONTEM_NOTA_DE_PROCESSO_SANITIZAR")
        if own_inputs:
            notes.append("INSUMOS_PROPRIOS_EXIGEM_FONTE_DE_PRECO_ATUAL")
        notes.append("COEFICIENTES_EXIGEM_CONFIRMACAO_NO_PROJETO_E_PARADIGMA")
        entries.append(
            {
                "codigo": code,
                "descricao": cpu["description"],
                "unidade": cpu["unit"],
                "referencia_declarada": cpu.get("reference"),
                "itens": cpu["items"],
                "uso_como_modelo": "LIBERADO",
                "uso_direto": "BLOQUEADO_ATE_REVALIDACAO",
                "preco": "RECALCULAR_NA_DATA_BASE_DA_OBRA",
                "validacoes_pendentes": notes,
                "origem": {
                    "projeto": args.projeto,
                    "revisao": args.revisao,
                    "arquivo": str(destination.relative_to(BASE_DIR)).replace("\\", "/"),
                    "sha256": source_hash,
                },
            }
        )
    previous = []
    if CATALOG_PATH.is_file():
        previous = json.loads(CATALOG_PATH.read_text(encoding="utf-8")).get("composicoes", [])
    preserved = [entry for entry in previous if entry.get("origem", {}).get("sha256") != source_hash]
    combined = sorted(preserved + entries, key=lambda entry: (entry["codigo"], entry["origem"]["sha256"]))
    payload = {
        "schema_version": "1.1.0",
        "gerado_em": datetime.now(timezone.utc).isoformat(),
        "politica": "Modelos históricos ajudam a montar CPUs, mas descrição, unidade, coeficientes, perdas e preços devem ser revalidados para cada obra.",
        "contagens": {"modelos": len(combined), "fontes_importadas": len({entry["origem"]["sha256"] for entry in combined}), "duplicatas_identicas_ignoradas_na_ultima_importacao": duplicates},
        "composicoes": combined,
    }
    CATALOG_PATH.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    registry = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))
    registry["fontes"]["CPU_PROPRIA"]["sha256_origem"] = sha256(CATALOG_PATH)
    temporary = REGISTRY_PATH.with_name(f".{REGISTRY_PATH.name}.{os.getpid()}.tmp")
    temporary.write_text(json.dumps(registry, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    os.replace(temporary, REGISTRY_PATH)
    print(f"{len(entries)} modelo(s) estrutural(is) importado(s); catálogo total: {len(combined)}; {duplicates} duplicata(s) idêntica(s) ignorada(s).")
    print("Preços e uso direto permanecem bloqueados até revalidação por obra.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
