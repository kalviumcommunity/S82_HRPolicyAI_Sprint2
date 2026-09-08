"""Run small, repeatable sanity checks against stored embedding records."""

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any, Callable


PROJECT_ROOT = Path(__file__).parent.parent
OUTPUT_DIR = PROJECT_ROOT / "outputs"
EMBEDDING_FILE = OUTPUT_DIR / "embedding_results.json"
REPORT_JSON = OUTPUT_DIR / "embedding_quality_report.json"
REPORT_TEXT = OUTPUT_DIR / "embedding_quality_report.txt"

TEST_CASES = [
    {
        "query": "How many paid annual leave days can an employee take?",
        "expected_source": "sample_leave_policy.txt",
        "expected_chunk_index": 0,
        "offline_query_vector": [0.1, 0.2, 0.3, 0.4],
        "note": "Specific entitlement wording should select the annual-leave chunk.",
    },
    {
        "query": "When should an employee submit a leave request?",
        "expected_source": "sample_leave_policy.txt",
        "expected_chunk_index": 1,
        "offline_query_vector": [0.5, 0.6, 0.7, 0.8],
        "note": "Specific process wording should select the request chunk.",
    },
    {
        "query": "Tell me about leave.",
        "expected_source": "sample_leave_policy.txt",
        "expected_chunk_index": 0,
        "offline_query_vector": [0.3, 0.4, 0.5, 0.6],
        "note": "Surprising case: a generic query is nearly tied and has no reliable section signal.",
    },
]


def cosine_similarity(first: list[float], second: list[float]) -> float:
    if len(first) != len(second):
        raise ValueError("Vectors must have the same dimension.")
    first_norm = sum(value * value for value in first) ** 0.5
    second_norm = sum(value * value for value in second) ** 0.5
    if first_norm == 0 or second_norm == 0:
        return 0.0
    return sum(left * right for left, right in zip(first, second)) / (first_norm * second_norm)


def rank_chunks(query_embedding: list[float], records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    ranked = [
        {
            "score": cosine_similarity(query_embedding, record["embedding"]),
            "text": record["text"],
            "metadata": record["metadata"],
        }
        for record in records
    ]
    return sorted(ranked, key=lambda result: result["score"], reverse=True)


def load_records() -> tuple[str, list[dict[str, Any]]]:
    if not EMBEDDING_FILE.exists():
        raise FileNotFoundError(f"Missing embedding artifact: {EMBEDDING_FILE}")
    stored = json.loads(EMBEDDING_FILE.read_text(encoding="utf-8"))
    records = stored.get("records", [])
    if not records:
        raise ValueError("Embedding artifact contains no records.")
    dimensions = {len(record.get("embedding", [])) for record in records}
    if len(dimensions) != 1 or 0 in dimensions:
        raise ValueError("Stored records must contain non-empty vectors of one dimension.")
    return stored.get("model", "unknown"), records


def live_query_embedder(model: str) -> Callable[[str], list[float]]:
    try:
        from dotenv import load_dotenv
        from openai import OpenAI
    except ImportError as error:
        raise RuntimeError("Live mode requires the dependencies in requirements.txt.") from error

    load_dotenv()
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("Live mode requires OPENAI_API_KEY.")
    base_url = os.getenv("OPENAI_BASE_URL") or os.getenv("API_BASE_URL")
    client = OpenAI(api_key=api_key, base_url=base_url or None)

    def embed(query: str) -> list[float]:
        response = client.embeddings.create(model=model, input=[query])
        return response.data[0].embedding

    return embed


def run_checks(records: list[dict[str, Any]], embed_query: Callable[[str], list[float]], mode: str) -> dict[str, Any]:
    results = []
    for case in TEST_CASES:
        ranked = rank_chunks(embed_query(case["query"]), records)
        top = ranked[0]
        top_metadata = top["metadata"]
        expected = (
            top_metadata.get("source") == case["expected_source"]
            and top_metadata.get("chunk_index") == case["expected_chunk_index"]
        )
        results.append(
            {
                "query": case["query"],
                "expected_source": case["expected_source"],
                "expected_chunk_index": case["expected_chunk_index"],
                "top_source": top_metadata.get("source"),
                "top_chunk_index": top_metadata.get("chunk_index"),
                "top_score": round(top["score"], 6),
                "second_score": round(ranked[1]["score"], 6) if len(ranked) > 1 else None,
                "passed": expected,
                "note": case["note"],
            }
        )
    passed = sum(result["passed"] for result in results)
    return {
        "model": mode,
        "metric": "cosine_similarity",
        "test_count": len(results),
        "passed": passed,
        "failed": len(results) - passed,
        "results": results,
        "notes": [
            "A top-ranked result is considered relevant only when both source and chunk_index match.",
            "The generic leave query is intentionally borderline: semantic similarity alone cannot identify a policy section.",
            "Live mode must use the same EMBEDDING_MODEL for corpus and query vectors; mismatched models invalidate ranking.",
        ],
    }


def format_report(report: dict[str, Any]) -> str:
    lines = [
        "EMBEDDING QUALITY SANITY REPORT",
        "=" * 60,
        f"Mode/model: {report['model']}",
        f"Metric: {report['metric']}",
        f"Tests: {report['test_count']}  Passed: {report['passed']}  Failed: {report['failed']}",
        "",
        "RESULTS",
        "-" * 60,
    ]
    for index, result in enumerate(report["results"], start=1):
        status = "PASS" if result["passed"] else "FAIL"
        lines.append(
            f"{status} {index}. {result['query']} | expected {result['expected_source']} "
            f"#{result['expected_chunk_index']} | top {result['top_source']} "
            f"#{result['top_chunk_index']} | score {result['top_score']:.6f} "
            f"(runner-up {result['second_score']:.6f})"
        )
        lines.append(f"   Note: {result['note']}")
    lines.extend(["", "NOTES", "-" * 60])
    lines.extend(f"- {note}" for note in report["notes"])
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--live", action="store_true", help="Embed queries through the configured API.")
    parser.add_argument("--strict", action="store_true", help="Exit nonzero when any check fails.")
    args = parser.parse_args()

    model, records = load_records()
    if args.live:
        embed_query = live_query_embedder(os.getenv("EMBEDDING_MODEL", model))
        report_model = os.getenv("EMBEDDING_MODEL", model)
    else:
        vectors = {case["query"]: case["offline_query_vector"] for case in TEST_CASES}
        embed_query = lambda query: vectors[query]
        report_model = f"offline-fixture ({model})"

    report = run_checks(records, embed_query, report_model)
    REPORT_JSON.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    REPORT_TEXT.write_text(format_report(report) + "\n", encoding="utf-8")
    print(format_report(report))
    return 0 if report["failed"] == 0 or not args.strict else 1


if __name__ == "__main__":
    sys.exit(main())