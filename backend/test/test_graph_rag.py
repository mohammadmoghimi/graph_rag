from elasticsearch import Elasticsearch

from knowledge.embeddings import get_embedding_model
from knowledge.retriever import ElasticsearchHybridRetriever
from knowledge.graph_rag import GraphRAG


es = Elasticsearch("http://localhost:9200")

embeddings = get_embedding_model()

retriever = ElasticsearchHybridRetriever(
    es_client=es,
    index_name="knowledge_chunks",
    embedding_model=embeddings,
    k=4
)

rag = GraphRAG(retriever)

answer = rag.answer(
    "یک نکته راجع به بازی mortal shells 2 بگو"
)

print(answer)