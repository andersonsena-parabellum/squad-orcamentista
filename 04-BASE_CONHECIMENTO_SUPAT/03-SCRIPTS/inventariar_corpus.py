#!/usr/bin/env python3
"""Inventaria candidatos a fonte do corpus com hash; não os declara oficiais."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path

EXTENSIONS = {".pdf", ".docx", ".doc", ".xlsx", ".xls", ".txt"}
KEYWORDS = ("analise", "análise", "parecer", "ressalva", "resposta", "rt-001", "supat")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--raiz", type=Path, required=True, help="raiz autorizada das obras")
    parser.add_argument("--saida", type=Path, required=True)
    args = parser.parse_args()
    root = args.raiz.resolve()
    records = []
    for path in sorted(root.rglob("*")):
        if not path.is_file() or path.suffix.lower() not in EXTENSIONS or path.name.startswith("~$"):
            continue
        searchable = f"{path.name} {path.parent}".casefold()
        if not any(keyword.casefold() in searchable for keyword in KEYWORDS):
            continue
        pcode = re.search(r"P\d{4,5}", str(path), re.IGNORECASE)
        revision = re.search(r"(?:^|[-_ ])R(\d{2,3})(?:\D|$)", str(path), re.IGNORECASE)
        records.append(
            {
                "path": str(path),
                "relative_path": path.relative_to(root).as_posix(),
                "sha256": sha256(path),
                "bytes": path.stat().st_size,
                "pcode_candidato": pcode.group(0).upper() if pcode else None,
                "revisao_candidata": f"R{revision.group(1)}" if revision else None,
                "classificacao": "CANDIDATO_NAO_REVISADO",
            }
        )
    payload = {
        "schema_version": "1.0.0",
        "status": "PENDENTE_REVISAO_HUMANA",
        "raiz": str(root),
        "gerado_em": datetime.now(timezone.utc).isoformat(),
        "documentos": records,
    }
    args.saida.parent.mkdir(parents=True, exist_ok=True)
    args.saida.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"{len(records)} candidato(s) inventariado(s); nenhum foi declarado oficial.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
