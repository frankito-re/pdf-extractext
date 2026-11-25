from application.checksum import ChecksumRepository
from application.document_service import DocumentRepository
from data.connection import get_database_connection
from data.models import ExtractedDocument


# Composition root: único punto donde presentation conoce la infraestructura
# (Beanie/Mongo). Los controladores de main.py dependen solo de estos providers.
async def init_database() -> None:
    await get_database_connection([ExtractedDocument])


# El import concreto vive dentro del provider: así la clase de Beanie no se
# arrastra al importar el módulo y queda aislada en el punto de wiring (DIP).
async def get_document_repo() -> DocumentRepository:
    from data.repository import BeanieDocumentRepository
    return BeanieDocumentRepository()


# Igual que get_document_repo: devuelve el puerto ChecksumRepository para que
# /extract no dependa de MongoChecksumRepository.
async def get_checksum_repo() -> ChecksumRepository:
    from data.repositories import MongoChecksumRepository
    return MongoChecksumRepository()
