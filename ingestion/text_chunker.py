def chunk_text(text, chunk_size=120, overlap=20):
    """Split text into word-based chunks with overlap."""

    if chunk_size <= 0:
        raise ValueError("chunk_size must be positive")

    if overlap < 0 or overlap >= chunk_size:
        raise ValueError("overlap must be smaller than chunk_size")

    words = text.split()
    chunks = []
    start = 0

    while start < len(words):
        end = start + chunk_size
        chunks.append(" ".join(words[start:end]))

        if end >= len(words):
            break

        start = end - overlap

    return chunks


if __name__ == "__main__":
    sample = (
        "Retrieval augmented generation uses document retrieval "
        "to provide relevant context to language models. "
        "Documents are split into chunks. "
        "Embeddings convert text into numerical vectors. "
        "ChromaDB stores vectors for semantic search. "
    ) * 20

    chunks = chunk_text(sample)

    print("CHUNKING SUCCESSFUL")
    print("Total chunks:", len(chunks))

    for i, chunk in enumerate(chunks, 1):
        print(f"\nChunk {i}:")
        print(chunk[:150])