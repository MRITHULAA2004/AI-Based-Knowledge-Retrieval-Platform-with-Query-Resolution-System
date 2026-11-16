from pathlib import Path
import sys
import chromadb

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from ingestion.embedder import generate_embeddings

# Persistent database location
DB_PATH = Path(__file__).resolve().parent / "chroma_db"

client = chromadb.PersistentClient(path=str(DB_PATH))

collection = client.get_or_create_collection(
    name="knowledge_base",
    metadata={"hnsw:space": "cosine"}
)


def upsert_chunks(chunks, embeddings, metadatas):
    """Store document chunks, embeddings and metadata."""

    if not (len(chunks) == len(embeddings) == len(metadatas)):
        raise ValueError("Chunks, embeddings and metadata must have equal lengths")

    if not chunks:
        return 0

    ids = [
        f"{metadata['source']}::{metadata['chunk_index']}"
        for metadata in metadatas
    ]

    collection.upsert(
        ids=ids,
        documents=chunks,
        embeddings=embeddings,
        metadatas=metadatas
    )

    return len(chunks)


def search_chunks(query, top_k=3):
    """Find the most relevant chunks for a question."""

    if top_k <= 0:
        raise ValueError("top_k must be positive")

    total = collection.count()

    if total == 0:
        return []

    query_embedding = generate_embeddings([query])[0]

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=min(top_k, total)
    )

    matches = []

    for i, document in enumerate(results["documents"][0]):
        matches.append({
            "text": document,
            "metadata": results["metadatas"][0][i],
            "distance": results["distances"][0][i]
        })

    return matches


if __name__ == "__main__":

    sample_chunks = [
        "Healthcare appointments can be scheduled through a hospital portal.",
        "Python is a programming language used to build software applications."
    ]

    sample_metadata = [
        {
            "source": "healthcare_sample.txt",
            "domain": "healthcare",
            "chunk_index": 0
        },
        {
            "source": "technology_sample.txt",
            "domain": "technology",
            "chunk_index": 0
        }
    ]

    sample_embeddings = generate_embeddings(sample_chunks)

    count = upsert_chunks(
        sample_chunks,
        sample_embeddings,
        sample_metadata
    )

    print("\nCHROMADB INDEXING SUCCESSFUL")
    print("Chunks stored:", count)
    print("Total collection count:", collection.count())

    results = search_chunks(
        "How can I schedule a hospital appointment?",
        top_k=2
    )

    print("\nSEMANTIC SEARCH RESULTS")

    for result in results:
        print("\nSource:", result["metadata"]["source"])
        print("Domain:", result["metadata"]["domain"])
        print("Distance:", round(result["distance"], 4))
        print("Text:", result["text"])
