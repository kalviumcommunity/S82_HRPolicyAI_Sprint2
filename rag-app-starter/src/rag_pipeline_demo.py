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


def extract_query_terms(query: str) -> set[str]:
    stopwords = {
        "a", "an", "and", "are", "as", "at", "be", "for", "from", "how", "in", "is",
        "it", "of", "on", "or", "that", "the", "this", "to", "what", "when", "where",
        "which", "who", "why", "with", "should", "do", "does", "did", "can", "could",
        "would", "may", "might", "will", "before", "after", "into",
    }
    tokens = {token.lower() for token in query.replace("?", " ").split() if token.lower() not in stopwords}
    return tokens


def context_supports_query(query: str, assembled_context: dict[str, Any]) -> tuple[bool, list[str]]:
    query_terms = extract_query_terms(query)
    if not query_terms:
        return False, []

    supporting_markers: list[str] = []
    for chunk in assembled_context["chunks"]:
        chunk_terms = extract_query_terms(chunk["text"])
        if query_terms.intersection(chunk_terms):
            supporting_markers.append(chunk["marker"])

    return bool(supporting_markers), supporting_markers


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
    prompt = render_answer_prompt(
        context=assembled_context["context_text"],
        question=query,
    )

    supported, supporting_markers = context_supports_query(query, assembled_context)

    if not assembled_context["chunks"] or not supported:
        answer_text = "I don't know based on the provided information."
        grounded = False
        support_reason = (
            "No retrieved chunk contained enough overlapping terms to support the answer."
            if assembled_context["chunks"]
            else "No retrieved context was provided."
        )
        top_context = None
    else:
        top_context = assembled_context["chunks"][0]
        answer_text = (
            f"According to {top_context['marker']} ({top_context['source']}), "
            f"{top_context['text']}"
        )
        grounded = True
        support_reason = f"Supported by markers {supporting_markers}."

    return {
        "query": query,
        "prompt": prompt,
        "generated_answer": answer_text,
        "grounded": grounded,
        "source_accuracy": {
            "uses_only_context": grounded,
            "supporting_markers": supporting_markers,
            "support_reason": support_reason,
        },
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


def build_without_retrieval_payload(query: str) -> dict[str, Any]:
    empty_context = {
        "chunks": [],
        "context_text": "",
        "context_token_count": 0,
        "remaining_token_budget": MODEL_CONTEXT_TOKEN_BUDGET - RESERVED_PROMPT_TOKENS,
        "max_context_tokens": MODEL_CONTEXT_TOKEN_BUDGET,
        "reserved_tokens": RESERVED_PROMPT_TOKENS,
    }

    generated = generate_answer(query, empty_context)

    return {
        "query": query,
        "retrieval_enabled": False,
        "retrieved_chunks": [],
        "assembled_context": empty_context,
        "generated_answer": generated,
    }


def build_grounding_comparison() -> dict[str, Any]:
    baseline_query = SAMPLE_QUERY
    no_context_query = "What is the company policy for flexible work schedules?"

    with_retrieval = build_payload(baseline_query, top_k=TOP_K)
    without_retrieval = build_without_retrieval_payload(baseline_query)
    missing_context_case = build_payload(no_context_query, top_k=TOP_K)

    return {
        "title": "Grounding comparison: with retrieval vs without retrieval",
        "baseline_query": baseline_query,
        "missing_context_query": no_context_query,
        "with_retrieval": with_retrieval,
        "without_retrieval": without_retrieval,
        "missing_context_case": missing_context_case,
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
        "GROUNDING COMPARISON",
        "-" * 70,
    ]

    for label, result in (
        ("WITH RETRIEVAL", payload["with_retrieval"]),
        ("WITHOUT RETRIEVAL", payload["without_retrieval"]),
        ("MISSING CONTEXT CASE", payload["missing_context_case"]),
    ):
        lines.extend(
            [
                f"{label}",
                f"- Query: {result['query']}",
                f"- Grounded: {result['generated_answer']['grounded']}",
                f"- Answer: {result['generated_answer']['generated_answer']}",
                f"- Source accuracy: {result['generated_answer']['source_accuracy']}",
                "",
            ]
        )

    lines.extend(
        [
            "WITH RETRIEVAL DETAIL",
            "-" * 70,
        ]
    )

    current = payload["with_retrieval"]
    lines.append(f"Sample query: {current['query']}")
    lines.append(f"Top-k used: {current['top_k']}")
    lines.append(f"Query vector: {current['query_vector']}")
    lines.append(f"Context token budget: {current['assembled_context']['max_context_tokens']}")
    lines.append(f"Reserved prompt tokens: {current['assembled_context']['reserved_tokens']}")
    lines.append(f"Context tokens used: {current['assembled_context']['context_token_count']}")
    lines.append(f"Remaining token budget: {current['assembled_context']['remaining_token_budget']}")
    lines.append("")
    lines.append("PROMPT CONTEXT INJECTED INTO MODEL")
    lines.append("-" * 70)
    lines.append(current["generated_answer"]["prompt"])

    lines.extend(
        [
            "",
            "RETRIEVED SOURCES",
            "-" * 70,
        ]
    )

    for item in current["assembled_context"]["chunks"]:
        lines.append(
            f"Rank {item['rank']}: marker={item['marker']} | section={item['section']} | source={item['source']} | chunk_index={item['chunk_index']} | score={item['score']:.4f} | text={item['text']}"
        )

    lines.extend(
        [
            "",
            "GENERATED ANSWER",
            "-" * 70,
            current["generated_answer"]["generated_answer"],
            "",
            "RETURNED SOURCES",
            "-" * 70,
        ]
    )

    for item in current["generated_answer"]["sources"]:
        lines.append(
            f"Rank {item['rank']}: marker={item['marker']} | section={item['section']} | source={item['source']} | chunk_index={item['chunk_index']} | score={item['score']:.4f} | text={item['text']}"
        )

    return "\n".join(lines) + "\n"


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    payload = build_grounding_comparison()

    RESULT_FILE.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    RESULT_TEXT_FILE.write_text(build_text_report(payload), encoding="utf-8")

    print(f"Saved pipeline results to {RESULT_FILE}")
    print(f"Saved readable pipeline report to {RESULT_TEXT_FILE}")
    print("\nWith retrieval answer:")
    print(payload["with_retrieval"]["generated_answer"]["generated_answer"])
    print("\nWithout retrieval answer:")
    print(payload["without_retrieval"]["generated_answer"]["generated_answer"])
    print("\nMissing-context fallback answer:")
    print(payload["missing_context_case"]["generated_answer"]["generated_answer"])


if __name__ == "__main__":
    main()
