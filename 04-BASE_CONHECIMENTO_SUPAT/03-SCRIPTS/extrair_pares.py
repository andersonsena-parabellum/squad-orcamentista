#!/usr/bin/env python3
"""Extrai evidências sem inferir regra, aceite ou ação do órgão.

O manifesto de entrada deve conter `documentos`, cada um com `path`, `sha256`,
`orgao`, `pcode` e `revisao`. A saída sempre fica PENDENTE_REVISAO_HUMANA.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def record_id(source_hash: str, locator: str, text: str) -> str:
    return hashlib.sha256(f"{source_hash}|{locator}|{text}".encode("utf-8")).hexdigest()


def extract_docx(path: Path, metadata: dict, source_hash: str) -> list[dict]:
    import docx

    document = docx.Document(path)
    paragraphs = [(index, paragraph.text.strip()) for index, paragraph in enumerate(document.paragraphs, 1) if paragraph.text.strip()]
    records = []
    for position, (index, text) in enumerate(paragraphs):
        next_text = paragraphs[position + 1][1] if position + 1 < len(paragraphs) else ""
        if not re.match(r"^(RESPOSTA|R\s*[-:])", next_text, re.IGNORECASE):
            continue
        locator = f"paragrafo:{index}"
        records.append(
            {
                "id": record_id(source_hash, locator, text),
                "classificacao": "PAR_ANALISTA_RESPOSTA_FPE",
                "texto_analista": text,
                "resposta_fpe": next_text,
                "localizador": locator,
                "revisao_humana": "PENDENTE",
                **metadata,
            }
        )
    return records


def extract_pdf(path: Path, metadata: dict, source_hash: str) -> list[dict]:
    import pypdf

    reader = pypdf.PdfReader(path)
    records = []
    for page_number, page in enumerate(reader.pages, 1):
        text = page.extract_text() or ""
        blocks = re.findall(r"(?:^|\n)(\d{1,2}\.\s+.+?)(?=\n\d{1,2}\.\s+|\Z)", text, flags=re.DOTALL)
        for index, block in enumerate(blocks, 1):
            cleaned = re.sub(r"\s+", " ", block).strip()
            if len(cleaned) < 20:
                continue
            locator = f"pagina:{page_number}:bloco:{index}"
            records.append(
                {
                    "id": record_id(source_hash, locator, cleaned),
                    "classificacao": "TEXTO_ANALISTA_CANDIDATO",
                    "texto_analista": cleaned,
                    "resposta_fpe": None,
                    "localizador": locator,
                    "revisao_humana": "PENDENTE",
                    **metadata,
                }
            )
    return records


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifesto", type=Path, required=True)
    parser.add_argument("--saida", type=Path, required=True)
    args = parser.parse_args()
    try:
        manifest = json.loads(args.manifesto.read_text(encoding="utf-8"))
        records = []
        for item in manifest.get("documentos", []):
            path = Path(item["path"]).resolve()
            expected_hash = item["sha256"]
            if not path.is_file() or sha256(path) != expected_hash:
                raise RuntimeError(f"fonte ausente ou hash divergente: {path}")
            metadata = {
                "orgao": item["orgao"],
                "pcode": item["pcode"],
                "revisao": item["revisao"],
                "arquivo_origem": str(path),
                "sha256_origem": expected_hash,
            }
            if path.suffix.lower() == ".docx":
                records.extend(extract_docx(path, metadata, expected_hash))
            elif path.suffix.lower() == ".pdf":
                records.extend(extract_pdf(path, metadata, expected_hash))
            else:
                raise ValueError(f"formato não suportado: {path.suffix}")
        payload = {
            "schema_version": "1.0.0",
            "status": "PENDENTE_REVISAO_HUMANA",
            "gerado_em": datetime.now(timezone.utc).isoformat(),
            "casos": records,
        }
        args.saida.parent.mkdir(parents=True, exist_ok=True)
        args.saida.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    except Exception as exc:
        print(f"BLOQUEADO: {exc}", file=sys.stderr)
        return 2
    print(f"Extraídos {len(records)} candidato(s), todos pendentes de revisão humana: {args.saida}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
