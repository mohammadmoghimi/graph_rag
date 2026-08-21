from elasticsearch import Elasticsearch

es = Elasticsearch("http://localhost:9200")

response = es.search(
    index="knowledge_chunks",
    size=5,
    source=[
        "text",
        "metadata"
    ]
)

for hit in response["hits"]["hits"]:
    print(hit["_source"])