from config.model_config import MODEL_PROVIDER, LLM, EMBEDDING
from llama_index.llms.openai import OpenAI
from llama_index.llms.ollama import Ollama
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.core import Settings
import os

def setup_llm_and_embeddings():
    if MODEL_PROVIDER == "openai":
        llm = OpenAI(model=LLM, temperature=0.1)
        embed_model = OpenAIEmbedding(model=EMBEDDING)
    elif MODEL_PROVIDER == "local":
        llm = Ollama(model=LLM.split("/")[-1], request_timeout=120.0)
        embed_model = HuggingFaceEmbedding(model_name=EMBEDDING)
    else:
        raise ValueError(f"Unknown MODEL_PROVIDER: {MODEL_PROVIDER}")

    Settings.llm = llm
    Settings.embed_model = embed_model
    
    # MALLM Cache (Query and Retrieval cache implementation)
    cache_url = os.getenv("REDIS_URL", "redis://localhost:6379")
    try:
        from llama_index.storage.kvstore.redis import RedisKVStore
        from llama_index.core import StorageContext
        redis_cache = RedisKVStore(redis_uri=cache_url)
        # Assuming cache integration points here
    except Exception as e:
        print(f"Failed to connect to Redis cache: {e}")
        
    return llm, embed_model
