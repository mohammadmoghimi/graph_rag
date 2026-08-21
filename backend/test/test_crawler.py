from crawler import crawl_website

documents = crawl_website(
    "https://digikala.ir/",
    max_pages=5
)

print(f"Documents: {len(documents)}")

for document in documents:
    print(document.metadata)
    print(document.page_content[:100])