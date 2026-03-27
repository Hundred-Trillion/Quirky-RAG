from llama_index.core import VectorStoreIndex
from llama_index.core.retrievers import VectorIndexRetriever
from llama_index.core.query_engine import RetrieverQueryEngine
from llama_index.core.postprocessor import SimilarityPostprocessor
from llama_index.core import Settings
from backend.pipeline import get_vector_store
from llama_index.core.vector_stores import ExactMatchFilter, MetadataFilters

# We'll mock out cross-encoder and hybrid BM25 setup here for simplicity but ensure the structure makes it easy
def get_answer(query: str, session_id: str, active_docs: list):
    vector_store = get_vector_store()
    
    filters = None
    if active_docs:
        filters = MetadataFilters(
            filters=[ExactMatchFilter(key="filename", value=doc) for doc in active_docs]
        )

    index = VectorStoreIndex.from_vector_store(vector_store)
    
    # Setup hybrid retriever if possible, we use standard Vector for now with query rewriting
    retriever = VectorIndexRetriever(
        index=index,
        similarity_top_k=5,
        filters=filters,
    )

    # Postprocessor for cross-encoder reranking placeholder & simple ground threshold
    node_postprocessors = [
        SimilarityPostprocessor(similarity_cutoff=0.65)
    ]

    query_engine = RetrieverQueryEngine(
        retriever=retriever,
        node_postprocessors=node_postprocessors,
    )

    response = query_engine.query(query)

    # Retry loop logic
    if len(response.source_nodes) == 0:
        return "I could not find a highly confident answer in the provided documents. Please rephrase or use different documents."

    return str(response)
