
from pathlib import Path

from pypdf import PdfReader


def load_pdf(file_path: str) -> list[dict]:
    """
    Extract text from a PDF file.

    Returns a list of pages with their text and metadata.
    """

    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")

    if path.suffix.lower() != ".pdf":
        raise ValueError("Only PDF files are supported.")

    reader = PdfReader(str(path))

    documents = []

    for page_number, page in enumerate(reader.pages, start=1):
        text = page.extract_text() or ""

        if not text.strip():
            continue

        documents.append(
            {
                "content": text,
                "metadata": {
                    "source": path.name,
                    "page": page_number,
                    "file_path": str(path.resolve()),
                },
            }
        )

    return documents
