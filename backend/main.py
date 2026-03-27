import os
from fastapi import FastAPI, UploadFile, File, HTTPException, Body
from fastapi.middleware.cors import CORSMiddleware
from backend.llm_setup import setup_llm_and_embeddings
from backend.pipeline import ingest_pdf, get_document_metadata
from backend.retriever import get_answer

# Initialize LLM and Emdeddings via centralized config
setup_llm_and_embeddings()

app = FastAPI(title="Quirky RAG API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = os.getenv("UPLOAD_DIR", "uploaded_pdfs")
os.makedirs(UPLOAD_DIR, exist_ok=True)

@app.post("/ingest/")
async def upload_and_ingest(file: UploadFile = File(...)):
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")
    
    file_path = os.path.join(UPLOAD_DIR, file.filename)
    with open(file_path, "wb") as f:
        f.write(file.file.read())
    
    # Run ingestion
    success = ingest_pdf(file_path, file.filename)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to ingest PDF.")
    
    return {"message": "Successfully ingested", "filename": file.filename}

@app.get("/documents/")
async def list_documents():
    return {"documents": get_document_metadata()}

@app.post("/query/")
async def query_rag(request: dict = Body(...)):
    query = request.get("query")
    session_id = request.get("session_id", "default")
    active_docs = request.get("active_documents", [])
    
    if not query:
        raise HTTPException(status_code=400, detail="Query is required.")
        
    response = get_answer(query, session_id, active_docs)
    return {"response": response}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
