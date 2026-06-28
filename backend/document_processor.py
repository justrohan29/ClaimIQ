import json
import re
from backend.utils import client

def clean_json_response(content: str):
    """Strip markdown code fences and clean JSON from LLM response."""
    content = content.strip()
    if content.startswith("```"):
        content = re.sub(r'^```(?:json)?\s*', '', content)
        content = re.sub(r'\s*```$', '', content)
    return content.strip()

def classify_and_quick_extract(docs_data: dict) -> dict:
    """
    Call 1: Batch Classify + Quick Extract for all uploaded documents.
    Input: { "doc_id": { "text": "...", "filename": "..." }, ... }
    Returns: { "doc_id": { "doc_type": "...", "patient_name": "...", ... } }
    """
    prompt_docs = []
    for doc_id, info in docs_data.items():
        snippet = info["text"][:1500]
        prompt_docs.append(f"--- DOCUMENT ID: {doc_id} (Filename: {info['filename']}) ---\n{snippet}\n")
        
    combined_text = "\n".join(prompt_docs)
    
    prompt = f"""You are an expert healthcare document auditor and data extractor. Below are snippets from documents submitted in an insurance claim package.

{combined_text}

For EACH DOCUMENT ID, determine its classification and extract key summary entities.
Allowed document types:
- hospital_bill
- discharge_summary
- prescription
- lab_report
- insurance_claim_form
- payment_receipt
- pharmacy_invoice
- doctor_certificate
- unknown

Return ONLY a valid JSON object matching this schema exactly (no markdown fences, no explanation):
{{
  "results": {{
    "doc_id": {{
      "doc_type": "hospital_bill",
      "confidence": 0.98,
      "patient_name": "Extracted name or null",
      "hospital_name": "Extracted hospital name or null",
      "admission_date": "YYYY-MM-DD or string found or null",
      "discharge_date": "YYYY-MM-DD or string found or null",
      "total_amount": 85000.0 or null,
      "doctor_name": "Extracted doctor name or null"
    }}
  }}
}}"""

    print("  [Call 1] Calling DeepSeek for Batch Classification & Quick Extraction...")
    try:
        response = client.chat.completions.create(
            model="deepseek-chat",
            temperature=0,
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": "You are a healthcare claim data extraction AI. Always output valid JSON."},
                {"role": "user", "content": prompt}
            ]
        )
        raw = clean_json_response(response.choices[0].message.content)
        parsed = json.loads(raw)
        return parsed.get("results", parsed)
    except Exception as e:
        print(f"  WARNING: Call 1 failed ({e}). Returning generic unclassified fallback.")
        fallback = {}
        for doc_id, info in docs_data.items():
            fallback[doc_id] = {"doc_type": "unknown", "confidence": 0.0, "patient_name": None}
        return fallback

def deep_extract_complex_docs(docs_data: dict, classified_results: dict) -> dict:
    """
    Call 2: Deep Extraction for Hospital Bill & Discharge Summary (and Claim Form if available).
    Extracts itemized line items, medications, ICD codes, and clinical history.
    """
    target_docs = []
    for doc_id, cinfo in classified_results.items():
        dtype = cinfo.get("doc_type", "")
        if dtype in ["hospital_bill", "discharge_summary", "insurance_claim_form", "pharmacy_invoice"]:
            target_docs.append((doc_id, dtype, docs_data[doc_id]["text"][:3500]))
            
    if not target_docs:
        return {}

    prompt_docs = []
    for doc_id, dtype, text in target_docs:
        prompt_docs.append(f"--- DOCUMENT ID: {doc_id} (Type: {dtype}) ---\n{text}\n")
        
    combined_text = "\n".join(prompt_docs)
    
    prompt = f"""You are a deep clinical and financial extraction AI. Below are full texts of complex medical documents from a claim.

{combined_text}

For each document, extract exhaustive detailed structured data.
Return ONLY valid JSON matching this structure:
{{
  "deep_results": {{
    "doc_id": {{
      "line_items": [
        {{"description": "Room Charges", "amount": 7500.0}},
        {{"description": "Insulin Glargine Admin", "amount": 700.0}}
      ],
      "medications_mentioned": [
        {{"name": "Tab Cefixime", "dosage": "200mg", "frequency": "1-0-1"}},
        {{"name": "Inj Insulin Glargine", "dosage": "10 IU", "frequency": "0-0-1"}}
      ],
      "diagnoses": ["Acute Appendicitis", "Diabetes Mellitus Type 2"],
      "icd_codes": ["K35.80"],
      "procedures": ["Laparoscopic Appendectomy"],
      "days_of_stay": 3,
      "claimed_total": 85600.0,
      "net_total": 85000.0
    }}
  }}
}}"""

    print("  [Call 2] Calling DeepSeek for Deep Clinical & Financial Extraction...")
    try:
        response = client.chat.completions.create(
            model="deepseek-chat",
            temperature=0,
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": "You are a clinical extraction expert. Output exact valid JSON."},
                {"role": "user", "content": prompt}
            ]
        )
        raw = clean_json_response(response.choices[0].message.content)
        parsed = json.loads(raw)
        return parsed.get("deep_results", parsed)
    except Exception as e:
        print(f"  WARNING: Call 2 failed ({e}). Returning empty deep extraction.")
        return {}
