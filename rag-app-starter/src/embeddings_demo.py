import os
from pathlib import Path

import numpy as np
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

# -----------------------------
# Configuration
# -----------------------------
API_KEY = os.getenv("OPENAI_API_KEY")
BASE_URL = os.getenv("OPENAI_BASE_URL")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL")

if not API_KEY:
    raise ValueError("OPENAI_API_KEY is missing from .env")

if not EMBEDDING_MODEL:
    raise ValueError("EMBEDDING_MODEL is missing from .env")

client = OpenAI(
    api_key=API_KEY,
    base_url=BASE_URL if BASE_URL else None,
)

# -----------------------------
# Sample texts
# -----------------------------
texts = [
    "How do I reset my account password?",
    "What are the steps to recover access to my login?",
    "The cafeteria menu has pasta today.",
]

# -----------------------------
# Generate embeddings
# -----------------------------
response = client.embeddings.create(
    model=EMBEDDING_MODEL,
    input=texts,
)

embeddings = [item.embedding for item in response.data]

# -----------------------------
# Cosine similarity
# -----------------------------
def cosine_similarity(a, b):
    a = np.array(a)
    b = np.array(b)

    denominator = np.linalg.norm(a) * np.linalg.norm(b)

    if denominator == 0:
        return 0.0

    return float(np.dot(a, b) / denominator)


similarity = cosine_similarity(
    embeddings[0],
    embeddings[1],
)

dissimilarity = cosine_similarity(
    embeddings[0],
    embeddings[2],
)

# -----------------------------
# Validation
# -----------------------------
dimensions = [len(vector) for vector in embeddings]

if len(set(dimensions)) != 1:
    raise ValueError("Embedding vectors do not have the same dimension.")

dimension = dimensions[0]

# -----------------------------
# Create output
# -----------------------------
output = []

output.append("EMBEDDINGS FUNDAMENTALS DEMONSTRATION")
output.append("=" * 60)

output.append("\nSAMPLE TEXTS")
output.append("-" * 60)

for index, text in enumerate(texts):
    output.append(f"{index + 1}. {text}")

output.append("\nVECTOR DIMENSION")
output.append("-" * 60)
output.append(f"Number of texts: {len(texts)}")
output.append(f"Vector dimensions: {dimensions}")
output.append(f"Common vector dimension: {dimension}")
output.append("PASS: Every text produced a vector of the same length.")

output.append("\nSAMPLE VECTOR OUTPUT")
output.append("-" * 60)

for index, vector in enumerate(embeddings):
    output.append(
        f"Text {index + 1} first 8 values: {vector[:8]}"
    )

output.append("\nCOSINE SIMILARITY")
output.append("-" * 60)

output.append(
    f"Similar pair (password recovery vs login recovery): "
    f"{similarity:.6f}"
)

output.append(
    f"Dissimilar pair (password recovery vs cafeteria): "
    f"{dissimilarity:.6f}"
)

if similarity > dissimilarity:
    output.append(
        "PASS: Similar meaning produced a higher similarity score."
    )
else:
    output.append(
        "WARNING: Similar pair did not score higher."
    )

output.append("\nWHAT EMBEDDING VECTORS REPRESENT")
output.append("-" * 60)
output.append(
    "Embedding vectors are numeric representations of the meaning "
    "of text. They are not random IDs and they are not simple "
    "keyword counts. Texts with similar meanings tend to have "
    "vectors that are closer together in vector space."
)

output.append("\nWHY THIS ENABLES SEMANTIC SEARCH")
output.append("-" * 60)
output.append(
    "In a RAG system, document chunks are converted into embedding "
    "vectors and stored in a vector database. When a user asks a "
    "question, the question is also converted into a vector. "
    "The system searches for nearby vectors, allowing it to find "
    "relevant content even when the question and document use "
    "different words."
)

result = "\n".join(output)

print(result)

# -----------------------------
# Save output
# -----------------------------
output_file = (
    Path(__file__).parent.parent
    / "outputs"
    / "embedding_results.txt"
)

output_file.parent.mkdir(parents=True, exist_ok=True)
output_file.write_text(result, encoding="utf-8")

print(f"\nResults saved to: {output_file}")