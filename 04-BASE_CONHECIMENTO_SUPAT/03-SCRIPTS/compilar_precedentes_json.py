#!/usr/bin/env python3
"""Compila apenas casos revisados, sem converter Markdown legado em evidência."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--entrada", type=Path, required=True)
    parser.add_argument("--saida", type=Path, required=True)
    args = parser.parse_args()
    try:
        payload = json.loads(args.entrada.read_text(encoding="utf-8"))
        cases = payload.get("casos", [])
        if not cases:
            raise ValueError("nenhum caso para compilar")
        for case in cases:
            review = case.get("revisao_humana", {})
            if not isinstance(review, dict) or review.get("status") != "APROVADO" or not review.get("responsavel") or not review.get("data"):
                raise ValueError(f"caso sem revisão humana aprovada: {case.get('id')}")
            source = Path(case.get("arquivo_origem", "")).resolve()
            if not source.is_file() or sha256(source) != case.get("sha256_origem"):
                raise RuntimeError(f"fonte ausente ou alterada: {source}")
            if case.get("classificacao") not in {"PAR_ANALISTA_RESPOSTA_FPE", "TEXTO_ANALISTA_CONFIRMADO"}:
                raise ValueError(f"classificação não liberável: {case.get('classificacao')}")
        output = {
            "schema_version": "1.0.0",
            "status": "LIBERADA",
            "compilado_em": datetime.now(timezone.utc).isoformat(),
            "casos": cases,
        }
        args.saida.parent.mkdir(parents=True, exist_ok=True)
        args.saida.write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    except Exception as exc:
        print(f"BLOQUEADO: {exc}", file=sys.stderr)
        return 2
    print(f"Corpus revisado compilado: {args.saida}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
