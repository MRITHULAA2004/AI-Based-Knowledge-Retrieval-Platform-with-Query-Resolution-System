
from pathlib import Path
import sys
import chromadb

# Project root configuration
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from ingestion.embedder import generate_embeddings


# Persistent ChromaDB storage
DB_PATH = Path(__file__).resolve().parent / "chroma_db"

client = chromadb.PersistentClient(path=str(DB_PATH))

collection = client.get_or_create_collection(
    name="knowledge_base",
    metadata={"hnsw:space": "cosine"}
)


def upsert_chunks(chunks, embeddings, metadatas):
    """
    Store document chunks and replace obsolete chunks
    when the same document is re-ingested.
    """

    if not (len(chunks) == len(embeddings) == len(metadatas)):
        raise ValueError(
            "Chunks, embeddings and metadata must have equal lengths"
        )

    if not chunks:
        return 0

    # Validate document identity
    sources = {metadata["source"] for metadata in metadatas}
    domains = {metadata["domain"] for metadata in metadatas}

    if len(sources) != 1 or len(domains) != 1:
        raise ValueError(
            "One ingestion operation must contain one document and one domain"
        )

    source = next(iter(sources))
    domain = next(iter(domains))

    # Remove previous chunks of this document
    collection.delete(
        where={
            "$and": [
                {"source": source},
                {"domain": domain}
            ]
        }
    )

    # Generate unique chunk IDs
    ids = [
        f"{source}::{metadata['chunk_index']}"
        for metadata in metadatas
    ]

    # Store latest chunks
    collection.add(
        ids=ids,
        documents=chunks,
        embeddings=embeddings,
        metadatas=metadatas
    )

    return len(chunks)


def search_chunks(query, top_k=3, domain=None):
    """
    Retrieve semantically relevant document chunks.

    Supports optional healthcare or technology filtering.
    """

    if not isinstance(query, str) or not query.strip():
        raise ValueError("Query must be a non-empty string")

    if not isinstance(top_k, int) or isinstance(top_k, bool) or top_k <= 0:
        raise ValueError("top_k must be a positive integer")

    if domain is not None and domain not in {
        "healthcare", "technology"
    }:
        raise ValueError("Invalid domain")

    total = collection.count()

    if total == 0:
        return []

    # Generate query embedding
    query_embedding = generate_embeddings([query])[0]

    # Configure search
    query_args = {
        "query_embeddings": [query_embedding],
        "n_results": min(top_k, total)
    }

    # Apply domain filtering before similarity ranking
    if domain is not None:
        query_args["where"] = {
            "domain": domain
        }

    # Execute vector search
    results = collection.query(**query_args)

    matches = []

    if not results["documents"] or not results["documents"][0]:
        return []

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

    stored = upsert_chunks(
        sample_chunks,
        sample_embeddings,
        sample_metadata
    )

    print("\nCHROMADB INDEXING SUCCESSFUL")
    print("Chunks stored:", stored)
    print("Total collection count:", collection.count())

    results = search_chunks(
        "How can I schedule a hospital appointment?",
        top_k=3,
        domain="healthcare"
    )

    print("\nSEMANTIC SEARCH RESULTS")

    for result in results:
        print("\nSource:", result["metadata"]["source"])
        print("Domain:", result["metadata"]["domain"])
        print("Distance:", round(result["distance"], 4))
        print("Text:", result["text"])
