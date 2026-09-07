import json
import os
import time
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from openai import OpenAI
import tiktoken


SAMPLE_CHUNKS = [
    {
        "text": "Employees may take up to 20 days of paid annual leave each year.",
        "metadata": {"source": "sample_leave_policy.txt", "chunk_index": 0, "section": "Annual leave"},
    },
    {
        "text": "Leave requests should be submitted to a manager at least two weeks in advance.",
        "metadata": {"source": "sample_leave_policy.txt", "chunk_index": 1, "section": "Requesting leave"},
    },
]


SAMPLE_QUERY = "How many paid annual leave days can an employee take?"


def chunk_key(chunk: dict[str, Any]) -> str:
    """Create a stable identity so unchanged chunks are not embedded twice."""
    return json.dumps(
        {"text": chunk["text"], "metadata": chunk.get("metadata", {})},
        sort_keys=True,
    )


def estimate_tokens(texts: list[str]) -> int:
    """Estimate input tokens for cost reporting without sending another request."""
    encoder = tiktoken.get_encoding("cl100k_base")
    return sum(len(encoder.encode(text)) for text in texts)


def is_retryable_error(error: Exception) -> bool:
    """Recognize rate limits and temporary provider/network failures."""
    status_code = getattr(error, "status_code", None) or getattr(error, "status", None)
    error_name = type(error).__name__.lower()
    return status_code == 429 or (isinstance(status_code, int) and status_code >= 500) or any(
        marker in error_name
        for marker in ("ratelimit", "timeout", "connection", "serviceunavailable", "internalserver")
    )


def batch_embed_chunks(
    chunks: list[dict[str, Any]],
    client: Any,
    model: str,
    existing_records: list[dict[str, Any]] | None = None,
    batch_size: int = 2,
    max_retries: int = 3,
    initial_backoff: float = 1.0,
    sleep_fn: Any = time.sleep,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """Embed new chunks in batches, retry temporary failures, and report the run."""
    if batch_size <= 0:
        raise ValueError("batch_size must be greater than zero.")
    if max_retries < 0:
        raise ValueError("max_retries cannot be negative.")

    stored_by_key = {chunk_key(record): record for record in (existing_records or []) if record.get("embedding")}
    records = list(stored_by_key.values())
    pending = [chunk for chunk in chunks if chunk_key(chunk) not in stored_by_key]
    failures: list[dict[str, Any]] = []
    generated = 0
    retries = 0
    estimated_tokens = 0

    for batch_start in range(0, len(pending), batch_size):
        batch = pending[batch_start:batch_start + batch_size]
        texts = [chunk["text"] for chunk in batch]
        estimated_tokens += estimate_tokens(texts)
        response = None
        for attempt in range(max_retries + 1):
            try:
                response = client.embeddings.create(model=model, input=texts)
                break
            except Exception as error:
                if not is_retryable_error(error) or attempt == max_retries:
                    failures.append(
                        {
                            "batch_start": batch_start,
                            "chunk_count": len(batch),
                            "error": str(error),
                            "attempts": attempt + 1,
                        }
                    )
                    break
                retries += 1
                sleep_fn(initial_backoff * (2 ** attempt))

        if response is None:
            continue
        if len(response.data) != len(batch):
            failures.append(
                {
                    "batch_start": batch_start,
                    "chunk_count": len(batch),
                    "error": "API returned a different number of vectors than chunks.",
                    "attempts": 1,
                }
            )
            continue
        for chunk, item in zip(batch, response.data):
            records.append(
                {
                    "text": chunk["text"],
                    "metadata": chunk.get("metadata", {}),
                    "embedding": item.embedding,
                }
            )
            generated += 1

    cost_per_1k = float(os.getenv("EMBEDDING_COST_PER_1K_TOKENS", "0.00002"))
    summary = {
        "total_chunks": len(chunks),
        "batch_size": batch_size,
        "batches_attempted": (len(pending) + batch_size - 1) // batch_size,
        "embeddings_generated": generated,
        "skipped_chunks": len(chunks) - len(pending),
        "failed_batches": len(failures),
        "retries": retries,
        "estimated_input_tokens": estimated_tokens,
        "approximate_cost_usd": round(estimated_tokens / 1000 * cost_per_1k, 8),
        "failures": failures,
    }
    return records, summary


def embed_chunks(chunks: list[dict[str, Any]], client: Any, model: str) -> list[dict[str, Any]]:
    """Embed chunks in one batch while preserving retrieval context."""
    if not chunks:
        return []

    response = client.embeddings.create(
        model=model,
        input=[chunk["text"] for chunk in chunks],
    )

    if len(response.data) != len(chunks):
        raise ValueError("The embeddings API returned a different number of vectors than chunks.")

    records = []
    for chunk, item in zip(chunks, response.data):
        records.append(
            {
                "text": chunk["text"],
                "metadata": chunk["metadata"],
                "embedding": item.embedding,
            }
        )

    dimensions = {len(record["embedding"]) for record in records}
    if len(dimensions) != 1:
        raise ValueError("Embedding vectors do not have the same dimension.")

    return records


def cosine_similarity(first: list[float], second: list[float]) -> float:
    """Compare vector direction, returning a score between -1 and 1."""
    if len(first) != len(second):
        raise ValueError("Vectors must have the same dimension.")

    first_norm = sum(value * value for value in first) ** 0.5
    second_norm = sum(value * value for value in second) ** 0.5
    if first_norm == 0 or second_norm == 0:
        return 0.0

    dot_product = sum(left * right for left, right in zip(first, second))
    return dot_product / (first_norm * second_norm)


def rank_chunks(query_embedding: list[float], records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Return chunk records ordered from most to least similar to a query."""
    ranked = []
    for record in records:
        ranked.append(
            {
                "score": cosine_similarity(query_embedding, record["embedding"]),
                "text": record["text"],
                "metadata": record["metadata"],
            }
        )
    return sorted(ranked, key=lambda result: result["score"], reverse=True)


def embed_query(query: str, client: Any, model: str) -> list[float]:
    """Embed one user query with the same model used for document chunks."""
    response = client.embeddings.create(model=model, input=[query])
    if len(response.data) != 1:
        raise ValueError("The embeddings API did not return exactly one query vector.")
    return response.data[0].embedding


def build_similarity_report(
    query: str, ranked_results: list[dict[str, Any]], model: str
) -> str:
    """Create a reviewable report showing every ranked result and its provenance."""
    lines = [
        "SIMILARITY RANKING VERIFICATION",
        "=" * 60,
        f"Model: {model}",
        "Metric: cosine similarity",
        "Why: cosine compares vector direction, which captures semantic orientation while reducing the effect of vector magnitude.",
        f"Query: {query}",
        "",
        "RANKED RESULTS",
        "-" * 60,
    ]
    for rank, result in enumerate(ranked_results, start=1):
        lines.extend(
            [
                f"Rank {rank} score: {result['score']:.6f}",
                f"Rank {rank} text: {result['text']}",
                f"Rank {rank} metadata: {json.dumps(result['metadata'], sort_keys=True)}",
            ]
        )
    if ranked_results:
        lines.extend(
            [
                "",
                f"Most similar: {ranked_results[0]['text']} ({ranked_results[0]['score']:.6f})",
                f"Least similar: {ranked_results[-1]['text']} ({ranked_results[-1]['score']:.6f})",
            ]
        )
    return "\n".join(lines)


def build_report(records: list[dict[str, Any]], model: str) -> str:
    """Create human-readable verification output without dumping full vectors."""
    vector_length = len(records[0]["embedding"]) if records else 0
    lines = [
        "EMBEDDINGS API VERIFICATION",
        "=" * 60,
        f"Model: {model}",
        f"Chunks embedded: {len(records)}",
        f"Vector length: {vector_length}",
        "",
        "STORED RECORDS",
        "-" * 60,
    ]
    for index, record in enumerate(records):
        lines.extend(
            [
                f"Record {index + 1} text: {record['text']}",
                f"Record {index + 1} metadata: {json.dumps(record['metadata'], sort_keys=True)}",
                f"Record {index + 1} sample values: {record['embedding'][:5]}",
            ]
        )
    lines.append("PASS: Every chunk has source text, metadata, and an embedding of the same length.")
    return "\n".join(lines)


def build_batch_report(summary: dict[str, Any], model: str) -> str:
    """Format operational totals so retries and skipped work are visible."""
    lines = [
        "BATCH EMBEDDING RUN SUMMARY",
        "=" * 60,
        f"Model: {model}",
        f"Batch size: {summary['batch_size']}",
        f"Batches attempted: {summary['batches_attempted']}",
        f"Total chunks: {summary['total_chunks']}",
        f"Embeddings generated: {summary['embeddings_generated']}",
        f"Skipped chunks: {summary['skipped_chunks']}",
        f"Failed batches: {summary['failed_batches']}",
        f"Retries: {summary['retries']}",
        f"Estimated input tokens: {summary['estimated_input_tokens']}",
        f"Approximate embedding cost (USD): ${summary['approximate_cost_usd']:.8f}",
    ]
    if summary["failures"]:
        lines.append("Failures:")
        for failure in summary["failures"]:
            lines.append(f"- Batch starting at {failure['batch_start']}: {failure['error']}")
    else:
        lines.append("Failures: none")
    return "\n".join(lines)


def main() -> None:
    load_dotenv()
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY is missing from .env or the environment.")

    model = os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")
    base_url = os.getenv("OPENAI_BASE_URL") or os.getenv("API_BASE_URL")
    client = OpenAI(api_key=api_key, base_url=base_url or None)
    output_dir = Path(__file__).parent.parent / "outputs"
    output_dir.mkdir(parents=True, exist_ok=True)
    embedding_file = output_dir / "embedding_results.json"
    existing_records: list[dict[str, Any]] = []
    if embedding_file.exists():
        stored = json.loads(embedding_file.read_text(encoding="utf-8"))
        if stored.get("model") == model:
            existing_records = stored.get("records", [])

    batch_size = int(os.getenv("EMBEDDING_BATCH_SIZE", "2"))
    max_retries = int(os.getenv("EMBEDDING_MAX_RETRIES", "3"))
    records, batch_summary = batch_embed_chunks(
        SAMPLE_CHUNKS,
        client,
        model,
        existing_records=existing_records,
        batch_size=batch_size,
        max_retries=max_retries,
    )
    embedding_file.write_text(
        json.dumps({"model": model, "records": records}, indent=2),
        encoding="utf-8",
    )
    batch_report = build_batch_report(batch_summary, model)
    (output_dir / "batch_run_summary.json").write_text(
        json.dumps({"model": model, **batch_summary}, indent=2),
        encoding="utf-8",
    )
    (output_dir / "batch_run_summary.txt").write_text(batch_report, encoding="utf-8")
    report = build_report(records, model)
    query_embedding = embed_query(SAMPLE_QUERY, client, model)
    ranked_results = rank_chunks(query_embedding, records)
    (output_dir / "embedding_results.txt").write_text(report, encoding="utf-8")
    similarity_report = build_similarity_report(SAMPLE_QUERY, ranked_results, model)
    (output_dir / "similarity_results.txt").write_text(similarity_report, encoding="utf-8")
    (output_dir / "similarity_results.json").write_text(
        json.dumps(
            {
                "model": model,
                "query": SAMPLE_QUERY,
                "metric": "cosine_similarity",
                "results": ranked_results,
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    print(batch_report)
    print(report)
    print(f"\n{similarity_report}")
    print(f"\nStored ranking results in: {output_dir / 'similarity_results.json'}")


if __name__ == "__main__":
    main()