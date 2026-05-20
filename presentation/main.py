from fastapi import FastAPI, UploadFile, File
from application.pdf_extractor import extract_text_from_bytes

app = FastAPI(
    title="PDF Extractext API",
    description="API for PDF text extraction using Clean Architecture",
    version="0.1.0"
)

@app.get("/health")
async def health_check():
    """Returns a simple health status to verify the server is running."""
    return {"status": "ok", "message": "pong"}

@app.post("/extract")
async def extract_text(file: UploadFile = File(...)):
    pdf_bytes = await file.read()
    text = extract_text_from_bytes(pdf_bytes)
    return {"text": text}
