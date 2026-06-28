import os
import traceback

def extract_text_from_pdf(pdf_path: str) -> dict:
    """
    Extract text and markdown from PDF using ultra-lightweight pypdf (~5MB RAM).
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

    try:
        from pypdf import PdfReader
        reader = PdfReader(pdf_path)
        text_pages = []
        for page in reader.pages:
            t = page.extract_text()
            if t:
                text_pages.append(t)
        
        full_text = "\n\n".join(text_pages)
        
        return {
            "text": full_text,
            "markdown": full_text,
            "success": True,
            "method": "pypdf"
        }
    except Exception as e:
        err = traceback.format_exc()
        print(f"pypdf extraction failed for {pdf_path}: {err}")
        return {
            "text": "",
            "markdown": "",
            "success": False,
            "method": "failed",
            "error": str(e)
        }
