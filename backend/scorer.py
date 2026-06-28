import re

def calculate_readiness_score(classified_data: dict, issues: list, deep_data: dict = None) -> dict:
    """
    Calculate claim readiness score (0-100), risk level, and financial impact.
    """
    # Base sub-scores
    completeness = 100
    identity = 100
    dates = 100
    financial = 100
    medical = 100
    
    amount_at_risk = 0.0
    total_claim = 0.0
    
    def parse_amt(val):
        if not val: return 0.0
        try:
            s = str(val).replace(",", "").replace("INR", "").replace("₹", "").strip()
            # find first float pattern
            m = re.search(r'[\d.]+', s)
            return float(m.group(0)) if m else 0.0
        except:
            return 0.0

    # Check total claimed amount from summary across bills or claim forms
    for doc_id, cinfo in classified_data.items():
        amt = parse_amt(cinfo.get("total_amount") or cinfo.get("claimed_total"))
        if amt > total_claim:
            total_claim = amt

    if deep_data:
        for doc_id, dinfo in deep_data.items():
            amt = parse_amt(dinfo.get("claimed_total") or dinfo.get("net_total"))
            if amt > total_claim:
                total_claim = amt

    # Deduct points based on issues
    for issue in issues:
        cat = issue.get("category", "")
        sev = issue.get("severity", "")
        
        # Estimate risk amount per issue dynamically
        if total_claim > 0:
            if sev == "critical":
                deduction = 35
                risk = total_claim * 0.35
            elif sev == "warning":
                deduction = 15
                risk = min(total_claim * 0.15, 5000.0)
            else:
                deduction = 5
                risk = min(total_claim * 0.05, 1000.0)
        else:
            if sev == "critical": deduction = 35
            elif sev == "warning": deduction = 15
            else: deduction = 5
            risk = 0.0
            
        amount_at_risk += risk

        if cat == "Completeness" or "missing" in issue["issue_id"]:
            completeness = max(0, completeness - deduction)
        elif cat == "Identity" or "name" in issue["issue_id"]:
            identity = max(0, identity - deduction)
        elif "Date" in cat or "date" in issue["issue_id"]:
            dates = max(0, dates - deduction)
        elif "Financial" in cat or "amount" in issue["issue_id"]:
            financial = max(0, financial - deduction)
        else:
            medical = max(0, medical - deduction)
            
    # Cap risk amount at total claim if total_claim exists
    if total_claim > 0:
        amount_at_risk = min(total_claim, round(amount_at_risk, 2))
    else:
        amount_at_risk = 0.0

    # Weighted average
    # Completeness (20%), Identity (20%), Dates (15%), Financial (20%), Medical (25%)
    overall = round(
        completeness * 0.20 +
        identity * 0.20 +
        dates * 0.15 +
        financial * 0.20 +
        medical * 0.25
    )
    
    if overall >= 90:
        risk_level = "Very Low"
    elif overall >= 75:
        risk_level = "Low"
    elif overall >= 60:
        risk_level = "Medium"
    elif overall >= 40:
        risk_level = "High"
    else:
        risk_level = "Very High"
        
    return {
        "overall_score": overall,
        "risk_level": risk_level,
        "breakdown": {
            "document_completeness": {"score": completeness, "weight": 20, "label": "Document Completeness"},
            "identity_consistency": {"score": identity, "weight": 20, "label": "Identity Verification"},
            "date_consistency": {"score": dates, "weight": 15, "label": "Timeline & Date Integrity"},
            "financial_accuracy": {"score": financial, "weight": 20, "label": "Financial & Billing Accuracy"},
            "medical_consistency": {"score": medical, "weight": 25, "label": "Clinical & Medical Logic"}
        },
        "financial_impact": {
            "total_claim_amount": total_claim,
            "amount_at_risk": amount_at_risk
        }
    }
