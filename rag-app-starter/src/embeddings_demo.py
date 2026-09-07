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
    (output_dir / "embedding_results.txt").write_text(report, encoding="utf-8")
    print(report)
    print(f"\nStored full records in: {output_dir / 'embedding_results.json'}")


if __name__ == "__main__":
    main()