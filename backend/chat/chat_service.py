from elasticsearch import Elasticsearch

from knowledge.embeddings import get_embedding_model
from knowledge.graph_retriever import GraphRetriever
from knowledge.graph_rag import GraphRAG
from knowledge.retriever import ElasticsearchHybridRetriever


def answer_question(question, website_ids, document_ids, history):
    es = Elasticsearch("http://localhost:9200")
    embeddings = get_embedding_model()

    retriever = ElasticsearchHybridRetriever(
        es_client=es,
        index_name="knowledge_chunks",
        embedding_model=embeddings,
        website_ids=website_ids,
        document_ids=document_ids,
        k=4
    )

    graph_retriever = GraphRetriever(
        retriever,
        website_ids,
        document_ids
    )

    rag = GraphRAG(graph_retriever)

    return rag.answer(question, history)