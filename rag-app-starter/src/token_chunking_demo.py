from pathlib import Path

from chunker import token_chunks, count_tokens, chunk_statistics


DATA_FILE = Path(__file__).parent.parent / "data" / "sample_leave_policy.txt"
OUTPUT_FILE = (
    Path(__file__).parent.parent / "outputs" / "token_chunking_results.txt"
)


CHUNK_SIZE = 400
OVERLAPS = [0, 60]


def load_document() -> str:
    """Load the sample HR policy document."""

    if not DATA_FILE.exists():
        raise FileNotFoundError(f"Document not found: {DATA_FILE}")

    return DATA_FILE.read_text(
        encoding="utf-8",
        errors="ignore"
    )


def show_boundary_demo(text: str) -> str:
    """
    Demonstrate how overlap preserves boundary context.

    We use a small token window so the effect can be clearly observed.
    """

    demo_size = 30

    no_overlap = token_chunks(
        text,
        chunk_size=demo_size,
        overlap=0
    )

    with_overlap = token_chunks(
        text,
        chunk_size=demo_size,
        overlap=10
    )

    output = []

    output.append("\nBOUNDARY CONTEXT DEMONSTRATION")
    output.append("=" * 60)

    output.append("\nWITHOUT OVERLAP")
    output.append("-" * 60)

    if len(no_overlap) >= 2:
        output.append("Chunk 1:")
        output.append(no_overlap[0])
        output.append("\nChunk 2:")
        output.append(no_overlap[1])

    output.append("\nWITH OVERLAP")
    output.append("-" * 60)

    if len(with_overlap) >= 2:
        output.append("Chunk 1:")
        output.append(with_overlap[0])
        output.append("\nChunk 2:")
        output.append(with_overlap[1])

    return "\n".join(output)


def main():
    text = load_document()

    output = []

    output.append("TOKEN-AWARE CHUNKING RESULTS")
    output.append("=" * 60)

    output.append(f"Source: {DATA_FILE.name}")
    output.append(f"Total document tokens: {count_tokens(text)}")

    # Compare different overlap values.
    for overlap in OVERLAPS:
        chunks = token_chunks(
            text,
            chunk_size=CHUNK_SIZE,
            overlap=overlap
        )

        stats = chunk_statistics(chunks)

        output.append("\n" + "-" * 60)
        output.append(f"Chunk size: {CHUNK_SIZE} tokens")
        output.append(f"Overlap: {overlap} tokens")
        output.append(f"Number of chunks: {stats['chunk_count']}")
        output.append(f"Average tokens/chunk: {stats['average_tokens']}")
        output.append(f"Minimum tokens/chunk: {stats['min_tokens']}")
        output.append(f"Maximum tokens/chunk: {stats['max_tokens']}")

    # Show actual chunks using the selected settings.
    selected_chunks = token_chunks(
        text,
        chunk_size=CHUNK_SIZE,
        overlap=60
    )

    output.append("\n" + "=" * 60)
    output.append("EXAMPLE CHUNKS")
    output.append("=" * 60)

    for index, chunk in enumerate(selected_chunks[:3]):
        output.append(f"\nCHUNK {index}")
        output.append(f"Token count: {count_tokens(chunk)}")
        output.append("-" * 60)
        output.append(chunk)

    output.append(show_boundary_demo(text))

    output.append("\n" + "=" * 60)
    output.append("JUSTIFICATION")
    output.append("=" * 60)

    output.append(
        "A chunk size of 400 tokens was selected because it keeps retrieved "
        "HR policy sections reasonably focused while leaving room in the "
        "model context for the question, prompt, and multiple retrieved chunks."
    )

    output.append(
        "A 60-token overlap was selected because it is 15% of the 400-token "
        "chunk size. This helps preserve information that falls near chunk "
        "boundaries without creating excessive duplication."
    )

    output.append(
        "Larger overlap increases repeated text, embedding work, and storage. "
        "Smaller overlap reduces cost but increases the chance of losing "
        "important boundary context."
    )

    output.append(
        "Chunk size also interacts with top-k retrieval. If k chunks are "
        "retrieved, approximately chunk_size × k tokens can enter the "
        "retrieval context, in addition to the prompt and expected output. "
        "Therefore chunk size, top-k, and the model context limit must be "
        "considered together."
    )

    final_output = "\n".join(output)

    print(final_output)

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_FILE.write_text(
        final_output,
        encoding="utf-8"
    )

    print(f"\nSaved results to: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()