from typing import Annotated

from fastapi import FastAPI, UploadFile, File, Depends, HTTPException

from application.document_service import DocumentRepository, get_document, get_all_documents
from application.pdf_extractor import extract_text_from_bytes

app = FastAPI(
    title="PDF Extractext API",
    description="API for PDF text extraction using Clean Architecture",
    version="0.1.0"
)


async def get_document_repo() -> DocumentRepository:
    from data.repository import BeanieDocumentRepository
    return BeanieDocumentRepository()


@app.get("/health")
async def health_check():
    return {"status": "ok", "message": "pong"}


@app.post("/extract")
async def extract_text(file: UploadFile = File(...)):
    pdf_bytes = await file.read()
    text = extract_text_from_bytes(pdf_bytes)
    return {"text": text}


@app.get("/documents")
async def list_documents(repo: Annotated[DocumentRepository, Depends(get_document_repo)]):
    docs = await get_all_documents(repo)
    return [{"id": d.id, "text": d.text, "checksum": d.checksum} for d in docs]


@app.get("/documents/{id}")
async def read_document(id: str, repo: Annotated[DocumentRepository, Depends(get_document_repo)]):
    doc = await get_document(id, repo)
    if doc is None:
        raise HTTPException(status_code=404, detail="Document not found")
    return {"id": doc.id, "text": doc.text, "checksum": doc.checksum}
