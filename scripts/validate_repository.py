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
    "importar_sinapi.py",
    "quarentenar_orse_legada.py",
}


def validate() -> dict:
    findings = []
    scripts_dir = REPO_ROOT / "scripts"
    for name in sorted(REQUIRED_SCRIPTS):
        if not (scripts_dir / name).is_file():
            findings.append({"severity": "P0", "type": "SCRIPT_AUSENTE", "detail": name})

    nested_scripts = [
        REPO_ROOT / "03-BASE_DE_PRECOS" / "04-SCRIPTS" / "consultar_composicao.py",
        REPO_ROOT / "03-BASE_DE_PRECOS" / "04-SCRIPTS" / "consultar_orse_oficial.py",
        REPO_ROOT / "03-BASE_DE_PRECOS" / "04-SCRIPTS" / "orse_oficial.py",
        REPO_ROOT / "03-BASE_DE_PRECOS" / "04-SCRIPTS" / "importar_cpu_propria.py",
        REPO_ROOT / "03-BASE_DE_PRECOS" / "04-SCRIPTS" / "consultar_cpu_propria.py",
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
            findings.append({"severity": "P1", "type": "PRECEDENTES_NAO_LIBERADOS", "detail": precedent_status})

    if not SOURCE_REGISTRY.is_file():
        findings.append({"severity": "P0", "type": "REGISTRO_FONTES_AUSENTE", "detail": str(SOURCE_REGISTRY)})
    else:
        registry = load_json(SOURCE_REGISTRY)
        released_sources = []
        for source, record in registry.get("fontes", {}).items():
            released, reason = source_is_releasable(source)
            if released:
                released_sources.append(source)
            else:
                findings.append({"severity": "P1", "type": "FONTE_NAO_LIBERADA", "detail": f"{source}: {reason}"})
        if not released_sources:
            findings.append({"severity": "P0", "type": "NENHUMA_FONTE_DE_PRECOS_LIBERADA", "detail": "O núcleo de precificação está indisponível"})

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
            released = []
            if SOURCE_REGISTRY.is_file():
                for source in load_json(SOURCE_REGISTRY).get("fontes", {}):
                    if source_is_releasable(source, "preco_direto")[0]:
                        released.append(source)
            placeholders = ",".join("?" for _ in released) or "''"
            checks = {
                "COMPOSICOES_SEM_PRECO_NA_UF": ("P1", "SELECT count(*) FROM composicoes WHERE fonte IN (" + placeholders + ") AND (custo_deson IS NULL OR custo_deson<=0 OR custo_nao_deson IS NULL OR custo_nao_deson<=0)", released),
                "INSUMOS_SEM_PRECO_NA_UF": ("P1", "SELECT count(*) FROM insumos WHERE fonte IN (" + placeholders + ") AND (preco_deson IS NULL OR preco_deson<=0 OR preco_nao_deson IS NULL OR preco_nao_deson<=0)", released),
                "COEFICIENTES_NAO_POSITIVOS": ("P1", "SELECT count(*) FROM composicao_itens WHERE fonte IN (" + placeholders + ") AND (coeficiente IS NULL OR coeficiente<=0)", released),
                "ORFAOS_INSUMO_FONTE_LIBERADA": ("P0", "SELECT count(*) FROM composicao_itens ci LEFT JOIN insumos i ON i.fonte=ci.fonte AND i.codigo=ci.codigo_item WHERE ci.fonte IN (" + placeholders + ") AND ci.tipo_item='INSUMO' AND i.codigo IS NULL", released),
                "ORFAOS_COMPOSICAO_FONTE_LIBERADA": ("P0", "SELECT count(*) FROM composicao_itens ci LEFT JOIN composicoes c ON c.fonte=ci.fonte AND c.codigo=ci.codigo_item WHERE ci.fonte IN (" + placeholders + ") AND ci.tipo_item<>'INSUMO' AND c.codigo IS NULL", released),
                "ORSE_OFICIAL_CONTAMINADA_POR_CARGA_GENERICA": ("P0", "SELECT count(*) FROM composicoes WHERE fonte='ORSE' AND descricao LIKE '%especificação analítica%execução técnica especializada%'", []),
            }
            for finding_type, (severity, query, params) in checks.items():
                count = conn.execute(query, params).fetchone()[0]
                if count:
                    findings.append({"severity": severity, "type": finding_type, "detail": count})
        finally:
            conn.close()

    cpu_map = REPO_ROOT / "03-BASE_DE_PRECOS" / "03-CPU_PROPRIAS" / "MAPA_CPU_PROPRIAS.md"
    if cpu_map.exists():
        content = cpu_map.read_text(encoding="utf-8")
        for link in re.findall(r"\(([^)]+\.md)\)", content):
            linked = (cpu_map.parent / link).resolve()
            if not linked.exists():
                findings.append({"severity": "P1", "type": "CPU_FICHA_AUSENTE", "detail": link})

    blocking = [finding for finding in findings if finding["severity"] == "P0"]
    return {
        "schema_version": "1.1.0",
        "generated_at": utc_now(),
        "gate": "LIBERADO" if not blocking else "BLOQUEADO",
        "restricoes_ativas": len(findings) - len(blocking),
        "findings": findings,
    }


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
