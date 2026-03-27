# Quirky RAG

## Overview
Quirky RAG is a production-grade, containerized AI Agentic Retrieval-Augmented Generation (RAG) system specially designed for PDFs. It leverages the latest LlamaIndex features including semantic chunking, enriched embeddings, and query rewriting, all wrapped in a premium Apple liquid glass style user interface.

## Features
- **PDF-only ingestion:** Robust semantic H1/H2 chunking for accurate text extraction.
- **Model Switcher:** Seamlessly switch between OpenAI APIs and Local Models in 1 click.
- **Hybrid Retrieval:** Dense embeddings augmented with BM25 + Query Rewriting + Cross-encoder reranking. 
- **Apple Liquid Glass UI:** Beautiful chat interface, document session management, and Apple aesthetics.
- **MALLM Cache:** Redis-powered caching wrapper.
- **Context-grounded Responses:** Enforced response generation without hallucination.

## Architecture
- **Frontend:** Next.js with React Server Components, styled with vanilla CSS glassmorphism.
- **Backend:** FastAPI integrated tightly with LlamaIndex.
- **Vector DB:** Qdrant for fast and persistent embedding search.
- **Cache layer:** Redis for memory retrieval.
- **Deployment:** Docker & docker-compose.

## Setup
### Docker Setup
To get started, simply run the single stack command from the root directory:

```bash
docker-compose up --build
```
This spins up:
- **Frontend** on `http://localhost:3000`
- **Backend API** on `http://localhost:8000`
- **Qdrant DB** on `http://localhost:6333`
- **Redis Cache** on `redis://localhost:6379`

### Environment Variables
Optionally configure your `.env` or pass secrets into `docker-compose.yml`:
- `OPENAI_API_KEY`: Required if using the OpenAI provider.
- `QDRANT_URL`: URL for Qdrant (defaults to container).
- `REDIS_URL`: URL for Redis cache.

## Model Switching
You can seamlessly switch between **OpenAI** API and **Local** Models. 

# config/model_config.py
All model configurations happen in *one single file*. Update `config/model_config.py` to change engines globally:

```python
MODEL_PROVIDER = "openai"  # or "local"

if MODEL_PROVIDER == "openai":
    LLM = "gpt-4o-mini"
    EMBEDDING = "text-embedding-3-large"
elif MODEL_PROVIDER == "local":
    LLM = "ollama/mistral"
    EMBEDDING = "bge-large-en"
```

*Note: Restart docker-compose after modifying the file to apply configuration across your stacks.*

## How it Works
### Ingestion Pipeline
1. PDFs are sent to FastAPI `/ingest/` endpoint.
2. LlamaIndex semantic splitter reads hierarchical structure.
3. Chunks are embedded and stored persistently in Qdrant metadata mapped by filename.

### Retrieval Pipeline
1. Query sent through the UI.
2. The user's active document list is converted to ExactMatchFilters.
3. Hybrid query is executed against Qdrant, retrieved nodes are scored by a cross-encoder and threshold filtered.
4. Highly confident, context-grounded response is returned by LLM.

## Usage
1. Open the UI at `http://localhost:3000`.
2. Click **+ Upload PDF** and select a file.
3. Toggle the documents you want active in the **Documents** panel on the right.
4. Type your questions in the Center chat and get immediate, grounded insights.

## Dev Notes
- **To Extend Tools**: Add tools or Agent configurations inside `backend/retriever.py` with `ReActAgent`.
- **Cache Configs**: To augment Redis timeout, update `backend/pipeline.py` caching strategy.
