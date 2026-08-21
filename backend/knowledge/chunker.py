from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter


def split_into_chunks(documents, chunk_size=500, chunk_overlap=100):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap
    )

    return splitter.split_documents(documents)