from docling.document_converter import DocumentConverter
import json

PDF_FILE = "KQ205.pdf"

converter = DocumentConverter()

result = converter.convert(PDF_FILE)

# Markdown
markdown = result.document.export_to_markdown()

with open("docling_output.md", "w", encoding="utf-8") as f:
    f.write(markdown)

# JSON export
try:
    doc_json = result.document.export_to_dict()

    with open("docling_output.json", "w", encoding="utf-8") as f:
        json.dump(doc_json, f, indent=2, ensure_ascii=False)

    print("Saved: docling_output.json")

except Exception as e:
    print(f"JSON export failed: {e}")

print("\n===== MARKDOWN PREVIEW =====\n")
print(markdown[:10000])