# Análisis de Arquitectura — `pdf-extractext`

**Fecha:** 2026-11-08
**Alcance:** repositorio `grupo_29/pdf-extractext` (rama `master`, HEAD `1a41f0e`).
**Patrones evaluados:** N-capas, Hexagonal (Puertos y Adaptadores), Onion y Clean Architecture.

## Resumen ejecutivo (veredicto)

| Patrón | ¿Lo usa? | Grado de fidelidad |
|---|---|---|
| **N-capas clásico** | ❌ No (solo "parece" por el nombre de las carpetas) | Bajo |
| **Hexagonal (Ports & Adapters)** | ✅ Sí | Alto |
| **Onion** | ⚠️ Parcial | Medio |
| **Clean Architecture** | ✅ Sí | **Alto (es el más fiel)** |

**Conclusión:** el proyecto implementa una **Clean Architecture de 3 capas** (`presentation → application ← data`), donde la capa de aplicación expone **puertos (`Protocol`)** que la capa de datos implementa como **adaptadores**, un mecanismo que además es la esencia de **Hexagonal**. La regla de dependencia apunta hacia adentro (patrón Onion/Clean), pero **no existe una capa de dominio separada**: las entidades son DTOs anémicos y la lógica de negocio vive en funciones de servicio. Por tanto, es **Clean + Hexagonal**, no una arquitectura N-capas tradicional.

---

## 1. Metodología

1. Lectura de la estructura de directorios y de todo el código fuente (`application/`, `presentation/`, `data/`).
2. Reconstrucción del grafo de dependencias entre capas (imports reales).
3. Comparación de la implementación contra las reglas definitorias de cada patrón.
4. Identificación de fortalezas, desviaciones y oportunidades.

---

## 2. Estructura observada

```
pdf-extractext/
├── presentation/          # interfaz de entrada (FastAPI)
│   └── main.py            # app, endpoints, DTOs de request/response, wiring
├── application/           # lógica de negocio + puertos (Protocol)
│   ├── document_service.py  # DocumentDTO, DocumentRepository (Protocol), casos de uso CRUD
│   ├── checksum.py          # ChecksumRepository (Protocol), regla de unicidad
│   ├── pdf_extractor.py     # caso de uso: extraer texto
│   └── exceptions.py        # errores de dominio
└── data/                  # infraestructura / persistencia
    ├── models.py            # ExtractedDocument (Beanie ODM)
    ├── repository.py        # BeanieDocumentRepository (implementa DocumentRepository)
    ├── repositories.py      # MongoChecksumRepository (implementa ChecksumRepository)
    ├── connection.py        # init Beanie
    └── config.py            # DatabaseSettings
```

### Grafo de dependencias (imports reales)

```
                  ┌──────────────┐
                  │ presentation │   (FastAPI: endpoints + wiring)
                  └──┬────────┬──┘
                     │        │  (wiring / composition root)
            depende  │        └──────────────┐
                     ▼                        ▼
               ┌─────────────┐          ┌──────────┐
               │ application │◄─────────│   data   │   (Beanie/Mongo)
               └─────────────┘  depende │          │
                 (stdlib+pypdf)          └──────────┘
```

- `application` **no importa** ni `presentation` ni `data` → núcleo puro.
- `data` **importa** `application` (usa `DocumentDTO`) → la dependencia de infraestructura se **invierte** hacia adentro.
- `presentation` importa `application` (puertos y casos de uso) y `data` (solo para *wiring*: conexión, modelos Beanie y repos concreto de checksum).

Este grafo es el sello distintivo de **Clean Architecture / Hexagonal**, no de N-capas.

---

## 3. Evaluación contra cada patrón

### 3.1 N-capas (tradicional)

**Regla definitoria:** capas apiladas con dependencias estrictas hacia abajo (`UI → BLL → DAL`), donde cada capa solo conoce a la inmediatamente inferior.

| Criterio N-capas | Observación | Cumple |
|---|---|---|
| Capas apiladas (presentación → negocio → datos) | Existen 3 capas con nombres similares | ⚠️ apariencia |
| Dependencia hacia abajo (`presentation → data`) | Aquí es `presentation → application ← data`; la capa de datos **apunta hacia arriba** a `application` | ❌ |
| `application` sin dependencia de framework | Sí, pero en N-capas la capa de negocio normalmente conoce la de datos | ❌ |

**Veredicto:** **no es N-capas clásico.** La inversión de dependencia en la capa de datos lo aleja del modelo tradicional. Solo los nombres de carpeta (`presentation`/`application`/`data`) dan una falsa impresión de N-capas.

### 3.2 Hexagonal (Puertos y Adaptadores)

**Regla definitoria:** un núcleo de negocio aislado que se comunica con el exterior mediante **puertos** (interfaces) y **adaptadores** (implementaciones). Distingue *driving* (entrada) y *driven* (salida).

| Concepto Hexagonal | Implementación en el proyecto | Cumple |
|---|---|---|
| **Núcleo** | `application/` (sin framework) | ✅ |
| **Puerto driven** (salida → persistencia) | `DocumentRepository` y `ChecksumRepository` (`Protocol`) | ✅ |
| **Adaptador driven** | `BeanieDocumentRepository`, `MongoChecksumRepository` | ✅ |
| **Puerto driving** (entrada) | los endpoints FastAPI | ✅ (implícito) |
| **Adaptador driving** | `presentation/main.py` (FastAPI) | ✅ |
| **Inyección de puerto** | funciones reciben el `Protocol` por parámetro | ✅ |

**Veredicto:** **alto grado de fidelidad hexagonal.** Los `Protocol` de `application` son literalmente *puertos*, y las clases de `data` son *adaptadores driven*. El hecho de que las funciones reciban el repositorio por parámetro (inversión de control) es la forma canónica del patrón.

### 3.3 Onion (Cebolla)

**Regla definitoria:** capas concéntricas con dependencias solo hacia el centro. El centro es el **modelo de dominio** (entidades + servicios de dominio); alrededor, servicios de aplicación; afuera, infraestructura y UI. Las interfaces de repositorio viven en el dominio.

| Concepto Onion | Implementación | Cumple |
|---|---|---|
| Dependencias hacia adentro | `presentation → application ← data` | ✅ |
| Interfaces de repositorio en el núcleo | `Protocol` definidos en `application` | ✅ |
| **Capa de dominio separada** (entidades con comportamiento) | No existe: `DocumentDTO` es un *dataclass* sin comportamiento | ❌ |
| Servicios de dominio vs. servicios de aplicación | Fusionados en `document_service.py` / `checksum.py` | ⚠️ |
| Infraestructura en el borde | `data/` | ✅ |

**Veredicto:** **parcial.** Cumple la regla de dependencia (el rasgo más importante de Onion), pero **colapsa** las capas de *dominio* y *servicios de aplicación* en una sola (`application/`), con entidades anémicas. Sería Onion "adelgazada".

### 3.4 Clean Architecture (Uncle Bob)

**Regla definitoria:** círculos concéntricos — Entidades → Casos de Uso → Adaptadores de Interfaz → Frameworks/Drivers — con la **regla de dependencia** (solo hacia adentro).

| Capa Clean | Implementación en el proyecto | Cumple |
|---|---|---|
| **Entities** (reglas de negocio) | `DocumentDTO`, `DuplicateDocumentError` (anémicos, sin comportamiento) | ⚠️ |
| **Use Cases** | `document_service.py` (CRUD), `checksum.py` (unicidad), `pdf_extractor.py` | ✅ |
| **Interface Adapters** | `presentation/` (controladores) + repos de `data/` (gateway) | ✅ |
| **Frameworks & Drivers** | FastAPI, Beanie/Mongo, pypdf | ✅ |
| **Regla de dependencia** (hacia adentro) | respetada (`presentation → application ← data`) | ✅ |

**Veredicto:** **es el patrón más fiel.** La estructura y la regla de dependencia coinciden 1:1 con Clean Architecture, con la salvedad de que las *entidades* carecen de lógica (todo vive en casos de uso). Es un mapeo directo de los círculos de Uncle Bob a tres carpetas.

---

## 4. Mapeo de conceptos del proyecto a los patrones

| Elemento del código | N-capas | Hexagonal | Onion | Clean |
|---|---|---|---|---|
| `application/checksum.py` (`Protocol`) | — | Puerto driven | Interfaz de repositorio | Gateway (puerto) |
| `data/repository.py`, `data/repositories.py` | DAL | Adaptador driven | Infraestructura | Interface Adapter (driven) |
| `application/document_service.py` | BLL | Caso de uso en el núcleo | Servicio de aplicación | Use Case |
| `application/exceptions.py` | — | Núcleo | Dominio | Entity/Use Case |
| `presentation/main.py` | UI | Adaptador driving | Borde | Interface Adapter (driving) + wiring |
| `data/models.py` (`ExtractedDocument`) | Entidad de datos | Adaptador | Infraestructura | Framework (Beanie ODM) |

---

## 5. Fortalezas

1. **Núcleo 100 % desacoplado de framework**: `application/` solo importa stdlib y `pypdf`. Se puede testear sin FastAPI, Beanie ni MongoDB (de hecho, los tests de API usan fakes).
2. **Regla de dependencia respetada**: `data` depende de `application` y no al revés; la inversión es correcta.
3. **Puertos explícitos y angostos**: `ChecksumRepository` (`exists`/`save`) separado de `DocumentRepository` (CRUD completo) — un ejemplo limpio de Hexagonal/ISP.
4. **Sustituibilidad demostrada**: los `Protocol` se reemplazan por fakes en tests sin tocar la lógica, lo que prueba que la arquitectura funciona como abstracción.
5. **Composition root único**: el *wiring* (fábricas de repositorios, `lifespan`) se concentra en `main.py`, el único punto permitido para tocar infraestructura.

---

## 6. Desviaciones / brechas

1. **No hay capa de dominio separada (anemia de entidades).** `DocumentDTO` es un simple `dataclass` sin comportamiento; toda la lógica vive en funciones de servicio. Para Onion/Clean "puros" faltaría una capa de *entidades* con invariantes (p. ej. que un documento siempre tenga checksum válido).
2. **El endpoint `/extract` rompe la inversión de dependencia.** Inyecta la clase concreta `MongoChecksumRepository` en lugar del puerto `ChecksumRepository` (`presentation/main.py:79`). Es la única fuga de infraestructura al adaptador *driving* (detallado en `analisis-clean-code.md`).
3. **Modelo ODM confundido con entidad de dominio.** `ExtractedDocument` (Beanie) vive en `data/models.py`, es infraestructura. La entidad de negocio equivalente (`DocumentDTO`) está en `application`. Es correcto que estén separadas, pero conviene explicitar que **solo** `DocumentDTO` es dominio.
4. **Capa de servicio CRUD "de paso".** Las funciones de `document_service.py` delegan 1:1 al repositorio sin lógica; el único caso de uso con reglas reales es el de checksum. La separación de "casos de uso" está, pero es fina.
5. **El `wiring` importa infraestructura directamente.** `main.py` importa `get_database_connection`, `ExtractedDocument` y `MongoChecksumRepository` (necesario, pero un `bootstrap.py`/`container.py` explícito separaría mejor el *composition root* de los controladores).
6. **Sin enforcement automatizado.** No hay linter de capas (p. ej. `import-linter`, `pydeps`, `dependency-cruiser`) que impida futuras fugas de dependencia. Hoy se cumple por disciplina, no por herramienta.

---

## 7. Matriz comparativa de fidelidad

| Patrón | Fidelidad | Resumen |
|---|---|---|
| N-capas | 🔴 Baja | Solo coincide en nombres; la inversión de dependencia lo descarta |
| Hexagonal | 🟢 Alta | Puertos (`Protocol`) + adaptadores (`data`) + núcleo aislado |
| Onion | 🟡 Media | Regla hacia adentro correcta, pero sin capa de dominio propia |
| Clean | 🟢 Alta | Mapeo directo de los círculos de Uncle Bob a 3 capas |

---

## 8. Conclusiones

El sistema usa una **arquitectura limpia de 3 capas que combina Clean Architecture y Hexagonal**:

- **Clean** por la regla de dependencia y la separación Entidades/Casos de Uso/Adaptadores/Frameworks.
- **Hexagonal** por el mecanismo explícito de *puertos* (`Protocol`) y *adaptadores* (repositorios Beanie) con inyección por constructor.
- **No es N-capas** tradicional, pese a la nomenclatura de carpetas.

La **fuga puntual de DIP en `/extract`** ya fue corregida (commit `d86df1b`): el endpoint y su provider dependen del puerto `ChecksumRepository`, no de la clase concreta. La única debilidad estructural relevante que queda es la **ausencia de una capa de dominio con entidades ricas** (el dominio es anémico), corregible sin rediseñar cuando la complejidad lo justifique.

---

## 9. Recomendaciones

| # | Recomendación | Estado |
|---|---|---|
| 1 | **Corregir la fuga de DIP en `/extract`**: tipar como `ChecksumRepository` (el puerto ya existe) para que el adaptador *driving* no conozca la infraestructura. | ✅ Hecho (`d86df1b`) |
| 2 | **Explicitar un `bootstrap`/`container`** para el *wiring* de `main.py` y dejar los controladores libres de imports de `data` (más fiel a Hexagonal/Clean). | ⏳ En curso (B1) |
| 3 | **Evaluar enriquecer el dominio**: mover invariantes (p. ej. checksum no vacío, longitud) a entidades de dominio en `application/` si la complejidad crece en la etapa de microservicios. | ⏸️ Diferido (YAGNI) |
