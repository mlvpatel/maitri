"""Eval harness for the Maitri pipeline.

Runs the verifier against a hand crafted adversarial set and computes precision,
recall, and accuracy for unsupported claim detection. Prints a markdown report
that the writeup can embed verbatim.

Run with: python -m eval.harness
"""

from __future__ import annotations

import json
import sys
import time
from pathlib import Path

# Add src to path when running as a module from the repo root.
_SRC = Path(__file__).resolve().parents[1] / "src"
if _SRC.exists() and str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

from maitri.agents.verifier import run_verifier  # noqa: E402
from maitri.gemma_client import GemmaClient  # noqa: E402
from tests.adversarial.poisoned_assessments import POISONED  # noqa: E402


def evaluate_verifier() -> dict[str, object]:
    tp = 0  # claims correctly flagged
    fp = 0  # claims flagged that should not have been
    fn = 0  # claims missed that should have been flagged
    tn_cases = 0  # cases with no unsupported claims, correctly accepted
    latencies: list[int] = []
    detail: list[dict[str, object]] = []

    with GemmaClient() as client:
        for assessment, evidence, expected_ids in POISONED:
            t0 = time.perf_counter()
            verdict = run_verifier(assessment, evidence, client=client)
            latencies.append(int((time.perf_counter() - t0) * 1000))

            predicted = set(verdict.unsupported_claim_ids)
            expected = set(expected_ids)

            tp += len(predicted & expected)
            fp += len(predicted - expected)
            fn += len(expected - predicted)
            if not expected and not predicted:
                tn_cases += 1

            detail.append({
                "case_id": assessment.case_id,
                "expected_unsupported": sorted(expected),
                "predicted_unsupported": sorted(predicted),
                "accepted": verdict.accepted,
                "rationale": verdict.rationale[:200],
            })

    precision = tp / (tp + fp) if (tp + fp) else 1.0
    recall = tp / (tp + fn) if (tp + fn) else 1.0
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) else 0.0
    latency_p50 = sorted(latencies)[len(latencies) // 2] if latencies else 0
    latency_p95 = sorted(latencies)[max(0, int(len(latencies) * 0.95) - 1)] if latencies else 0

    return {
        "n_cases": len(POISONED),
        "tp": tp,
        "fp": fp,
        "fn": fn,
        "tn_no_unsupported_correctly_accepted": tn_cases,
        "precision": round(precision, 3),
        "recall": round(recall, 3),
        "f1": round(f1, 3),
        "latency_ms_p50": latency_p50,
        "latency_ms_p95": latency_p95,
        "detail": detail,
    }


def print_markdown_report(metrics: dict[str, object]) -> None:
    print("# Verifier evaluation on the adversarial set")
    print()
    print(f"Cases run: {metrics['n_cases']}")
    print()
    print("| metric | value |")
    print("|---|---|")
    print(f"| precision | {metrics['precision']} |")
    print(f"| recall | {metrics['recall']} |")
    print(f"| f1 | {metrics['f1']} |")
    print(f"| true positives | {metrics['tp']} |")
    print(f"| false positives | {metrics['fp']} |")
    print(f"| false negatives | {metrics['fn']} |")
    print(f"| latency p50 ms | {metrics['latency_ms_p50']} |")
    print(f"| latency p95 ms | {metrics['latency_ms_p95']} |")
    print()
    print("## Per case")
    print()
    for d in metrics["detail"]:  # type: ignore[assignment]
        print(f"### {d['case_id']}")
        print(f"- expected unsupported: {d['expected_unsupported']}")
        print(f"- predicted unsupported: {d['predicted_unsupported']}")
        print(f"- accepted: {d['accepted']}")
        print(f"- rationale: {d['rationale']}")
        print()


def main() -> int:
    metrics = evaluate_verifier()
    out_dir = Path("eval/reports")
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "verifier_metrics.json").write_text(
        json.dumps(metrics, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print_markdown_report(metrics)
    return 0


if __name__ == "__main__":
    sys.exit(main())
