#!/usr/bin/env python3
"""Inventaria CPUs recebidas; não concede aprovação ou vigência automaticamente."""

from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]
CPU_DIR = BASE_DIR / "03-CPU_PROPRIAS"
ORIGINALS_DIR = CPU_DIR / "_ORIGINAIS"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--saida", type=Path, default=CPU_DIR / "INVENTARIO_PENDENTE.json")
    args = parser.parse_args()
    ORIGINALS_DIR.mkdir(parents=True, exist_ok=True)
    files = sorted(p for p in ORIGINALS_DIR.rglob("*") if p.is_file() and p.name.lower() != "desktop.ini")
    payload = {
        "gerado_em": datetime.now(timezone.utc).isoformat(),
        "status": "PENDENTE_REVISAO_HUMANA",
        "aviso": "Inventário não significa validação, aprovação ou vigência de preço.",
        "arquivos": [
            {
                "arquivo": str(path.relative_to(CPU_DIR)).replace("\\", "/"),
                "sha256": sha256(path),
                "tamanho": path.stat().st_size,
            }
            for path in files
        ],
    }
    args.saida.parent.mkdir(parents=True, exist_ok=True)
    args.saida.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"{len(files)} arquivo(s) inventariado(s); todos permanecem pendentes de revisão humana.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
