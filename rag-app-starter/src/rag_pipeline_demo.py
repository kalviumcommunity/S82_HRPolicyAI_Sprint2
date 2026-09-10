import json
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).parent.parent
OUTPUT_DIR = PROJECT_ROOT / "outputs"
RESULT_FILE = OUTPUT_DIR / "rag_pipeline_results.json"
RESULT_TEXT_FILE = OUTPUT_DIR / "rag_pipeline_results.txt"


SAMPLE_QUERY = "How should a leave request be submitted?"
TOP_K = 3


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


def cosine_similarity(first: list[float], second: list[float]) -> float:
    if len(first) != len(second):
        raise ValueError("Vectors must have the same dimension.")

    first_norm = sum(value * value for value in first) ** 0.5
    second_norm = sum(value * value for value in second) ** 0.5
    if first_norm == 0 or second_norm == 0:
        return 0.0

    dot_product = sum(left * right for left, right in zip(first, second))
    return dot_product / (first_norm * second_norm)


def embed_query(query: str) -> list[float]:
    """
    Stage 1: embed the incoming query.

    This is a deterministic demo embedding. In a live app, this stage would call an
    embedding model (for example OpenAI embeddings) and return an embedding vector.
    """
    lowered = query.lower()
    vector = [0.0, 0.0, 0.0, 0.0]

    if "annual" in lowered or "leave" in lowered:
        vector[0] += 0.70
    if "request" in lowered or "submitted" in lowered or "manager" in lowered:
        vector[1] += 0.95
    if "sick" in lowered:
        vector[2] += 1.00
    if "parent" in lowered or "caregiver" in lowered:
        vector[3] += 1.00

    return vector


def retrieve_candidates(query_vector: list[float], top_k: int = TOP_K) -> list[dict[str, Any]]:
    """
    Stage 2: retrieve top-k candidate chunks.
    """
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


def assemble_context(retrieved: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """
    Stage 3: assemble the retrieval context for generation.
    """
    assembled = []

    for rank, item in enumerate(retrieved, start=1):
        assembled.append(
            {
                "rank": rank,
                "score": round(item["score"], 4),
                "section": item["metadata"]["section"],
                "source": item["metadata"]["source"],
                "chunk_index": item["metadata"]["chunk_index"],
                "text": item["text"],
            }
        )

    return assembled


def generate_answer(query: str, assembled_context: list[dict[str, Any]]) -> dict[str, Any]:
    """
    Stage 4: generate the final answer grounded in the retrieved context.

    This demo keeps generation deterministic and transparent. In a production system,
    this stage would call the chat model with the assembled context as the prompt.
    """
    top_context = assembled_context[0]

    answer_text = (
        f"According to the {top_context['section']} policy section ({top_context['source']}), "
        f"{top_context['text']}"
    )

    return {
        "query": query,
        "generated_answer": answer_text,
        "sources": [
            {
                "rank": item["rank"],
                "section": item["section"],
                "source": item["source"],
                "chunk_index": item["chunk_index"],
                "score": item["score"],
                "text": item["text"],
            }
            for item in assembled_context
        ],
    }


def build_payload(query: str, top_k: int = TOP_K) -> dict[str, Any]:
    query_vector = embed_query(query)
    retrieved = retrieve_candidates(query_vector, top_k=top_k)
    assembled = assemble_context(retrieved)
    generated = generate_answer(query, assembled)

    return {
        "query": query,
        "top_k": top_k,
        "query_vector": query_vector,
        "retrieved_chunks": retrieved,
        "assembled_context": assembled,
        "generated_answer": generated,
    }


def build_text_report(payload: dict[str, Any]) -> str:
    lines = [
        "QUERY-TO-ANSWER RAG FLOW DEMO",
        "=" * 70,
        "Flow overview:",
        "1. embed_query - create a query vector from the incoming user question.",
        "2. retrieve_candidates - score corpus chunks against that vector.",
        "3. assemble_context - package the top-ranked chunks with metadata for generation.",
        "4. generate_answer - return an answer grounded in the chosen sources.",
        "",
        f"Sample query: {payload['query']}",
        f"Top-k used: {payload['top_k']}",
        f"Query vector: {payload['query_vector']}",
        "",
        "RETRIEVED SOURCES",
        "-" * 70,
    ]

    for item in payload["assembled_context"]:
        lines.append(
            f"Rank {item['rank']}: section={item['section']} | source={item['source']} | chunk_index={item['chunk_index']} | score={item['score']:.4f} | text={item['text']}"
        )

    lines.extend(
        [
            "",
            "GENERATED ANSWER",
            "-" * 70,
            payload["generated_answer"]["generated_answer"],
            "",
            "RETURNED SOURCES",
            "-" * 70,
        ]
    )

    for item in payload["generated_answer"]["sources"]:
        lines.append(
            f"Rank {item['rank']}: section={item['section']} | source={item['source']} | chunk_index={item['chunk_index']} | score={item['score']:.4f} | text={item['text']}"
        )

    return "\n".join(lines) + "\n"


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    payload = build_payload(SAMPLE_QUERY, top_k=TOP_K)

    RESULT_FILE.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    RESULT_TEXT_FILE.write_text(build_text_report(payload), encoding="utf-8")

    print(f"Saved pipeline results to {RESULT_FILE}")
    print(f"Saved readable pipeline report to {RESULT_TEXT_FILE}")
    print("\nGenerated answer:")
    print(payload["generated_answer"]["generated_answer"])
    print("\nReturned sources:")
    for source in payload["generated_answer"]["sources"]:
        print(f"- {source['section']} ({source['source']}): {source['text']}")


if __name__ == "__main__":
    main()
