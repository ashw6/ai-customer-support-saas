from io import BytesIO

from pypdf import PdfReader
from langchain_community.document_loaders import PyPDFLoader


class PDFLoadError(ValueError):
    pass


def extract_pdf_text(file_bytes: bytes) -> str:
    """Extract text from PDF using LangChain's PyPDFLoader for better compatibility."""
    try:
        # Save bytes to temporary file for LangChain loader
        import tempfile
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
            tmp_file.write(file_bytes)
            tmp_file_path = tmp_file.name

        # Use LangChain's PyPDFLoader
        loader = PyPDFLoader(tmp_file_path)
        pages = loader.load()

        # Extract text from pages
        extracted_pages: list[str] = []
        for page_number, page in enumerate(pages, start=1):
            text = page.page_content or ""
            if text.strip():
                extracted_pages.append(f"Page {page_number}\n{text.strip()}")

        extracted = "\n\n".join(extracted_pages).strip()

        # Clean up temporary file
        import os
        os.unlink(tmp_file_path)

        if not extracted:
            raise PDFLoadError("No extractable text was found in the PDF.")
        return extracted

    except Exception as exc:
        # Fallback to pypdf if LangChain fails
        try:
            reader = PdfReader(BytesIO(file_bytes))
            pages: list[str] = []
            for page_number, page in enumerate(reader.pages, start=1):
                text = page.extract_text() or ""
                if text.strip():
                    pages.append(f"Page {page_number}\n{text.strip()}")
            extracted = "\n\n".join(pages).strip()
            if not extracted:
                raise PDFLoadError("No extractable text was found in the PDF.")
            return extracted
        except Exception as fallback_exc:
            raise PDFLoadError("Uploaded file is not a readable PDF.") from fallback_exc
