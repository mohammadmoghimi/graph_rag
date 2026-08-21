from knowledge.pipeline import crawl_and_chunk
documents, chunks = crawl_and_chunk(
    "https://example.com",
    max_pages=5
)

print(f"Documents: {len(documents)}")
print(f"Chunks: {len(chunks)}")