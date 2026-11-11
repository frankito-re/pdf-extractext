# Análisis de cumplimiento de TDD — `pdf-extractext`

**Fecha:** 2026-11-08
**Alcance:** repositorio `grupo_29/pdf-extractext` (rama `master`, HEAD `1a41f0e`).
**Autor:** análisis automatizado de ingeniería de software.

## Resumen ejecutivo (veredicto)

| Dimensión | Resultado |
|---|---|
| ¿El proyecto **declara** TDD como metodología? | ✅ Sí (CLAUDE.md y README) |
| ¿Existen tests automatizados? | ✅ Sí (16 tests, 15 en suite sin BD) |
| ¿Los tests pasan? | ✅ Sí (15 passed / 16 collected) |
| ¿Hay evidencia de **test-first** (Red → Green → Refactor) en el historial? | ❌ No verificable; la evidencia apunta a test y código juntos |
| **¿Cumple TDD?** | ⚠️ **Parcial / No demostrable** |

**Conclusión:** el proyecto **aplica buenas prácticas de testing** y tiene una suite que cubre la lógica de negocio pura, pero **no hay evidencia en el historial de Git de que se haya seguido el ciclo estricto de TDD** (escribir primero un test que falla y luego el código mínimo para pasarlo). Los commits muestran test y producción agregados en el **mismo commit**, y el endpoint principal (`POST /extract`) **no tiene ningún test**.

---

## 1. Criterios evaluados

TDD se define por tres reglas de ciclo y dos precondiciones verificables:

1. **Red** — se escribe primero un test que describe el comportamiento deseado y que **falla** porque la funcionalidad no existe.
2. **Green** — se escribe el **mínimo** código para que ese test pase.
3. **Refactor** — se limpia el código manteniendo los tests en verde.

Verificable en un repositorio a partir de:

- **Orden temporal**: commits de test que preceden a commits de implementación.
- **Cobertura**: todo comportamiento público tiene al menos un test que lo especifica.
- **Tooling**: infraestructura que hace reproducible el ciclo (config de pytest, medición de cobertura).

---

## 2. Metodología del análisis

1. Lectura de la estructura de carpetas y del código fuente (`application/`, `presentation/`, `data/`).
2. Lectura completa de la suite de tests (`tests/`).
3. Inspección del historial de Git (`git log --all --name-only`) para reconstruir el **orden** en que se introdujeron tests y código.
4. Ejecución real de la suite con `uv run pytest`.
5. Verificación de configuración de tooling (`pyproject.toml`, ausencia de `pytest.ini`/`conftest.py`/`[tool.pytest]`).

---

## 3. Evidencia: historial de commits (orden test vs. código)

La tabla reconstruye, para cada funcionalidad, qué archivos se agregaron en **el mismo commit**.

| Commit | Funcionalidad | Código agregado | Tests agregados | ¿Test antes del código? |
|---|---|---|---|---|
| `52e848b` | Arquitectura multicapa | `presentation/main.py` | `tests/test_api.py` | ❌ mismo commit |
| `781c141` | Conexión a BD | `data/config.py`, `data/connection.py` | `tests/test_database.py` | ❌ mismo commit |
| `8385715` | Calcular checksum | `application/checksum.py` | `tests/test_checksum.py` | ❌ mismo commit |
| `f08e556` | Unicidad por checksum | `application/checksum.py`, `exceptions.py`, `data/models.py` | `tests/test_checksum.py` | ❌ mismo commit |
| `c0710fc` | Guardar doc + checksum | `application/checksum.py`, `data/connection.py`, `data/repositories.py` | `tests/test_api.py`, `tests/test_checksum.py` | ❌ mismo commit |
| `1f4286d` | Leer documentos | `application/document_service.py`, `data/repository.py`, `presentation/main.py` | `tests/test_api.py` | ❌ mismo commit |
| `f9a5aef` | Actualizar documentos | `application/document_service.py`, `data/repository.py`, `presentation/main.py` | `tests/test_api.py` | ❌ mismo commit |
| `9fafff7` | Borrar documentos | `application/document_service.py`, `data/repository.py`, `presentation/main.py` | `tests/test_api.py` | ❌ mismo commit |
| `62d906a` | Extractor de texto PDF | `application/pdf_extractor.py`, `presentation/main.py` | `tests/test_pdf_extractor.py` | ❌ mismo commit |

**Hallazgo clave:** en los 9 commits de funcionalidad, los tests y el código de producción se introducen **siempre juntos**. No existe ningún commit que agregue únicamente un test (fase *Red*), ni un commit posterior que agregue la implementación (fase *Green*). Los mensajes de tipo `auto-commit` y la aparición pareada de archivos sugieren un flujo en el que se escribe código y test en una sola pasada, no un ciclo Red → Green → Refactor iterativo.

> Nota de honestidad metodológica: un mismo commit no permite *descartar* que internamente se haya escrito el test antes. Pero TDD deja una huella típica (test que falla primero, commiteado antes de la implementación) que **no aparece** en este repositorio. Por tanto, el cumplimiento del ciclo estricto **no es demostrable** y la evidencia disponible lo contradice.

---

## 4. Cobertura de tests por módulo

| Módulo / comportamiento | Test existente | Estado |
|---|---|---|
| `application/checksum.py` — `calculate_checksum` | `test_checksum_of_known_content_returns_expected_hash` | ✅ |
| `application/checksum.py` — `ensure_unique_checksum` (duplicado) | `test_ensure_unique_checksum_raises_on_duplicate` | ✅ |
| `application/checksum.py` — `ensure_unique_checksum` (único) | `test_ensure_unique_checksum_passes_when_unique` | ✅ |
| `application/checksum.py` — `save_document_if_unique` | `test_document_is_inserted_after_successful_uniqueness_check` | ✅ |
| `application/pdf_extractor.py` — `extract_text_from_bytes` | `test_extract_text_returns_expected_content` | ✅ |
| `application/pdf_extractor.py` — sin escritura a disco | `test_extract_text_never_writes_to_disk` | ✅ |
| `presentation/main.py` — `GET /health` | `test_ping_server` | ✅ |
| `presentation/main.py` — `GET /documents/{id}` 200/404 | `test_read_document_by_id_*` | ✅ |
| `presentation/main.py` — `GET /documents` | `test_list_all_documents_returns_200` | ✅ |
| `presentation/main.py` — `PATCH /documents/{id}` 200/404 | `test_update_document_*` | ✅ |
| `presentation/main.py` — `DELETE /documents/{id}` 204/404 | `test_delete_document_*`, `test_get_deleted_document_returns_404` | ✅ |
| `presentation/main.py` — `POST /extract` (endpoint **principal**) | — | ❌ **sin test** |
| `presentation/main.py` — `UpdateDocumentRequest` (validador `at_least_one_field`) | — | ❌ sin test |
| `presentation/main.py` — `GET /` (redirect a `/docs`) | — | ❌ sin test |
| `application/document_service.py` — `get_document`, `get_all_documents`, `update_document`, `delete_document` | — (solo indirecto vía API) | ⚠️ sin test unitario directo |
| `data/repository.py` — `BeanieDocumentRepository` | — | ❌ sin test directo |
| `data/repositories.py` — `MongoChecksumRepository` | — | ❌ sin test directo |
| Persistencia real del modelo `ExtractedDocument` | `test_write_and_read_from_database` | ⚠️ débil (ver §5) |

---

## 5. Hallazgos críticos (brechas)

1. **El endpoint principal no está testeado.** `POST /extract` es el corazón del producto (extraer texto + calcular checksum + deduplicar + persistir) y **no existe ningún test de API** que lo ejercite. Bajo un criterio estricto de TDD ("si no hay test, la funcionalidad no existe", según el propio CLAUDE.md), esta funcionalidad no estaría cubierta.

2. **Sin evidencia de fase *Red* en Git.** Ningún commit de test precedió a su implementación (ver §3). El requisito del CLAUDE.md —"Never add implementation code without a test written first"— no es verificable y los datos lo contradicen.

3. **Test de integración de BD que no testea el código real.** `tests/test_database.py` define una clase `SampleDoc` *ad hoc* y verifica que Beanie funciona, pero **no** ejercita `ExtractedDocument`, `BeanieDocumentRepository` ni `MongoChecksumRepository`. Es un test que valida la librería, no la persistencia del proyecto.

4. **Repositorios concretos sin test directo.** `BeanieDocumentRepository` (CRUD) y `MongoChecksumRepository` (`exists`/`save`) no tienen tests unitarios; su corrección solo se infiere indirectamente.

5. **Validación de request sin test.** El `@model_validator` que exige al menos un campo en `PATCH` (`at_least_one_field`) no está cubierto.

6. **Sin medición de cobertura.** No hay `pytest-cov` ni configuración `[tool.pytest]`; no es posible cuantificar cobertura ni fijar un umbral (lo que TDD+CI suele exigir).

7. **Sin config de pytest.** No existe `pytest.ini`, `conftest.py` ni sección `[tool.pytest]`; la configuración de `asyncio` depende de marcadores implícitos y del entorno por defecto.

---

## 6. Fortalezas (buenas prácticas de testing presentes)

Aunque no se demuestre TDD estricto, la suite tiene cualidades reales y alineadas a los objetivos de TDD:

- **Nombres descriptivos y expresivos** de tests (comportamiento, no implementación): `test_read_document_by_id_returns_404_when_not_found`.
- **Aislamiento sin dependencias reales**: los tests de API usan `httpx.ASGITransport` + `app.dependency_overrides`, y parchean `get_database_connection`; no requieren MongoDB.
- **Diseño orientado a testabilidad**: el uso de `Protocol` (DIP/ISP) permite *fakes* intercambiables, exactamente lo que TDD premia.
- **Datos determinísticos**: el test de checksum usa un hash SHA-256 esperado fijo, y el de PDF genera el binario en memoria (sin fixtures de disco).
- **Limpieza de estado**: `app.dependency_overrides.clear()` tras cada test evita acoplamiento entre tests.
- **Suite en verde**: 15 tests pasan sin base de datos; el 16.º (integración) requiere MongoDB.

---

## 7. Conclusiones

| Criterio TDD | Cumple | Evidencia |
|---|---|---|
| Tests automatizados presentes | ✅ | 16 tests en `tests/` |
| Tests en verde | ✅ | `15 passed` (suite sin BD) |
| Red → Green → Refactor (orden test-first) | ❌ | commits pareados código+test, sin fase *Red* |
| Cobertura de toda la funcionalidad pública | ❌ | `POST /extract`, validación PATCH, redirect, repositorios sin test |
| Tooling de soporte (cobertura, config) | ❌ | sin `pytest-cov`, sin `[tool.pytest]` |

**Veredicto final: cumple TDD de forma parcial.** El proyecto tiene una cultura de testing sólida y tests de calidad para la lógica pura, pero no satisface los dos requisitos definitorios del TDD estricto: (a) **test escrito antes que el código** (no demostrable y contradicho por el historial) y (b) **cobertura total del comportamiento** (el endpoint principal y varios artefactos carecen de test).

---

## 8. Recomendaciones

1. **Añadir tests para `POST /extract`** (prioridad máxima): éxito con PDF válido único, rechazo `409` ante checksum duplicado, y `400`/error ante archivo no PDF.
2. **Registrar el ciclo en Git**: committear el test que falla *antes* del código que lo hace pasar, para dejar evidencia verificable del *Red → Green*.
3. **Reemplazar el test de BD** para que ejercite `ExtractedDocument` + `BeanieDocumentRepository` + `MongoChecksumRepository` reales (test de integración auténtico).
4. **Cubrir validaciones**: `UpdateDocumentRequest.at_least_one_field` y el redirect `/` → `/docs`.
5. **Agregar medición de cobertura** (`pytest-cov`) y un umbral mínimo en CI, y añadir `[tool.pytest]` para configurar `asyncio_mode`.
6. **Unit-testear** `application/document_service.py` y los repositorios concretos de forma aislada.
