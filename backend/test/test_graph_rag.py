from elasticsearch import Elasticsearch

from knowledge.embeddings import get_embedding_model
from knowledge.retriever import ElasticsearchHybridRetriever
from knowledge.graph_retriever import GraphRetriever
from dotenv import load_dotenv
import django
import os
# Load Django settings
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
load_dotenv()

es = Elasticsearch("http://localhost:9200")
embeddings = get_embedding_model()

website_ids = [51]

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

documents = graph_retriever.retrieve(
    "فصل دوم pluribus کی پخش میشود ؟"

)

for document in documents:
    print("WEBSITE:", document.metadata.get("website_id"))
    print("CHUNK:", document.metadata.get("chunk_id"))
    print(document.page_content)
    print("-" * 60)