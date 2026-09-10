import json
import sys
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from prompts.answer import render_answer_prompt

PROJECT_ROOT = Path(__file__).parent.parent
OUTPUT_DIR = PROJECT_ROOT / "outputs"
RESULT_FILE = OUTPUT_DIR / "rag_pipeline_results.json"
RESULT_TEXT_FILE = OUTPUT_DIR / "rag_pipeline_results.txt"


SAMPLE_QUERY = "How should a leave request be submitted?"
TOP_K = 3
MODEL_CONTEXT_TOKEN_BUDGET = 300
RESERVED_PROMPT_TOKENS = 120


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


def estimate_token_count(text: str) -> int:
    return max(1, len(text.split()))


def assemble_context(
    retrieved: list[dict[str, Any]],
    max_context_tokens: int = MODEL_CONTEXT_TOKEN_BUDGET,
    reserved_tokens: int = RESERVED_PROMPT_TOKENS,
) -> dict[str, Any]:
    """
    Stage 3: assemble the retrieval context for generation.

    Each chunk is formatted with a source marker such as [1], [2], etc., so the
    model can reference it in its final answer. The assembled context is trimmed to
    stay within a token budget while leaving room for instructions, the question,
    and the answer itself.
    """
    assembled = []
    formatted_context = []
    used_tokens = 0
    max_context_for_chunks = max_context_tokens - reserved_tokens

    for rank, item in enumerate(retrieved, start=1):
        marker = f"[{rank}]"
        chunk_payload = {
            "rank": rank,
            "marker": marker,
            "score": round(item["score"], 4),
            "section": item["metadata"]["section"],
            "source": item["metadata"]["source"],
            "chunk_index": item["metadata"]["chunk_index"],
            "text": item["text"],
        }

        block_text = (
            f"{marker} {chunk_payload['section']} ({chunk_payload['source']})\n"
            f"{chunk_payload['text']}"
        )
        block_tokens = estimate_token_count(block_text)

        if used_tokens + block_tokens > max_context_for_chunks:
            break

        used_tokens += block_tokens
        chunk_payload["block_text"] = block_text
        formatted_context.append(block_text)
        assembled.append(chunk_payload)

    context_text = "\n\n".join(formatted_context)

    return {
        "chunks": assembled,
        "context_text": context_text,
        "context_token_count": used_tokens,
        "remaining_token_budget": max_context_for_chunks - used_tokens,
        "max_context_tokens": max_context_tokens,
        "reserved_tokens": reserved_tokens,
    }


def generate_answer(query: str, assembled_context: dict[str, Any]) -> dict[str, Any]:
    """
    Stage 4: generate the final answer grounded in the retrieved context.

    This demo keeps generation deterministic and transparent. In a production system,
    this stage would call the chat model with the assembled context as the prompt.
    """
    top_context = assembled_context["chunks"][0]
    prompt = render_answer_prompt(
        context=assembled_context["context_text"],
        question=query,
    )

    answer_text = (
        f"According to {top_context['marker']} ({top_context['source']}), "
        f"{top_context['text']}"
    )

    return {
        "query": query,
        "prompt": prompt,
        "generated_answer": answer_text,
        "sources": [
            {
                "rank": item["rank"],
                "marker": item["marker"],
                "section": item["section"],
                "source": item["source"],
                "chunk_index": item["chunk_index"],
                "score": item["score"],
                "text": item["text"],
            }
            for item in assembled_context["chunks"]
        ],
    }


def build_payload(
    query: str,
    top_k: int = TOP_K,
    max_context_tokens: int = MODEL_CONTEXT_TOKEN_BUDGET,
    reserved_tokens: int = RESERVED_PROMPT_TOKENS,
) -> dict[str, Any]:
    query_vector = embed_query(query)
    retrieved = retrieve_candidates(query_vector, top_k=top_k)
    assembled = assemble_context(
        retrieved,
        max_context_tokens=max_context_tokens,
        reserved_tokens=reserved_tokens,
    )
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
        "3. assemble_context - package the top-ranked chunks with metadata, source markers, and a token budget.",
        "4. generate_answer - return an answer grounded in the chosen sources via a prompt with explicit grounding instructions.",
        "",
        f"Sample query: {payload['query']}",
        f"Top-k used: {payload['top_k']}",
        f"Query vector: {payload['query_vector']}",
        f"Context token budget: {payload['assembled_context']['max_context_tokens']}",
        f"Reserved prompt tokens: {payload['assembled_context']['reserved_tokens']}",
        f"Context tokens used: {payload['assembled_context']['context_token_count']}",
        f"Remaining token budget: {payload['assembled_context']['remaining_token_budget']}",
        "",
        "PROMPT CONTEXT INJECTED INTO MODEL",
        "-" * 70,
    ]

    lines.append(payload["generated_answer"]["prompt"])

    lines.extend(
        [
            "",
            "RETRIEVED SOURCES",
            "-" * 70,
        ]
    )

    for item in payload["assembled_context"]["chunks"]:
        lines.append(
            f"Rank {item['rank']}: marker={item['marker']} | section={item['section']} | source={item['source']} | chunk_index={item['chunk_index']} | score={item['score']:.4f} | text={item['text']}"
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
            f"Rank {item['rank']}: marker={item['marker']} | section={item['section']} | source={item['source']} | chunk_index={item['chunk_index']} | score={item['score']:.4f} | text={item['text']}"
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
