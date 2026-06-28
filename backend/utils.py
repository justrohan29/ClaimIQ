import re
from difflib import SequenceMatcher
from datetime import datetime
from openai import OpenAI

import os

env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env")
if os.path.exists(env_path):
    with open(env_path, "r") as f:
        for line in f:
            if "=" in line and not line.strip().startswith("#"):
                k, v = line.strip().split("=", 1)
                os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))

# DeepSeek client
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "")
client = OpenAI(
    api_key=DEEPSEEK_API_KEY,
    base_url="https://api.deepseek.com"
)

FUZZY_THRESHOLD = 0.85

def normalize_value(val):
    """Normalize a value for comparison: strip currency, commas, whitespace."""
    if val is None:
        return ""
    s = str(val).strip()
    s = s.replace("￥", "").replace("¥", "").replace("₹", "").replace("INR", "").replace(",", "").strip()
    
    # Normalize percentage: "25%" -> "0.25"
    pct = re.match(r'^(\d+(?:\.\d+)?)%$', s)
    if pct:
        return str(float(pct.group(1)) / 100)
        
    return s

def try_as_number(val):
    """Try parsing a normalized value as float."""
    try:
        clean = normalize_value(val)
        return float(clean)
    except (ValueError, TypeError):
        return None

def fuzzy_match(s1, s2, threshold=FUZZY_THRESHOLD):
    """Return similarity ratio between two strings."""
    if not s1 or not s2:
        return 0.0
    n1 = str(s1).lower().strip()
    n2 = str(s2).lower().strip()
    if n1 == n2:
        return 1.0
    return SequenceMatcher(None, n1, n2).ratio()

def parse_date(date_str):
    """Try parsing common Indian/international date formats."""
    if not date_str:
        return None
    s = str(date_str).strip().split(',')[0] # Remove time part if comma separated like "12-Jun-2024, 09:30 AM"
    s = re.sub(r'\s+\d{1,2}:\d{2}\s*(?:AM|PM|am|pm)?', '', s).strip()
    
    formats = [
        "%d-%b-%Y", "%d/%m/%Y", "%Y-%m-%d", "%d %b %Y", "%d-%B-%Y", "%d %B %Y"
    ]
    for fmt in formats:
        try:
            return datetime.strptime(s, fmt)
        except ValueError:
            continue
    return None

def compare_values(field_name, val1, val2):
    """Deterministic comparison adapted from comparator.py."""
    result = {
        "field": field_name,
        "val1": str(val1) if val1 else "",
        "val2": str(val2) if val2 else "",
    }
    
    norm1 = normalize_value(val1)
    norm2 = normalize_value(val2)
    
    if not norm1 and not norm2:
        result.update(status="match", confidence=1.0, reason="Both empty")
        return result
        
    if not norm1 or not norm2:
        result.update(status="mismatch", confidence=0.0, reason="One value is missing")
        return result
        
    if norm1 == norm2 or norm1.lower() == norm2.lower():
        result.update(status="match", confidence=1.0, reason="Exact match")
        return result
        
    num1 = try_as_number(norm1)
    num2 = try_as_number(norm2)
    
    if num1 is not None and num2 is not None:
        if abs(num1 - num2) < 1.0: # 1 rupee tolerance
            result.update(status="match", confidence=1.0, reason="Numeric match")
        else:
            diff = abs(num1 - num2)
            result.update(status="mismatch", confidence=0.0, reason=f"Numeric mismatch (diff: ₹{diff:.2f})")
        return result
        
    ratio = fuzzy_match(norm1, norm2)
    if ratio >= FUZZY_THRESHOLD:
        result.update(status="match", confidence=round(ratio, 3), reason=f"Fuzzy match ({ratio:.2f})")
    else:
        result.update(status="mismatch", confidence=round(ratio, 3), reason=f"String mismatch ({ratio:.2f})")
        
    return result
