import json
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).parent.parent
OUTPUT_DIR = PROJECT_ROOT / "outputs"
RESULT_FILE = OUTPUT_DIR / "reranking_results.json"
RESULT_TEXT_FILE = OUTPUT_DIR / "reranking_results.txt"


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


QUERY = {
    "text": "How should a leave request be submitted?",
    "keywords": ["leave", "request", "submitted", "manager"],
    "query_vector": [0.95, 0.10, 0.00, 0.00],
}


INITIAL_CANDIDATE_COUNT = 6
FINAL_K = 3


def cosine_similarity(first: list[float], second: list[float]) -> float:
    if len(first) != len(second):
        raise ValueError("Vectors must have the same dimension.")

    first_norm = sum(value * value for value in first) ** 0.5
    second_norm = sum(value * value for value in second) ** 0.5
    if first_norm == 0 or second_norm == 0:
        return 0.0

    dot_product = sum(left * right for left, right in zip(first, second))
    return dot_product / (first_norm * second_norm)


def lexical_overlap_score(text: str, keywords: list[str]) -> float:
    lowered_text = text.lower()
    matches = sum(1 for keyword in keywords if keyword.lower() in lowered_text)
    return matches / max(len(keywords), 1)


def retrieve_candidates(query_vector: list[float], candidate_count: int) -> list[dict[str, Any]]:
    candidates = []
    for record in CORPUS:
        vector_score = cosine_similarity(query_vector, record["embedding"])
        candidates.append(
            {
                "vector_score": vector_score,
                "text": record["text"],
                "metadata": record["metadata"],
            }
        )

    candidates.sort(key=lambda item: item["vector_score"], reverse=True)
    return candidates[:candidate_count]


def re_rank_candidates(candidates: list[dict[str, Any]], query: dict[str, Any]) -> list[dict[str, Any]]:
    reranked = []

    for item in candidates:
        lexical_score = lexical_overlap_score(item["text"], query["keywords"])
        rerank_score = (0.55 * item["vector_score"]) + (0.45 * lexical_score)
        reranked.append(
            {
                **item,
                "lexical_overlap": lexical_score,
                "rerank_score": rerank_score,
            }
        )

    reranked.sort(key=lambda item: item["rerank_score"], reverse=True)
    return reranked


def build_reports() -> dict[str, Any]:
    candidates = retrieve_candidates(QUERY["query_vector"], INITIAL_CANDIDATE_COUNT)
    reranked = re_rank_candidates(candidates, QUERY)
    final_top_k = reranked[:FINAL_K]

    before_results = []
    after_results = []

    for rank, item in enumerate(candidates, start=1):
        before_results.append(
            {
                "rank": rank,
                "vector_score": round(item["vector_score"], 4),
                "text": item["text"],
                "section": item["metadata"]["section"],
                "source": item["metadata"]["source"],
                "chunk_index": item["metadata"]["chunk_index"],
            }
        )

    for rank, item in enumerate(reranked, start=1):
        after_results.append(
            {
                "rank": rank,
                "vector_score": round(item["vector_score"], 4),
                "lexical_overlap": round(item["lexical_overlap"], 4),
                "rerank_score": round(item["rerank_score"], 4),
                "text": item["text"],
                "section": item["metadata"]["section"],
                "source": item["metadata"]["source"],
                "chunk_index": item["metadata"]["chunk_index"],
            }
        )

    return {
        "query": QUERY["text"],
        "initial_candidate_count": INITIAL_CANDIDATE_COUNT,
        "final_k": FINAL_K,
        "before_rerank": before_results,
        "after_rerank": after_results,
        "final_selected_chunks": after_results[:FINAL_K],
        "improved_top_result": {
            "before": before_results[0]["section"],
            "after": after_results[0]["section"],
            "before_rank_1_text": before_results[0]["text"],
            "after_rank_1_text": after_results[0]["text"],
        },
    }


def build_text_report(payload: dict[str, Any]) -> str:
    lines = [
        "RE-RANKING DEMO",
        "=" * 70,
        f"Query: {payload['query']}",
        f"Candidate set size: {payload['initial_candidate_count']}",
        f"Final k: {payload['final_k']}",
        "",
        "INITIAL CANDIDATE ORDER (vector retrieval)",
        "-" * 70,
    ]

    for item in payload["before_rerank"]:
        lines.append(
            f"Rank {item['rank']}: vector_score={item['vector_score']:.4f} | section={item['section']} | source={item['source']} | chunk_index={item['chunk_index']} | text={item['text']}"
        )

    lines.extend(
        [
            "",
            "AFTER RE-RANKING",
            "-" * 70,
        ]
    )

    for item in payload["after_rerank"]:
        lines.append(
            f"Rank {item['rank']}: vector_score={item['vector_score']:.4f} | lexical_overlap={item['lexical_overlap']:.4f} | rerank_score={item['rerank_score']:.4f} | section={item['section']} | source={item['source']} | chunk_index={item['chunk_index']} | text={item['text']}"
        )

    lines.extend(
        [
            "",
            "FINAL SELECTED CHUNKS",
            "-" * 70,
        ]
    )

    for item in payload["final_selected_chunks"]:
        lines.append(
            f"Selected rank {item['rank']}: section={item['section']} | source={item['source']} | chunk_index={item['chunk_index']} | rerank_score={item['rerank_score']:.4f} | text={item['text']}"
        )

    lines.extend(
        [
            "",
            "IMPROVEMENT SUMMARY",
            "-" * 70,
            f"Before rerank top result section: {payload['improved_top_result']['before']}",
            f"After rerank top result section: {payload['improved_top_result']['after']}",
            f"Before rerank top result text: {payload['improved_top_result']['before_rank_1_text']}",
            f"After rerank top result text: {payload['improved_top_result']['after_rank_1_text']}",
            "",
            "Why this matters:",
            "- The initial vector ranking was driven by semantic similarity only.",
            "- The re-ranker adds an explicit keyword/phrase signal so direct answer chunks rise in the ranking.",
            "- The final top-k chunk set is therefore more directly relevant to the query than the raw vector order.",
        ]
    )

    return "\n".join(lines) + "\n"


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    payload = build_reports()
    RESULT_FILE.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    RESULT_TEXT_FILE.write_text(build_text_report(payload), encoding="utf-8")

    print(f"Saved reranking results to {RESULT_FILE}")
    print(f"Saved readable report to {RESULT_TEXT_FILE}")
    print("\nTop result after re-ranking:")
    print(payload["after_rerank"][0]["text"])


if __name__ == "__main__":
    main()
