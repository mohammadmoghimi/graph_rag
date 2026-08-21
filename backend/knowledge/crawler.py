import time
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse, urldefrag
from concurrent.futures import ThreadPoolExecutor, as_completed
from requests.adapters import HTTPAdapter
from langchain_core.documents import Document


def normalize_url(url):
    url = urldefrag(url)[0]
    parsed = urlparse(url)
    return parsed._replace(
        netloc=parsed.netloc.lower(),
        path=parsed.path.rstrip("/") or "/",
        fragment=""
    ).geturl()


def create_session(user_agent, max_retries):
    session = requests.Session()
    session.headers.update({"User-Agent": user_agent})

    retry = requests.adapters.Retry(
        total=max_retries,
        backoff_factor=1,
        status_forcelist=[429, 500, 502, 503, 504]
    )
    adapter = HTTPAdapter(
        max_retries=retry,
        pool_connections=20,
        pool_maxsize=20
    )

    session.mount("http://", adapter)
    session.mount("https://", adapter)
    return session

def extract_links(html, url, domain, visited):
    soup = BeautifulSoup(html, "lxml")
    links = set()

    for tag in soup.select("a[href]"):
        link = normalize_url(urljoin(url, tag["href"]))
        parsed = urlparse(link)

        if (
            parsed.scheme in ("http", "https")
            and parsed.netloc == domain
            and link not in visited
        ):
            links.add(link)

    return links


def extract_content(html, url):
    soup = BeautifulSoup(html, "lxml")

    for tag in soup.select(
        "script, style, noscript, nav"
    ):
        tag.decompose()

    return Document(
        page_content=soup.get_text(" ", strip=True),
        metadata={"source_url": url}
    )


def fetch_page(url, session, domain, visited, delay, timeout):
    try:
        time.sleep(delay)

        response = session.get(url, timeout=timeout)
        response.raise_for_status()

        html = response.text

        links = extract_links(html, url, domain, visited)

        document = extract_content(html, url)

        return document, links

    except requests.RequestException as e:
        print(f"Request failed: {url} — {e}")
        return None, set()


def crawl_website(
    start_url,
    max_pages=5,
    concurrent_workers=5,
    delay=0.5,
    timeout=10,
    max_retries=2,
    user_agent="Mozilla/5.0",
    page_timeout=None,
):
    start_url = normalize_url(start_url)
    domain = urlparse(start_url).netloc
    session = create_session(user_agent, max_retries)

    visited = set()
    queued = {start_url}
    queue = [start_url]
    documents = []

    if page_timeout is None:
        page_timeout = timeout + delay + 5  

    print(f"Starting crawl of {start_url} (max {max_pages} pages)")
    print(f"Per‑page timeout: {page_timeout} seconds")

    with ThreadPoolExecutor(max_workers=concurrent_workers) as executor:

        while queue and len(documents) < max_pages:
            urls = queue[:max_pages - len(documents)]
            queue = queue[len(urls):]

            futures = {
                executor.submit(
                    fetch_page,
                    url,
                    session,
                    domain,
                    visited,
                    delay,
                    timeout
                ): url
                for url in urls
            }

            for future in as_completed(futures):
                url = futures[future]
                visited.add(url)

                try:
                    document, links = future.result(timeout=page_timeout)
                except TimeoutError:
                    print(f"Page {url} timed out after {page_timeout}s")
                    continue
                except Exception as exc:
                    print(f"Page {url} raised an unexpected error: {exc}")
                    continue

                if document:
                    documents.append(document)
                    print(
                        f"Page {len(documents)}/{max_pages}: {url}"
                    )

                for link in links:
                    if link not in visited and link not in queued:
                        queued.add(link)
                        queue.append(link)

                if len(documents) >= max_pages:
                    break

    if not documents:
        print("No pages fetched")

    return documents