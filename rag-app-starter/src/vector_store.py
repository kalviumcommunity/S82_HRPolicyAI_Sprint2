"""Create a local Chroma collection and verify one stored embedding record."""

import json
import os
from pathlib import Path
from typing import Any

import chromadb
from dotenv import load_dotenv


PROJECT_ROOT = Path(__file__).parent.parent
OUTPUT_DIR = PROJECT_ROOT / "outputs"
EMBEDDING_FILE = OUTPUT_DIR / "embedding_results.json"
READBACK_FILE = OUTPUT_DIR / "vector_store_readback.json"
READBACK_TEXT_FILE = OUTPUT_DIR / "vector_store_readback.txt"
DEFAULT_DB_PATH = PROJECT_ROOT / ".chroma"
DEFAULT_COLLECTION_NAME = "hr_policy_chunks"


def load_embedding_record() -> tuple[str, dict[str, Any], int]:
    stored = json.loads(EMBEDDING_FILE.read_text(encoding="utf-8"))
    records = stored.get("records", [])
    if not records:
        raise ValueError(f"No records found in {EMBEDDING_FILE}.")

    dimensions = {len(record.get("embedding", [])) for record in records}
    if len(dimensions) != 1 or 0 in dimensions:
        raise ValueError("All embedding records must contain non-empty vectors of one dimension.")
    return stored.get("model", "unknown"), records[0], dimensions.pop()


def get_collection(client: Any, name: str, dimension: int, model: str) -> Any:
    collection = client.get_or_create_collection(
        name=name,
        metadata={
            "embedding_model": model,
            "vector_dimension": dimension,
            "hnsw:space": "cosine",
        },
    )
    stored_dimension = collection.metadata.get("vector_dimension")
    if stored_dimension is not None and int(stored_dimension) != dimension:
        raise ValueError(
            f"Collection dimension mismatch: configured {dimension}, stored {stored_dimension}."
        )
    return collection


def insert_and_read_back(collection: Any, record: dict[str, Any], dimension: int) -> dict[str, Any]:
    record_id = f"{record['metadata']['source']}:{record['metadata']['chunk_index']}"
    collection.upsert(
        ids=[record_id],
        embeddings=[record["embedding"]],
        documents=[record["text"]],
        metadatas=[record["metadata"]],
    )
    stored = collection.get(
        ids=[record_id],
        include=["embeddings", "documents", "metadatas"],
    )
    if not stored["ids"] or stored["ids"][0] != record_id:
        raise RuntimeError("Chroma readback did not return the inserted record ID.")

    vector = stored["embeddings"][0]
    if len(vector) != dimension:
        raise RuntimeError(f"Readback vector dimension {len(vector)} does not match {dimension}.")
    return {
        "id": stored["ids"][0],
        "vector_length": len(vector),
        "text": stored["documents"][0],
        "metadata": stored["metadatas"][0],
    }


def format_readback(result: dict[str, Any], db_path: Path, collection_name: str, model: str) -> str:
    lines = [
        "VECTOR DATABASE READBACK",
        "=" * 60,
        "Database: Chroma PersistentClient",
        f"Path: {db_path}",
        f"Collection: {collection_name}",
        f"Embedding model: {model}",
        "Distance metric: cosine",
        "",
        "READ-BACK RECORD",
        "-" * 60,
        f"ID: {result['id']}",
        f"Vector length: {result['vector_length']}",
        f"Text: {result['text']}",
        f"Metadata: {json.dumps(result['metadata'], sort_keys=True)}",
        "PASS: The application inserted and read back the test record successfully.",
    ]
    return "\n".join(lines)


def main() -> None:
    load_dotenv()
    model, record, dimension = load_embedding_record()
    db_path = Path(os.getenv("CHROMA_DB_PATH", str(DEFAULT_DB_PATH)))
    if not db_path.is_absolute():
        db_path = PROJECT_ROOT / db_path
    collection_name = os.getenv("CHROMA_COLLECTION_NAME", DEFAULT_COLLECTION_NAME)

    db_path.mkdir(parents=True, exist_ok=True)
    client = chromadb.PersistentClient(path=str(db_path))
    collection = get_collection(client, collection_name, dimension, model)
    readback = insert_and_read_back(collection, record, dimension)
    report = {
        "database": "chroma",
        "path": str(db_path),
        "collection": collection_name,
        "embedding_model": model,
        "vector_dimension": dimension,
        "distance_metric": "cosine",
        "record_count": collection.count(),
        "readback": readback,
    }
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    READBACK_FILE.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    READBACK_TEXT_FILE.write_text(
        format_readback(readback, db_path, collection_name, model) + "\n", encoding="utf-8"
    )
    print(format_readback(readback, db_path, collection_name, model))


if __name__ == "__main__":
    main()