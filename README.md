# pdf-extractext

API para extraer texto de archivos PDF y persistirlo en una base de datos NoSQL, con deduplicación por checksum. Proyecto académico de **Desarrollo de Software 2026** — UTN Facultad Regional San Rafael (Ingeniería en Sistemas).

## Qué hace

1. Recibe un PDF vía `multipart/form-data`.
2. Extrae su texto en memoria (nunca se escribe el binario a disco).
3. Calcula un checksum SHA-256 sobre el contenido del PDF.
4. Si el checksum ya existe, rechaza el documento como duplicado (`409`).
5. Si es único, persiste **solo el texto extraído** (nunca el binario) junto con el checksum en MongoDB.
6. Expone una API CRUD completa sobre los documentos persistidos.

## Arquitectura

Clean Architecture en tres capas, con dependencias que solo apuntan hacia adentro (`presentation → application ← data`):

- **`application/`** — lógica de negocio pura, sin imports de framework. Define interfaces `Protocol` (`DocumentRepository` en [application/document_service.py](application/document_service.py), `ChecksumRepository` en [application/checksum.py](application/checksum.py)) que la capa `data` implementa. Incluye la extracción de texto ([application/pdf_extractor.py](application/pdf_extractor.py)) y el cálculo/verificación de checksum ([application/checksum.py](application/checksum.py)).
- **`presentation/main.py`** — la app FastAPI real. Conecta los `Depends` de FastAPI con las clases concretas de repositorio, define los modelos de request/response y arranca la conexión a MongoDB (Beanie) en el `lifespan`.
- **`data/`** — modelos Beanie/ODM y repositorios concretos:
  - `BeanieDocumentRepository` ([data/repository.py](data/repository.py)) implementa `DocumentRepository` para el CRUD completo.
  - `MongoChecksumRepository` ([data/repositories.py](data/repositories.py)) implementa `ChecksumRepository`, usado solo por `/extract` para garantizar unicidad.

> `api/main.py` es un stub mínimo; la app de producción vive en `presentation/main.py`.

## Requisitos

- Python 3.13+
- [uv](https://docs.astral.sh/uv/)
- Docker (para levantar MongoDB localmente)

## Instalación y arranque

```bash
# 1. Instalar dependencias
uv sync

# 2. Levantar MongoDB
docker compose up mongodb -d

# 3. Levantar la API en modo desarrollo (hot reload)
uv run uvicorn presentation.main:app --reload
```

La API queda disponible en `http://localhost:8000`.

Alternativamente, para levantar todo el stack (API + Mongo) con hot reload vía Docker:

```bash
docker compose up --watch
```

## Configuración

Variables de entorno (prefijo `DB_`):

| Variable | Descripción | Default |
|---|---|---|
| `DB_URL` | Connection string de MongoDB | `mongodb://localhost:27017` |
| `DB_NAME` | Nombre de la base de datos | `pdf_extractext` |

## Documentación interactiva

Con la API corriendo, FastAPI genera la documentación automáticamente:

- Swagger UI: [http://localhost:8000/docs](http://localhost:8000/docs) (la ruta raíz `/` redirige acá)
- ReDoc: [http://localhost:8000/redoc](http://localhost:8000/redoc)

## Endpoints

| Método | Path | Descripción |
|---|---|---|
| `GET` | `/health` | Chequeo de salud de la API |
| `POST` | `/extract` | Sube un PDF, extrae su texto y lo persiste si es único |
| `GET` | `/documents` | Lista todos los documentos persistidos |
| `GET` | `/documents/{id}` | Obtiene un documento por id |
| `PATCH` | `/documents/{id}` | Actualiza texto y/o checksum de un documento |
| `DELETE` | `/documents/{id}` | Elimina un documento |

## Reglas de negocio

- **Sin archivos temporales**: el binario del PDF nunca se escribe a disco durante el procesamiento.
- **Sin duplicados**: antes de persistir se calcula el checksum SHA-256 y se rechaza si ya existe.
- **Solo texto**: únicamente el texto extraído se persiste; el binario del PDF nunca se guarda en la base de datos.

## Tests

El proyecto sigue TDD (Red → Green → Refactor).

```bash
# Toda la suite
uv run pytest

# Un archivo puntual
uv run pytest tests/test_api.py

# Un test puntual
uv run pytest tests/test_api.py::test_ping_server
```

> `tests/test_database.py` contiene tests de integración que requieren una instancia de MongoDB corriendo (`docker compose up mongodb -d`).

## Licencia

MIT — ver [LICENSE](LICENSE).
