import tiktoken


# Tokenizer used for token counting.
# cl100k_base is suitable for the OpenAI-compatible models
# used in this project unless your provider specifies another tokenizer.
enc = tiktoken.get_encoding("cl100k_base")


def count_tokens(text: str) -> int:
    """Return the number of tokens in a text."""
    return len(enc.encode(text))


def token_chunks(
    text: str,
    chunk_size: int = 400,
    overlap: int = 60
) -> list[str]:
    """
    Split text into chunks based on token count.

    Each chunk contains at most chunk_size tokens.
    Adjacent chunks share 'overlap' tokens.
    """

    if chunk_size <= 0:
        raise ValueError("chunk_size must be greater than 0")

    if overlap < 0:
        raise ValueError("overlap cannot be negative")

    if overlap >= chunk_size:
        raise ValueError("overlap must be smaller than chunk_size")

    tokens = enc.encode(text)

    chunks = []
    step = chunk_size - overlap

    for start in range(0, len(tokens), step):
        chunk_tokens = tokens[start:start + chunk_size]

        if not chunk_tokens:
            break

        chunks.append(enc.decode(chunk_tokens))

        if start + chunk_size >= len(tokens):
            break

    return chunks


def chunk_statistics(chunks: list[str]) -> dict:
    """Calculate useful statistics for generated chunks."""

    token_counts = [count_tokens(chunk) for chunk in chunks]

    if not token_counts:
        return {
            "chunk_count": 0,
            "average_tokens": 0,
            "min_tokens": 0,
            "max_tokens": 0,
        }

    return {
        "chunk_count": len(chunks),
        "average_tokens": round(sum(token_counts) / len(token_counts), 2),
        "min_tokens": min(token_counts),
        "max_tokens": max(token_counts),
    }