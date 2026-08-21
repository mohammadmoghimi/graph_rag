from langchain_elasticsearch import ElasticsearchStore
import time

ES_URL = "http://localhost:9200"
INDEX_NAME = "knowledge_chunks"


def index_chunks(chunks, embeddings):
    print("Starting indexing process")
    print(f"Connecting to Elasticsearch at {ES_URL}")
    print(f"Target index name: {INDEX_NAME}")
    print(f"Number of chunks to index: {len(chunks)}")
    
    start_time = time.perf_counter()
    vectorstore = ElasticsearchStore(
        es_url=ES_URL,
        index_name=INDEX_NAME,
        embedding=embeddings,
    )

    texts = [chunk.page_content for chunk in chunks]
    metadatas = [chunk.metadata for chunk in chunks]

    print("Adding documents to the index...")
    vectorstore.add_texts(
        texts=texts,
        metadatas=metadatas,
        refresh=False
    )

    vectorstore.client.indices.refresh(index=INDEX_NAME)

    end_time = time.perf_counter()
    duration = end_time - start_time
    
    print(f"Indexing completed. All {len(chunks)} chunks have been stored.")
    print(f"Duration: {duration:.2f} seconds")
    
    return vectorstore