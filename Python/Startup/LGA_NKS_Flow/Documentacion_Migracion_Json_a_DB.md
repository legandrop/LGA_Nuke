# Migración de JSON a Base de Datos SQLite (pipesync.db)

Este documento describe el mapeo de campos entre el archivo JSON utilizado por el script Python `LGA_NKS_Flow_Pull.py` y la base de datos SQLite `pipesync.db` ubicada en:

    C:\Portable\LGA\PipeSync\cache\pipesync.db

El objetivo es que la base de datos contenga toda la información relevante que antes se obtenía del JSON, permitiendo reemplazar completamente el uso del archivo JSON.

---

## Archivos y funciones principales involucradas

- **Script Python:**
  - `Python/Startup/LGA_NKS_Flow/LGA_NKS_Flow_Pull.py`
    - Clase principal de acceso: `ShotGridManager`
    - Funciones clave: `find_project`, `find_shot`, `find_task`, `find_highest_version_for_shot`
- **Base de datos SQLite:**
  - `C:\Portable\LGA\PipeSync\cache\pipesync.db`
  - Documentación de estructura: `Python/Startup/LGA_NKS_Flow/Documentacion_DB.md`

---

## Estructura y mapeo de campos

### 1. Proyectos

- **JSON:**
  - projects[]: lista de proyectos
    - project_name
- **DB:**
  - Tabla: `projects`
    - project_name

### 2. Shots

- **JSON:**
  - projects[].shots[]: lista de shots por proyecto
    - shot_name
- **DB:**
  - Tabla: `shots`
    - shot_name
    - project_id (relación con projects)

### 3. Tasks (Tareas)

- **JSON:**
  - projects[].shots[].tasks[]: lista de tareas por shot
    - task_type
    - task_status
    - task_assigned_to
- **DB:**
  - Tabla: `tasks`
    - task_type
    - task_status
    - shot_id (relación con shots)
  - Tabla: `task_assignments`
    - assigned_to (corresponde a task_assigned_to)
    - task_id (relación con tasks)

### 4. Versions (Versiones)

- **JSON:**
  - projects[].shots[].tasks[].versions[]: lista de versiones por tarea
    - version_number
    - version_status
    - version_description
- **DB:**
  - Tabla: `versions`
    - version_number (en la DB es INTEGER, en el JSON es string tipo "SHOTNAME_comp_v001")
    - status (corresponde a version_status)
    - description (corresponde a version_description)
    - task_id (relación con tasks)
  - Tabla: `version_notes`
    - content (comentarios o descripciones adicionales)

---

## Tabla resumen de mapeo

| JSON                                      | DB (tabla.campo)                |
|--------------------------------------------|---------------------------------|
| projects[].project_name                    | projects.project_name           |
| projects[].shots[].shot_name               | shots.shot_name                 |
| projects[].shots[].tasks[].task_type       | tasks.task_type                 |
| projects[].shots[].tasks[].task_status     | tasks.task_status               |
| projects[].shots[].tasks[].task_assigned_to| task_assignments.assigned_to    |
| projects[].shots[].tasks[].versions[].version_number | versions.version_number (convertido a int) |
| projects[].shots[].tasks[].versions[].version_status | versions.status              |
| projects[].shots[].tasks[].versions[].version_description | versions.description      |

---

## Notas adicionales

- El campo `version_number` en la base de datos es numérico (ej: 1, 2, 3), mientras que en el JSON suele venir como string (ej: "SHOTNAME_comp_v001"). Se debe extraer el número para almacenarlo en la DB.
- El campo `task_assigned_to` del JSON se almacena en la tabla `task_assignments` de la DB, relacionada por `task_id`.
- Si existen comentarios o notas adicionales en las versiones, pueden almacenarse en la tabla `version_notes`.
- Las relaciones entre entidades (proyecto, shot, tarea, versión) se mantienen mediante claves foráneas en la base de datos.

---

## Ejemplo de migración de un shot

**JSON:**
```json
{
  "project_name": "PROY1",
  "shots": [
    {
      "shot_name": "SHOT_001",
      "tasks": [
        {
          "task_type": "Comp",
          "task_status": "progre",
          "task_assigned_to": "Juan Perez",
          "versions": [
            {
              "version_number": "SHOT_001_comp_v003",
              "version_status": "rev",
              "version_description": "Primera review"
            }
          ]
        }
      ]
    }
  ]
}
```

**DB (tablas):**
- projects: project_name = "PROY1"
- shots: shot_name = "SHOT_001", project_id = (id de PROY1)
- tasks: task_type = "Comp", task_status = "progre", shot_id = (id de SHOT_001)
- task_assignments: assigned_to = "Juan Perez", task_id = (id de la tarea Comp)
- versions: version_number = 3, status = "rev", description = "Primera review", task_id = (id de la tarea Comp)

---

## Referencias
- Script de lectura: `Python/Startup/LGA_NKS_Flow/LGA_NKS_Flow_Pull.py` (clase `ShotGridManager`)
- Documentación de la base de datos: `Python/Startup/LGA_NKS_Flow/Documentacion_DB.md`
- Base de datos destino: `C:\Portable\LGA\PipeSync\cache\pipesync.db`
