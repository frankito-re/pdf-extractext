from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, File, HTTPException, UploadFile

from application.checksum import calculate_checksum, save_document_if_unique
from application.exceptions import DuplicateDocumentError
from application.pdf_extractor import extract_text_from_bytes
from data.connection import get_database_connection
from data.models import ExtractedDocument
from data.repositories import MongoChecksumRepository


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


def get_repository() -> MongoChecksumRepository:
    return MongoChecksumRepository()


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
