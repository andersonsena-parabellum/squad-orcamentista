#!/usr/bin/env python3
"""Utilitarios compartilhados e invariantes do Squad de Orcamento FPE."""

from __future__ import annotations

import hashlib
import json
import os
import re
import sys
import tempfile
import unicodedata
from contextlib import contextmanager
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from pathlib import Path
from typing import Any, Iterator


def configure_utf8_console() -> None:
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8")


configure_utf8_console()


REPO_ROOT = Path(__file__).resolve().parents[1]
PRICE_DB = REPO_ROOT / "03-BASE_DE_PRECOS" / "base_precos.db"
SOURCE_REGISTRY = REPO_ROOT / "03-BASE_DE_PRECOS" / "FONTES_DADOS.json"

PRE_EXPORT_APPROVAL_GATES = {"PRE_LIBERADO"}
REVISION_RE = re.compile(r"^R\d{2,3}$", re.IGNORECASE)


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def sha256_file(path: Path, chunk_size: int = 1024 * 1024) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        while chunk := stream.read(chunk_size):
            digest.update(chunk)
    return digest.hexdigest()


def normalize_text(value: Any) -> str:
    """Normaliza somente representacao; nao remove palavras nem pontuacao."""
    if value is None:
        return ""
    text = unicodedata.normalize("NFC", str(value))
    return re.sub(r"\s+", " ", text).strip().upper()


def normalize_unit(value: Any) -> str:
    unit = normalize_text(value).replace("²", "2").replace("³", "3")
    aliases = {"UND": "UN", "UNID": "UN", "UNIDADE": "UN"}
    return aliases.get(unit, unit)


def money(value: Any) -> Decimal:
    if value in (None, ""):
        raise InvalidOperation("valor ausente")
    if isinstance(value, str):
        value = value.replace("R$", "").strip()
        if "," in value:
            value = value.replace(".", "").replace(",", ".")
    return Decimal(str(value)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as stream:
        return json.load(stream)


def atomic_write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temp_name = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as stream:
            json.dump(data, stream, ensure_ascii=False, indent=2)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temp_name, path)
    finally:
        if os.path.exists(temp_name):
            os.unlink(temp_name)


@contextmanager
def exclusive_lock(lock_path: Path, actor: str) -> Iterator[None]:
    """Lock exclusivo. Nunca remove silenciosamente lock preexistente."""
    lock_path.parent.mkdir(parents=True, exist_ok=True)
    try:
        fd = os.open(lock_path, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
    except FileExistsError as exc:
        raise RuntimeError(f"Recurso em uso; lock existente: {lock_path}") from exc
    try:
        payload = json.dumps({"actor": actor, "pid": os.getpid(), "created_at": utc_now()})
        os.write(fd, payload.encode("utf-8"))
        os.close(fd)
        yield
    finally:
        try:
            lock_path.unlink()
        except FileNotFoundError:
            pass


def source_registry() -> dict[str, Any]:
    if not SOURCE_REGISTRY.exists():
        raise FileNotFoundError(f"Registro de fontes ausente: {SOURCE_REGISTRY}")
    return load_json(SOURCE_REGISTRY)


def source_record(source: str) -> dict[str, Any] | None:
    return source_registry().get("fontes", {}).get(normalize_text(source))


def source_is_releasable(source: str) -> tuple[bool, str]:
    record = source_record(source)
    if not record:
        return False, "fonte sem registro de proveniencia"
    status = normalize_text(record.get("status"))
    if status != "LIBERADA":
        return False, f"fonte com status {status}: {record.get('motivo', '')}"
    origin = record.get("arquivo_origem")
    expected_hash = record.get("sha256_origem")
    if not record.get("competencia") or not origin or not expected_hash:
        return False, "fonte sem competencia, arquivo bruto ou hash oficial"
    origin_path = (SOURCE_REGISTRY.parent / origin).resolve()
    if not origin_path.is_file():
        return False, f"arquivo bruto ausente: {origin_path}"
    if sha256_file(origin_path) != expected_hash:
        return False, "hash do arquivo bruto diverge do registro"
    return True, "OK"


def validate_revision(value: str) -> str:
    value = value.upper()
    if not REVISION_RE.fullmatch(value):
        raise ValueError("Revisao deve seguir R00..R999")
    return value


def _inside(path: Path, parent: Path) -> bool:
    try:
        path.resolve().relative_to(parent.resolve())
        return True
    except ValueError:
        return False


def validate_handoff_file(path: Path, state: dict[str, Any], producer: str, project_dir: Path) -> dict[str, Any]:
    """Valida o contrato mínimo e todos os artefatos referenciados pelo handoff."""
    if path.suffix.lower() != ".json":
        raise ValueError("Handoff deve ser JSON")
    if not _inside(path, project_dir):
        raise ValueError("Handoff deve permanecer dentro da pasta da obra")
    data = load_json(path)
    required = {
        "schema_version", "project_id", "revision_id", "producer", "consumer",
        "created_at", "source_manifest_sha256", "artifacts", "status", "open_issues",
    }
    missing = sorted(required - set(data))
    if missing:
        raise ValueError(f"Handoff incompleto: {missing}")
    expected = {
        "schema_version": "1.0.0",
        "project_id": state.get("project_id"),
        "revision_id": state.get("revision_id"),
        "producer": producer,
        "source_manifest_sha256": state.get("manifesto_fontes", {}).get("sha256"),
        "status": "PRONTO",
    }
    divergences = [key for key, value in expected.items() if data.get(key) != value]
    if divergences:
        raise ValueError(f"Handoff divergente do estado: {divergences}")
    if data.get("open_issues"):
        raise ValueError("Handoff PRONTO nao pode conter pendencias abertas")
    artifacts = data.get("artifacts")
    if not isinstance(artifacts, list) or not artifacts:
        raise ValueError("Handoff sem artefatos")
    for record in artifacts:
        artifact = (project_dir / str(record.get("path", ""))).resolve()
        if not _inside(artifact, project_dir) or not artifact.is_file():
            raise ValueError(f"Artefato ausente ou fora da obra: {record.get('path')}")
        if sha256_file(artifact) != record.get("sha256"):
            raise ValueError(f"Hash divergente: {record.get('path')}")
    return data
