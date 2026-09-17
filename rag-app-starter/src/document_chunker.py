from pathlib import Path


def fixed_chunks(text: str, size: int = 500, overlap: int = 50) -> list[str]:
    """Split text into fixed-size chunks with overlap."""
    if size <= 0:
        raise ValueError("Chunk size must be greater than 0.")

    if overlap < 0 or overlap >= size:
        raise ValueError("Overlap must be >= 0 and smaller than chunk size.")

    chunks = []
    start = 0
    step = size - overlap

    while start < len(text):
        chunk = text[start:start + size].strip()

        if chunk:
            chunks.append(chunk)

        start += step

    return chunks


def paragraph_chunks(text: str) -> list[str]:
    """Split text using paragraph boundaries."""
    return [
        paragraph.strip()
        for paragraph in text.split("\n\n")
        if paragraph.strip()
    ]


def chunk_stats(chunks: list[str]) -> tuple[int, float]:
    """Return chunk count and average chunk size."""
    if not chunks:
        return 0, 0.0

    sizes = [len(chunk) for chunk in chunks]
    return len(chunks), sum(sizes) / len(sizes)


def print_chunks(name: str, chunks: list[str], samples: int = 3) -> None:
    """Print statistics and sample chunks."""
    count, average = chunk_stats(chunks)

    print(f"\n{name.upper()} CHUNKING")
    print("-" * 50)
    print(f"Chunk count: {count}")
    print(f"Average chunk size: {average:.2f} characters")

    for index, chunk in enumerate(chunks[:samples], start=1):
        print(f"\nSample chunk {index}:")
        print(chunk[:300])


def main():
    document_path = Path("data/sample_leave_policy.txt")

    if not document_path.exists():
        print(f"ERROR: Document not found: {document_path}")
        return

    try:
        text = document_path.read_text(
            encoding="utf-8",
            errors="ignore"
        )
    except Exception as error:
        print(f"ERROR: Could not read document: {error}")
        return

    if not text.strip():
        print("ERROR: Document is empty.")
        return

    print(f"Document: {document_path.name}")
    print(f"Document length: {len(text)} characters")

    # Strategy 1: fixed-size chunks with overlap
    fixed = fixed_chunks(
        text,
        size=500,
        overlap=50
    )

    # Strategy 2: paragraph-based chunks
    paragraph = paragraph_chunks(text)

    print_chunks("Fixed-size with overlap", fixed)
    print_chunks("Paragraph-based", paragraph)

    print("\nSTRATEGY DECISION")
    print("-" * 50)
    print(
        "Chosen strategy: paragraph-based chunking. "
        "The HR policy corpus contains logically separated policy "
        "sections and paragraphs, so preserving paragraph boundaries "
        "helps keep related policy information together and improves "
        "retrieval context."
    )


if __name__ == "__main__":
    main()