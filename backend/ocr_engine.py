import os
import traceback

os.environ["OMP_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"

_docling_converter = None

def get_docling_converter():
    global _docling_converter
    if _docling_converter is None:
        from docling.document_converter import DocumentConverter, PdfFormatOption
        from docling.datamodel.pipeline_options import PdfPipelineOptions
        
        pipeline_options = PdfPipelineOptions()
        pipeline_options.do_ocr = False
        pipeline_options.do_table_structure = False
        
        _docling_converter = DocumentConverter(
            format_options={"pdf": PdfFormatOption(pipeline_options=pipeline_options)}
        )
    return _docling_converter

def extract_text_from_pdf(pdf_path: str) -> dict:
    """
    Extract text and markdown from PDF using lightweight Docling (no heavy AI vision models).
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
        converter = get_docling_converter()
        result = converter.convert(pdf_path)
        markdown = result.document.export_to_markdown()
        text = markdown.replace("#", "").replace("|", " ").replace("---", "")
        return {
            "text": text,
            "markdown": markdown,
            "success": True,
            "method": "docling"
        }
    except Exception as e:
        err = traceback.format_exc()
        print(f"Docling OCR failed for {pdf_path}: {err}")
        return {
            "text": "",
            "markdown": "",
            "success": False,
            "method": "failed",
            "error": str(e)
        }
