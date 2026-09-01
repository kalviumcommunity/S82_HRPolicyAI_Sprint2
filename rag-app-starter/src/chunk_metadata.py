"""
Chunk Metadata & Source Tracking

This module attaches consistent metadata to every document chunk.
The metadata allows retrieved chunks to be traced back to their
original source document and location.
"""

from pathlib import Path
from typing import List, Dict, Any


def create_chunk_metadata(
    source: str,
    chunks: List[str],
    section: str = "unknown",
    page: int | None = None,
) -> List[Dict[str, Any]]:
    """
    Attach metadata to every chunk.

    Every chunk has the same structure:

    {
        "text": "...",
        "metadata": {
            "source": "...",
            "chunk_index": 0,
            "section": "...",
            "page": ...,
            "char_start": 0
        }
    }
    """

    tagged_chunks = []

    char_position = 0

    for index, chunk in enumerate(chunks):
        tagged_chunk = {
            "text": chunk,
            "metadata": {
                "source": source,
                "chunk_index": index,
                "section": section,
                "page": page,
                "char_start": char_position,
            },
        }

        tagged_chunks.append(tagged_chunk)

        char_position += len(chunk)

    return tagged_chunks


def trace_chunk(chunk: Dict[str, Any]) -> str:
    """
    Return a human-readable source reference for a retrieved chunk.
    """

    metadata = chunk["metadata"]

    source = metadata["source"]
    chunk_index = metadata["chunk_index"]
    section = metadata["section"]
    page = metadata["page"]

    if page is not None:
        return (
            f"Source: {source} | "
            f"Page: {page} | "
            f"Section: {section} | "
            f"Chunk: {chunk_index}"
        )

    return (
        f"Source: {source} | "
        f"Section: {section} | "
        f"Chunk: {chunk_index}"
    )


def demonstrate_metadata() -> None:
    """
    Demonstrate metadata creation and source tracing.
    """

    sample_chunks = [
        "Employees are entitled to 12 days of casual leave per year.",
        "Leave requests should be submitted through the HR portal.",
        "Managers should approve or reject requests within three working days.",
    ]

    tagged_chunks = create_chunk_metadata(
        source="sample_leave_policy.txt",
        chunks=sample_chunks,
        section="Leave Policy",
        page=None,
    )

    print("=" * 70)
    print("CHUNK METADATA DEMONSTRATION")
    print("=" * 70)

    for chunk in tagged_chunks:
        print("\nChunk:")
        print(chunk["text"])

        print("\nMetadata:")
        for key, value in chunk["metadata"].items():
            print(f"  {key}: {value}")

    print("\n" + "=" * 70)
    print("TRACEBACK DEMONSTRATION")
    print("=" * 70)

    retrieved_chunk = tagged_chunks[1]

    print("\nRetrieved chunk:")
    print(retrieved_chunk["text"])

    print("\nTraceback:")
    print(trace_chunk(retrieved_chunk))


def main() -> None:
    demonstrate_metadata()


if __name__ == "__main__":
    main()