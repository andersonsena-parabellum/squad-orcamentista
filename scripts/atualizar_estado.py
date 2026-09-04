#!/usr/bin/env python3
"""Atualiza a maquina de estados com segregacao de funcoes e hashes."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from squad_common import (
    PRE_EXPORT_APPROVAL_GATES,
    atomic_write_json,
    exclusive_lock,
    load_json,
    sha256_file,
    source_is_releasable,
    utc_now,
    validate_handoff_file,
)


TRANSITIONS = {
    "FONTES_CONGELADAS": {"QTO_PRONTO": {"levi"}},
    "QTO_PRONTO": {"EAP_PRONTA": {"elias"}},
    "EAP_PRONTA": {"PRECIFICACAO_PRONTA": {"otavio"}},
    "PRECIFICACAO_PRONTA": {"COTACOES_PRONTAS": {"carlos"}},
    "COTACOES_PRONTAS": {"AUDITORIA_PENDENTE": {"sofia"}},
    "AUDITORIA_PENDENTE": {"AUDITORIA_APROVADA": {"ana"}, "AUDITORIA_BLOQUEADA": {"ana"}},
    "AUDITORIA_BLOQUEADA": {"QTO_PRONTO": {"levi"}, "EAP_PRONTA": {"elias"}, "PRECIFICACAO_PRONTA": {"otavio"}, "COTACOES_PRONTAS": {"carlos"}},
    "AUDITORIA_APROVADA": {"EXPORTACAO_STAGING": {"eduardo"}},
    "EXPORTACAO_STAGING": {"POS_EXPORTACAO_OK": {"verificador"}, "AUDITORIA_BLOQUEADA": {"verificador"}},
    "POS_EXPORTACAO_OK": {"AUTORIZADO": {"anderson"}},
    "AUTORIZADO": {"SELADO": {"eduardo"}},
}


def verify_frozen_sources(project_dir: Path, state: dict) -> list[str]:
    manifest_info = state.get("manifesto_fontes", {})
    manifest_path = project_dir / "_squad" / manifest_info.get("path", "manifesto_fontes.json")
    failures = []
    if not manifest_path.exists() or sha256_file(manifest_path) != manifest_info.get("sha256"):
        return ["Manifesto de fontes ausente ou adulterado"]
    manifest = load_json(manifest_path)
    for entry in manifest.get("files", []):
        path = project_dir / entry["relative_path"]
        if not path.exists():
            failures.append(f"Fonte removida: {entry['relative_path']}")
        elif sha256_file(path) != entry["sha256"]:
            failures.append(f"Fonte alterada: {entry['relative_path']}")
    return failures


def verify_report_artifacts(report: dict, project_dir: Path, field: str) -> None:
    records = report.get(field, {})
    records = records.values() if isinstance(records, dict) else records
    if not isinstance(records, (list, type({}.values()))):
        raise ValueError(f"Relatorio sem estrutura valida em {field}")
    checked = 0
    for record in records:
        if not record:
            continue
        path = Path(str(record.get("path", ""))).resolve()
        try:
            path.relative_to(project_dir)
        except ValueError as exc:
            raise ValueError(f"Relatorio referencia artefato fora da obra: {path}") from exc
        if not path.is_file() or sha256_file(path) != record.get("sha256"):
            raise RuntimeError(f"Artefato ausente ou alterado depois do relatorio: {path}")
        checked += 1
    if not checked:
        raise ValueError(f"Relatorio sem artefatos verificaveis em {field}")


def update(args: argparse.Namespace) -> Path:
    project_dir = args.pasta_obra.resolve()
    state_path = project_dir / "_squad" / "estado.json"
    if not state_path.exists():
        raise FileNotFoundError("Execute iniciar_squad.py antes")
    with exclusive_lock(project_dir / "_squad" / ".estado.lock", args.agente):
        state = load_json(state_path)
        current = state.get("status_fluxo")
        allowed_actors = TRANSITIONS.get(current, {}).get(args.transicao, set())
        if args.agente not in allowed_actors:
            raise PermissionError(f"Transicao {current} -> {args.transicao} nao permitida para {args.agente}")
        source_failures = verify_frozen_sources(project_dir, state)
        if source_failures:
            raise RuntimeError("; ".join(source_failures))

        artifact_record = None
        if args.artefato:
            artifact = args.artefato.resolve()
            if not artifact.is_file():
                raise FileNotFoundError(f"Artefato nao encontrado: {artifact}")
            try:
                artifact.relative_to(project_dir)
            except ValueError as exc:
                raise ValueError("Artefato de transicao deve permanecer dentro da pasta da obra") from exc
            artifact_record = {"path": str(artifact), "sha256": sha256_file(artifact), "producer": args.agente, "recorded_at": utc_now()}

        if args.transicao in {"QTO_PRONTO", "EAP_PRONTA", "PRECIFICACAO_PRONTA", "COTACOES_PRONTAS", "AUDITORIA_PENDENTE", "AUDITORIA_APROVADA", "AUDITORIA_BLOQUEADA", "EXPORTACAO_STAGING", "POS_EXPORTACAO_OK"} and not artifact_record:
            raise ValueError(f"Transicao {args.transicao} exige --artefato")

        handoff_transitions = {"QTO_PRONTO", "EAP_PRONTA", "PRECIFICACAO_PRONTA", "COTACOES_PRONTAS", "AUDITORIA_PENDENTE", "EXPORTACAO_STAGING"}
        if args.transicao in handoff_transitions:
            handoff = validate_handoff_file(args.artefato, state, args.agente, project_dir)
            if args.transicao == "PRECIFICACAO_PRONTA":
                price_sources = handoff.get("price_sources")
                if not isinstance(price_sources, list) or not price_sources:
                    raise ValueError("Handoff de precificacao exige price_sources")
                for source in price_sources:
                    if source in {"SINAPI", "ORSE"}:
                        released, reason = source_is_releasable(source)
                        if not released:
                            raise RuntimeError(f"Fonte de preco bloqueada: {source}: {reason}")

        if args.transicao == "AUDITORIA_APROVADA":
            audit = load_json(args.artefato)
            verify_report_artifacts(audit, project_dir, "pieces")
            gate = audit.get("gate")
            if gate not in PRE_EXPORT_APPROVAL_GATES:
                raise RuntimeError(f"Auditoria nao liberada: {gate}")
            state["status_gate"] = gate
        elif args.transicao == "AUDITORIA_BLOQUEADA":
            audit = load_json(args.artefato)
            if audit.get("gate") != "BLOQUEADO":
                raise RuntimeError("Artefato nao comprova auditoria bloqueada")
            state["status_gate"] = "BLOQUEADO"
        elif args.transicao == "POS_EXPORTACAO_OK":
            verification = load_json(args.artefato)
            if verification.get("gate") != "POS_EXPORTACAO_OK":
                raise RuntimeError(f"Verificacao pos-exportacao invalida: {verification.get('gate')}")
            verify_report_artifacts(verification, project_dir, "artifacts")
            state["status_gate"] = "POS_EXPORTACAO_OK"
        elif args.transicao == "AUTORIZADO":
            if state.get("status_gate") != "POS_EXPORTACAO_OK":
                raise RuntimeError("Autorizacao proibida sem verificacao pos-exportacao")
            if not args.justificativa:
                raise ValueError("Autorizacao humana exige --justificativa")
            state["human_authorization"] = {"actor": "anderson", "at": utc_now(), "justificativa": args.justificativa}
        elif args.transicao == "SELADO":
            if not state.get("human_authorization") or "POS_EXPORTACAO_OK" not in state.get("artifacts", {}):
                raise RuntimeError("Selo exige autorizacao humana e verificacao pos-exportacao")
            state["status_gate"] = "LIBERADO"

        if artifact_record:
            state.setdefault("artifacts", {})[args.transicao] = artifact_record

        state["status_fluxo"] = args.transicao
        state["updated_at"] = utc_now()
        state.setdefault("history", []).append(
            {"at": utc_now(), "actor": args.agente, "from": current, "to": args.transicao, "artifact": artifact_record, "note": args.justificativa}
        )
        atomic_write_json(state_path, state)
    return state_path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("pasta_obra", type=Path)
    parser.add_argument("--agente", required=True, choices=["sofia", "levi", "elias", "otavio", "carlos", "ana", "eduardo", "verificador", "anderson"])
    parser.add_argument("--transicao", required=True, choices=sorted({target for mapping in TRANSITIONS.values() for target in mapping}))
    parser.add_argument("--artefato", type=Path)
    parser.add_argument("--justificativa")
    args = parser.parse_args()
    try:
        path = update(args)
    except Exception as exc:
        print(f"[BLOQUEADO] {exc}", file=sys.stderr)
        return 2
    print(f"[OK] Estado atualizado: {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
