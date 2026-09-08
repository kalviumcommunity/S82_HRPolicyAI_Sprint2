"""Index all embedded chunks into the vector database."""

import json
import os
from pathlib import Path
from typing import Any

import chromadb
from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).parent.parent
OUTPUT_DIR = PROJECT_ROOT / "outputs"
EMBEDDING_FILE = OUTPUT_DIR / "embedding_results.json"
SUMMARY_JSON_FILE = OUTPUT_DIR / "indexing_summary.json"
SUMMARY_TEXT_FILE = OUTPUT_DIR / "indexing_summary.txt"
DEFAULT_DB_PATH = PROJECT_ROOT / ".chroma"
DEFAULT_COLLECTION_NAME = "hr_policy_chunks"

def load_embedding_records() -> tuple[str, list[dict[str, Any]], int]:
    stored = json.loads(EMBEDDING_FILE.read_text(encoding="utf-8"))
    records = stored.get("records", [])
    if not records:
        raise ValueError(f"No records found in {EMBEDDING_FILE}.")

    dimensions = {len(record.get("embedding", [])) for record in records}
    if len(dimensions) != 1 or 0 in dimensions:
        raise ValueError("All embedding records must contain non-empty vectors of one dimension.")
    return stored.get("model", "unknown"), records, dimensions.pop()

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

def format_summary(report: dict[str, Any]) -> str:
    lines = [
        "VECTOR DATABASE INDEXING SUMMARY",
        "=" * 60,
        f"Database: Chroma PersistentClient",
        f"Path: {report['path']}",
        f"Collection: {report['collection']}",
        f"Embedding model: {report['embedding_model']}",
        f"Vector dimension: {report['vector_dimension']}",
        "",
        "INDEXING RESULTS",
        "-" * 60,
        f"Total chunks provided: {report['chunks_provided']}",
        f"Indexed record count: {report['record_count']}",
        f"Counts match: {report['counts_match']}",
        "",
        "SPOT-CHECK READBACK RECORD",
        "-" * 60,
        f"ID: {report['readback']['id']}",
        f"Vector length: {report['readback']['vector_length']}",
        f"Text: {report['readback']['text']}",
        f"Metadata: {json.dumps(report['readback']['metadata'], sort_keys=True)}",
    ]
    return "\n".join(lines)

def main() -> None:
    load_dotenv()
    model, records, dimension = load_embedding_records()
    db_path = Path(os.getenv("CHROMA_DB_PATH", str(DEFAULT_DB_PATH)))
    if not db_path.is_absolute():
        db_path = PROJECT_ROOT / db_path
    collection_name = os.getenv("CHROMA_COLLECTION_NAME", DEFAULT_COLLECTION_NAME)

    db_path.mkdir(parents=True, exist_ok=True)
    client = chromadb.PersistentClient(path=str(db_path))
    collection = get_collection(client, collection_name, dimension, model)
    
    ids = []
    embeddings = []
    documents = []
    metadatas = []
    
    for record in records:
        record_id = f"{record['metadata']['source']}:{record['metadata']['chunk_index']}"
        ids.append(record_id)
        embeddings.append(record["embedding"])
        documents.append(record["text"])
        metadatas.append(record["metadata"])
        
    collection.upsert(
        ids=ids,
        embeddings=embeddings,
        documents=documents,
        metadatas=metadatas,
    )
    
    indexed_count = collection.count()
    counts_match = indexed_count == len(records)
    
    spot_check_id = ids[0]
    stored = collection.get(
        ids=[spot_check_id],
        include=["embeddings", "documents", "metadatas"],
    )
    
    vector = stored["embeddings"][0]
    readback = {
        "id": stored["ids"][0],
        "vector_length": len(vector),
        "text": stored["documents"][0],
        "metadata": stored["metadatas"][0],
    }
    
    report = {
        "database": "chroma",
        "path": str(db_path),
        "collection": collection_name,
        "embedding_model": model,
        "vector_dimension": dimension,
        "distance_metric": "cosine",
        "chunks_provided": len(records),
        "record_count": indexed_count,
        "counts_match": counts_match,
        "readback": readback,
        "failures": []
    }
    
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    SUMMARY_JSON_FILE.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    summary_text = format_summary(report)
    SUMMARY_TEXT_FILE.write_text(summary_text + "\n", encoding="utf-8")
    print(summary_text)

if __name__ == "__main__":
    main()
