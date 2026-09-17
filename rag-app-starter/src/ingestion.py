from pathlib import Path

from document_loader import load_text
from chunker import token_chunks, count_tokens


DATA_DIR = Path(__file__).parent.parent / "data"
OUTPUT_FILE = (
    Path(__file__).parent.parent / "outputs" / "ingestion_summary.txt"
)

CHUNK_SIZE = 400
CHUNK_OVERLAP = 60


def clean_text(text: str) -> str:
    """
    Basic text cleaning before chunking.

    Removes excessive whitespace while preserving
    meaningful text content.
    """
    lines = [line.strip() for line in text.splitlines()]
    lines = [line for line in lines if line]

    return "\n".join(lines)


def tag_chunks(source: str, chunks: list[str]) -> list[dict]:
    """
    Attach metadata to every chunk.
    """

    tagged = []

    for index, chunk in enumerate(chunks):
        tagged.append(
            {
                "text": chunk,
                "metadata": {
                    "source": source,
                    "chunk_index": index,
                    "token_count": count_tokens(chunk),
                },
            }
        )

    return tagged


def ingest(folder: Path):
    """
    Run the complete ingestion pipeline:

    load → clean → chunk → metadata
    """

    files = [
        path
        for path in folder.rglob("*")
        if path.is_file()
    ]

    documents_ingested = 0
    all_chunks = []
    failures = []

    for path in files:
        try:
            # 1. Load document
            text = load_text(path)

            # 2. Clean extracted text
            cleaned_text = clean_text(text)

            if not cleaned_text.strip():
                raise ValueError("document contains no usable text")

            # 3. Token-aware chunking
            chunks = token_chunks(
                cleaned_text,
                chunk_size=CHUNK_SIZE,
                overlap=CHUNK_OVERLAP,
            )

            if not chunks:
                raise ValueError("no chunks were created")

            # 4. Add metadata
            tagged = tag_chunks(
                path.name,
                chunks
            )

            all_chunks.extend(tagged)
            documents_ingested += 1

        except Exception as error:
            failures.append(
                {
                    "source": path.name,
                    "error": str(error),
                }
            )

    return files, documents_ingested, all_chunks, failures


def validate_ingestion(
    total_files: int,
    documents_ingested: int,
    failures: list[dict],
):
    """
    Ensure every source file is accounted for.

    files = successfully ingested + failures
    """

    accounted_for = documents_ingested + len(failures)

    if accounted_for != total_files:
        raise AssertionError(
            "A document was silently dropped: "
            f"{total_files} files, "
            f"{documents_ingested} ingested, "
            f"{len(failures)} failures"
        )


def generate_report(
    files,
    documents_ingested,
    chunks,
    failures,
):
    """
    Generate a human-readable ingestion report.
    """

    output = []

    output.append("HR POLICY CORPUS INGESTION REPORT")
    output.append("=" * 60)

    output.append(f"Source directory: {DATA_DIR}")
    output.append(f"Total source files: {len(files)}")
    output.append(
        f"Successfully ingested documents: {documents_ingested}"
    )
    output.append(f"Total chunks created: {len(chunks)}")
    output.append(f"Failed documents: {len(failures)}")

    output.append("\nCOMPLETENESS VALIDATION")
    output.append("-" * 60)

    accounted_for = documents_ingested + len(failures)

    output.append(
        f"Files accounted for: "
        f"{documents_ingested} + {len(failures)} = {accounted_for}"
    )

    output.append(
        f"Expected files: {len(files)}"
    )

    if accounted_for == len(files):
        output.append("PASS: Every source file is accounted for.")
    else:
        output.append("FAIL: Some files were silently dropped.")

    output.append("\nFAILURES")
    output.append("-" * 60)

    if failures:
        for failure in failures:
            output.append(
                f"FAILED: {failure['source']} | "
                f"{failure['error']}"
            )
    else:
        output.append("No ingestion failures.")

    output.append("\nSAMPLE CHUNKS")
    output.append("-" * 60)

    for chunk in chunks[:3]:
        output.append(
            f"\nSource: {chunk['metadata']['source']}"
        )
        output.append(
            f"Chunk index: {chunk['metadata']['chunk_index']}"
        )
        output.append(
            f"Token count: {chunk['metadata']['token_count']}"
        )
        output.append("Text:")
        output.append(chunk["text"][:500])

    return "\n".join(output)


def main():
    print("Starting HR policy corpus ingestion...")

    files, documents_ingested, chunks, failures = ingest(
        DATA_DIR
    )

    # Critical validation
    validate_ingestion(
        total_files=len(files),
        documents_ingested=documents_ingested,
        failures=failures,
    )

    report = generate_report(
        files,
        documents_ingested,
        chunks,
        failures,
    )

    print("\n" + report)

    OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    OUTPUT_FILE.write_text(
        report,
        encoding="utf-8"
    )

    print(
        f"\nReport saved to: {OUTPUT_FILE}"
    )


if __name__ == "__main__":
    main()