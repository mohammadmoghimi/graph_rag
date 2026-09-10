from pathlib import Path
from pypdf import PdfReader


def extract_text(file_path):
    extension = Path(file_path).suffix.lower()

    if extension == ".pdf":
        return extract_pdf(file_path)

    if extension == ".txt":
        return extract_txt(file_path)

    raise ValueError("Only PDF and TXT files are supported.")


def extract_pdf(file_path):
    reader = PdfReader(file_path)

    text = []

    for page in reader.pages:
        content = page.extract_text()

        if content:
            text.append(content)

    return "\n".join(text)


def extract_txt(file_path):
    return Path(file_path).read_text(encoding="utf-8")