# AI-Based-Knowledge-Retrieval-Platform-with-Query-Resolution-System
Multi-Agent RAG Voice Assistant with document ingestion, embeddings and semantic retrieval.
# AI-Based Knowledge Retrieval Platform with Query Resolution System

A **Multi-Agent Retrieval-Augmented Generation (RAG) voice assistant** that ingests documents, converts them into embeddings, and answers natural-language questions (typed or spoken) using semantic retrieval grounded in your own data.

> **Note:** Items marked `TODO` depend on your implementation. Replace them with the exact libraries, models and file names you use.

---

## Table of Contents

- [Overview](#overview)
- [Key Features](#key-features)
- [Architecture](#architecture)
- [Project Structure](#project-structure)
- [Tech Stack](#tech-stack)
- [Setup](#setup)
- [Usage](#usage)
- [Configuration](#configuration)
- [Sample Data](#sample-data)
- [Roadmap](#roadmap)
- [Limitations](#limitations)
- [Contributing](#contributing)
- [License](#license)

---

## Overview

Finding answers inside large collections of documents is slow, and general-purpose LLMs can hallucinate when they lack domain context. This platform solves that by combining:

1. **Document ingestion**: load, clean and chunk source documents.
2. **Embeddings and semantic search**: index chunks as vectors so queries match on meaning, not just keywords.
3. **Multi-agent query resolution**: specialised agents cooperate to interpret the question, retrieve evidence, and compose a grounded answer.
4. **Voice interface**: ask questions by speaking and hear the answer back.

The included sample knowledge base is **healthcare** documents (`data/healthcare`), but the pipeline is domain-agnostic. Drop in any documents and re-run ingestion.

---

## Key Features

- **Multi-agent pipeline** with separate responsibilities (routing, retrieval, answer generation, voice I/O)
- **Semantic retrieval** over embedded document chunks
- **Retrieval-augmented answers** grounded in your documents, with source references
- **Voice input and output** (speech-to-text and text-to-speech)
- **Modular ingestion** so new document sets can be added without changing agent code
- **Persistent storage** for embeddings and metadata

---

## Architecture

### High-level flow

```
                ┌────────────────────────┐
                │  Documents (PDF/TXT…)  │
                └───────────┬────────────┘
                            │
                 ┌──────────▼──────────┐
                 │   Ingestion Layer   │  load → clean → chunk
                 └──────────┬──────────┘
                            │
                 ┌──────────▼──────────┐
                 │  Embedding Model    │  text → vectors
                 └──────────┬──────────┘
                            │
                 ┌──────────▼──────────┐
                 │   Vector Database   │  store + index
                 └──────────┬──────────┘
                            │
┌──────────┐   ┌────────────▼────────────┐   ┌──────────────┐
│  Voice / │──▶│     Agent Orchestrator   │──▶│  Voice / Text│
│  Text In │   │  (multi-agent pipeline)  │   │    Output    │
└──────────┘   └────────────┬────────────┘   └──────────────┘
                            │
     ┌──────────────┬───────┴────────┬────────────────┐
     ▼              ▼                ▼                ▼
 Query Agent   Retrieval Agent   Answer Agent    Voice Agent
 (understand   (semantic search   (LLM composes   (STT / TTS)
  and rewrite)  top-k chunks)     grounded reply)
```

### Components

| Component | Responsibility |
|---|---|
| **Ingestion** (`ingestion/`) | Reads raw documents, cleans text, splits into overlapping chunks, generates embeddings, writes to the database. |
| **Database** (`database/`) | Stores vectors and chunk metadata (source file, page, chunk id) and exposes similarity search. |
| **Query Agent** | Interprets the user's question, normalises or rewrites it for better retrieval. |
| **Retrieval Agent** | Embeds the query and fetches the top-k most similar chunks. |
| **Answer Agent** | Passes the question plus retrieved context to an LLM and returns a grounded answer with sources. |
| **Voice Agent** | Converts speech to text for input and text to speech for output. |

### Request lifecycle

1. The user asks a question by voice or text.
2. If voice, the audio is transcribed to text.
3. The Query Agent refines the question.
4. The Retrieval Agent embeds it and runs a similarity search over the vector store.
5. The Answer Agent builds a prompt from the question and the retrieved chunks, then generates a response.
6. The response is returned as text and optionally spoken aloud.

---

## Project Structure

```
.
├── data/
│   └── healthcare/        # Sample knowledge-base documents
├── database/              # Vector store / metadata layer
├── ingestion/             # Document loading, chunking, embedding
├── requirements.txt       # Python dependencies
├── .gitignore
└── README.md
```

> TODO: add the entry-point script(s) and agent modules here (for example `agents/`, `main.py`, `app.py`) as you build them.

---

## Tech Stack

> TODO: confirm and edit to match your code.

- **Language:** Python 3.10+
- **Embeddings:** TODO (e.g., Sentence-Transformers, OpenAI, or similar)
- **Vector store:** TODO (e.g., FAISS, ChromaDB, or similar)
- **LLM:** TODO (e.g., a hosted API or a local model)
- **Speech:** TODO (e.g., SpeechRecognition / Whisper for STT, pyttsx3 / gTTS for TTS)
- **Agent orchestration:** TODO (e.g., custom pipeline, LangChain, or similar)

---

## Setup

### Prerequisites

- Python 3.10 or newer
- `pip` and `venv`
- A microphone and speakers (for voice mode)
- API keys, if you use hosted models (see [Configuration](#configuration))

### Installation

```bash
# 1. Clone the repository
git clone https://github.com/MRITHULAA2004/AI-Based-Knowledge-Retrieval-Platform-with-Query-Resolution-System.git
cd AI-Based-Knowledge-Retrieval-Platform-with-Query-Resolution-System

# 2. Create and activate a virtual environment
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt
```

---

## Configuration

Create a `.env` file in the project root (never commit it):

```env
# TODO: keep only the variables your code actually reads
LLM_API_KEY=your_api_key_here
EMBEDDING_MODEL=your_embedding_model_name
VECTOR_DB_PATH=./database/store
CHUNK_SIZE=500
CHUNK_OVERLAP=50
TOP_K=4
```

| Variable | Description | Example |
|---|---|---|
| `LLM_API_KEY` | Key for the language model provider | `sk-...` |
| `EMBEDDING_MODEL` | Model used to create embeddings | `all-MiniLM-L6-v2` |
| `VECTOR_DB_PATH` | Where the vector index is stored | `./database/store` |
| `CHUNK_SIZE` | Characters (or tokens) per chunk | `500` |
| `CHUNK_OVERLAP` | Overlap between adjacent chunks | `50` |
| `TOP_K` | Number of chunks retrieved per query | `4` |

---

## Usage

> TODO: replace the commands below with your real script names.

### 1. Ingest documents

Place your files in `data/<your-domain>/` (the sample uses `data/healthcare/`), then run:

```bash
python -m ingestion.ingest --source data/healthcare
```

This will load, chunk and embed the documents, then save them to the vector store.

### 2. Ask questions

**Text mode**

```bash
python main.py --mode text
```

```
You: What are the common symptoms of type 2 diabetes?
Assistant: Common symptoms include increased thirst, frequent urination, ...
Sources: healthcare/diabetes_guide.pdf (p. 3)
```

**Voice mode**

```bash
python main.py --mode voice
```

Speak your question after the prompt. The assistant transcribes it, retrieves relevant context, and replies in text and speech.

### 3. Add your own knowledge base

1. Create a folder under `data/`, for example `data/legal/`.
2. Add your documents.
3. Run ingestion with `--source data/legal`.
4. Query as usual.

---

## Sample Data

The `data/healthcare/` folder holds the demo corpus. These documents are for **demonstration only** and are not medical advice.

---

## Roadmap

- [ ] Web UI (Streamlit / Gradio / React)
- [ ] Hybrid search (keyword + semantic) and re-ranking
- [ ] Conversation memory for follow-up questions
- [ ] Citation highlighting in answers
- [ ] Support for more file types (DOCX, HTML, CSV)
- [ ] Evaluation suite (retrieval precision/recall, answer faithfulness)
- [ ] Docker support

---

## Limitations

- Answer quality depends on the quality and coverage of the ingested documents.
- Voice accuracy depends on microphone quality and background noise.
- Not a substitute for professional advice, especially with the healthcare sample data.

---

## Contributing

Contributions are welcome.

1. Fork the repository
2. Create a branch: `git checkout -b feature/your-feature`
3. Commit your changes: `git commit -m "Add your feature"`
4. Push: `git push origin feature/your-feature`
5. Open a Pull Request

---

## License

TODO: add a license (e.g., MIT) and a `LICENSE` file.

---

## Author

**MRITHULAA2004**: [GitHub](https://github.com/MRITHULAA2004)
