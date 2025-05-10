# backend/main.py
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
from typing import Optional
import uuid
import json
from your_agents_module import AAOIFIStandardsSystem, StandardDocument

app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize the system
system = AAOIFIStandardsSystem()

class AnalysisRequest(BaseModel):
    text: str
    standard_name: Optional[str] = None

class FeedbackRequest(BaseModel):
    feedback: str
    standard_name: str
    enhancement_result: dict

@app.post("/api/analyze-standard")
async def analyze_standard(file: UploadFile = File(...)):
    try:
        # Save uploaded file temporarily
        file_path = f"temp_{uuid.uuid4()}.pdf"
        with open(file_path, "wb") as buffer:
            buffer.write(file.file.read())
        
        # Process the PDF
        text = extract_text_from_pdf(file_path)  # Use your existing function
        standard = StandardDocument(name=file.filename, content=text)
        
        # Run through the system
        results = system.process_standard(standard)
        
        # Clean up
        os.remove(file_path)
        
        return results
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/analyze-text")
async def analyze_text(request: AnalysisRequest):
    try:
        standard = StandardDocument(
            name=request.standard_name or "Unnamed Standard",
            content=request.text
        )
        results = system.process_standard(standard)
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/submit-feedback")
async def submit_feedback(request: FeedbackRequest):
    try:
        feedback_result = system.incorporate_feedback(
            request.feedback,
            request.enhancement_result
        )
        return feedback_result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))