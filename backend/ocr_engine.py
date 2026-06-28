import os
import traceback

def extract_text_from_pdf(pdf_path: str) -> dict:
    """
    Extract text and markdown from PDF using Docling, with pdfplumber fallback.
    Returns:
        {
            "text": str,
            "markdown": str,
            "success": bool,
            "method": str
        }
    """
    if not os.path.exists(pdf_path):
        return {"text": "", "markdown": "", "success": False, "method": "none", "error": "File not found"}

    # Try Docling first
    try:
        from docling.document_converter import DocumentConverter
        converter = DocumentConverter()
        result = converter.convert(pdf_path)
        markdown = result.document.export_to_markdown()
        # For plain text, we can just use the markdown or strip basic markdown chars
        text = markdown.replace("#", "").replace("|", " ").replace("---", "")
        return {
            "text": text,
            "markdown": markdown,
            "success": True,
            "method": "docling"
        }
    except Exception as e:
        print(f"Docling OCR failed for {pdf_path}: {e}. Falling back to pdfplumber...")

    # Fallback to pdfplumber
    try:
        import pdfplumber
        text_pages = []
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                t = page.extract_text()
                if t:
                    text_pages.append(t)
        full_text = "\n\n".join(text_pages)
        return {
            "text": full_text,
            "markdown": full_text,
            "success": True,
            "method": "pdfplumber"
        }
    except Exception as e:
        err = traceback.format_exc()
        print(f"pdfplumber also failed for {pdf_path}: {err}")
        return {
            "text": "",
            "markdown": "",
            "success": False,
            "method": "failed",
            "error": str(e)
        }
