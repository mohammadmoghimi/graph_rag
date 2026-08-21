from django.utils import timezone

from .pipeline import crawl_and_chunk


def process_website(website, crawl):
    crawl.status = "running"
    crawl.started_at = timezone.now()
    crawl.save()

    try:
        documents, chunks = crawl_and_chunk(
            website.url,
            website.id,
            crawl.id,
            max_pages=5
        )

        if not documents:
            raise ValueError("No pages were crawled.")

        if not chunks:
            raise ValueError("No chunks were created.")

        crawl.pages_found = len(documents)
        crawl.pages_processed = len(documents)
        crawl.status = "completed"
        crawl.completed_at = timezone.now()
        crawl.save()

        return documents, chunks

    except Exception as e:
        crawl.status = "failed"
        crawl.error_message = str(e)
        crawl.completed_at = timezone.now()
        crawl.save()

        raise

