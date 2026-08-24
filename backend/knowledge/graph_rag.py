from .graph_retriever import GraphRetriever
from .llm import generate


class GraphRAG:
    def __init__(self, retriever):
        self.retriever = retriever

    def answer(self, question):
        documents = self.retriever.retrieve(question)

        context = "\n\n".join(
            document.page_content
            for document in documents
        )

        prompt = f"""
تو یک دستیار پرسش و پاسخ درباره یک وب‌سایت هستی.

فقط بر اساس اطلاعات موجود در Context پاسخ بده.
اگر اطلاعات کافی برای پاسخ وجود ندارد، بگو:
«اطلاعات کافی برای پاسخ به این سؤال پیدا نشد.»

پاسخ را به زبان فارسی و کوتاه ارائه کن.

Context:
{context}

Question:
{question}
"""

        return generate(prompt)