from typing import Annotated, Optional
from contextlib import asynccontextmanager

from fastapi import FastAPI, UploadFile, File, Depends, HTTPException
from fastapi.responses import RedirectResponse
from pydantic import BaseModel, model_validator

from application.document_service import DocumentRepository, get_document, get_all_documents, update_document, delete_document
from application.checksum import calculate_checksum, save_document_if_unique
from application.exceptions import DuplicateDocumentError

from application.pdf_extractor import extract_text_from_bytes
from data.connection import get_database_connection
from data.models import ExtractedDocument
from data.repositories import MongoChecksumRepository


class UpdateDocumentRequest(BaseModel):
    text: Optional[str] = None
    checksum: Optional[str] = None

    @model_validator(mode="after")
    def at_least_one_field(self) -> "UpdateDocumentRequest":
        if self.text is None and self.checksum is None:
            raise ValueError("At least one of 'text' or 'checksum' must be provided")
        return self


@asynccontextmanager
async def lifespan(app: FastAPI):
    await get_database_connection([ExtractedDocument])
    yield


app = FastAPI(
    title="PDF Extractext API",
    description="API for PDF text extraction using Clean Architecture",
    version="0.1.0",
    lifespan=lifespan,
)


async def get_document_repo() -> DocumentRepository:
    from data.repository import BeanieDocumentRepository
    return BeanieDocumentRepository()


def get_repository() -> MongoChecksumRepository:
    return MongoChecksumRepository()

@app.get("/")
async def root():
    return RedirectResponse(url="/docs")

@app.get("/health")
async def health_check():
    return {"status": "ok", "message": "pong"}


@app.post("/extract")
async def extract_text(
    file: UploadFile = File(...),
    repository: MongoChecksumRepository = Depends(get_repository),
):
    pdf_bytes = await file.read()
    checksum = calculate_checksum(pdf_bytes)
    try:
        text = extract_text_from_bytes(pdf_bytes)
        await save_document_if_unique(text, checksum, repository)
    except DuplicateDocumentError:
        raise HTTPException(status_code=409, detail=f"Duplicate document: {checksum}")
    return {"text": text, "checksum": checksum}


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


@app.patch("/documents/{id}")
async def update_document_endpoint(
    id: str,
    body: UpdateDocumentRequest,
    repo: Annotated[DocumentRepository, Depends(get_document_repo)],
):
    doc = await update_document(id, body.text, body.checksum, repo)
    if doc is None:
        raise HTTPException(status_code=404, detail="Document not found")
    return {"id": doc.id, "text": doc.text, "checksum": doc.checksum}


@app.delete("/documents/{id}", status_code=204)
async def delete_document_endpoint(
    id: str,
    repo: Annotated[DocumentRepository, Depends(get_document_repo)],
):
    deleted = await delete_document(id, repo)
    if not deleted:
        raise HTTPException(status_code=404, detail="Document not found")
    return None
