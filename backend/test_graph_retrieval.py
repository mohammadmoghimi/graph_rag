from knowledge.retriever import ElasticsearchHybridRetriever
from knowledge.graph_retriever import GraphRetriever
from knowledge.embeddings import get_embedding_model
from elasticsearch import Elasticsearch
from dotenv import load_dotenv
import django
import os
# Load Django settings
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
load_dotenv()

es = Elasticsearch("http://localhost:9200")
embeddings = get_embedding_model()
retriever = ElasticsearchHybridRetriever(
    es_client=es,
    index_name="knowledge_chunks",
    embedding_model=embeddings,
    website_ids=[8],
    k=5
)
print("Creating graph retriever...")
graph_retriever = GraphRetriever(
    retriever,
    website_ids=[8],
    k=5
)
print("Starting retrieval...")

query = " کامبرین چیست ؟"

documents = graph_retriever.retrieve(query)
print(f"Retrieved {len(documents)} documents")

for i, document in enumerate(documents, 1):
    print(f"\n--- RESULT {i} ---")
    print("Chunk:", document.metadata.get("chunk_id"))
    print(document.page_content[:1000])