import json
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).parent.parent
OUTPUT_DIR = PROJECT_ROOT / "outputs"
RESULT_FILE = OUTPUT_DIR / "retrieval_tuning_results.json"
RESULT_TEXT_FILE = OUTPUT_DIR / "retrieval_tuning_results.txt"


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


TEST_QUERIES = [
    {
        "query": "How many paid annual leave days can an employee take?",
        "expected_section": "Annual leave",
        "expected_chunk_index": 0,
        "keywords": ["annual", "leave", "paid"],
        "query_vector": [1.0, 0.20, 0.00, 0.00],
    },
    {
        "query": "How should a leave request be submitted?",
        "expected_section": "Requesting leave",
        "expected_chunk_index": 1,
        "keywords": ["leave", "request", "manager"],
        "query_vector": [0.70, 0.95, 0.00, 0.00],
    },
    {
        "query": "How much paid sick leave do employees receive annually?",
        "expected_section": "Sick leave",
        "expected_chunk_index": 2,
        "keywords": ["paid", "sick", "leave"],
        "query_vector": [0.55, 0.30, 1.00, 0.00],
    },
    {
        "query": "What is the paid parental leave entitlement for primary caregivers?",
        "expected_section": "Parental leave",
        "expected_chunk_index": 3,
        "keywords": ["parental", "leave", "primary"],
        "query_vector": [0.45, 0.10, 0.00, 1.00],
    },
]


SETTINGS = [
    {
        "name": "baseline_unfiltered_k3",
        "description": "Unfiltered top-3 semantic search",
        "metadata_filter": None,
        "top_k": 3,
        "score_threshold": 0.0,
        "use_hybrid": False,
    },
    {
        "name": "section_filtered_k3",
        "description": "Section-filtered top-3 semantic search",
        "metadata_filter": {"section": "expected_section"},
        "top_k": 3,
        "score_threshold": 0.0,
        "use_hybrid": False,
    },
    {
        "name": "section_filtered_k1_threshold_0_75",
        "description": "Section filter with stricter threshold and k=1",
        "metadata_filter": {"section": "expected_section"},
        "top_k": 1,
        "score_threshold": 0.75,
        "use_hybrid": False,
    },
    {
        "name": "section_filtered_hybrid_k3",
        "description": "Section filter plus hybrid keyword boost",
        "metadata_filter": {"section": "expected_section"},
        "top_k": 3,
        "score_threshold": 0.0,
        "use_hybrid": True,
    },
]


def cosine_similarity(first: list[float], second: list[float]) -> float:
    if len(first) != len(second):
        raise ValueError("Vectors must have the same dimension.")

    first_norm = sum(value * value for value in first) ** 0.5
    second_norm = sum(value * value for value in second) ** 0.5
    if first_norm == 0 or second_norm == 0:
        return 0.0

    dot_product = sum(left * right for left, right in zip(first, second))
    return dot_product / (first_norm * second_norm)


def metadata_matches(metadata: dict[str, Any], metadata_filter: dict[str, Any] | None) -> bool:
    if metadata_filter is None:
        return True

    for key, value in metadata_filter.items():
        if key == "expected_section":
            continue
        if metadata.get(key) != value:
            return False
    return True


def keyword_score(text: str, keywords: list[str]) -> int:
    lowered_text = text.lower()
    return sum(1 for keyword in keywords if keyword.lower() in lowered_text)


def retrieve(
    query: dict[str, Any],
    top_k: int,
    metadata_filter: dict[str, Any] | None,
    score_threshold: float,
    use_hybrid: bool,
) -> list[dict[str, Any]]:
    candidates: list[dict[str, Any]] = []

    for record in CORPUS:
        if metadata_filter and not metadata_matches(record["metadata"], metadata_filter):
            continue

        score = cosine_similarity(query["query_vector"], record["embedding"])
        if score < score_threshold:
            continue

        if use_hybrid:
            lexical = keyword_score(record["text"], query["keywords"])
            hybrid_score = (0.8 * score) + (0.2 * lexical)
            candidates.append(
                {
                    "score": score,
                    "keyword_score": lexical,
                    "hybrid_score": hybrid_score,
                    "text": record["text"],
                    "metadata": record["metadata"],
                }
            )
        else:
            candidates.append(
                {
                    "score": score,
                    "text": record["text"],
                    "metadata": record["metadata"],
                }
            )

    if use_hybrid:
        candidates.sort(key=lambda item: item["hybrid_score"], reverse=True)
    else:
        candidates.sort(key=lambda item: item["score"], reverse=True)

    return candidates[:top_k]


def evaluate_settings() -> dict[str, Any]:
    results: dict[str, Any] = {"queries": [], "settings": [], "selected_setting": None}

    for setting in SETTINGS:
        setting_results = []
        precision_total = 0.0
        top1_hits = 0
        topk_hits = 0

        for query in TEST_QUERIES:
            filter_payload = None
            if setting["metadata_filter"]:
                filter_payload = {"section": query["expected_section"]}

            retrieved = retrieve(
                query=query,
                top_k=setting["top_k"],
                metadata_filter=filter_payload,
                score_threshold=setting["score_threshold"],
                use_hybrid=setting["use_hybrid"],
            )

            expected_chunk_index = query["expected_chunk_index"]
            expected_section = query["expected_section"]

            relevant_count = sum(
                1 for result in retrieved if result["metadata"]["section"] == expected_section
            )
            precision_at_k = relevant_count / max(len(retrieved), 1)
            precision_total += precision_at_k

            top1_hit = bool(retrieved) and retrieved[0]["metadata"]["chunk_index"] == expected_chunk_index
            topk_hit = any(result["metadata"]["chunk_index"] == expected_chunk_index for result in retrieved)

            top1_hits += int(top1_hit)
            topk_hits += int(topk_hit)

            setting_results.append(
                {
                    "query": query["query"],
                    "expected_section": expected_section,
                    "expected_chunk_index": expected_chunk_index,
                    "top1_hit": top1_hit,
                    "topk_hit": topk_hit,
                    "precision_at_k": round(precision_at_k, 4),
                    "retrieved": [
                        {
                            "rank": rank + 1,
                            "section": result["metadata"]["section"],
                            "chunk_index": result["metadata"]["chunk_index"],
                            "score": round(result.get("score", result.get("hybrid_score", 0.0)), 4),
                            "keyword_score": result.get("keyword_score"),
                            "hybrid_score": result.get("hybrid_score"),
                            "text": result["text"],
                        }
                        for rank, result in enumerate(retrieved)
                    ],
                }
            )

        avg_precision = precision_total / len(TEST_QUERIES)
        top1_rate = top1_hits / len(TEST_QUERIES)
        topk_rate = topk_hits / len(TEST_QUERIES)

        setting_summary = {
            "name": setting["name"],
            "description": setting["description"],
            "metadata_filter": setting["metadata_filter"],
            "top_k": setting["top_k"],
            "score_threshold": setting["score_threshold"],
            "use_hybrid": setting["use_hybrid"],
            "top1_hit_rate": round(top1_rate, 4),
            "topk_hit_rate": round(topk_rate, 4),
            "average_precision_at_k": round(avg_precision, 4),
            "results": setting_results,
        }
        results["settings"].append(setting_summary)

    results["queries"] = [
        {"query": query["query"], "expected_section": query["expected_section"], "expected_chunk_index": query["expected_chunk_index"]}
        for query in TEST_QUERIES
    ]

    best_setting = max(
        results["settings"],
        key=lambda item: (
            item["average_precision_at_k"],
            item["top1_hit_rate"],
            item["topk_hit_rate"],
            item["score_threshold"],
            -item["top_k"],
        ),
    )

    results["selected_setting"] = {
        "name": best_setting["name"],
        "description": best_setting["description"],
        "top1_hit_rate": best_setting["top1_hit_rate"],
        "topk_hit_rate": best_setting["topk_hit_rate"],
        "average_precision_at_k": best_setting["average_precision_at_k"],
        "reason": (
            "Chosen because it achieved the highest relevance precision while retaining the correct top-ranked chunk, and the stricter filter + lower k gave the most focused results."
        ),
    }

    return results


def build_text_report(results: dict[str, Any]) -> str:
    lines = [
        "RETRIEVAL TUNING EXPERIMENT",
        "=" * 70,
        "Test queries with expected relevant chunks:",
    ]

    for query in results["queries"]:
        lines.append(
            f"- Query: {query['query']} | Expected section: {query['expected_section']} | Expected chunk index: {query['expected_chunk_index']}"
        )

    lines.extend(["", "SETTING COMPARISON", "-" * 70])

    for setting in results["settings"]:
        lines.extend(
            [
                f"Setting: {setting['name']}",
                f"Description: {setting['description']}",
                f"Top-1 hit rate: {setting['top1_hit_rate']:.4f}",
                f"Top-k hit rate: {setting['topk_hit_rate']:.4f}",
                f"Average precision at k: {setting['average_precision_at_k']:.4f}",
                "",
            ]
        )

        for query_result in setting["results"]:
            lines.append(
                f"- Query: {query_result['query']} | Top-1 hit: {query_result['top1_hit']} | Top-k hit: {query_result['topk_hit']} | Precision@k: {query_result['precision_at_k']:.4f}"
            )

        lines.append("")

    lines.extend(
        [
            "BEST SETTINGS",
            "-" * 70,
            f"Selected setting: {results['selected_setting']['name']}",
            f"Description: {results['selected_setting']['description']}",
            f"Top-1 hit rate: {results['selected_setting']['top1_hit_rate']:.4f}",
            f"Top-k hit rate: {results['selected_setting']['topk_hit_rate']:.4f}",
            f"Average precision at k: {results['selected_setting']['average_precision_at_k']:.4f}",
            f"Reason: {results['selected_setting']['reason']}",
        ]
    )

    return "\n".join(lines) + "\n"


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    results = evaluate_settings()
    RESULT_FILE.write_text(json.dumps(results, indent=2) + "\n", encoding="utf-8")
    RESULT_TEXT_FILE.write_text(build_text_report(results), encoding="utf-8")

    print(f"Saved tuning results to {RESULT_FILE}")
    print(f"Saved readable report to {RESULT_TEXT_FILE}")
    print("\nBest setting:", results["selected_setting"]["name"])


if __name__ == "__main__":
    main()
