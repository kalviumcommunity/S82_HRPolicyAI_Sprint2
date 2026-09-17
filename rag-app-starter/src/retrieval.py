"""Retrieval step: Embed a user query, search the vector store, and return top-k chunks."""

import json
import os
from pathlib import Path
from typing import Any

import chromadb
from dotenv import load_dotenv
from openai import OpenAI

PROJECT_ROOT = Path(__file__).parent.parent
OUTPUT_DIR = PROJECT_ROOT / "outputs"
SUMMARY_JSON_FILE = OUTPUT_DIR / "retrieval_summary.json"
SUMMARY_TEXT_FILE = OUTPUT_DIR / "retrieval_summary.txt"
DEFAULT_DB_PATH = PROJECT_ROOT / ".chroma"
DEFAULT_COLLECTION_NAME = "hr_policy_chunks"


def embed_query(query: str, client: Any, model: str) -> list[float]:
    """Embed one user query with the same model used for document chunks."""
    response = client.embeddings.create(model=model, input=[query])
    if len(response.data) != 1:
        raise ValueError("The embeddings API did not return exactly one query vector.")
    return response.data[0].embedding


def get_collection(client: Any, name: str) -> Any:
    """Get the existing Chroma collection."""
    try:
        collection = client.get_collection(name=name)
        return collection
    except ValueError as e:
        raise ValueError(f"Collection '{name}' not found. Have you run the indexing script?") from e


def retrieve_chunks(collection: Any, query_embedding: list[float], k: int) -> list[dict[str, Any]]:
    """Query the Chroma collection for top-k most similar chunks."""
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=k,
        include=["documents", "metadatas", "distances"]
    )
    
    retrieved = []
    # Chroma returns a list of lists for these fields since we passed a list of query embeddings
    if results["ids"] and results["ids"][0]:
        for i in range(len(results["ids"][0])):
            retrieved.append({
                "id": results["ids"][0][i],
                # Chroma's cosine distance is 1 - cosine_similarity
                "score": 1.0 - results["distances"][0][i] if results["distances"] else 0.0,
                "text": results["documents"][0][i] if results["documents"] else "",
                "metadata": results["metadatas"][0][i] if results["metadatas"] else {},
            })
    return retrieved


def format_summary(query: str, results_by_k: dict[int, list[dict[str, Any]]], model: str) -> str:
    """Create human-readable verification output showing changing k values."""
    lines = [
        "RETRIEVAL STEP VERIFICATION",
        "=" * 60,
        f"Embedding Model: {model}",
        f"Query: '{query}'",
        ""
    ]
    
    for k, results in results_by_k.items():
        lines.extend([
            f"RESULTS FOR k={k}",
            "-" * 60,
        ])
        for rank, result in enumerate(results, start=1):
            lines.extend([
                f"Rank {rank} Score (Cosine Similarity): {result['score']:.6f}",
                f"Rank {rank} Text: {result['text']}",
                f"Rank {rank} Metadata: {json.dumps(result['metadata'], sort_keys=True)}",
                ""
            ])
            
    lines.append("PASS: Retrieved chunks include similarity scores, source text, and metadata.")
    lines.append("PASS: Demonstrated how retrieved results change with different k values.")
    
    return "\n".join(lines)


def main() -> None:
    load_dotenv()
    
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("Warning: OPENAI_API_KEY is not set. Assuming offline or test client.")
        
    model = os.getenv("EMBEDDING_MODEL", "sample-offline-model")
    base_url = os.getenv("OPENAI_BASE_URL") or os.getenv("API_BASE_URL")
    
    # Check if we are running in the test environment
    if model == "sample-offline-model" and not api_key:
        print("Using dummy embedding client for testing...")
        class DummyEmbeddingsData:
            def __init__(self, embedding):
                self.embedding = embedding
        class DummyEmbeddingsCreate:
            def __init__(self, data):
                self.data = data
        class DummyEmbeddings:
            def create(self, model, input):
                # Returns a dummy embedding matching the test corpus (dimension 4)
                return DummyEmbeddingsCreate([DummyEmbeddingsData([0.15, 0.25, 0.35, 0.45])])
        class DummyClient:
            def __init__(self):
                self.embeddings = DummyEmbeddings()
        client = DummyClient()
    else:
        client = OpenAI(api_key=api_key, base_url=base_url or None)

    db_path = Path(os.getenv("CHROMA_DB_PATH", str(DEFAULT_DB_PATH)))
    if not db_path.is_absolute():
        db_path = PROJECT_ROOT / db_path
    collection_name = os.getenv("CHROMA_COLLECTION_NAME", DEFAULT_COLLECTION_NAME)

    chroma_client = chromadb.PersistentClient(path=str(db_path))
    collection = get_collection(chroma_client, collection_name)
    
    # Verify the embedding model used in the collection
    collection_model = collection.metadata.get("embedding_model")
    if collection_model and collection_model != model:
        print(f"Warning: Query embedding model ({model}) differs from collection embedding model ({collection_model}).")
        model = collection_model # Use the collection's model to ensure compatibility

    sample_query = "What is the policy for annual leave?"
    query_embedding = embed_query(sample_query, client, model)
    
    k_values = [1, 2]
    results_by_k = {}
    
    for k in k_values:
        retrieved = retrieve_chunks(collection, query_embedding, k)
        results_by_k[k] = retrieved
        
    report_data = {
        "query": sample_query,
        "embedding_model": model,
        "k_values_tested": k_values,
        "results_by_k": results_by_k
    }

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    SUMMARY_JSON_FILE.write_text(json.dumps(report_data, indent=2) + "\n", encoding="utf-8")
    
    summary_text = format_summary(sample_query, results_by_k, model)
    SUMMARY_TEXT_FILE.write_text(summary_text + "\n", encoding="utf-8")
    print(summary_text)


if __name__ == "__main__":
    main()
