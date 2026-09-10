from .llm import generate

class GraphRAG:
    def __init__(self, retriever):
        self.retriever = retriever

    def answer(self, question, history):
        documents = self.retriever.retrieve(question)

        if not documents:
            return "اطلاعات کافی برای پاسخ به این سؤال پیدا نشد."

        print("\nTOP CHUNK:")
        print(documents[0].page_content)
        print()

        context = "\n\n".join(
            document.page_content
            for document in documents
        )

        prompt = f"""
Answer the question using the context.

Context:
{context}


Question:
{question}

Give a short answer in Persian.
If the answer is present in the context, answer it directly.
If the context does not contain the answer, say:
اطلاعات کافی برای پاسخ به این سؤال پیدا نشد.

Answer:
"""

        return generate(prompt)
    



# from .llm import generate


# class GraphRAG:
#     def __init__(self, retriever):
#         self.retriever = retriever

#     def answer(self, question, history):
#         documents = self.retriever.retrieve(question)

#         context = "\n\n".join(
#             document.page_content
#             for document in documents
#         )

#         conversation = "\n".join(
#             f"{message['role']}: {message['content']}"
#             for message in history
#         )

#         print("context:", context)

#         prompt = f"""
# You are a question-answering assistant for a Retrieval-Augmented Generation system.

# Your task is to answer the user's question using ONLY the information provided in the Context.

# Rules:
# 1. Carefully read the Context and identify information that answers the Question.
# 2. The answer does not need to use the exact wording of the Question. Understand the meaning of the Question and find the corresponding information in the Context.
# 3. You may combine information from different parts of the Context when necessary.
# 4. Do not use your general knowledge, training knowledge, assumptions, or outside information.
# 5. If the Context contains enough information to answer the Question, provide the answer.
# 6. Only if the Context does not contain enough information to answer the Question, respond exactly with:
# "اطلاعات کافی برای پاسخ به این سؤال پیدا نشد."
# 7. Keep the answer concise and directly answer the Question.
# 8. Always answer in Persian (Farsi).
# 9. Conversation history is provided only to understand the context of the current question. Do not use it as a source of factual information.

# Conversation History:
# {conversation}

# Context:
# {context}

# Question:
# {question}

# Answer:
# """

#         return generate(prompt)