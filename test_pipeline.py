import asyncio
import json
from backend.ocr_engine import extract_text_from_pdf
from backend.document_processor import classify_and_quick_extract, deep_extract_complex_docs
from backend.cross_checker import run_deterministic_checks, run_ai_medical_and_financial_reasoning
from backend.scorer import calculate_readiness_score
from backend.report_generator import generate_audit_report
import os

SAMPLE_DIR = os.path.join(os.path.dirname(__file__), "sample_data", "output")

def run_test():
    print("=== CLAIMIQ BACKEND PIPELINE VERIFICATION ===")
    files = sorted([f for f in os.listdir(SAMPLE_DIR) if f.endswith(".pdf")])
    print(f"Found {len(files)} sample PDFs in {SAMPLE_DIR}")
    
    docs_data = {}
    for fn in files:
        path = os.path.join(SAMPLE_DIR, fn)
        res = extract_text_from_pdf(path)
        docs_data[fn] = {"filename": fn, "text": res["text"], "markdown": res["markdown"]}
        print(f"  [OCR] {fn}: extracted {len(res['text'])} chars (method: {res['method']})")
        
    print("\n--- Running Stage 2: Classification & Quick Extract ---")
    classified = classify_and_quick_extract(docs_data)
    print("Classified Results summary:")
    for k, v in classified.items():
        print(f"  {k} -> {v.get('doc_type')} (Patient: {v.get('patient_name')})")
        
    print("\n--- Running Stage 3: Deep Extraction ---")
    deep = deep_extract_complex_docs(docs_data, classified)
    print(f"Deep extracted {len(deep)} complex documents.")
    
    print("\n--- Running Stage 4: Consistency Verification ---")
    det_issues = run_deterministic_checks(classified, deep)
    print(f"Deterministic checks found {len(det_issues)} issues.")
    for iss in det_issues:
        print(f"  - [{iss['severity'].upper()}] {iss['title']}")
        
    ai_issues = run_ai_medical_and_financial_reasoning(classified, deep)
    print(f"AI reasoning found {len(ai_issues)} issues.")
    for iss in ai_issues:
        print(f"  - [{iss['severity'].upper()}] {iss['title']}")
        
    all_issues = det_issues + ai_issues
    
    print("\n--- Running Stage 5: Scoring & Report ---")
    score_data = calculate_readiness_score(classified, all_issues, deep)
    print(f"Readiness Score: {score_data['overall_score']}/100 ({score_data['risk_level']} Risk)")
    print(f"Amount at Risk: INR {score_data['financial_impact']['amount_at_risk']:,.2f}")
    
    report_data = generate_audit_report(classified, all_issues, score_data)
    print(f"\nExecutive Summary:\n\"{report_data['summary']}\"")
    print(f"\nPrioritized Fixes: {len(report_data['fixes'])} items.")
    
    print("\n=== VERIFICATION SUCCESSFUL ===")

if __name__ == "__main__":
    run_test()
