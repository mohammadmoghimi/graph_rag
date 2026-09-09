from .graph_retriever import GraphRetriever
from .llm import generate


class GraphRAG:
    def __init__(self, retriever):
        self.retriever = retriever

    def answer(self, question, history):
        documents = self.retriever.retrieve(question)

        context = "\n\n".join(
            document.page_content
            for document in documents
        )

        conversation = "\n".join(
            f"{message['role']}: {message['content']}"
            for message in history
        )
        print('context' , context)


        prompt = f"""
You are a precise question-answering assistant focused on the content of a specific website.

Strict Rules:
1. Base your answer SOLELY on the provided "Context" section below. Do not use your general knowledge, training data, or any information outside this context.
2. If the context does not explicitly contain the information needed to answer the "Question", or if the context is irrelevant, do not guess, infer beyond clear implications, or invent facts. 
3. In such cases, respond verbatim with the exact Persian phrase: "اطلاعات کافی برای پاسخ به این سؤال پیدا نشد."
4. Keep your answer short and to the point, but ensure it fully addresses the question based on the context.
5. CRITICAL: Your entire response MUST be written in Persian (Farsi). Never use any other language in your reply, regardless of the language used in the question.

Conversation History:
{conversation}

Context:
{context}

Question:
{question}
"""

        return generate(prompt)