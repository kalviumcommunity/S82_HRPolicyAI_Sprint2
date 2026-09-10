import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

PROJECT_ROOT = Path(__file__).parent.parent
OUTPUT_DIR = PROJECT_ROOT / "outputs"
LABELLED_QUERIES_FILE = OUTPUT_DIR / "labelled_queries.json"
RESULT_FILE = OUTPUT_DIR / "retrieval_evaluation_results.json"
RESULT_TEXT_FILE = OUTPUT_DIR / "retrieval_evaluation_results.txt"


CORPUS = [
    {
        "text": "Employees may take up to 20 days of paid annual leave each year.",
        "metadata": {
            "source": "sample_leave_policy.txt",
            "section": "Annual leave",
            "document_type": "policy",
            "user_group": "all_employees",
            "chunk_index": 0,
        },
        "embedding": [1.0, 0.20, 0.00, 0.00],
    },
    {
        "text": "Leave requests should be submitted to a manager at least two weeks in advance.",
        "metadata": {
            "source": "sample_leave_policy.txt",
            "section": "Requesting leave",
            "document_type": "policy",
            "user_group": "all_employees",
            "chunk_index": 1,
        },
        "embedding": [0.70, 0.95, 0.00, 0.00],
    },
    {
        "text": "All employees receive 10 days of paid sick leave annually on January 1st.",
        "metadata": {
            "source": "sample_leave_policy.txt",
            "section": "Sick leave",
            "document_type": "policy",
            "user_group": "all_employees",
            "chunk_index": 2,
        },
        "embedding": [0.55, 0.30, 1.00, 0.00],
    },
    {
        "text": "Primary caregivers are eligible for up to 16 consecutive weeks of fully paid parental leave.",
        "metadata": {
            "source": "sample_leave_policy.txt",
            "section": "Parental leave",
            "document_type": "policy",
            "user_group": "parents",
            "chunk_index": 3,
        },
        "embedding": [0.45, 0.10, 0.00, 1.00],
    },
    {
        "text": "Parking permits must be renewed annually before the end of the month.",
        "metadata": {
            "source": "sample_parking_policy.txt",
            "section": "Parking",
            "document_type": "policy",
            "user_group": "all_employees",
            "chunk_index": 4,
        },
        "embedding": [0.95, 0.18, 0.00, 0.00],
    },
    {
        "text": "Performance reviews are scheduled annually for all managers in November.",
        "metadata": {
            "source": "sample_performance_policy.txt",
            "section": "Performance reviews",
            "document_type": "policy",
            "user_group": "managers",
            "chunk_index": 5,
        },
        "embedding": [0.85, 0.22, 0.10, 0.00],
    },
]


LABELED_QUERIES = [
    {
        "id": "Q1",
        "query": "How many paid annual leave days can an employee take?",
        "expected_chunk_ids": [0],
        "expected_sections": ["Annual leave"],
        "keywords": ["annual", "leave", "paid", "days"],
        "query_vector": [1.0, 0.20, 0.00, 0.00],
        "notes": "Exact match to the annual leave chunk; ideal baseline case.",
        "likely_failure_causes": [],
    },
    {
        "id": "Q2",
        "query": "How should a leave request be submitted?",
        "expected_chunk_ids": [1],
        "expected_sections": ["Requesting leave"],
        "keywords": ["leave", "request", "submitted", "manager"],
        "query_vector": [0.70, 0.95, 0.00, 0.00],
        "notes": "Exact match to the requesting-leave policy chunk.",
        "likely_failure_causes": [],
    },
    {
        "id": "Q3",
        "query": "How much paid sick leave do employees receive annually?",
        "expected_chunk_ids": [2],
        "expected_sections": ["Sick leave"],
        "keywords": ["paid", "sick", "leave", "annually"],
        "query_vector": [0.55, 0.30, 1.00, 0.00],
        "notes": "Exact match to the sick leave chunk.",
        "likely_failure_causes": [],
    },
    {
        "id": "Q4",
        "query": "What is the paid parental leave entitlement for primary caregivers?",
        "expected_chunk_ids": [3],
        "expected_sections": ["Parental leave"],
        "keywords": ["parental", "leave", "primary", "caregivers"],
        "query_vector": [0.45, 0.10, 0.00, 1.00],
        "notes": "Exact match to the parental leave chunk.",
        "likely_failure_causes": [],
    },
    {
        "id": "Q5",
        "query": "When do I need to ask my manager for approval before taking leave?",
        "expected_chunk_ids": [1],
        "expected_sections": ["Requesting leave"],
        "keywords": ["manager", "approval", "leave", "before"],
        "query_vector": [0.68, 0.92, 0.00, 0.00],
        "notes": "Paraphrased version of the leave request guidance; useful for testing lexical robustness.",
        "likely_failure_causes": [
            "Paraphrased query wording can weaken lexical overlap.",
            "If the target chunk does not rise in the ranking, the likely cause is query wording or embedding mismatch.",
        ],
    },
    {
        "id": "Q6",
        "query": "What is the process for renewing a parking permit?",
        "expected_chunk_ids": [4],
        "expected_sections": ["Parking"],
        "keywords": ["parking", "permit", "renew", "process"],
        "query_vector": [0.00, 0.00, 0.80, 0.00],
        "notes": "Intentional mismatch query to demonstrate a low-scoring failure case and highlight likely causes such as embedding mismatch.",
        "likely_failure_causes": [
            "The query vector is intentionally misaligned with the target parking chunk.",
            "This case likely fails because the retrieval system is not using the right query embedding or the query text is too generic for the target chunk.",
        ],
    },
]


TOP_K_VALUES = [1, 3, 5]


def cosine_similarity(first: List[float], second: List[float]) -> float:
    if len(first) != len(second):
        raise ValueError("Vectors must have the same dimension.")

    first_norm = sum(value * value for value in first) ** 0.5
    second_norm = sum(value * value for value in second) ** 0.5
    if first_norm == 0 or second_norm == 0:
        return 0.0

    dot_product = sum(left * right for left, right in zip(first, second))
    return dot_product / (first_norm * second_norm)


def retrieve_candidates(query_vector: List[float], top_k: int) -> List[Dict[str, Any]]:
    candidates = []

    for record in CORPUS:
        score = cosine_similarity(query_vector, record["embedding"])
        candidates.append(
            {
                "score": score,
                "text": record["text"],
                "metadata": record["metadata"],
            }
        )

    candidates.sort(key=lambda item: item["score"], reverse=True)
    return candidates[:top_k]


def recall_at_k(top_k_results: List[Dict[str, Any]], expected_chunk_ids: List[int]) -> float:
    relevant_ids = set(expected_chunk_ids)
    top_k_ids = {result["metadata"]["chunk_index"] for result in top_k_results}
    return 1.0 if relevant_ids.intersection(top_k_ids) else 0.0


def precision_at_k(top_k_results: List[Dict[str, Any]], expected_chunk_ids: List[int], k: int) -> float:
    expected = set(expected_chunk_ids)
    relevant_in_top_k = sum(
        1 for result in top_k_results if result["metadata"]["chunk_index"] in expected
    )
    return relevant_in_top_k / float(k)


def suggest_failure_causes(label: Dict[str, Any], query_result: Dict[str, Any]) -> List[str]:
    causes = []

    if query_result["recall_at_k"]["5"] < 1.0:
        causes.append(
            "Expected chunk is missing from the top-5 results, which usually points to query wording, embedding mismatch, or a retrieval setup issue."
        )

    if query_result["recall_at_k"]["1"] < 1.0 and query_result["top_1"].get("chunk_index") not in label["expected_chunk_ids"]:
        causes.append(
            "The top-ranked chunk is not the expected chunk; this often means the query vector or keyword weighting is not aligned with the target chunk."
        )

    if label.get("likely_failure_causes"):
        causes.extend(label["likely_failure_causes"])

    if not causes:
        causes.append("No obvious failure: the expected chunk is retrieved and ranked as expected.")

    return causes


def build_labelled_queries_payload() -> Dict[str, Any]:
    return {
        "description": "Labelled retrieval evaluation queries for the deterministic HRPolicyAI sample corpus.",
        "queries": LABELED_QUERIES,
    }


def evaluate_queries() -> Dict[str, Any]:
    query_results = []

    for label in LABELED_QUERIES:
        retrieved = retrieve_candidates(label["query_vector"], top_k=max(TOP_K_VALUES))

        per_query = {
            "id": label["id"],
            "query": label["query"],
            "expected_chunk_ids": label["expected_chunk_ids"],
            "expected_sections": label["expected_sections"],
            "notes": label["notes"],
            "retrieved": [
                {
                    "rank": rank,
                    "chunk_index": item["metadata"]["chunk_index"],
                    "section": item["metadata"]["section"],
                    "score": round(item["score"], 4),
                    "text": item["text"],
                }
                for rank, item in enumerate(retrieved, start=1)
            ],
            "recall_at_k": {},
            "precision_at_k": {},
            "top_1": {},
        }

        for k in TOP_K_VALUES:
            top_k_results = retrieved[:k]
            per_query["recall_at_k"][str(k)] = round(
                recall_at_k(top_k_results, label["expected_chunk_ids"]), 4
            )
            per_query["precision_at_k"][str(k)] = round(
                precision_at_k(top_k_results, label["expected_chunk_ids"], k), 4
            )

        per_query["top_1"] = per_query["retrieved"][0] if per_query["retrieved"] else {}
        per_query["failure_analysis"] = suggest_failure_causes(label, per_query)
        query_results.append(per_query)

    averages = {}
    for k in TOP_K_VALUES:
        recall_values = [query["recall_at_k"][str(k)] for query in query_results]
        precision_values = [query["precision_at_k"][str(k)] for query in query_results]
        averages[str(k)] = {
            "average_recall": round(sum(recall_values) / len(recall_values), 4),
            "average_precision": round(sum(precision_values) / len(precision_values), 4),
        }

    failed_queries = [
        query
        for query in query_results
        if query["recall_at_k"]["5"] < 1.0
        or query["top_1"].get("chunk_index") not in query["expected_chunk_ids"]
    ]

    return {
        "evaluation_configuration": {
            "candidate_count": max(TOP_K_VALUES),
            "k_values": TOP_K_VALUES,
            "retrieval_type": "deterministic cosine similarity over sample corpus",
        },
        "labelled_queries": LABELED_QUERIES,
        "query_results": query_results,
        "average_metrics": averages,
        "failed_queries": [query["id"] for query in failed_queries],
        "failure_summary": [
            {
                "id": query["id"],
                "query": query["query"],
                "likely_causes": query["failure_analysis"],
            }
            for query in failed_queries
        ],
    }


def build_text_report(results: Dict[str, Any]) -> str:
    lines = [
        "RETRIEVAL EVALUATION REPORT",
        "=" * 70,
        "Labelled query set:",
    ]

    for query in results["labelled_queries"]:
        lines.append(
            f"- {query['id']}: {query['query']} | expected chunk(s) {query['expected_chunk_ids']} | notes: {query['notes']}"
        )

    lines.extend(
        [
            "",
            "AVERAGE METRICS",
            "-" * 70,
        ]
    )

    for k in TOP_K_VALUES:
        metrics = results["average_metrics"][str(k)]
        lines.append(
            f"Recall@{k}: {metrics['average_recall']:.4f} | Precision@{k}: {metrics['average_precision']:.4f}"
        )

    lines.extend(
        [
            "",
            "PER-QUERY RESULTS",
            "-" * 70,
        ]
    )

    for query_result in results["query_results"]:
        lines.append(f"Query {query_result['id']}: {query_result['query']}")
        lines.append(
            f"  Expected chunks: {query_result['expected_chunk_ids']} | Top-1 chunk: {query_result['top_1'].get('chunk_index', 'None')}"
        )
        lines.append(
            f"  Recall@1: {query_result['recall_at_k']['1']:.4f} | Recall@3: {query_result['recall_at_k']['3']:.4f} | Recall@5: {query_result['recall_at_k']['5']:.4f}"
        )
        lines.append(
            f"  Precision@1: {query_result['precision_at_k']['1']:.4f} | Precision@3: {query_result['precision_at_k']['3']:.4f} | Precision@5: {query_result['precision_at_k']['5']:.4f}"
        )
        lines.append(f"  Failure analysis: {query_result['failure_analysis'][0]}")
        lines.append("  Top retrieved chunks:")

        for item in query_result["retrieved"]:
            lines.append(
                f"    - rank={item['rank']} | chunk_index={item['chunk_index']} | section={item['section']} | score={item['score']:.4f} | text={item['text']}"
            )

        lines.append("")

    lines.extend(
        [
            "FAILED OR LOW-SCORING CASES",
            "-" * 70,
        ]
    )

    if results["failure_summary"]:
        for failure in results["failure_summary"]:
            lines.append(f"- {failure['id']}: {failure['query']}")
            for cause in failure["likely_causes"]:
                lines.append(f"  * {cause}")
            lines.append("")
    else:
        lines.append("No failed or low-scoring queries were detected in this deterministic evaluation set.")

    return "\n".join(lines) + "\n"


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    labelled_queries_payload = build_labelled_queries_payload()
    LABELLED_QUERIES_FILE.write_text(
        json.dumps(labelled_queries_payload, indent=2) + "\n",
        encoding="utf-8",
    )

    results = evaluate_queries()
    RESULT_FILE.write_text(json.dumps(results, indent=2) + "\n", encoding="utf-8")
    RESULT_TEXT_FILE.write_text(build_text_report(results), encoding="utf-8")

    print(f"Saved labelled query set to {LABELLED_QUERIES_FILE}")
    print(f"Saved evaluation results to {RESULT_FILE}")
    print(f"Saved readable evaluation report to {RESULT_TEXT_FILE}")


if __name__ == "__main__":
    main()
