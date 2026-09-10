from pathlib import Path
from pypdf import PdfReader


def extract_text(file):
    extension = Path(file.name).suffix.lower()

    if extension == ".pdf":
        return extract_pdf(file)

    if extension == ".txt":
        return extract_txt(file)

    raise ValueError("Only PDF and TXT files are supported.")


def extract_pdf(file):
    reader = PdfReader(file)

    text = []

    for page in reader.pages:
        content = page.extract_text()

        if content:
            text.append(content)

    return "\n".join(text)


def extract_txt(file):
    return file.read().decode("utf-8")