from typing import Annotated
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from claritydocs.schemas import BreakdownReport
from claritydocs.sanitizer import LocalPrivacySanitizer
from claritydocs.extractor import DocumentIngestionService
from claritydocs.matcher import StatutoryRuleMatcher


class TextAnalysisRequest(BaseModel):
    text: str


app = FastAPI(
    title="ClarityDocs API",
    description="Privacy-preserving document breakdown engine for UK immigration and statutory notices",
    version="0.1.0"
)

# CORS setup for web client
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

sanitizer = LocalPrivacySanitizer()
matcher = StatutoryRuleMatcher()


@app.get("/health")
def health():
    return {"status": "ok", "service": "ClarityDocs", "version": "0.1.0"}


@app.post("/api/v1/analyze-text", response_model=BreakdownReport)
def analyze_text(payload: TextAnalysisRequest | None = None, text: str | None = None):
    raw_input = payload.text if payload else (text or "")
    if not raw_input.strip():
        raise HTTPException(status_code=400, detail="Text cannot be empty.")
    
    clean_text, redactions = sanitizer.sanitize(raw_input)
    report = matcher.analyze_and_match(clean_text, len(redactions))
    return report


@app.post("/api/v1/analyze-pdf", response_model=BreakdownReport)
async def analyze_pdf(file: Annotated[UploadFile, File(description="PDF notice to analyze")]):
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")
    
    content = await file.read()
    raw_text = DocumentIngestionService.extract_from_pdf_bytes(content)
    if not raw_text.strip():
        raise HTTPException(status_code=400, detail="Could not extract text from PDF (it may be a scanned image).")
    
    clean_text, redactions = sanitizer.sanitize(raw_text)
    report = matcher.analyze_and_match(clean_text, len(redactions))
    return report
