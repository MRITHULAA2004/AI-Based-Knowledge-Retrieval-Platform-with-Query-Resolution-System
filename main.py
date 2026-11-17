
from pathlib import Path
from uuid import uuid4

# pyright: reportMissingImports=false
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from ingestion.pipeline import ingest_document
from database.vector_store import search_chunks


# Project configuration
PROJECT_ROOT = Path(__file__).resolve().parent
UPLOAD_DIR = PROJECT_ROOT / "data" / "uploads"

ALLOWED_DOMAINS = {"healthcare", "technology"}
ALLOWED_EXTENSIONS = {".pdf", ".docx", ".txt", ".csv"}
MAX_FILE_SIZE = 20 * 1024 * 1024  # 20 MB


# Create FastAPI application
app = FastAPI(
    title="Knowledge AI API",
    description="Document ingestion and knowledge retrieval API",
    version="1.0.0"
)


# Allow frontend to communicate with backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"]
)


# Question request format
class QueryRequest(BaseModel):
    question: str
    domain: str = "all"


# Home endpoint
@app.get("/")
def home():
    return {
        "message": "Knowledge AI backend is running."
    }


# Health check endpoint
@app.get("/health")
def health():
    return {
        "status": "healthy"
    }


# Upload and process documents
@app.post("/ingest")
def upload_document(
    file: UploadFile = File(...),
    domain: str = Form(...)
):
    if domain not in ALLOWED_DOMAINS:
        raise HTTPException(
            status_code=400,
            detail="Invalid knowledge domain."
        )

    original_name = Path(file.filename or "").name
    extension = Path(original_name).suffix.lower()

    if not original_name or extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail="Only PDF, DOCX, TXT and CSV files are supported."
        )

    content = file.file.read()

    if not content:
        raise HTTPException(
            status_code=400,
            detail="The uploaded file is empty."
        )

    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=413,
            detail="File size exceeds the 20 MB limit."
        )

    domain_dir = UPLOAD_DIR / domain
    domain_dir.mkdir(parents=True, exist_ok=True)

    stored_name = f"{uuid4().hex[:8]}_{original_name}"
    file_path = domain_dir / stored_name

    try:
        file_path.write_bytes(content)

        chunk_count = ingest_document(
            file_path=file_path,
            domain=domain
        )

        return {
            "status": "success",
            "message": "Document processed successfully.",
            "filename": original_name,
            "domain": domain,
            "chunk_count": chunk_count
        }

    except Exception as error:
        file_path.unlink(missing_ok=True)

        raise HTTPException(
            status_code=500,
            detail=f"Document processing failed: {str(error)}"
        )


# Retrieve relevant document information
@app.post("/query")
def query_documents(request: QueryRequest):

    question = request.question.strip()

    if not question:
        raise HTTPException(
            status_code=400,
            detail="Please enter a question."
        )

    if request.domain not in ALLOWED_DOMAINS | {"all"}:
        raise HTTPException(
            status_code=400,
            detail="Invalid knowledge domain."
        )

    try:
        matches = search_chunks(
            query=question,
            top_k=20
        )

        if request.domain != "all":
            matches = [
                match for match in matches
                if match["metadata"].get("domain") == request.domain
            ]

        matches = matches[:3]

        if not matches:
            return {
                "answer": "No relevant information was found in the selected domain.",
                "sources": []
            }

        sources = [
            {
                "source": match["metadata"].get(
                    "source", "Unknown"
                ),
                "domain": match["metadata"].get(
                    "domain", "Unknown"
                ),
                "text": match["text"],
                "distance": match["distance"]
            }
            for match in matches
        ]

        retrieved_context = "\n\n".join(
            match["text"] for match in matches
        )

        return {
            "answer": (
                "Relevant information retrieved from your documents:\n\n"
                + retrieved_context
            ),
            "sources": sources
        }

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"Retrieval failed: {str(error)}"
        )
