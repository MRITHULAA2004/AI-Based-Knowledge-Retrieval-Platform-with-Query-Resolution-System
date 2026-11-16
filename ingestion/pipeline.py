from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from ingestion.document_loader import load_document
from ingestion.text_chunker import chunk_text
from ingestion.embedder import generate_embeddings
from database.vector_store import upsert_chunks

def ingest_document(file_path, domain):
    """Load, chunk, embed and index one document."""

    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(f"Document not found: {path}")

    print(f"\nProcessing: {path.name}")

    # 1. Extract text
    text = load_document(path)

    if not text.strip():
        raise ValueError(f"No text extracted from {path.name}")

    print("Text extraction successful.")

    # 2. Split text into chunks
    chunks = chunk_text(text, chunk_size=120, overlap=20)

    if not chunks:
        raise ValueError(f"No chunks created from {path.name}")

    print("Chunks created:", len(chunks))

    # 3. Generate embeddings
    embeddings = generate_embeddings(chunks)

    print("Embeddings generated:", len(embeddings))

    # 4. Prepare metadata
    metadatas = [
        {
            "source": path.name,
            "domain": domain,
            "chunk_index": index
        }
        for index in range(len(chunks))
    ]

    # 5. Store in ChromaDB
    stored = upsert_chunks(chunks, embeddings, metadatas)

    print("Chunks indexed:", stored)
    print(f"INGESTION SUCCESSFUL: {path.name}")

    return stored


if __name__ == "__main__":

    project_root = Path(__file__).resolve().parent.parent

    sample_file = project_root / "data" / "healthcare" / "sample.txt"

    if not sample_file.exists():
        print("Create data/healthcare/sample.txt before running this test.")
    else:
        ingest_document(sample_file, domain="healthcare")
