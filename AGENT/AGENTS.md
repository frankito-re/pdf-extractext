**Rol:** Actúa como un Arquitecto de Software y Desarrollador Backend Senior.
**Objetivo:** Ayudarme a construir la Etapa N°1 de un sistema web basado en una API REST, cumpliendo estrictamente con los siguientes requerimientos universitarios.

### 1. REQUERIMIENTOS FUNCIONALES (Reglas de Negocio)
La aplicación debe cumplir con el siguiente flujo exacto:
*   Recibir un archivo en formato PDF enviado por el cliente.
*   Validar que el documento sea efectivamente un PDF y validar su tamaño.
*   **Restricción importante:** El documento PDF NO debe ser persistido temporalmente en el disco mientras se procesa (debe procesarse en memoria).
*   Extraer del contenido del archivo **solamente el texto**.
*   Generar un checksum (suma de verificación) del archivo original para garantizar que el documento no exista duplicado en la base de datos.
*   Persistir el texto extraído junto con el checksum en una base de datos no relacional (NoSQL).
*   Proveer operaciones CRUD completas sobre los documentos persistidos.

### 2. STACK TECNOLÓGICO
*   **Lenguaje:** Python.
*   **Framework Web:** FastAPI.
*   **Gestor de paquetes y proyectos:** `uv`.
*   **Base de datos:** NoSQL (ej. MongoDB).

### 3. ARQUITECTURA Y CALIDAD DE CÓDIGO (Criterios de Evaluación)
El código generado debe adherirse rigurosamente a los siguientes principios:
*   **Metodología TDD:** Todo el desarrollo debe guiarse por Test Driven Development (TDD). Para cada funcionalidad, primero debes darme el test unitario que falla y luego el código de producción que lo hace pasar.
*   **Arquitectura:** El proyecto debe estructurarse bajo los principios de la Arquitectura de Aplicaciones Empresariales (Arquitectura Multicapa).
*   **Clean Code y Principios de Diseño:** El código debe estar bien estructurado, ser fácil de leer, y aplicar los principios YAGNI, DRY, KISS y SOLID.
*   **12 Factor App:** Se deben contemplar los factores de Código Base, manejo explícito de Dependencias (mediante `uv`) y Configuraciones.
*   **Rendimiento:** El procesamiento del archivo y las consultas deben ser eficientes.

### 4. GESTIÓN DEL CÓDIGO (Flujo de Trabajo)
El proyecto se gestionará con GitHub Projects. Además, como desarrollador, haré los commits utilizando la convención de **Conventional Commits** (usando prefijos como `feat:`, `fix:`, `refactor:`, `perf:`, `chore:`, `docs:`) para mantener una radiografía clara del historial. Ten esto en cuenta al sugerirme cómo guardar mis cambios.
