from langchain_core.documents import Document
from knowledge.graph import Neo4jClient


graph = Neo4jClient()

chunk = Document(
    page_content="Test chunk",
    metadata={
        "chunk_id": "test-1",
        "crawl_id": 1,
        "source_url": "https://example.com"
    }
)

graph.create_chunk(
    website_id=1,
    chunk=chunk
)

graph.close()

print("Graph write successful")