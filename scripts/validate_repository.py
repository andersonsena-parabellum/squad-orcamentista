#!/usr/bin/env python3
"""Autodiagnostico do repositorio e da base de precos."""

from __future__ import annotations

import argparse
import json
import re
import sqlite3
from pathlib import Path

from squad_common import PRICE_DB, REPO_ROOT, SOURCE_REGISTRY, load_json, sha256_file, source_is_releasable, utc_now


REQUIRED_SCRIPTS = {
    "simulate_supat_preenvio.py",
    "build_audit_workbook.py",
    "amostrar_codigos.py",
    "iniciar_squad.py",
    "atualizar_estado.py",
    "verify_export_package.py",
    "build_handoff.py",
    "migrate_db_schema.py",
}


def validate() -> dict:
    findings = []
    scripts_dir = REPO_ROOT / "scripts"
    for name in sorted(REQUIRED_SCRIPTS):
        if not (scripts_dir / name).is_file():
            findings.append({"severity": "P0", "type": "SCRIPT_AUSENTE", "detail": name})

    nested_scripts = [
        REPO_ROOT / "03-BASE_DE_PRECOS" / "04-SCRIPTS" / "consultar_composicao.py",
        REPO_ROOT / "03-BASE_DE_PRECOS" / "04-SCRIPTS" / "gerar_indices_md.py",
        REPO_ROOT / "04-BASE_CONHECIMENTO_SUPAT" / "03-SCRIPTS" / "consultar_precedente.py",
        REPO_ROOT / "04-BASE_CONHECIMENTO_SUPAT" / "03-SCRIPTS" / "extrair_pares.py",
        REPO_ROOT / "04-BASE_CONHECIMENTO_SUPAT" / "03-SCRIPTS" / "rodar_calibracao.py",
        REPO_ROOT / "04-BASE_CONHECIMENTO_SUPAT" / "03-SCRIPTS" / "inventariar_corpus.py",
        REPO_ROOT / "04-BASE_CONHECIMENTO_SUPAT" / "03-SCRIPTS" / "compilar_precedentes_json.py",
    ]
    for path in nested_scripts:
        if not path.is_file():
            findings.append({"severity": "P0", "type": "SCRIPT_AUSENTE", "detail": str(path.relative_to(REPO_ROOT))})

    precedent_registry = REPO_ROOT / "04-BASE_CONHECIMENTO_SUPAT" / "FONTES_PRECEDENTES.json"
    if not precedent_registry.is_file():
        findings.append({"severity": "P0", "type": "REGISTRO_PRECEDENTES_AUSENTE", "detail": str(precedent_registry)})
    else:
        precedent_status = load_json(precedent_registry).get("status")
        if precedent_status != "LIBERADA":
            findings.append({"severity": "P0", "type": "PRECEDENTES_NAO_LIBERADOS", "detail": precedent_status})

    if not SOURCE_REGISTRY.is_file():
        findings.append({"severity": "P0", "type": "REGISTRO_FONTES_AUSENTE", "detail": str(SOURCE_REGISTRY)})
    else:
        registry = load_json(SOURCE_REGISTRY)
        for source, record in registry.get("fontes", {}).items():
            released, reason = source_is_releasable(source)
            if not released:
                findings.append({"severity": "P0", "type": "FONTE_NAO_LIBERADA", "detail": f"{source}: {reason}"})

    if not PRICE_DB.is_file():
        findings.append({"severity": "P0", "type": "BASE_AUSENTE", "detail": str(PRICE_DB)})
    else:
        expected_db_hash = load_json(SOURCE_REGISTRY).get("database", {}).get("sha256") if SOURCE_REGISTRY.is_file() else None
        if not expected_db_hash or sha256_file(PRICE_DB) != expected_db_hash:
            findings.append({"severity": "P0", "type": "HASH_SQLITE_DIVERGENTE", "detail": "Atualize somente por migração/importação controlada"})
        conn = sqlite3.connect(f"file:{PRICE_DB.as_posix()}?mode=ro", uri=True)
        try:
            integrity = conn.execute("PRAGMA integrity_check").fetchone()[0]
            if integrity != "ok":
                findings.append({"severity": "P0", "type": "SQLITE_CORROMPIDO", "detail": integrity})
            pk_columns = [row[1] for row in sorted((row for row in conn.execute("PRAGMA table_info(composicoes)") if row[5]), key=lambda row: row[5])]
            if pk_columns != ["fonte", "codigo"]:
                findings.append({"severity": "P0", "type": "CHAVE_COMPOSICOES_INSEGURA", "detail": pk_columns})
            checks = {
                "COMPOSICOES_PRECO_ZERO": "SELECT count(*) FROM composicoes WHERE custo_deson<=0 OR custo_nao_deson<=0",
                "INSUMOS_PRECO_ZERO": "SELECT count(*) FROM insumos WHERE preco_deson<=0 OR preco_nao_deson<=0",
                "COEFICIENTES_NAO_POSITIVOS": "SELECT count(*) FROM composicao_itens WHERE coeficiente IS NULL OR coeficiente<=0",
                "ORFAOS_INSUMO_POR_FONTE": "SELECT count(*) FROM composicao_itens ci LEFT JOIN insumos i ON i.fonte=ci.fonte AND i.codigo=ci.codigo_item WHERE ci.tipo_item='INSUMO' AND i.codigo IS NULL",
                "ORFAOS_COMPOSICAO_POR_FONTE": "SELECT count(*) FROM composicao_itens ci LEFT JOIN composicoes c ON c.fonte=ci.fonte AND c.codigo=ci.codigo_item WHERE ci.tipo_item<>'INSUMO' AND c.codigo IS NULL",
                "ORSE_DESCRICAO_GENERICA": "SELECT count(*) FROM composicoes WHERE fonte='ORSE' AND descricao LIKE '%especificação analítica%execução técnica especializada%'",
            }
            for finding_type, query in checks.items():
                count = conn.execute(query).fetchone()[0]
                if count:
                    findings.append({"severity": "P0" if finding_type.startswith(("ORFAOS", "ORSE")) else "P1", "type": finding_type, "detail": count})
        finally:
            conn.close()

    cpu_map = REPO_ROOT / "03-BASE_DE_PRECOS" / "03-CPU_PROPRIAS" / "MAPA_CPU_PROPRIAS.md"
    if cpu_map.exists():
        content = cpu_map.read_text(encoding="utf-8")
        for link in re.findall(r"\(([^)]+\.md)\)", content):
            linked = (cpu_map.parent / link).resolve()
            if not linked.exists():
                findings.append({"severity": "P1", "type": "CPU_FICHA_AUSENTE", "detail": link})

    return {"schema_version": "1.0.0", "generated_at": utc_now(), "gate": "LIBERADO" if not findings else "BLOQUEADO", "findings": findings}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()
    report = validate()
    payload = json.dumps(report, ensure_ascii=False, indent=2)
    if args.out:
        args.out.write_text(payload + "\n", encoding="utf-8")
    print(payload)
    return 0 if report["gate"] == "LIBERADO" else 2


if __name__ == "__main__":
    raise SystemExit(main())
