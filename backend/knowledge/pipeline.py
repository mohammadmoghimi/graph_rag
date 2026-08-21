from .crawler import crawl_website
from .chunker import split_into_chunks


def crawl_and_chunk(url, website_id, crawl_id, max_pages=5):
    documents = crawl_website(url, max_pages=max_pages)

    if not documents:
        raise ValueError("No pages were crawled.")

    chunks = split_into_chunks(documents)

    if not chunks:
        raise ValueError("No chunks were created.")

    for index, chunk in enumerate(chunks):
        chunk.metadata.update({
            "chunk_id": f"{crawl_id}-{index}",
            "website_id": website_id,
            "crawl_id": crawl_id,
            "source_url": chunk.metadata.get("source_url")
        })
    

    return documents, chunks