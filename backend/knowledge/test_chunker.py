from crawler import crawl_website
from chunker import split_into_chunks

documents = crawl_website(
    "https://example.com",
    max_pages=5
)

chunks = split_into_chunks(documents)

print(f"Documents: {len(documents)}")
print(f"Chunks: {len(chunks)}")

for chunk in chunks[:3]:
    print(chunk.metadata)
    print(chunk.page_content[:100])