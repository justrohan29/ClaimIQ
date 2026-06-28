import json
from backend.utils import fuzzy_match, compare_values, client
from backend.document_processor import clean_json_response

REQUIRED_DOC_TYPES = ["hospital_bill", "discharge_summary", "insurance_claim_form", "payment_receipt"]

def run_deterministic_checks(classified_data: dict, deep_data: dict) -> list:
    """Run deterministic Python consistency rules across documents."""
    issues = []
    
    # Map available doc types to their IDs and data
    doc_by_type = {}
    for doc_id, cinfo in classified_data.items():
        dtype = cinfo.get("doc_type", "unknown")
        doc_by_type[dtype] = {"id": doc_id, "summary": cinfo, "deep": deep_data.get(doc_id, {})}
        
    # 1. Missing Documents Check
    for req in REQUIRED_DOC_TYPES:
        if req not in doc_by_type:
            name_readable = req.replace("_", " ").title()
            issues.append({
                "issue_id": f"missing_doc_{req}",
                "title": f"Missing Required Document: {name_readable}",
                "category": "Completeness",
                "severity": "critical",
                "documents": ["Missing Document"],
                "explanation": f"The claim package does not include a {name_readable}. Insurance payers require this document before processing or releasing payment.",
                "fix_recommendation": f"Upload the official {name_readable} to complete the claim packet.",
                "financial_impact": "Full claim rejection or processing hold",
                "needs_human_review": False,
                "confidence": 1.0
            })

    # 2. Patient Identity Consistency
    names = []
    for dtype, dinfo in doc_by_type.items():
        pname = dinfo["summary"].get("patient_name")
        if pname and len(pname) > 2:
            names.append((dtype, pname))
            
    for i in range(len(names)):
        for j in range(i + 1, len(names)):
            t1, n1 = names[i]
            t2, n2 = names[j]
            ratio = fuzzy_match(n1, n2)
            if ratio < 0.85:
                issues.append({
                    "issue_id": f"name_mismatch_{t1}_{t2}",
                    "title": "Patient Identity Mismatch Across Documents",
                    "category": "Identity",
                    "severity": "critical",
                    "documents": [t1.replace("_", " ").title(), t2.replace("_", " ").title()],
                    "explanation": f"Patient name is stated as '{n1}' on the {t1.replace('_', ' ')} but '{n2}' on the {t2.replace('_', ' ')}. Payers reject claims with conflicting patient identity.",
                    "fix_recommendation": f"Verify legal patient identity and amend the {t2.replace('_', ' ')} to match hospital records.",
                    "financial_impact": "Likely claim rejection — full amount at risk",
                    "needs_human_review": False,
                    "confidence": 0.98
                })

    # 3. Admission Date Consistency
    bill_info = doc_by_type.get("hospital_bill")
    form_info = doc_by_type.get("insurance_claim_form")
    if bill_info and form_info:
        b_date = bill_info["summary"].get("admission_date")
        f_date = form_info["summary"].get("admission_date")
        if b_date and f_date and b_date != f_date:
            # Check string match or partial match
            if not fuzzy_match(b_date, f_date, 0.8):
                issues.append({
                    "issue_id": "admission_date_mismatch",
                    "title": "Admission Date Discrepancy",
                    "category": "Date Consistency",
                    "severity": "critical",
                    "documents": ["Hospital Bill", "Insurance Claim Form"],
                    "explanation": f"Hospital bill shows admission on '{b_date}', whereas the insurance claim form reports admission on '{f_date}'. Timeline discrepancies trigger mandatory fraud audit holds.",
                    "fix_recommendation": f"Correct the admission date on the insurance claim form to exactly match the hospital bill ({b_date}).",
                    "financial_impact": "Claim processing freeze & manual audit",
                    "needs_human_review": False,
                    "confidence": 0.95
                })

    # 4. Financial Total & Arithmetic Check
    if bill_info and form_info:
        b_deep = bill_info["deep"]
        f_deep = form_info["deep"]
        b_net = b_deep.get("net_total") or bill_info["summary"].get("total_amount")
        f_claim = f_deep.get("claimed_total") or form_info["summary"].get("total_amount")
        
        if b_net and f_claim:
            try:
                bn = float(b_net)
                fc = float(f_claim)
                if abs(bn - fc) > 10.0: # Mismatch over 10 rupees
                    issues.append({
                        "issue_id": "claimed_amount_mismatch",
                        "title": "Claimed Amount vs Hospital Bill Net Mismatch",
                        "category": "Financial Accuracy",
                        "severity": "warning",
                        "documents": ["Hospital Bill", "Insurance Claim Form"],
                        "explanation": f"Insurance form claims INR {fc:,.2f}, but hospital bill net payable is INR {bn:,.2f} (difference of INR {abs(fc-bn):,.2f}, likely due to ignored institutional discount).",
                        "fix_recommendation": f"Adjust the insurance claim amount to match the exact net hospital bill of INR {bn:,.2f}.",
                        "financial_impact": f"Partial deduction or query for INR {abs(fc-bn):,.2f}",
                        "needs_human_review": False,
                        "confidence": 0.92
                    })
            except (ValueError, TypeError):
                pass

    return issues

def run_ai_medical_and_financial_reasoning(classified_data: dict, deep_data: dict) -> list:
    """Call 3 & 4 combined into one efficient AI reasoning prompt to save latency and tokens."""
    prompt = f"""You are an expert medical auditor and insurance claim investigator. Analyze the extracted data from a hospital claim packet below.

SUMMARY DATA:
{json.dumps(classified_data, indent=2)}

DEEP CLINICAL & FINANCIAL DATA:
{json.dumps(deep_data, indent=2)}

Perform deep medical logic reasoning and financial auditing. Specifically check for:
1. Medical Logic: Are prescribed medications (e.g. insulin, metformin) justified by the diagnosis (e.g. appendicitis)? Are there contradictions between lab results (e.g. normal fasting sugar 96 mg/dL) and pre-existing condition claims (e.g. Diabetes Type 2)?
2. Timeline Sanity: Was any lab test or procedure conducted before the admission date?
3. Financial Overcharge: Are there charges on the bill for unneeded therapies (like insulin administration for appendicitis)?

Return ONLY valid JSON containing a list of reasoned issues:
{{
  "ai_issues": [
    {{
      "issue_id": "unjustified_insulin_therapy",
      "title": "Insulin & Metformin Prescribed Without Diabetes Diagnosis",
      "category": "Medical Logic",
      "severity": "warning",
      "documents": ["Prescription", "Discharge Summary", "Lab Report"],
      "explanation": "Patient is diagnosed solely with acute appendicitis. However, prescription lists Insulin Glargine and Metformin, and lab report shows normal Fasting Blood Sugar (96 mg/dL). Prescribing anti-diabetic drugs without clinical indication flags audit failure.",
      "fix_recommendation": "Obtain clarification or treating doctor's addendum explaining diabetes therapy, or remove unverified medication charges.",
      "financial_impact": "Deduction of pharmacy & injection charges (~INR 780+)",
      "needs_human_review": True,
      "confidence": 0.88
    }}
  ]
}}"""

    print("  [Call 3 & 4] Calling DeepSeek for Medical Logic & Financial Auditing...")
    try:
        response = client.chat.completions.create(
            model="deepseek-chat",
            temperature=0.1,
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": "You are a healthcare claim fraud and medical reasoning auditor. Output exact JSON."},
                {"role": "user", "content": prompt}
            ]
        )
        raw = clean_json_response(response.choices[0].message.content)
        parsed = json.loads(raw)
        return parsed.get("ai_issues", [])
    except Exception as e:
        print(f"  WARNING: AI Reasoning call failed ({e}).")
        return []
