from elasticsearch import Elasticsearch
from knowledge.embeddings import get_embedding_model
from knowledge.retriever import ElasticsearchHybridRetriever
from knowledge.graph_retriever import GraphRetriever
from dotenv import load_dotenv

load_dotenv()


INDEX_NAME = "knowledge_chunks"

es = Elasticsearch("http://localhost:9200")
embeddings = get_embedding_model()

retriever = ElasticsearchHybridRetriever(
    es_client=es,
    index_name=INDEX_NAME,
    embedding_model=embeddings,
    k=4
)

graph_retriever = GraphRetriever(retriever)

documents = graph_retriever.retrieve(
    "بازی mortal shell 2 "
)

for document in documents:
    print("METADATA:")
    print(document.metadata)

    print("CONTENT:")
    print(document.page_content)

    print("-" * 50)