from django.utils import timezone

from .embeddings import get_embedding_model
from .indexer import index_chunks
from .pipeline import crawl_and_chunk


def process_website(website, crawl):
    start_crawl(crawl)

    try:
        documents, chunks = crawl_and_chunk(
            website.url,
            website.id,
            crawl.id,
            max_pages=1
        )

        index_website(chunks)

        complete_crawl(crawl, len(documents))

        return documents, chunks

    except Exception as error:
        fail_crawl(crawl, error)
        raise


def start_crawl(crawl):
    crawl.status = "running"
    crawl.started_at = timezone.now()
    crawl.save()


def index_website(chunks):
    embeddings = get_embedding_model()
    index_chunks(chunks, embeddings)


def complete_crawl(crawl, page_count):
    crawl.pages_found = page_count
    crawl.pages_processed = page_count
    crawl.status = "completed"
    crawl.completed_at = timezone.now()
    crawl.save()


def fail_crawl(crawl, error):
    crawl.status = "failed"
    crawl.error_message = str(error)
    crawl.completed_at = timezone.now()
    crawl.save()