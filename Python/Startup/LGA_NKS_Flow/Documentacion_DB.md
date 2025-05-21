# Documentación de la Base de Datos SQLite de PipeSync

## Introducción

PipeSync utiliza una base de datos SQLite para almacenar información sobre proyectos, shots, tareas y versiones. Esta base de datos permite mantener un registro local de los datos sincronizados con ShotGrid/Flow y Wasabi S3, facilitando operaciones offline y mejorando el rendimiento de la aplicación.

## Ubicación de la Base de Datos

La base de datos se encuentra en la siguiente ubicación:

```
[carpeta_ejecutable]/cache/pipesync.db
```

Siguiendo el principio de portabilidad de la aplicación, la carpeta `cache` se encuentra junto al ejecutable, permitiendo que la aplicación sea completamente portable.

## Estructura de la Base de Datos

La base de datos consta de las siguientes tablas:

1. **projects**: Almacena información de proyectos
2. **shots**: Almacena información de tomas (shots) asociadas a proyectos
3. **tasks**: Almacena tareas asociadas a shots
4. **task_assignments**: Almacena asignaciones de tareas a usuarios
5. **versions**: Almacena versiones de archivos asociadas a tareas
6. **version_notes**: Almacena notas asociadas a cada versión
7. **sync_status**: Almacena información sobre el estado de sincronización
8. **task_timelogs**: Almacena los registros de tiempo trabajado en cada tarea
9. **app_settings**: Almacena la configuración global de la aplicación
10. **wasabi_auto_download_shots**: Almacena los shots seleccionados por los usuarios Downloader para la descarga automática

### 1. Tabla `projects` (Proyectos)

Almacena información básica sobre los proyectos.

| Columna | Tipo | Restricciones | Descripción |
|---------|------|---------------|-------------|
| id | INTEGER | PRIMARY KEY AUTOINCREMENT | Identificador único del proyecto |
| project_name | TEXT | NOT NULL, UNIQUE | Nombre del proyecto |
| created_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Fecha y hora de creación del registro |
| updated_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Fecha y hora de última actualización |
| last_sync_date | TIMESTAMP | | Fecha y hora de la última sincronización |

**Índices:**
- `sqlite_autoindex_projects_1`: UNIQUE (project_name)

### 2. Tabla `shots` (Tomas)

Almacena información sobre las tomas (shots) asociadas a cada proyecto.

| Columna | Tipo | Restricciones | Descripción |
|---------|------|---------------|-------------|
| id | INTEGER | PRIMARY KEY AUTOINCREMENT | Identificador único del shot |
| project_id | INTEGER | NOT NULL, FOREIGN KEY | ID del proyecto al que pertenece |
| shot_name | TEXT | NOT NULL | Nombre del shot |
| sequence | TEXT | | Secuencia a la que pertenece el shot |
| shot_status | TEXT | | Estado actual del shot |
| thumbnail_url | TEXT | | URL de la miniatura en ShotGrid/Flow |
| local_thumbnail_path | TEXT | | Ruta local de la miniatura |
| created_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Fecha y hora de creación del registro |
| updated_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Fecha y hora de última actualización |
| last_sync_date | TIMESTAMP | | Fecha y hora de la última sincronización |

**Claves Foráneas:**
- `project_id` -> `projects(id)` ON DELETE CASCADE

**Índices:**
- `idx_shots_project_id`: NOT UNIQUE (project_id)
- `sqlite_autoindex_shots_1`: UNIQUE (project_id, shot_name)

### 3. Tabla `tasks` (Tareas)

Almacena información sobre las tareas asociadas a cada shot.

| Columna | Tipo | Restricciones | Descripción |
|---------|------|---------------|-------------|
| id | INTEGER | PRIMARY KEY AUTOINCREMENT | Identificador único de la tarea |
| shot_id | INTEGER | NOT NULL, FOREIGN KEY | ID del shot al que pertenece |
| shot_sg_id | INTEGER | | ID del shot en ShotGrid |
| task_type | TEXT | NOT NULL | Tipo de tarea (ej. Compositing, Animation) |
| task_description | TEXT | | Descripción de la tarea |
| task_status | TEXT | | Estado actual de la tarea |
| task_id | INTEGER | | ID de la tarea en ShotGrid |
| start_date | TIMESTAMP | | Fecha de inicio de la tarea |
| due_date | TIMESTAMP | | Fecha límite de la tarea |
| duration | REAL | | Duración estimada de la tarea en días (soporta valores decimales) |
| created_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Fecha y hora de creación del registro |
| updated_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Fecha y hora de última actualización |
| last_sync_date | TIMESTAMP | | Fecha y hora de la última sincronización |

**Claves Foráneas:**
- `shot_id` -> `shots(id)` ON DELETE CASCADE

**Índices:**
- `idx_tasks_shot_id`: NOT UNIQUE (shot_id)

### 4. Tabla `task_timelogs` (Registros de Tiempo)

Almacena los registros de tiempo trabajado en cada tarea.

| Columna | Tipo | Restricciones | Descripción |
|---------|------|---------------|-------------|
| id | INTEGER | PRIMARY KEY AUTOINCREMENT | Identificador único del registro de tiempo |
| task_id | INTEGER | NOT NULL, FOREIGN KEY | ID de la tarea asociada |
| timelog_sg_id | INTEGER | | ID del registro de tiempo en ShotGrid |
| duration | REAL | NOT NULL | Duración en minutos |
| person | TEXT | | Persona que registró el tiempo |
| description | TEXT | | Descripción del trabajo realizado |
| date | TIMESTAMP | | Fecha y hora del registro |
| created_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Fecha y hora de creación del registro |

**Claves Foráneas:**
- `task_id` -> `tasks(id)` ON DELETE CASCADE

**Índices:**
- `idx_task_timelogs_task_id`: NOT UNIQUE (task_id)
- `sqlite_autoindex_task_timelogs_1`: UNIQUE (task_id, timelog_sg_id)

### 5. Tabla `task_assignments` (Asignaciones de Tareas)

Almacena información sobre las asignaciones de tareas a usuarios.

| Columna | Tipo | Restricciones | Descripción |
|---------|------|---------------|-------------|
| id | INTEGER | PRIMARY KEY AUTOINCREMENT | Identificador único de la asignación |
| task_id | INTEGER | NOT NULL, FOREIGN KEY | ID de la tarea asignada |
| assigned_to | TEXT | NOT NULL | Nombre o ID del usuario asignado |
| created_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Fecha y hora de creación del registro |

**Claves Foráneas:**
- `task_id` -> `tasks(id)` ON DELETE CASCADE

**Índices:**
- `idx_task_assignments_task_id`: NOT UNIQUE (task_id)
- `sqlite_autoindex_task_assignments_1`: UNIQUE (task_id, assigned_to)

### 6. Tabla `versions` (Versiones)

Almacena información sobre las versiones de archivos asociadas a cada tarea.

| Columna | Tipo | Restricciones | Descripción |
|---------|------|---------------|-------------|
| id | INTEGER | PRIMARY KEY AUTOINCREMENT | Identificador único de la versión |
| task_id | INTEGER | NOT NULL, FOREIGN KEY | ID de la tarea a la que pertenece |
| version_number | INTEGER | NOT NULL | Número de versión |
| version_sg_id | INTEGER | | ID de la versión en ShotGrid |
| file_path | TEXT | | Ruta del archivo local |
| status | TEXT | | Estado de la versión |
| description | TEXT | | Descripción de la versión |
| created_by | TEXT | | Usuario que creó la versión |
| created_on | TIMESTAMP | | Fecha y hora de creación en ShotGrid |
| is_synced | BOOLEAN | DEFAULT 0 | Indica si la versión está sincronizada |
| created_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Fecha y hora de creación del registro |

**Claves Foráneas:**
- `task_id` -> `tasks(id)` ON DELETE CASCADE

**Índices:**
- `idx_versions_task_id`: NOT UNIQUE (task_id)
- `sqlite_autoindex_versions_1`: UNIQUE (task_id, version_number)

### 7. Tabla `version_notes` (Notas de Versiones)

Almacena notas detalladas asociadas a cada versión.

**Importante**: Esta tabla ahora es el único lugar donde se almacenan comentarios y notas de versiones. El campo `comments` de la tabla `versions` ya no se utiliza para evitar duplicación de datos.

| Columna | Tipo | Restricciones | Descripción |
|---------|------|---------------|-------------|
| id | INTEGER | PRIMARY KEY AUTOINCREMENT | Identificador único de la nota |
| version_id | INTEGER | NOT NULL, FOREIGN KEY | ID de la versión a la que pertenece |
| note_sg_id | INTEGER | | ID de la nota en ShotGrid |
| content | TEXT | | Contenido de la nota |
| created_by | TEXT | | Usuario que creó la nota |
| created_on | TIMESTAMP | | Fecha y hora de creación en ShotGrid |
| from_playlist | BOOLEAN | DEFAULT 0 | Indica si la nota proviene de una playlist |
| playlist_name | TEXT | | Nombre de la playlist (si aplica) |
| note_links | TEXT | | Campo note_links de Flow en formato JSON |
| created_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Fecha y hora de creación del registro |

**Claves Foráneas:**
- `version_id` -> `versions(id)` ON DELETE CASCADE

**Índices:**
- `idx_version_notes_version_id`: NOT UNIQUE (version_id)

### 8. Tabla `wasabi_auto_download_shots` (Shots para descarga automática)

Almacena los shots seleccionados por los usuarios Downloader para la descarga automática.

| Columna | Tipo | Restricciones | Descripción |
|---------|------|---------------|-------------|
| shot_id | INTEGER | PRIMARY KEY, FOREIGN KEY | ID del shot en la tabla shots |
| is_enabled | INTEGER | NOT NULL DEFAULT 1 | Indica si la descarga automática está habilitada para este shot (1=ON, 0=OFF) |
| added_timestamp | INTEGER | NOT NULL DEFAULT | Timestamp Unix de cuando se añadió (en segundos) |

**Claves Foráneas:**
- `shot_id` -> `shots(id)` ON DELETE CASCADE

**Índices:**
- `idx_wasabi_auto_download_shots_shot_id`: NOT UNIQUE (shot_id)

**Comportamiento por defecto:**
- Todos los shots con estado activo ('ready', 'progre', 'plylst') se añaden automáticamente a esta tabla cuando se crea por primera vez.
- Al cargar un shot en la interfaz, si no tiene un registro en esta tabla, se crea automáticamente con `is_enabled` en 1 (ON).
- Por defecto, todos los shots tienen el autodownload activado (is_enabled=1).
- Cuando el usuario desmarca un checkbox, se cambia el valor de `is_enabled` a 0 en lugar de eliminar el registro.

### 9. Tabla `sync_status` (Estado de Sincronización)

Almacena información sobre el estado de las operaciones de sincronización.

| Columna | Tipo | Restricciones | Descripción |
|---------|------|---------------|-------------|
| id | INTEGER | PRIMARY KEY AUTOINCREMENT | Identificador único del registro de sincronización |
| sync_type | TEXT | NOT NULL | Tipo de sincronización (ej. "flow_to_local", "local_to_wasabi") |
| start_time | TIMESTAMP | | Fecha y hora de inicio de la sincronización |
| end_time | TIMESTAMP | | Fecha y hora de finalización de la sincronización |
| status | TEXT | | Estado de la sincronización (ej. "success", "error", "in_progress") |
| items_processed | INTEGER | DEFAULT 0 | Número de elementos procesados |
| items_total | INTEGER | DEFAULT 0 | Número total de elementos a procesar |
| updated_shots | INTEGER | DEFAULT 0 | Número de shots actualizados |
| created_shots | INTEGER | DEFAULT 0 | Número de shots creados |
| last_updated_shotid | TEXT | | Lista de IDs de shots actualizados (separados por comas) |
| error_message | TEXT | | Mensaje de error (si lo hay) |
| created_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Fecha y hora de creación del registro |

### 10. Tabla `app_settings` (Configuración de la Aplicación)

Almacena la configuración global de la aplicación, incluyendo información del usuario actual.

| Columna | Tipo | Restricciones | Descripción |
|---------|------|---------------|-------------|
| id | INTEGER | PRIMARY KEY AUTOINCREMENT | Identificador único del registro |
| setting_key | TEXT | NOT NULL, UNIQUE | Clave de la configuración |
| setting_value | TEXT | | Valor de la configuración |
| created_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Fecha y hora de creación del registro |
| updated_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Fecha y hora de última actualización |

**Índices:**
- `sqlite_autoindex_app_settings_1`: UNIQUE (setting_key)

**Valores predeterminados:**
- `user_id`: ID del usuario actual en ShotGrid
- `user_login`: Login del usuario actual
- `user_name`: Nombre completo del usuario
- `last_sync_date`: Fecha de la última sincronización exitosa

## Cambios Recientes en la Estructura

### Marzo 2025: Adición de la tabla `task_timelogs`

En marzo de 2025, se realizaron dos cambios importantes en la estructura de la base de datos:

1. **Nueva tabla `task_timelogs`**: Se añadió para almacenar los registros de tiempo trabajado en cada tarea:
   - Almacena la duración en minutos para mayor precisión
   - Incluye información sobre quién registró el tiempo y cuándo
   - Mantiene sincronización con los timelogs de ShotGrid
   - Permite un seguimiento detallado del tiempo invertido en cada tarea

2. **Actualización de la estructura `TaskInfo`**:
   - Se añadió el campo `total_logged_time` para almacenar la suma total de timelogs
   - Este campo se calcula automáticamente al cargar las tareas
   - La interfaz muestra el tiempo loggeado en el campo "Log:" de cada tarea
   - Los valores se muestran en horas si son menos de 8 horas, o en días si son 8 horas o más

### Marzo 2025: Cambio en el campo `duration` de la tabla `tasks`

En marzo de 2025, se realizó un cambio importante en la estructura de la tabla `tasks`:

1. **Cambio de tipo de dato**: El campo `duration` se cambió de `INTEGER` a `REAL` para permitir almacenar valores decimales.
2. **Motivación**: Este cambio permite representar con precisión las estimaciones de tiempo que incluyen fracciones de día (por ejemplo, 1.5 días).
3. **Impacto en la UI**: La interfaz de usuario ahora muestra los valores decimales exactos sin redondeo, mejorando la precisión de la información mostrada.
4. **Correspondencia con Flow**: En la base de datos local se usa el campo `duration`, mientras que en ShotGrid/Flow el campo equivalente es `sg_estdias`. Anteriormente se usaba `sg_estimated_days`, pero ahora exclusivamente se utiliza `sg_estdias`.
5. **Cambios relacionados**:
   - La estructura `TaskInfo` en C++ se actualizó para usar `double` en lugar de `int`.
   - El código de lectura de la base de datos ahora usa `toDouble()` en lugar de `toInt()`.
   - La visualización en la interfaz usa formato de precisión adecuado para mostrar los decimales.

Este cambio es completamente compatible con versiones anteriores, ya que SQLite convierte automáticamente los valores enteros existentes a valores de punto flotante.

## Notas sobre la gestión de comentarios

La versión actual de PipeSync almacena los comentarios exclusivamente en la tabla `version_notes`. Si tienes una base de datos antigua que aún utiliza el campo `comments` de la tabla `versions`, puedes migrar esos datos usando el siguiente proceso:

```sql
-- 1. Migrar comentarios existentes de la tabla versions a version_notes
INSERT INTO version_notes (version_id, content, created_by, created_on)
SELECT id, 
       SUBSTRING(comments, INSTR(comments, ': ') + 2), -- Contenido después de ": "
       SUBSTRING(comments, 1, INSTR(comments, ': ') - 1), -- Autor antes de ": "
       created_on
FROM versions 
WHERE comments IS NOT NULL AND comments != '' AND INSTR(comments, ': ') > 0;

-- 2. Limpiar el campo comments después de la migración
UPDATE versions SET comments = '' WHERE comments IS NOT NULL AND comments != '';
```

Este proceso extrae el autor y el contenido del comentario del campo `comments` y los guarda en la tabla `version_notes`, manteniendo la relación con la versión original.

## Scripts de Gestión de la Base de Datos

Se han creado varios scripts en Python para gestionar la base de datos:

### 1. `create_database.py`

**Propósito**: Crear la estructura inicial de la base de datos SQLite.

**Uso**: 
```bash
python py_scr/create_database.py [--force]
```

**Parámetros**:
- `--force`: Opcional. Si se especifica, elimina la base de datos existente y crea una nueva.

**Funciones principales**:
- `get_db_path()`: Obtiene la ruta a la base de datos.
- `create_database(force=False)`: Crea la base de datos con todas las tablas necesarias.

**Uso en la aplicación**: Este script se utilizará principalmente durante la instalación inicial de la aplicación o cuando sea necesario reiniciar la base de datos. No se ejecutará durante el uso normal de la aplicación.

### 2. `migrate_database.py`

**Propósito**: Migrar bases de datos existentes a la nueva estructura.

**Uso**: 
```bash
python py_scr/migrate_database.py [--db_path RUTA] [--backup]
```

**Parámetros**:
- `--db_path`: Opcional. Ruta personalizada a la base de datos.
- `--backup`: Opcional. Si se especifica, crea una copia de seguridad antes de la migración.

**Funciones principales**:
- `migrate_tasks_table()`: Migra la tabla tasks, cambiando task_url a task_id y añadiendo shot_sg_id.
- `migrate_versions_table()`: Migra la tabla versions, añadiendo los nuevos campos.
- `create_version_notes_table()`: Crea la nueva tabla version_notes.

**Uso en la aplicación**: Este script se utiliza cuando es necesario actualizar la estructura de la base de datos sin perder los datos existentes.

#### Migración de comentarios

La versión actual de PipeSync almacena los comentarios exclusivamente en la tabla `version_notes`. Si tienes una base de datos antigua que aún utiliza el campo `comments` de la tabla `versions`, puedes migrar esos datos usando el siguiente proceso:

```sql
-- 1. Migrar comentarios existentes de la tabla versions a version_notes
INSERT INTO version_notes (version_id, content, created_by, created_on)
SELECT id, 
       SUBSTRING(comments, INSTR(comments, ': ') + 2), -- Contenido después de ": "
       SUBSTRING(comments, 1, INSTR(comments, ': ') - 1), -- Autor antes de ": "
       created_on
FROM versions 
WHERE comments IS NOT NULL AND comments != '' AND INSTR(comments, ': ') > 0;

-- 2. Limpiar el campo comments después de la migración
UPDATE versions SET comments = '' WHERE comments IS NOT NULL AND comments != '';
```

Este proceso extrae el autor y el contenido del comentario del campo `comments` y los guarda en la tabla `version_notes`, manteniendo la relación con la versión original.

### 3. `check_database.py`

**Propósito**: Verificar la estructura completa de la base de datos.

**Uso**: 
```bash
python py_scr/check_database.py [--db_path RUTA]
```

**Parámetros**:
- `--db_path`: Opcional. Ruta personalizada a la base de datos.

**Funciones principales**:
- `check_database(db_path)`: Verifica la estructura de la base de datos, mostrando información detallada sobre tablas, columnas, claves foráneas e índices.

**Uso en la aplicación**: Este script es principalmente una herramienta de diagnóstico para desarrolladores y no se utilizará en la aplicación final.

### 4. `check_table.py`

**Propósito**: Verificar la estructura de una tabla específica en la base de datos.

**Uso**: 
```bash
python py_scr/check_table.py NOMBRE_TABLA
```

**Parámetros**:
- `NOMBRE_TABLA`: Nombre de la tabla a verificar.

**Funciones principales**:
- `check_table(table_name)`: Verifica la estructura de una tabla específica, mostrando información detallada sobre columnas, claves foráneas e índices.

**Uso en la aplicación**: Este script es principalmente una herramienta de diagnóstico para desarrolladores y no se utilizará en la aplicación final.

### 5. `check_shot.py`

**Propósito**: Buscar y mostrar información detallada de un shot específico.

**Uso**: 
```bash
python py_scr/check_shot.py NOMBRE_SHOT
```

**Parámetros**:
- `NOMBRE_SHOT`: Nombre del shot a buscar (puede ser parcial).

**Funciones principales**:
- `check_shot(shot_name)`: Busca un shot en la base de datos y muestra toda su información, incluyendo tareas, versiones y asignaciones.

**Uso en la aplicación**: Este script es principalmente una herramienta de diagnóstico para desarrolladores.

### 6. `list_tables.py`

**Propósito**: Listar todas las tablas presentes en la base de datos.

**Uso**: 
```bash
python py_scr/list_tables.py
```

**Funciones principales**:
- `list_tables()`: Lista todas las tablas presentes en la base de datos.

**Uso en la aplicación**: Este script es principalmente una herramienta de diagnóstico para desarrolladores y no se utilizará en la aplicación final.

### 7. `get_Flow_info.py`

**Propósito**: Obtener información de ShotGrid/Flow y guardarla en la base de datos SQLite.

**Uso**: 
```bash
python py_scr/get_Flow_info.py
```

**Funciones principales**:
- `connect_to_shotgrid()`: Establece conexión con ShotGrid/Flow usando credenciales de variables de entorno.
- `get_user_id(sg, user_login)`: Obtiene el ID del usuario usando su login.
- `get_assigned_tasks(sg, user_id)`: Obtiene todas las tareas asignadas al usuario, filtrando por estado del proyecto.
- `extract_version_info(version_code, task_type)`: Extrae información de versión del código.
- `get_all_versions_for_task(sg, task_id, shot_id)`: Obtiene todas las versiones asociadas a una tarea.
- `save_task_to_db(task, sg, db_manager)`: Guarda la información de la tarea en la base de datos, incluyendo todas sus versiones.
- `main()`: Función principal que coordina todo el proceso de sincronización.

**Uso en la aplicación**: Este script se ejecuta cuando el usuario solicita sincronizar datos desde ShotGrid/Flow a la base de datos local. Registra el progreso de la sincronización en la tabla `sync_status` y guarda toda la información relevante en las tablas correspondientes.

### 8. `test_versiones.py`

**Propósito**: Probar la obtención de versiones desde ShotGrid.

**Uso**: 
```bash
python py_scr/test_versiones.py
```

**Funciones principales**:
- `connect_to_shotgrid()`: Establece conexión con ShotGrid.
- `get_all_versions_for_task(sg, task_id, shot_id)`: Prueba la obtención de todas las versiones para una tarea.
- `extract_version_info(version_code, task_type)`: Prueba la extracción de información de versiones.
- `test_shotgrid_versions()`: Prueba la obtención y filtrado de versiones.

**Uso en la aplicación**: Este script es una herramienta de prueba para desarrolladores.

## Clase `DBManager`

La clase `DBManager` es el componente central para la interacción con la base de datos SQLite. Se encuentra en el archivo `py_scr/db_manager.py` y proporciona métodos para realizar operaciones CRUD en todas las tablas.

**Métodos principales**:

- `__init__(self, db_path=None)`: Constructor que establece la conexión con la base de datos.
- `connect(self)`: Establece una conexión con la base de datos.
- `close(self)`: Cierra la conexión con la base de datos.
- `execute(self, query, params=())`: Ejecuta una consulta SQL con parámetros.
- `fetch_one(self, query, params=())`: Ejecuta una consulta y devuelve un solo resultado.
- `fetch_all(self, query, params=())`: Ejecuta una consulta y devuelve todos los resultados.
- `add_project(self, project_name)`: Añade un proyecto a la base de datos.
- `add_shot(self, project_id, shot_name, sequence=None, shot_status=None, thumbnail_url=None)`: Añade un shot a la base de datos.
- `add_task(self, shot_id, task_type, task_description=None, task_status=None, task_id=None, shot_sg_id=None)`: Añade una tarea a la base de datos.
- `add_task_assignment(self, task_id, assigned_to)`: Añade una asignación de tarea a la base de datos.
- `add_version(self, task_id, version_number, version_sg_id=None, file_path=None, status=None, description=None, created_by=None, created_on=None, comments=None)`: Añade una versión a la base de datos.
- `add_version_note(self, version_id, note_sg_id=None, content=None, created_by=None, created_on=None)`: Añade una nota de versión a la base de datos.
- `create_sync_status(self, sync_type, items_total=0)`: Crea un registro de estado de sincronización.
- `update_sync_status(self, sync_id, status=None, items_processed=None, error_message=None)`: Actualiza un registro de estado de sincronización.
- `finalize_sync_status(self, sync_id, status, items_processed)`: Finaliza un registro de estado de sincronización.

**Funciones auxiliares**:

- `add_project(project_name, db_manager=None)`: Función auxiliar para añadir un proyecto.
- `add_shot(project_id, shot_name, sequence=None, shot_status=None, thumbnail_url=None, db_manager=None)`: Función auxiliar para añadir un shot.
- `add_task(shot_id, task_type, task_description=None, task_status=None, task_id=None, shot_sg_id=None, db_manager=None)`: Función auxiliar para añadir una tarea.
- `add_task_assignment(task_id, assigned_to, db_manager=None)`: Función auxiliar para añadir una asignación de tarea.
- `add_version(task_id, version_number, version_sg_id=None, file_path=None, status=None, description=None, created_by=None, created_on=None, comments=None, db_manager=None)`: Función auxiliar para añadir una versión.
- `add_version_note(version_id, note_sg_id=None, content=None, created_by=None, created_on=None, db_manager=None)`: Función auxiliar para añadir una nota de versión.
- `create_sync_status(sync_type, items_total=0, db_manager=None)`: Función auxiliar para crear un registro de estado de sincronización.
- `update_sync_status(sync_id, status=None, items_processed=None, error_message=None, db_manager=None)`: Función auxiliar para actualizar un registro de estado de sincronización.
- `finalize_sync_status(sync_id, status, items_processed, db_manager=None)`: Función auxiliar para finalizar un registro de estado de sincronización.

## Uso de la Base de Datos en la Aplicación

La aplicación PipeSync utilizará la base de datos SQLite para:

1. **Almacenamiento local de datos**: Guardar información sobre proyectos, shots, tareas y versiones descargadas de ShotGrid/Flow.
2. **Seguimiento de sincronización**: Mantener un registro del estado de sincronización entre ShotGrid/Flow y Wasabi S3.
3. **Operaciones offline**: Permitir trabajar con datos cuando no hay conexión a internet.
4. **Caché de datos**: Mejorar el rendimiento al evitar consultas repetidas a ShotGrid/Flow.
5. **Historial de versiones**: Mantener un registro completo de todas las versiones de cada tarea.

La interacción con la base de datos se realizará principalmente a través de la clase `DBManager` que proporciona métodos para realizar operaciones CRUD (Crear, Leer, Actualizar, Eliminar) en las diferentes tablas.

## Flujo de Sincronización de Datos

El proceso de sincronización de datos desde ShotGrid/Flow a la base de datos local sigue estos pasos:

1. **Inicio de la sincronización**: Se crea un registro en la tabla `sync_status` con el tipo "flow_to_local" y estado "in_progress".
2. **Conexión a ShotGrid/Flow**: Se establece conexión con ShotGrid/Flow usando las credenciales almacenadas.
3. **Obtención de tareas**: Se obtienen todas las tareas asignadas al usuario actual.
4. **Procesamiento de tareas**: Para cada tarea:
   - Se verifica si el proyecto existe en la base de datos, si no, se crea.
   - Se verifica si el shot existe en la base de datos, si no, se crea.
   - Se verifica si la tarea existe en la base de datos, si no, se crea.
   - Se guardan las asignaciones de la tarea.
   - Se obtienen todas las versiones asociadas a la tarea y se filtran por tipo.
   - Se guardan todas las versiones filtradas en la base de datos.
   - Se guardan las notas asociadas a cada versión **exclusivamente en la tabla `version_notes`** (no se utiliza el campo `comments` de la tabla `versions` para evitar duplicación).
5. **Finalización de la sincronización**: Se actualiza el registro en la tabla `sync_status` con el estado "success" y el número de elementos procesados.

## Consideraciones de Seguridad

- La base de datos no almacena credenciales de acceso a ShotGrid/Flow o Wasabi S3.
- Las credenciales se manejan a través del módulo `SecureConfig` de la aplicación.
- La base de datos es local y no se sincroniza con servicios externos.

## Mantenimiento de la Base de Datos

- La aplicación realizará comprobaciones periódicas de integridad de la base de datos.
- Se implementará un sistema de respaldo automático antes de operaciones críticas.
- La opción de reiniciar la base de datos estará disponible en la configuración avanzada de la aplicación.

## Diagrama de Relaciones

```
projects
    |
    +--> shots
           |
           +--> tasks
                  |
                  +--> versions
                  |     |
                  |     +--> version_notes
                  |
                  +--> task_assignments
                  |
                  +--> task_timelogs
```

## Consultas Comunes

A continuación se presentan algunas consultas SQL comunes que se utilizan en la aplicación:

### Obtener todos los proyectos
```sql
SELECT * FROM projects ORDER BY project_name;
```

### Obtener todos los shots de un proyecto
```sql
SELECT * FROM shots WHERE project_id = ? ORDER BY shot_name;
```

### Obtener todas las tareas de un shot con tiempo total loggeado
```sql
SELECT t.*, 
       COALESCE((SELECT SUM(duration) FROM task_timelogs WHERE task_id = t.id), 0) as total_logged_time 
FROM tasks t 
WHERE t.shot_id = ? 
ORDER BY t.task_type;
```

### Obtener todos los timelogs de una tarea
```sql
SELECT * FROM task_timelogs 
WHERE task_id = ? 
ORDER BY date DESC;
```

### Obtener el tiempo total loggeado por persona para una tarea
```sql
SELECT person, SUM(duration) as total_minutes,
       SUM(duration)/60.0 as total_hours,
       SUM(duration)/(60.0 * 8.0) as total_days
FROM task_timelogs 
WHERE task_id = ? 
GROUP BY person;
```

### Obtener todas las asignaciones de una tarea
```sql
SELECT * FROM task_assignments WHERE task_id = ? ORDER BY assigned_to;
```

### Obtener todas las versiones de una tarea
```sql
SELECT * FROM versions WHERE task_id = ? ORDER BY version_number DESC;
```

### Obtener todas las notas de una versión
```sql
SELECT * FROM version_notes WHERE version_id = ? ORDER BY created_on DESC;
```

### Obtener todas las notas que provienen de playlists
```sql
SELECT * FROM version_notes WHERE version_id = ? AND from_playlist = 1 ORDER BY created_on DESC;
```

### Verificar si un shot está marcado para descarga automática
```sql
SELECT EXISTS(SELECT 1 FROM wasabi_auto_download_shots WHERE shot_id = ? AND is_enabled = 1) as is_auto_download;
```

### Obtener todos los shots marcados para descarga automática
```sql
SELECT s.id, s.shot_name, p.project_name 
FROM shots s 
JOIN projects p ON s.project_id = p.id 
WHERE EXISTS (SELECT 1 FROM wasabi_auto_download_shots WHERE shot_id = s.id AND is_enabled = 1)
ORDER BY p.project_name, s.shot_name;
```

### Obtener información completa de una versión con sus notas
```sql
SELECT v.id, v.version_number, v.status, v.description, v.created_by, v.created_on,
       n.content as note_content, n.created_by as note_author, n.created_on as note_date,
       n.from_playlist, n.playlist_name
FROM versions v 
LEFT JOIN version_notes n ON v.id = n.version_id
WHERE v.id = ?
ORDER BY n.created_on DESC;
```

### Obtener el último estado de sincronización
```sql
SELECT * FROM sync_status ORDER BY id DESC LIMIT 1;
```

### Obtener información completa de un shot (con joins)
```sql
SELECT s.*, p.project_name 
FROM shots s 
JOIN projects p ON s.project_id = p.id 
WHERE s.id = ?;
```

### Obtener información completa de una tarea (con joins)
```sql
SELECT t.*, s.shot_name, p.project_name 
FROM tasks t 
JOIN shots s ON t.shot_id = s.id 
JOIN projects p ON s.project_id = p.id 
WHERE t.id = ?;
```

### Buscar un shot por nombre
```sql
SELECT s.id, s.shot_name, p.project_name, t.task_type, t.id as task_id, t.task_id as task_sg_id, t.shot_sg_id 
FROM shots s 
JOIN projects p ON s.project_id = p.id 
JOIN tasks t ON s.id = t.shot_id 
WHERE s.shot_name LIKE '%?%';
```

### Obtener versiones de un shot específico con información detallada
```sql
SELECT v.id, v.version_number, v.version_sg_id, v.status, v.description, 
       v.created_by, v.created_on, v.comments 
FROM versions v 
JOIN tasks t ON v.task_id = t.id 
JOIN shots s ON t.shot_id = s.id 
WHERE s.shot_name = ? 
ORDER BY v.version_number DESC;
```