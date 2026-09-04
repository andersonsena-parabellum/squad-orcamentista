#!/usr/bin/env python3
"""Mede precisão e cobertura usando previsões independentes e gabarito imutável."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]


def load_cases(path: Path) -> dict[str, dict]:
    data = json.loads(path.read_text(encoding="utf-8"))
    cases = data.get("casos") if isinstance(data, dict) else data
    if not isinstance(cases, list):
        raise ValueError(f"{path}: esperado array ou objeto com chave 'casos'")
    result = {}
    for item in cases:
        case_id = str(item.get("id", "")).strip()
        if not case_id or case_id in result:
            raise ValueError(f"{path}: id ausente ou duplicado: {case_id!r}")
        result[case_id] = item
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--previsoes", type=Path, required=True)
    parser.add_argument("--gabarito", type=Path, required=True)
    parser.add_argument("--saida", type=Path, default=BASE_DIR / "06-CALIBRACAO.json")
    parser.add_argument("--min-precision", type=float, default=0.80)
    parser.add_argument("--min-recall", type=float, default=0.70)
    args = parser.parse_args()

    predictions = load_cases(args.previsoes)
    truth = load_cases(args.gabarito)
    predicted_positive = {key for key, value in predictions.items() if bool(value.get("ressalva"))}
    actual_positive = {key for key, value in truth.items() if bool(value.get("ressalva"))}
    universe = set(predictions) | set(truth)
    missing_predictions = sorted(set(truth) - set(predictions))
    tp = len(predicted_positive & actual_positive)
    fp = len(predicted_positive - actual_positive)
    fn = len(actual_positive - predicted_positive)
    tn = len(universe - predicted_positive - actual_positive)
    precision = tp / (tp + fp) if tp + fp else 0.0
    recall = tp / (tp + fn) if tp + fn else 0.0
    passed = not missing_predictions and precision >= args.min_precision and recall >= args.min_recall
    result = {
        "executado_em": datetime.now(timezone.utc).isoformat(),
        "metodologia": "previsões congeladas comparadas por ID com gabarito independente",
        "arquivos": {"previsoes": str(args.previsoes), "gabarito": str(args.gabarito)},
        "matriz_confusao": {"tp": tp, "fp": fp, "fn": fn, "tn": tn},
        "precision": round(precision, 4),
        "recall": round(recall, 4),
        "ids_sem_previsao": missing_predictions,
        "limiares": {"precision": args.min_precision, "recall": args.min_recall},
        "veredito": "APROVADO" if passed else "REPROVADO",
    }
    args.saida.parent.mkdir(parents=True, exist_ok=True)
    args.saida.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if passed else 2


if __name__ == "__main__":
    raise SystemExit(main())
