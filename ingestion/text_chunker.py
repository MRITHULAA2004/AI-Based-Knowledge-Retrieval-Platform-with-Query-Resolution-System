
import re


def chunk_text(text, chunk_size=120, overlap=15):
    """
    Split text into sentence-aware chunks with controlled overlap.

    chunk_size: Maximum approximate number of words per chunk.
    overlap: Number of words carried into the next chunk.
    """

    if not isinstance(text, str):
        raise TypeError("Text must be a string")

    if chunk_size <= 0:
        raise ValueError("chunk_size must be positive")

    if overlap < 0 or overlap >= chunk_size:
        raise ValueError("overlap must be smaller than chunk_size")

    # Normalize whitespace
    text = re.sub(r"\s+", " ", text).strip()

    if not text:
        return []

    # Split text into sentences
    sentences = re.split(r"(?<=[.!?])\s+", text)

    chunks = []
    current_sentences = []
    current_words = 0

    for sentence in sentences:
        sentence = sentence.strip()

        if not sentence:
            continue

        sentence_words = sentence.split()
        sentence_count = len(sentence_words)

        # Handle unusually long individual sentences
        if sentence_count > chunk_size:
            if current_sentences:
                chunks.append(" ".join(current_sentences))
                current_sentences = []
                current_words = 0

            for start in range(0, sentence_count, chunk_size - overlap):
                part = sentence_words[start:start + chunk_size]
                if part:
                    chunks.append(" ".join(part))

            continue

        # Add sentence when it fits
        if current_words + sentence_count <= chunk_size:
            current_sentences.append(sentence)
            current_words += sentence_count

        else:
            # Save current chunk
            chunks.append(" ".join(current_sentences))

            # Carry controlled overlap into next chunk
            previous_words = " ".join(current_sentences).split()
            overlap_words = previous_words[-overlap:] if overlap else []

            current_sentences = [" ".join(overlap_words)] if overlap_words else []
            current_words = len(overlap_words)

            current_sentences.append(sentence)
            current_words += sentence_count

    # Save final chunk
    if current_sentences:
        chunks.append(" ".join(current_sentences))

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
        print(chunk)
        print("Word count:", len(chunk.split()))
