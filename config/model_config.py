MODEL_PROVIDER = "openai"  # or "local"

if MODEL_PROVIDER == "openai":
    LLM = "gpt-4o-mini"
    EMBEDDING = "text-embedding-3-large"
elif MODEL_PROVIDER == "local":
    LLM = "ollama/mistral"
    EMBEDDING = "bge-large-en"
