from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
import time


def split_into_chunks(documents, chunk_size=500, chunk_overlap=100):
    print("Starting document splitting process")
    print(f"Number of input documents: {len(documents)}")
    print(f"Chunk size: {chunk_size}, Chunk overlap: {chunk_overlap}")
    
    start_time = time.perf_counter()

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap
    )

    chunks = splitter.split_documents(documents)
    
    end_time = time.perf_counter()
    duration = end_time - start_time
    
    print(f"Splitting completed. Total chunks produced: {len(chunks)}")
    print(f"Duration: {duration:.2f} seconds")

    return chunks