#!/usr/bin/env python
import sys
from elasticsearch import Elasticsearch

# Connect to your local Elasticsearch (adjust URL if needed)
ES_URL = "http://localhost:9200"
INDEX_NAME = "knowledge_chunks"

def search_by_crawl_id(crawl_id, size=10):
    """
    Search for documents in the knowledge_chunks index that match a specific crawl_id.
    Prints document count and sample documents.
    """
    es = Elasticsearch(ES_URL)

    # Build a term query on metadata.crawl_id
    query_body = {
        "query": {
            "term": {
                "metadata.crawl_id": crawl_id
            }
        }
    }

    # Execute search
    response = es.search(index=INDEX_NAME, body=query_body, size=size)
    
    total = response['hits']['total']['value']
    print(f"Found {total} chunks for crawl_id: {crawl_id}")

    if total == 0:
        return

    print(f"\nShowing up to {size} sample documents:")
    for idx, hit in enumerate(response['hits']['hits'], 1):
        print(f"\n--- Document {idx} ---")
        print(f"_id: {hit['_id']}")
        source = hit['_source']
        # Print the whole source or just metadata
        print("Source:")
        print(f"  text: {source.get('text', '')[:200]}...")  # first 200 chars
        print(f"  metadata: {source.get('metadata', {})}")

def count_by_crawl_id(crawl_id):
    """Quick count of documents for a given crawl_id."""
    es = Elasticsearch(ES_URL)
    query = {
        "query": {
            "term": {"metadata.crawl_id": crawl_id}
        }
    }
    response = es.count(index=INDEX_NAME, body=query)
    print(f"Total documents for crawl_id {crawl_id}: {response['count']}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python search_by_crawl.py <crawl_id> [--count]")
        sys.exit(1)

    crawl_id = sys.argv[1]
    if "--count" in sys.argv:
        count_by_crawl_id(crawl_id)
    else:
        search_by_crawl_id(crawl_id, size=10)