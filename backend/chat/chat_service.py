from knowledge.embeddings import get_embedding_model
from knowledge.retriever import ElasticsearchHybridRetriever
from knowledge.graph_retriever import GraphRetriever
from knowledge.graph_rag import GraphRAG
from elasticsearch import Elasticsearch


def answer_question(question, website_ids,history):
    es = Elasticsearch("http://localhost:9200")
    embeddings = get_embedding_model()

    retriever = ElasticsearchHybridRetriever(
        es_client=es,
        index_name="knowledge_chunks",
        embedding_model=embeddings,
        website_ids=website_ids,
        k=4
    )

    graph_retriever = GraphRetriever(
        retriever,
        website_ids
    )

    rag = GraphRAG(graph_retriever)

    return rag.answer(question , history)