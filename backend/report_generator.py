import json
from backend.utils import client
from backend.document_processor import clean_json_response

def generate_audit_report(classified_data: dict, issues: list, score_data: dict) -> dict:
    """
    Call 5: Generate Claims Intelligence Summary, prioritized fix recommendations, and dynamic chronological timeline.
    """
    prompt = f"""You are an expert Chief Claims Auditor at a major insurance company. Below are the findings and document summaries of an automated audit on a healthcare claim package.

DOCUMENT CLASSIFICATIONS & EXTRACTED DATES:
{json.dumps(classified_data, indent=2)}

SCORE & FINANCIAL IMPACT:
{json.dumps(score_data, indent=2)}

DETECTED DISCREPANCIES & ISSUES:
{json.dumps(issues, indent=2)}

Generate a professional, executive-level audit briefing and construct a chronological timeline of clinical events observed across the submitted documents.
Return ONLY valid JSON matching this structure:
{{
  "claims_intelligence_summary": "A cohesive 3-4 sentence conversational paragraph written in an authoritative auditor voice explaining the claim situation, the primary reason for the risk level, and the financial exposure.",
  "prioritized_fixes": [
    {{
      "priority": 1,
      "action": "Clear, actionable step to fix the top critical issue",
      "expected_score_gain": "+15 points"
    }}
  ],
  "chronological_timeline": [
    {{
      "date": "Extracted date (e.g. 11-Jun-2024 or YYYY-MM-DD)",
      "label": "Description of clinical event (e.g. Hospital Admission, Lab Sample Collected)",
      "doc": "Source Document Name",
      "flag": "Warning string if anomalous chronological timing or discrepancy exists, else null"
    }}
  ]
}}"""

    print("  [Call 5] Calling DeepSeek for Executive Claims Intelligence Summary & Timeline...")
    try:
        response = client.chat.completions.create(
            model="deepseek-chat",
            temperature=0.2,
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": "You are a healthcare claim executive auditor. Output exact JSON."},
                {"role": "user", "content": prompt}
            ]
        )
        raw = clean_json_response(response.choices[0].message.content)
        parsed = json.loads(raw)
        return {
            "summary": parsed.get("claims_intelligence_summary", "Audit completed. Discrepancies found requiring attention before submission."),
            "fixes": parsed.get("prioritized_fixes", []),
            "timeline": parsed.get("chronological_timeline", [])
        }
    except Exception as e:
        print(f"  WARNING: Call 5 failed ({e}). Returning unstyled fallback.")
        fixes = []
        for idx, issue in enumerate(issues[:4]):
            fixes.append({
                "priority": idx + 1,
                "action": issue.get("fix_recommendation", "Resolve discrepancy"),
                "expected_score_gain": "+10 points"
            })
        
        # Build fallback timeline from classified docs
        timeline = []
        for doc_id, cinfo in classified_data.items():
            if cinfo.get("admission_date"):
                timeline.append({"date": cinfo["admission_date"], "label": "Admission noted", "doc": cinfo.get("doc_type", "Document"), "flag": None})
                
        return {
            "summary": f"Automated audit identified {len(issues)} potential discrepancies across the submitted claim packet. Overall readiness score is {score_data['overall_score']}/100 ({score_data['risk_level']} Risk).",
            "fixes": fixes,
            "timeline": timeline
        }
