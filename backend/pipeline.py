import os
from llama_index.core import SimpleDirectoryReader, StorageContext, VectorStoreIndex
from llama_index.core.ingestion import IngestionPipeline
from llama_index.core.node_parser import SemanticSplitterNodeParser
from llama_index.core.extractors import TitleExtractor
from llama_index.vector_stores.qdrant import QdrantVectorStore
from llama_index.storage.kvstore.redis import RedisKVStore as RedisCache
from llama_index.core.storage.docstore import SimpleDocumentStore
import qdrant_client
from backend.llm_setup import setup_llm_and_embeddings

def get_qdrant_client():
    url = os.getenv("QDRANT_URL", "http://localhost:6333")
    return qdrant_client.QdrantClient(url=url)

def get_vector_store():
    client = get_qdrant_client()
    return QdrantVectorStore(client=client, collection_name="quirky_rag_docs")

def get_redis_cache():
    url = os.getenv("REDIS_URL", "redis://localhost:6379")
    return RedisCache(redis_uri=url)

def _get_document_metadata_key():
    return "quirky_rag_doc_metrics"

active_documents = set()

def ingest_pdf(file_path: str, filename: str):
    llm, embed_model = setup_llm_and_embeddings()
    # Read PDF
    reader = SimpleDirectoryReader(input_files=[file_path])
    documents = reader.load_data()
    
    # Give metadata to docs
    for doc in documents:
        doc.metadata["filename"] = filename
    
    # Advanced structure-aware chunking
    splitter = SemanticSplitterNodeParser(
        buffer_size=1, breakpoint_percentile_threshold=95, embed_model=embed_model
    )
    title_extractor = TitleExtractor(nodes=5)
    
    # Create pipeline
    pipeline = IngestionPipeline(
        transformations=[splitter, title_extractor, embed_model]
    )
    
    nodes = pipeline.run(documents=documents)
    
    # Store in Qdrant Vector Store
    vector_store = get_vector_store()
    storage_context = StorageContext.from_defaults(vector_store=vector_store)
    
    index = VectorStoreIndex(nodes, storage_context=storage_context)
    
    # Add to global docs listing
    active_documents.add(filename)
    return True

def get_document_metadata():
    return list(active_documents)
