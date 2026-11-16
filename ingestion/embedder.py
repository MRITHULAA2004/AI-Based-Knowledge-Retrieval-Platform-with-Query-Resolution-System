
from sentence_transformers import SentenceTransformer

MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"

model = None


def load_embedding_model():
    global model

    if model is None:
        print("Loading embedding model...")
        model = SentenceTransformer(MODEL_NAME)
        model.max_seq_length = 256
        print("Embedding model loaded!")

    return model


def generate_embeddings(texts):
    """Convert text into numerical vectors."""

    if not texts:
        return []

    embedding_model = load_embedding_model()

    vectors = embedding_model.encode(
        texts,
        normalize_embeddings=True,
        show_progress_bar=False
    )

    return vectors.tolist()


if __name__ == "__main__":

    sample_texts = [
        "Retrieval augmented generation uses document retrieval.",
        "ChromaDB stores vector embeddings for semantic search."
    ]

    embeddings = generate_embeddings(sample_texts)

    print("\nEMBEDDING GENERATION SUCCESSFUL")
    print("Number of embeddings:", len(embeddings))
    print("Vector dimensions:", len(embeddings[0]))
    print("First vector values:", embeddings[0][:5])
