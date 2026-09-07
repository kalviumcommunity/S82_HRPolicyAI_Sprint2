import json
import os
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from openai import OpenAI


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


def main() -> None:
    load_dotenv()
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY is missing from .env or the environment.")

    model = os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")
    base_url = os.getenv("OPENAI_BASE_URL") or os.getenv("API_BASE_URL")
    client = OpenAI(api_key=api_key, base_url=base_url or None)
    records = embed_chunks(SAMPLE_CHUNKS, client, model)

    output_dir = Path(__file__).parent.parent / "outputs"
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "embedding_results.json").write_text(
        json.dumps({"model": model, "records": records}, indent=2),
        encoding="utf-8",
    )
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
    print(report)
    print(f"\n{similarity_report}")
    print(f"\nStored ranking results in: {output_dir / 'similarity_results.json'}")


if __name__ == "__main__":
    main()