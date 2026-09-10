import json
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).parent.parent
OUTPUT_DIR = PROJECT_ROOT / "outputs"
RESULT_FILE = OUTPUT_DIR / "filtered_search_results.json"
RESULT_TEXT_FILE = OUTPUT_DIR / "filtered_search_results.txt"


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
]


QUERY = "How many paid annual leave days can an employee take?"
QUERY_VECTOR = [1.0, 0.20, 0.00, 0.00]
FILTER = {"section": "Annual leave"}
KEYWORDS = ["annual", "leave"]


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
        if metadata.get(key) != value:
            return False
    return True


def retrieve(query_vector: list[float], top_k: int = 3, metadata_filter: dict[str, Any] | None = None) -> list[dict[str, Any]]:
    ranked: list[dict[str, Any]] = []

    for record in CORPUS:
        if metadata_matches(record["metadata"], metadata_filter):
            ranked.append(
                {
                    "score": cosine_similarity(query_vector, record["embedding"]),
                    "text": record["text"],
                    "metadata": record["metadata"],
                }
            )

    ranked.sort(key=lambda item: item["score"], reverse=True)
    return ranked[:top_k]


def keyword_score(text: str, keywords: list[str]) -> int:
    lowered_text = text.lower()
    return sum(1 for keyword in keywords if keyword.lower() in lowered_text)


def hybrid_rank(vector_results: list[dict[str, Any]], keywords: list[str], vector_weight: float = 0.8, keyword_weight: float = 0.2) -> list[dict[str, Any]]:
    ranked = []
    for item in vector_results:
        lexical = keyword_score(item["text"], keywords)
        combined = (vector_weight * item["score"]) + (keyword_weight * lexical)
        ranked.append(
            {
                **item,
                "keyword_score": lexical,
                "hybrid_score": combined,
            }
        )
    return sorted(ranked, key=lambda item: item["hybrid_score"], reverse=True)


def show_results(label: str, results: list[dict[str, Any]]) -> list[dict[str, Any]]:
    print(f"\n{label}")
    for item in results:
        print(f"score: {item['score']:.4f}")
        print(f"source: {item['metadata']['source']}")
        print(f"section: {item['metadata'].get('section')}")
        if "hybrid_score" in item:
            print(f"keyword_score: {item['keyword_score']}")
            print(f"hybrid_score: {item['hybrid_score']:.4f}")
        print(f"text: {item['text']}")
        print("-" * 60)
    return results


def build_results_payload() -> dict[str, Any]:
    unfiltered = retrieve(QUERY_VECTOR, top_k=3)
    filtered = retrieve(QUERY_VECTOR, top_k=3, metadata_filter=FILTER)
    hybrid = hybrid_rank(filtered, KEYWORDS)

    return {
        "query": QUERY,
        "filter": FILTER,
        "keywords": KEYWORDS,
        "unfiltered_results": unfiltered,
        "filtered_results": filtered,
        "hybrid_results": hybrid,
        "precision_summary": {
            "unfiltered_top_result_section": unfiltered[0]["metadata"]["section"],
            "filtered_top_result_section": filtered[0]["metadata"]["section"],
            "filter_improves_precision": filtered[0]["metadata"]["section"] == FILTER["section"],
            "relevant_results_removed": len(unfiltered) > len(filtered),
        },
    }


def build_text_report(payload: dict[str, Any]) -> str:
    lines = [
        "METADATA FILTERING & HYBRID SEARCH DEMO",
        "=" * 70,
        f"Query: {payload['query']}",
        f"Metadata filter: {json.dumps(payload['filter'], sort_keys=True)}",
        f"Hybrid keywords: {', '.join(payload['keywords'])}",
        "",
        "UNFILTERED RESULTS",
        "-" * 70,
    ]

    for index, result in enumerate(payload["unfiltered_results"], start=1):
        lines.extend(
            [
                f"Rank {index} score: {result['score']:.4f}",
                f"Rank {index} section: {result['metadata'].get('section')}",
                f"Rank {index} source: {result['metadata'].get('source')}",
                f"Rank {index} text: {result['text']}",
                "",
            ]
        )

    lines.extend(["FILTERED RESULTS", "-" * 70])

    for index, result in enumerate(payload["filtered_results"], start=1):
        lines.extend(
            [
                f"Rank {index} score: {result['score']:.4f}",
                f"Rank {index} section: {result['metadata'].get('section')}",
                f"Rank {index} source: {result['metadata'].get('source')}",
                f"Rank {index} text: {result['text']}",
                "",
            ]
        )

    lines.extend(["HYBRID RESULTS", "-" * 70])

    for index, result in enumerate(payload["hybrid_results"], start=1):
        lines.extend(
            [
                f"Rank {index} score: {result['score']:.4f}",
                f"Rank {index} keyword_score: {result['keyword_score']}",
                f"Rank {index} hybrid_score: {result['hybrid_score']:.4f}",
                f"Rank {index} section: {result['metadata'].get('section')}",
                f"Rank {index} source: {result['metadata'].get('source')}",
                f"Rank {index} text: {result['text']}",
                "",
            ]
        )

    lines.extend(
        [
            "PRECISION SUMMARY",
            "-" * 70,
            f"Unfiltered top result section: {payload['precision_summary']['unfiltered_top_result_section']}",
            f"Filtered top result section: {payload['precision_summary']['filtered_top_result_section']}",
            f"Filter improves precision: {payload['precision_summary']['filter_improves_precision']}",
            f"Relevant results removed by filter: {payload['precision_summary']['relevant_results_removed']}",
            "",
            "Why this matters:",
            "- Metadata filtering scopes retrieval to the relevant slice of the corpus.",
            "- Hybrid search adds an exact-term signal when keyword matches matter.",
            "- Filtering improves precision when the metadata reflects the user's intent.",
        ]
    )

    return "\n".join(lines) + "\n"


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    payload = build_results_payload()
    RESULT_FILE.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    RESULT_TEXT_FILE.write_text(build_text_report(payload), encoding="utf-8")

    print("Metadata filtering and hybrid search demo results written to outputs/filtered_search_results.json")
    print("Readable report written to outputs/filtered_search_results.txt")
    show_results("UNFILTERED", payload["unfiltered_results"])
    show_results("FILTERED", payload["filtered_results"])
    show_results("HYBRID FILTERED", payload["hybrid_results"])


if __name__ == "__main__":
    main()
