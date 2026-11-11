import io
from pypdf import PdfReader


class DocumentIngestionService:
    """Extracts raw text from uploaded PDF or plain text notices."""

    @staticmethod
    def extract_from_pdf_bytes(pdf_bytes: bytes) -> str:
        reader = PdfReader(io.BytesIO(pdf_bytes))
        pages_text = []
        for idx, page in enumerate(reader.pages):
            text = page.extract_text()
            if text:
                pages_text.append(f"--- PAGE {idx + 1} ---\n{text}")
        return "\n\n".join(pages_text)
