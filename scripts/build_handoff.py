#!/usr/bin/env python3
"""Cria um handoff versionado com hashes dos artefatos entre agentes."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from squad_common import atomic_write_json, load_json, sha256_file, utc_now, validate_handoff_file


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("pasta_obra", type=Path)
    parser.add_argument("--producer", required=True, choices=("sofia", "levi", "elias", "otavio", "carlos", "ana", "eduardo", "verificador"))
    parser.add_argument("--consumer", required=True)
    parser.add_argument("--artifact", action="append", type=Path, required=True)
    parser.add_argument("--price-source", action="append", choices=("SINAPI", "ORSE", "CPU_PROPRIA", "COTACAO"))
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    project = args.pasta_obra.resolve()
    state_path = project / "_squad" / "estado.json"
    try:
        state = load_json(state_path)
        records = []
        for supplied in args.artifact:
            artifact = supplied.resolve()
            relative = artifact.relative_to(project)
            if not artifact.is_file():
                raise FileNotFoundError(artifact)
            records.append({"path": relative.as_posix(), "sha256": sha256_file(artifact)})
        payload = {
            "schema_version": "1.0.0",
            "project_id": state["project_id"],
            "revision_id": state["revision_id"],
            "producer": args.producer,
            "consumer": args.consumer,
            "created_at": utc_now(),
            "source_manifest_sha256": state["manifesto_fontes"]["sha256"],
            "artifacts": records,
            "status": "PRONTO",
            "open_issues": [],
        }
        if args.price_source:
            payload["price_sources"] = sorted(set(args.price_source))
        output = args.out.resolve()
        output.relative_to(project)
        atomic_write_json(output, payload)
        validate_handoff_file(output, state, args.producer, project)
    except Exception as exc:
        print(f"[BLOQUEADO] {exc}", file=sys.stderr)
        return 2
    print(f"[OK] Handoff criado: {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
