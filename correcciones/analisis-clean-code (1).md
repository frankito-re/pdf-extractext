# Análisis de Clean Code — `pdf-extractext`

**Fecha:** 2026-11-08
**Alcance:** repositorio `grupo_29/pdf-extractext` (rama `master`, HEAD `1a41f0e`).
**Principios evaluados:** DRY, KISS, YAGNI, SOLID (SRP, OCP, LSP, ISP, DIP).

## Resumen ejecutivo (veredicto)

| Principio | Cumplimiento | Resumen |
|---|---|---|
| **DRY** | ✅ Bueno (con 1 oportunidad) | Duplicación mínima; puntos de conversión centralizados. |
| **KISS** | ✅ Bueno (con 1 matiz) | Soluciones simples; capa de servicio "anémica" en CRUD. |
| **YAGNI** | ✅ Muy bueno | Sin código especulativo; modelos y funciones mínimas. |
| **SRP** | ✅ Bueno | Módulos y funciones con responsabilidad única. |
| **OCP** | ⚠️ Parcial | Abierto para repositorios nuevos; cerrado solo en capa de aplicación. |
| **LSP** | ✅ Cumple | Los `Protocol` se sustituyen por implementaciones y fakes. |
| **ISP** | ⚠️ Parcial | `ChecksumRepository` bien acotado; `DocumentRepository` compartido por todos los endpoints CRUD. |
| **DIP** | ⚠️ Parcial | CRUD invierte dependencia vía `Protocol`; `/extract` depende de la clase **concreta** `MongoChecksumRepository`. |

**Conclusión:** el proyecto demuestra **sólida aplicación de DRY, KISS, YAGNI y SRP/LSP**, con una arquitectura limpia en tres capas y dependencias que mayoritariamente apuntan hacia adentro. Los puntos débiles están en **DIP** (el endpoint principal inyecta la clase concreta en lugar del `Protocol`) y, en menor medida, en **ISP** y **OCP**. Existe además una incoherencia de **naming** (`repository.py` vs `repositories.py`) que lastra la legibilidad.

---

## 1. Metodología

1. Lectura completa del código fuente (`application/`, `presentation/`, `data/`).
2. Lectura de los artefactos de soporte (`pyproject.toml`, `Dockerfile`, `docker-compose.yml`, `CLAUDE.md`/`README.md`).
3. Mapeo de cada principio a evidencia concreta en el código (con referencias `archivo:línea`).
4. Detección de violaciones, incoherencias y oportunidades de mejora.

---

## 2. DRY — Don't Repeat Yourself

### Cumplimientos

- **Serialización centralizada** — `presentation/main.py:61-62` define `_doc_to_response()` y la reutilizan los 4 endpoints de documentos (`list`, `read`, `update`, `delete`). No se repite el dict `{"id", "text", "checksum"}`.
- **Conversión de dominio centralizada** — `data/repository.py:15-16` define `_to_dto()` como único punto de conversión `ExtractedDocument → DocumentDTO`, reutilizado por `get_by_id`, `get_all` y `update`.
- **Regla de unicidad con una sola fuente de verdad** — `application/checksum.py:24` separa `ensure_unique_checksum()` para no duplicar la regla de duplicados entre el chequeo y el guardado.

### Oportunidad de mejora

- **Manejo de "no encontrado" repetido (404)** — en `presentation/main.py:108-109`, `121-122` y `133-134` se repite la lógica "si es `None`/`False` → `HTTPException(404, "Document not found")`" en `read`, `update` y `delete`. No es duplicación grave, pero un helper (`_raise_if_not_found(doc)`) eliminaría la repetición del literal y del código de estado.

**Veredicto DRY: ✅ Cumple**, con una oportunidad menor de consolidación en el manejo de 404.

---

## 3. KISS — Keep It Simple, Stupid

### Cumplimientos

- **Checksum directo** — `application/checksum.py:14-19` usa `hashlib.sha256` de la librería estándar, sin envolturas propias. Solución más simple posible.
- **Extracción PDF directa** — `application/pdf_extractor.py:7-9` delega en `pypdf` con una sola expresión, sin manejar casos no pedidos (encriptado, OCR, metadata).
- **Configuración delegada** — `data/config.py:7-11` usa `pydantic-settings` en lugar de parsear variables de entorno a mano.

### Matiz (KISS/YAGNI fronterizo)

- **Capa de servicio "anémica"** — `application/document_service.py:26-44` define cuatro funciones (`get_document`, `get_all_documents`, `update_document`, `delete_document`) que **solo delegan 1:1** al repositorio, sin lógica propia. Como los endpoints ya dependen del `Protocol` (no de la clase concreta), estas funciones añaden un salto extra sin valor agregado. Es una indirección defendible (capa de aplicación explícita), pero roza la sobre-ingeniería. Contraste: `checksum.py` sí justifica su capa de servicio porque contiene reglas reales (orden de `exists → save`).

**Veredicto KISS: ✅ Cumple**, con un matiz de indirección prescindible en la capa CRUD.

---

## 4. YAGNI — You Aren't Gonna Need It

### Cumplimientos (destacado)

- **Modelo mínimo** — `data/models.py:4-13`: solo `text` y `checksum`. Sin metadata especulativa (nombre de archivo, fecha, tamaño, mime-type).
- **DTO mínimo** — `application/document_service.py:5-9`: solo `id`, `text`, `checksum`.
- **Request de actualización acotado** — `presentation/main.py:20-28`: solo `text`/`checksum`, y un validador que exige al menos uno.
- **Sin manejo de casos no pedidos** — `pdf_extractor.py` no implementa OCR/encriptado hasta que sea requisito.

### Observación

- El **CRUD completo** (`get_all`, `update`, `delete`, `list`) *sí* está justificado: responde a los issues #9/#10/#11 del tracker. No es código especulativo.

**Veredicto YAGNI: ✅ Cumple** — es el principio mejor aplicado del proyecto.

---

## 5. SOLID

### 5.1 SRP — Single Responsibility Principle

| Módulo | Responsabilidad única | Veredicto |
|---|---|---|
| `application/checksum.py` | cálculo de hash, regla de unicidad y guardado en funciones separadas (`calculate_checksum`, `ensure_unique_checksum`, `save_document_if_unique`) | ✅ |
| `application/exceptions.py` | transportar el checksum duplicado (sin saber de HTTP) | ✅ |
| `application/pdf_extractor.py` | solo extraer texto | ✅ |
| `data/config.py` | solo settings | ✅ |
| `data/connection.py` | solo inicializar Beanie | ✅ |
| `presentation/main.py` | *wiring* + endpoints (composition root) | ⚠️ |

**Matiz:** `main.py` concentra muchos roles (modelos de request, `lifespan`, fábricas de repositorios, endpoints). Es inherente a FastAPI, pero crece sin pausa; en la fase de microservicios convendría descomponer.

**Veredicto SRP: ✅ Cumple.**

### 5.2 OCP — Open/Closed Principle

- **Abierto para nuevas implementaciones de repositorio**: las funciones de `document_service.py` y `checksum.py` trabajan contra `Protocol`, por lo que una nueva implementación se agrega **sin modificar** la capa de aplicación.
- **Limitación:** agregar un *endpoint* nuevo requiere editar `main.py`. Es esperable en un composition root, así que no se considera violación real, pero OCP solo se cumple "por capas", no de punta a punta.

**Veredicto OCP: ⚠️ Parcial.**

### 5.3 LSP — Liskov Substitution Principle

- Los `Protocol` (`DocumentRepository`, `ChecksumRepository`) definen contratos que tanto `BeanieDocumentRepository`/`MongoChecksumRepository` como los fakes de tests (`BaseMockRepo`, `TrackingRepo`, `AlwaysExistsRepo`) cumplen sin alterar comportamiento esperado.
- La suite de tests demuestra sustituibilidad: los endpoints reciben fakes y responden igual.

**Veredicto LSP: ✅ Cumple.**

### 5.4 ISP — Interface Segregation Principle

- **Bien aplicado** en `ChecksumRepository` (`application/checksum.py:9-11`): solo `exists`/`save`, de modo que `/extract` no depende del CRUD completo. La decisión está documentada.
- **Matiz** en `DocumentRepository` (`application/document_service.py:16-20`): los cuatro endpoints CRUD comparten **un único** `get_document_repo` que devuelve el protocolo de 4 métodos, aunque cada endpoint usa solo 1 (`get_by_id` **o** `get_all` **o** `update` **o** `delete`). Un ISP más estricto definiría protocolos acotados por endpoint.

**Veredicto ISP: ⚠️ Parcial** (bien en checksum, mejorable en CRUD).

### 5.5 DIP — Dependency Inversion Principle

**Cumplimientos:**

- `presentation → application ← data`: las dependencias apuntan hacia adentro.
- `application/` no importa framework ni capa `data` (solo stdlib + `pypdf`). Es lógica pura.
- Los endpoints CRUD dependen del **Protocol** `DocumentRepository` (`main.py:98, 105, 117, 129`), no de `BeanieDocumentRepository`.

**Violación (hallazgo principal):**

- El endpoint principal **`POST /extract` inyecta la clase concreta**:
  ```python
  # presentation/main.py:79
  repository: MongoChecksumRepository = Depends(get_checksum_repo)
  ```
  Debería ser `ChecksumRepository` (el Protocol ya definido en `checksum.py`), igual que hace el CRUD. Además, `get_checksum_repo()` (`main.py:55-56`) retorna el tipo concreto `MongoChecksumRepository`. Esto rompe la simetría con `get_document_repo()`, que sí retorna el `Protocol`.

  **Consecuencia práctica:** a diferencia del CRUD, `/extract` no puede sustituirse por un fake vía `dependency_overrides` de forma limpia (de hecho, es la razón por la que este endpoint no tiene test).

**Veredicto DIP: ⚠️ Parcial** — invertido en el 80 % del código, roto en el endpoint más importante.

---

## 6. Hallazgo transversal: naming incoherente

En `data/` conviven dos archivos con nombres casi idénticos y significados distintos:

- `data/repository.py` → `BeanieDocumentRepository` (CRUD).
- `data/repositories.py` → `MongoChecksumRepository` (checksum).

El singular/plural no comunica la diferencia real entre ambos repositorios. Esto contraviene el principio de **nombres descriptivos** de Clean Code y facilita errores de import (en `main.py` se importa `MongoChecksumRepository` desde `data.repositories` a nivel de módulo, pero `BeanieDocumentRepository` desde `data.repository` con un import local dentro de `get_document_repo`, `main.py:51` — otra incoherencia).

**Recomendación:** renombrar a `data/checksum_repository.py` y `data/document_repository.py`, y unificar el estilo de imports.

---

## 7. Matriz de cumplimiento

| Principio | Nivel | Nota |
|---|---|---|
| DRY | ✅ 9/10 | 1 oportunidad (404 repetido) |
| KISS | ✅ 8/10 | capa de servicio CRUD anémica |
| YAGNI | ✅ 10/10 | sin especulación |
| SRP | ✅ 9/10 | `main.py` sobrecargado (esperable) |
| OCP | ⚠️ 7/10 | abierto solo para repositorios |
| LSP | ✅ 10/10 | sustitución verificada por tests |
| ISP | ⚠️ 7/10 | `DocumentRepository` compartido |
| DIP | ⚠️ 6/10 | `/extract` depende de clase concreta |

---

## 8. Conclusiones y recomendaciones

**Fortalezas (mantener):** arquitectura de 3 capas limpia, `application/` sin acoplamiento a framework, YAGNI ejemplar (modelos mínimos), DRY en conversiones, y `Protocol` bien usado para SRP/ISP/DIP en la mayor parte del código.

**Recomendaciones priorizadas:**

1. **Corregir DIP en `/extract`**: tipar el parámetro como `ChecksumRepository` y hacer que `get_checksum_repo()` devuelva el `Protocol`. Desbloquea además el test unitario del endpoint (necesario para TDD — ver `analisis-tdd.md`).
2. **Renombrar `data/repositories.py` y `data/repository.py`** para eliminar ambigüedad (`checksum_repository.py`, `document_repository.py`).
3. **Unificar imports** en `main.py` (mover el import de `BeanieDocumentRepository` al nivel de módulo como el resto).
4. **Extraer el manejo de 404** en un helper para cumplir DRY en los tres endpoints.
5. **Evaluar la capa de servicio CRUD**: si no aporta lógica, decidir conscientemente entre (a) conservarla como frontera arquitectónica documentada, o (b) que los endpoints llamen al `Protocol` directamente (más KISS), manteniendo la indirección solo donde hay reglas (`checksum.py`).
6. **Valorar protocolos por endpoint** (ISP estricto) si el número de operaciones sigue creciendo en la etapa de microservicios.
