import os
import uuid
import json
import asyncio
from typing import List, Optional
from fastapi import FastAPI, UploadFile, File, BackgroundTasks, Query
from fastapi.middleware.cors import CORSMiddleware
from sse_starlette.sse import EventSourceResponse

from backend.ocr_engine import extract_text_from_pdf
from backend.document_processor import classify_and_quick_extract, deep_extract_complex_docs
from backend.cross_checker import run_deterministic_checks, run_ai_medical_and_financial_reasoning
from backend.scorer import calculate_readiness_score
from backend.report_generator import generate_audit_report

app = FastAPI(title="ClaimIQ API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory storage for uploaded files and audit results
UPLOAD_DIR = os.path.join(os.path.dirname(__file__), "..", "temp_uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)
SAMPLE_DIR = os.path.join(os.path.dirname(__file__), "..", "sample_data", "output")

audit_results = {}

@app.post("/api/upload")
async def upload_claim_files(files: List[UploadFile] = File(...)):
    """Accept user-uploaded PDFs and return a claim_id."""
    claim_id = str(uuid.uuid4())
    claim_folder = os.path.join(UPLOAD_DIR, claim_id)
    os.makedirs(claim_folder, exist_ok=True)
    
    saved_files = []
    for file in files:
        file_path = os.path.join(claim_folder, file.filename)
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        saved_files.append({"filename": file.filename, "path": file_path})
        
    audit_results[claim_id] = {"files": saved_files, "status": "ready"}
    return {"claim_id": claim_id, "file_count": len(saved_files)}

@app.post("/api/prepare-demo")
async def prepare_demo_packet():
    """Load the 6 generated demo PDFs from sample_data/output/."""
    claim_id = "demo-" + str(uuid.uuid4())[:8]
    
    if not os.path.exists(SAMPLE_DIR):
        return {"error": "Sample data not generated yet."}
        
    saved_files = []
    for fn in sorted(os.listdir(SAMPLE_DIR)):
        if fn.endswith(".pdf"):
            saved_files.append({"filename": fn, "path": os.path.join(SAMPLE_DIR, fn)})
            
    audit_results[claim_id] = {"files": saved_files, "status": "ready"}
    return {"claim_id": claim_id, "file_count": len(saved_files)}

@app.get("/api/stream/{claim_id}")
async def stream_audit_progress(claim_id: str):
    """SSE Endpoint yielding real-time processing stages and final audit report."""
    async def event_generator():
        if claim_id not in audit_results:
            yield {"event": "error", "data": json.dumps({"message": "Invalid claim ID"})}
            return

        files = audit_results[claim_id]["files"]
        
        # Stage 1: OCR Digitization
        yield {"event": "progress", "data": json.dumps({
            "stage": 1, "name": "Document Digitization", "status": "running", 
            "progress": 15, "message": f"Extracting text via OCR from {len(files)} files..."
        })}
        await asyncio.sleep(0.5) # Allow UI transition
        
        docs_data = {}
        for f in files:
            res = extract_text_from_pdf(f["path"])
            docs_data[f["filename"]] = {"filename": f["filename"], "text": res["text"], "markdown": res["markdown"]}
            
        yield {"event": "progress", "data": json.dumps({
            "stage": 1, "name": "Document Digitization", "status": "done", 
            "progress": 25, "message": f"Successfully digitized {len(files)} documents."
        })}
        await asyncio.sleep(0.3)

        # Stage 2: Classification & Quick Extract
        yield {"event": "progress", "data": json.dumps({
            "stage": 2, "name": "AI Document Classification", "status": "running", 
            "progress": 40, "message": "DeepSeek analyzing document types and patient metadata..."
        })}
        await asyncio.sleep(0.2)
        
        classified = classify_and_quick_extract(docs_data)
        
        yield {"event": "progress", "data": json.dumps({
            "stage": 2, "name": "AI Document Classification", "status": "done", 
            "progress": 55, "message": f"Classified {len(classified)} documents."
        })}
        await asyncio.sleep(0.3)

        # Stage 3: Deep Extraction
        yield {"event": "progress", "data": json.dumps({
            "stage": 3, "name": "Clinical Deep Extraction", "status": "running", 
            "progress": 65, "message": "Extracting itemized billing charges and ICD clinical codes..."
        })}
        await asyncio.sleep(0.2)
        
        deep = deep_extract_complex_docs(docs_data, classified)
        
        yield {"event": "progress", "data": json.dumps({
            "stage": 3, "name": "Clinical Deep Extraction", "status": "done", 
            "progress": 75, "message": "Extracted detailed line items and medication schedules."
        })}
        await asyncio.sleep(0.3)

        # Stage 4: Consistency Verification
        yield {"event": "progress", "data": json.dumps({
            "stage": 4, "name": "Consistency & Medical Verification", "status": "running", 
            "progress": 85, "message": "Cross-checking dates, identity rules, and clinical logic..."
        })}
        await asyncio.sleep(0.2)
        
        det_issues = run_deterministic_checks(classified, deep)
        ai_issues = run_ai_medical_and_financial_reasoning(classified, deep)
        all_issues = det_issues + ai_issues
        
        yield {"event": "progress", "data": json.dumps({
            "stage": 4, "name": "Consistency & Medical Verification", "status": "done", 
            "progress": 90, "message": f"Detected {len(all_issues)} potential discrepancies."
        })}
        await asyncio.sleep(0.3)

        # Stage 5: Scoring & Intelligence Report
        yield {"event": "progress", "data": json.dumps({
            "stage": 5, "name": "Claims Intelligence & Scoring", "status": "running", 
            "progress": 95, "message": "Calculating readiness gauge and financial risk exposure..."
        })}
        await asyncio.sleep(0.2)
        
        score_data = calculate_readiness_score(classified, all_issues, deep)
        report_data = generate_audit_report(classified, all_issues, score_data)
        
        final_payload = {
            "claim_id": claim_id,
            "classified_documents": classified,
            "deep_extraction": deep,
            "issues": all_issues,
            "score": score_data,
            "report": report_data
        }
        audit_results[claim_id]["result"] = final_payload
        
        yield {"event": "complete", "data": json.dumps(final_payload)}

    return EventSourceResponse(event_generator())

@app.get("/api/result/{claim_id}")
async def get_audit_result(claim_id: str):
    if claim_id not in audit_results or "result" not in audit_results[claim_id]:
        return {"error": "Result not found"}
    return audit_results[claim_id]["result"]
