
from pathlib import Path
import csv
from pypdf import PdfReader
from docx import Document


def load_document(file_path):
    """Extract text from PDF, DOCX, TXT or CSV."""

    path = Path(file_path)
    extension = path.suffix.lower()

    if extension == ".pdf":
        reader = PdfReader(str(path))
        return "\n".join(
            page.extract_text() or "" for page in reader.pages
        )

    elif extension == ".docx":
        document = Document(str(path))
        return "\n".join(
            paragraph.text for paragraph in document.paragraphs
        )

    elif extension == ".txt":
        return path.read_text(encoding="utf-8")

    elif extension == ".csv":
        with path.open(
            "r", encoding="utf-8-sig", newline=""
        ) as file:
            rows = list(csv.reader(file))

        return "\n".join(
            " | ".join(row) for row in rows
        )

    else:
        raise ValueError(
            f"Unsupported file format: {extension}"
        )


if __name__ == "__main__":
    print("Document loader ready!")
