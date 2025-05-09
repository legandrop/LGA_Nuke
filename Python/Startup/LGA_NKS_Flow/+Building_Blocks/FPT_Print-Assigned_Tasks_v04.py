# Version que descarga todas las versiones y notas asociadas a las tareas asignadas al usuario
# v04: muestra las tareas asignadas y como reviewer, y agrega el campo user_role para indicar el rol del usuario

import os
import shotgun_api3

# Recuperar datos de autenticacion de las variables de entorno
url = os.environ.get("SHOTGRID_URL")
login = os.environ.get("SHOTGRID_LOGIN")
password = os.environ.get("SHOTGRID_PASSWORD")

# Crear una instancia de la API de ShotGrid usando login y password
sg = shotgun_api3.Shotgun(url, login=login, password=password)


def get_assigned_tasks(sg, user_login, min_date=None):
    filters = [
        ["task_assignees.HumanUser.login", "is", user_login],
        ["sg_status_list", "is_not", "fin"],
    ]

    # Añadir filtros de fecha si se especifica una fecha mínima
    if min_date:
        date_filter = {
            "filter_operator": "any",
            "filters": [
                ["created_at", "greater_than", min_date],
                ["updated_at", "greater_than", min_date],
            ],
        }
        filters.append(date_filter)

    # Añadir campos para versiones y notas
    fields = [
        "id",
        "content",
        "sg_description",
        "sg_status_list",
        "entity",
        "entity.Shot.code",
        "entity.Shot.description",
        "entity.Shot.sg_status_list",
        "project.Project.name",
        "project.Project.sg_status",
        "versions",  # Versiones asociadas a la tarea
        "notes",  # Notas asociadas a la tarea
        "task_assignees",
        "task_reviewers",  # Campo para reviewers
    ]
    tasks = sg.find("Task", filters, fields)
    for t in tasks:
        t["user_role"] = "Artista"
    return tasks


def get_reviewer_tasks(sg, user_login, min_date=None):
    filters = [
        ["task_reviewers.HumanUser.login", "is", user_login],
        ["sg_status_list", "is_not", "fin"],
    ]
    if min_date:
        date_filter = {
            "filter_operator": "any",
            "filters": [
                ["created_at", "greater_than", min_date],
                ["updated_at", "greater_than", min_date],
            ],
        }
        filters.append(date_filter)
    fields = [
        "id",
        "content",
        "sg_description",
        "sg_status_list",
        "entity",
        "entity.Shot.code",
        "entity.Shot.description",
        "entity.Shot.sg_status_list",
        "project.Project.name",
        "project.Project.sg_status",
        "versions",
        "notes",
        "task_assignees",
        "task_reviewers",
    ]
    tasks = sg.find("Task", filters, fields)
    for t in tasks:
        t["user_role"] = "Reviewer"
    return tasks


def find_latest_version_for_shot(sg, shot_id):
    # Buscar la última versión asociada al shot
    filters = [["entity", "is", {"type": "Shot", "id": shot_id}]]
    fields = ["id", "code", "sg_status_list", "description", "created_at", "user"]
    # Ordenar por fecha de creación descendente y limitar a 1 resultado
    return sg.find_one(
        "Version", filters, fields, [{"field_name": "created_at", "direction": "desc"}]
    )


def print_task_info(task, sg):
    print(f"\nProject: {task.get('project.Project.name', 'No project available')}")
    print(
        f"Project Status: {task.get('project.Project.sg_status', 'No status available')}"
    )
    print(f"Shot: {task.get('entity.Shot.code', 'No shot available')}")
    print(
        f"Shot Status: {task.get('entity.Shot.sg_status_list', 'No status available')}"
    )
    print(f"Task: {task['content']}")
    print(f"Task Status: {task['sg_status_list']}")
    print(
        f"Description: {task.get('entity.Shot.description', 'No description available')}"
    )
    print(f"Rol: {task.get('user_role', 'Desconocido')}")

    # Obtener la última versión asociada al shot
    if task.get("entity"):
        shot_id = task["entity"]["id"]
        version = find_latest_version_for_shot(sg, shot_id)

        if version:
            print("\nÚltima versión:")
            print(f"  - Version SG: {version.get('code', 'No version code')}")
            print(f"    Status: {version.get('sg_status_list', 'No status')}")
            print(f"    Description: {version.get('description', 'No description')}")
            print(f"    Created At: {version.get('created_at', 'No date available')}")
            print(
                f"    User: {version['user']['name'] if version.get('user') else 'No user available'}"
            )

            # Obtener notas de la versión
            notes = sg.find(
                "Note",
                [["note_links", "in", {"type": "Version", "id": version["id"]}]],
                ["content", "user"],
            )
            if notes:
                print("    Comments:")
                for note in notes:
                    print(f"      - {note['content']} (User: {note['user']['name']})")
            else:
                print("    No comments found.")
        else:
            print("\nNo se encontraron versiones asociadas en ShotGrid.")

    # Generar URL de la tarea usando la base URL de ShotGrid
    task_url = f"{sg.base_url}/detail/Task/{task['id']}"
    print(f"\nTask URL: {task_url}")


def main():
    try:
        # Especificar fecha mínima con formato completo (ejemplo: 1 de marzo de 2025 a las 00:00 UTC)
        min_date = "2025-03-01T00:00:00Z"
        tasks_artist = get_assigned_tasks(sg, login, min_date)
        tasks_reviewer = get_reviewer_tasks(sg, login, min_date)
        # Unificar por id, priorizando el rol de artista si está en ambos
        tasks_dict = {}
        for t in tasks_reviewer:
            tasks_dict[t["id"]] = t
        for t in tasks_artist:
            tasks_dict[t["id"]] = t  # Sobrescribe si ya estaba como reviewer
        all_tasks = list(tasks_dict.values())
        if all_tasks:
            print(f"\nTareas asignadas o como reviewer:")
            for task in all_tasks:
                print_task_info(task, sg)
        else:
            print("No se encontraron tareas asignadas ni como reviewer")

    except Exception as e:
        print(f"Error al obtener tareas: {e}")


if __name__ == "__main__":
    main()
