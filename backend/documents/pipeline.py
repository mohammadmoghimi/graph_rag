from langchain_core.documents import Document
from knowledge.chunker import split_into_chunks


def document_to_chunks(document):
    text = extract_document_text(document)

    if not text.strip():
        raise ValueError("No text could be extracted from the document.")

    source = Document(
        page_content=text,
        metadata={
            "source_file": document.name,
            "source_type": "document",
            "document_id": document.id,
        }
    )

    chunks = split_into_chunks([source])

    for index, chunk in enumerate(chunks):
        chunk.metadata.update({
            "chunk_id": f"doc-{document.id}-{index}",
            "document_id": document.id,
            "source_type": "document",
            "source_file": document.name,
        })

    return chunks


def extract_document_text(document):
    from .extractor import extract_text

    return extract_text(document.file.path)