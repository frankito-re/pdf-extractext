# PDF Extractext

API REST para extracción de texto desde archivos PDF.

## Estructura del proyecto (Arquitectura Multicapa)

```
presentation/     # Capa de Presentación (API endpoints)
application/      # Capa de Aplicación (lógica de negocio)
data/             # Capa de Datos (persistencia MongoDB)
tests/            # Tests (TDD)
```

## Stack

- Python 3.13+
- FastAPI + Uvicorn
- MongoDB + Beanie (ODM)
- uv (gestor de paquetes)
- pytest + httpx (testing)

## Prerrequisitos

- Python 3.13+
- uv instalado
- MongoDB corriendo localmente o en contenedor Docker

## Instalación

```bash
uv sync
```

## Configurar MongoDB

```bash
docker run -d --name pdf-extractext-mongo -p 27017:27017 mongo:7
```

## Variables de entorno

| Variable | Default | Descripción |
|----------|---------|-------------|
| `DB_URL` | `mongodb://localhost:27017` | URL de conexión a MongoDB |
| `DB_NAME` | `pdf_extractext` | Nombre de la base de datos |

## Ejecutar la API

```bash
uv run uvicorn presentation.main:app --reload
```

La API estará disponible en `http://localhost:8000`

## Ejecutar tests

```bash
uv run pytest tests/ -v
```

## Endpoints

| Método | Ruta | Descripción |
|--------|------|-------------|
| GET | `/health` | Health check del servidor |

## Documentación interactiva

Una vez corriendo el servidor, acceder a:

- **Swagger UI:** `http://localhost:8000/docs`
- **ReDoc:** `http://localhost:8000/redoc`
