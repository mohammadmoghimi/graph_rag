# test_trafilatura.py
import time
from urllib.parse import urlparse
from knowledge.crawler import create_session, extract_content  # assuming your file is named crawler.py

def test_trafilatura_on_urls(urls, delay=1):
    session = create_session("Mozilla/5.0", 2)
    results = []

    for url in urls:
        print(f"\n--- Testing: {url} ---")
        try:
            time.sleep(delay)
            resp = session.get(url, timeout=15)
            resp.raise_for_status()

            doc = extract_content(resp.text, url)
            if doc is None:
                print("❌ No main content extracted (returned None)")
                results.append((url, None, 0))
            else:
                text = doc.page_content
                print(f"✅ Extracted {len(text):,} characters")
                print(f"Preview (first 300 chars):\n{text[:30000]}...")
                results.append((url, text, len(text)))
        except Exception as e:
            print(f"❌ Error: {e}")
            results.append((url, None, 0))

    # Summary
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    for url, text, length in results:
        status = "✅" if text else "❌"
        print(f"{status} {url}: {length:,} chars")
    return results

if __name__ == "__main__":
    # Replace with URLs you want to test (news articles, blog posts, etc.)
    test_urls = [
        "https://fa.wikipedia.org/wiki/%DA%A9%D9%84%D8%A7%D9%84%D9%87"
    ]
    test_trafilatura_on_urls(test_urls)