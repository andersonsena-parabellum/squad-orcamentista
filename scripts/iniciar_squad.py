#!/usr/bin/env python3
"""Inicializa uma revisao do squad com manifesto imutavel das fontes."""

from __future__ import annotations

import argparse
import re
import sys
import uuid
from pathlib import Path

from squad_common import atomic_write_json, exclusive_lock, sha256_file, utc_now, validate_revision


SOURCE_EXTENSIONS = {".pdf", ".dwg", ".dxf", ".ifc", ".rvt", ".xlsx", ".xls", ".docx", ".txt"}
OUTPUT_RE = re.compile(r"(?:DC|EC)-00[1-7]|RELATORIO-SQUAD|AUDITORIA|RESPOSTAS", re.IGNORECASE)


def source_category(path: Path) -> str:
    text = str(path).upper()
    name = path.name.upper()
    if "-LI-" in name or "LISTA DE INSUM" in name or "LISTA DE MATER" in name:
        return "LI"
    if "MEMORIAL" in name:
        return "MEMORIAL"
    if any(token in text for token in ("PROJETO", "ARQUITET", "ESTRUT", "ELETR", "HIDR", "SPDA", "CFTV")):
        return "PROJETO"
    if any(token in name for token in ("ANALISE", "ANÁLISE", "PARECER", "RESSALVA")):
        return "ANALISE_ORGAO"
    return "OUTRA_FONTE"


def build_manifest(project_dir: Path) -> dict:
    entries = []
    for path in sorted(project_dir.rglob("*")):
        if not path.is_file() or path.suffix.lower() not in SOURCE_EXTENSIONS:
            continue
        rel = path.relative_to(project_dir)
        upper_parts = {part.upper() for part in rel.parts}
        if ".GIT" in upper_parts or "_SQUAD" in upper_parts or "ENVIO" in upper_parts or "ENVIOS" in upper_parts:
            continue
        if OUTPUT_RE.search(path.name) or path.name.startswith("~$"):
            continue
        stat = path.stat()
        entries.append(
            {
                "relative_path": rel.as_posix(),
                "category": source_category(rel),
                "bytes": stat.st_size,
                "mtime_ns": stat.st_mtime_ns,
                "sha256": sha256_file(path),
            }
        )
    return {"schema_version": "1.0.0", "created_at": utc_now(), "project_dir": str(project_dir), "files": entries}


def initialize(args: argparse.Namespace) -> Path:
    project_dir = args.pasta_obra.resolve()
    if not project_dir.is_dir():
        raise FileNotFoundError(f"Pasta da obra nao encontrada: {project_dir}")
    revision = validate_revision(args.revisao)
    squad_dir = project_dir / "_squad"
    state_path = squad_dir / "estado.json"
    manifest_path = squad_dir / "manifesto_fontes.json"
    with exclusive_lock(squad_dir / ".estado.lock", "sofia"):
        if state_path.exists():
            raise FileExistsError(f"Estado ja existe; nao sobrescrever: {state_path}")
        manifest = build_manifest(project_dir)
        if not manifest["files"]:
            raise RuntimeError("Nenhuma fonte de projeto/LI/memorial foi localizada; inicializacao bloqueada")
        atomic_write_json(manifest_path, manifest)
        state = {
            "schema_version": "1.0.0",
            "project_id": str(uuid.uuid5(uuid.NAMESPACE_URL, str(project_dir).casefold())),
            "obra": project_dir.name,
            "pasta_obra": str(project_dir),
            "revision_id": revision,
            "tipologia": args.tipologia,
            "requirements_profile": {
                "fonte_recursos": args.fonte_recursos,
                "regime_tributario": args.regime_tributario,
                "orgao": args.orgao,
                "exige_10pct_itens": args.fonte_recursos in {"FEDERAL", "MISTO"},
            },
            "status_fluxo": "FONTES_CONGELADAS",
            "status_gate": "EM_ANDAMENTO",
            "manifesto_fontes": {"path": manifest_path.name, "sha256": sha256_file(manifest_path)},
            "artifacts": {},
            "pending_issues": [],
            "human_authorization": None,
            "created_at": utc_now(),
            "updated_at": utc_now(),
            "history": [{"at": utc_now(), "actor": "sofia", "event": "FONTES_CONGELADAS"}],
        }
        atomic_write_json(state_path, state)
    return state_path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("pasta_obra", type=Path)
    parser.add_argument("--revisao", required=True)
    parser.add_argument("--tipologia", required=True)
    parser.add_argument("--fonte-recursos", required=True, choices=["FEDERAL", "ESTADUAL", "MUNICIPAL", "PRIVADO", "MISTO"])
    parser.add_argument("--regime-tributario", required=True, choices=["DESONERADO", "NAO_DESONERADO", "NAO_APLICAVEL"])
    parser.add_argument("--orgao", required=True)
    args = parser.parse_args()
    try:
        path = initialize(args)
    except Exception as exc:
        print(f"[BLOQUEADO] {exc}", file=sys.stderr)
        return 2
    print(f"[OK] Estado e fontes congelados em {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
