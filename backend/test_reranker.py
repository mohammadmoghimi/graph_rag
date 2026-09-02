# test_reranker.py
from sentence_transformers import CrossEncoder
from langchain_core.documents import Document
import os

class Reranker:
    def __init__(self):
        # Load the model. If you have it locally, use the folder path.
        self.model = CrossEncoder("BAAI/bge-reranker-v2-m3")

    def rerank(self, query, documents, top_k=5):
        if not documents:
            return []

        pairs = [(query, doc.page_content) for doc in documents]
        scores = self.model.predict(pairs)

        ranked = sorted(zip(documents, scores), key=lambda x: x[1], reverse=True)
        return [doc for doc, _ in ranked[:top_k]]


# Create some dummy documents (mix of relevant & irrelevant)
query = "علیرضا محمدی کیست؟"

documents = [
    Document(
        page_content="علیرضا محمدی یک نویسنده و کارگردان ایرانی است که بیشتر به خاطر کتاب‌های علمی-تخیلی و فیلم‌های کوتاه خود شناخته می‌شود."
    ),
    Document(
        page_content="آخرین اخبار از وضعیت آب و هوا در تهران: امروز هوا ابری و بارانی است."
    ),
    Document(
        page_content="علیرضا محمدی در مصاحبه‌ای با خبرگزاری مهر گفت که پروژه جدید خود را با همکاری نشر نیما آغاز کرده است."
    ),
    Document(
        page_content="این مقاله به بررسی تأثیر شبکه‌های اجتماعی بر روابط خانوادگی می‌پردازد."
    ),
    Document(
        page_content="محمد رضا محمدی (برادر علیرضا) نیز در حوزه سینما فعالیت دارد اما بیشتر به عنوان تهیه‌کننده شناخته می‌شود."
    ),
    Document(
        page_content="نشست نقد و بررسی کتاب «جهان های موازی» با حضور علیرضا محمدی در کتابخانه ملی برگزار شد."
    ),
]

print("Testing Reranker with Persian query...\n")

try:
    reranker = Reranker()
    ranked_docs = reranker.rerank(query, documents, top_k=3)

    print(f"Query: {query}\n")
    print("Top ranked documents:")
    for i, doc in enumerate(ranked_docs, 1):
        print(f"{i}. {doc.page_content[:100]}...")

except Exception as e:
    print(f"Error: {e}")
    print("\nPossible solutions:")
    print("1. Set environment variable: export HF_ENDPOINT=https://hf-mirror.com")
    print("2. Download model manually and use local path: CrossEncoder('./path/to/model')")