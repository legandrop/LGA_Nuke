# Script para crear un nuevo campo "Estimated" (est_in_mins) en Task en ShotGrid

import os
import sys

# Agregar la ruta donde se encuentra el módulo shotgun_api3
# La carpeta LGA_ToolPack está en la raíz de .nuke
shotgun_path = os.path.join(
    os.path.dirname(os.path.expanduser("~/.nuke")), ".nuke", "LGA_ToolPack"
)
if not os.path.exists(shotgun_path):
    shotgun_path = r"C:\Users\leg4-pc\.nuke\LGA_ToolPack"
if shotgun_path not in sys.path:
    sys.path.append(shotgun_path)

import shotgun_api3

# Recuperar datos de autenticación de las variables de entorno o solicitar al usuario
url = os.environ.get("SHOTGRID_URL")
login = os.environ.get("SHOTGRID_LOGIN")
password = os.environ.get("SHOTGRID_PASSWORD")

# Si alguna de las credenciales no está disponible, solicitar al usuario
if not url or not login or not password:
    print("\n=== CONFIGURACIÓN DE SHOTGRID ===")
    if not url:
        url = input("URL de ShotGrid (ej: https://tudominio.shotgunstudio.com): ")
    if not login:
        login = input("Usuario de ShotGrid: ")
    if not password:
        import getpass

        password = getpass.getpass("Contraseña de ShotGrid: ")

try:
    # Crear una instancia de la API de ShotGrid usando login y password
    print("\nConectando a ShotGrid...")
    sg = shotgun_api3.Shotgun(url, login=login, password=password)
    print("Conexión exitosa!")
except Exception as e:
    print(f"\nError al conectar con ShotGrid: {e}")
    sys.exit(1)


def actualizar_campo_estimado(task_id, minutos):
    """
    Actualiza el campo est_in_mins (Estimated) para una tarea específica.

    Args:
        task_id (int): ID de la tarea a actualizar
        minutos (int): Cantidad de minutos estimados

    Returns:
        dict: Resultado de la actualización o None si hubo error
    """
    try:
        print(f"\nActualizando estimación para tarea ID: {task_id}")
        print(f"Valor a establecer: {minutos} minutos")

        # Actualizar el campo est_in_mins
        result = sg.update("Task", task_id, {"est_in_mins": minutos})

        # Verificar la actualización
        task = sg.find_one(
            "Task", [["id", "is", task_id]], ["id", "content", "est_in_mins"]
        )
        if task and "est_in_mins" in task:
            print(f"\n¡Actualización exitosa!")
            print(f"Tarea: {task.get('content', 'Sin nombre')}")
            print(f"Estimación actual: {task.get('est_in_mins')} minutos")
        else:
            print(
                "\nLa actualización parece haber sido exitosa, pero no se pudo verificar el valor actual."
            )

        return result
    except Exception as e:
        print(f"\nError al actualizar el campo de estimación: {e}")
        return None


def listar_tareas_asignadas():
    """
    Lista todas las tareas asignadas al usuario actual.

    Returns:
        list: Lista de tareas asignadas o lista vacía si hubo error
    """
    try:
        print("\nBuscando tareas asignadas al usuario actual...")

        # Filtrar tareas asignadas al usuario actual y no finalizadas
        filters = [
            ["task_assignees.HumanUser.login", "is", login],
            ["sg_status_list", "is_not", "fin"],  # Tareas no finalizadas
        ]

        # Campos a recuperar
        fields = ["id", "content", "entity", "project", "sg_status_list", "est_in_mins"]

        # Ordenar por proyecto y entidad
        order = [
            {"field_name": "project", "direction": "asc"},
            {"field_name": "entity", "direction": "asc"},
        ]

        # Buscar tareas
        tasks = sg.find("Task", filters, fields, order)

        if tasks:
            print(f"\nSe encontraron {len(tasks)} tareas asignadas:")
            for i, task in enumerate(tasks, 1):
                entity_name = task.get("entity", {}).get("name", "Sin entidad")
                project_name = task.get("project", {}).get("name", "Sin proyecto")
                status = task.get("sg_status_list", "")
                est_mins = task.get("est_in_mins")

                est_display = (
                    f"{est_mins} minutos" if est_mins is not None else "No establecido"
                )

                print(
                    f"{i}. ID: {task['id']} | {project_name} - {entity_name} | {task['content']}"
                )
                print(f"   Status: {status} | Estimación actual: {est_display}")

            return tasks
        else:
            print("\nNo se encontraron tareas asignadas al usuario actual.")
            return []
    except Exception as e:
        print(f"\nError al buscar tareas: {e}")
        return []


def main():
    print("\n=== ACTUALIZACIÓN DE CAMPO ESTIMADO EN TAREAS ===")

    # Paso 1: Listar tareas asignadas al usuario
    tareas = listar_tareas_asignadas()

    if not tareas:
        print("\nNo hay tareas disponibles para actualizar.")
        return

    # Paso 2: Permitir al usuario seleccionar una tarea
    seleccion = input(
        "\nIngresa el número de la tarea a actualizar (o 'q' para salir): "
    )

    if seleccion.lower() == "q":
        print("Saliendo sin actualizar tareas.")
        return

    try:
        indice = int(seleccion) - 1
        if 0 <= indice < len(tareas):
            tarea_seleccionada = tareas[indice]

            # Paso 3: Solicitar nuevo valor de estimación
            print(f"\nTarea seleccionada: {tarea_seleccionada['content']}")

            # Mostrar valor actual si existe
            valor_actual = tarea_seleccionada.get("est_in_mins")
            if valor_actual is not None:
                print(f"Estimación actual: {valor_actual} minutos")
            else:
                print("Actualmente no tiene estimación establecida.")

            # Solicitar nuevo valor
            nuevo_valor = input("\nIngresa el nuevo valor de estimación en minutos: ")

            try:
                minutos = int(nuevo_valor)
                # Paso 4: Actualizar el campo de estimación
                actualizar_campo_estimado(tarea_seleccionada["id"], minutos)
            except ValueError:
                print("Error: Debes ingresar un número entero para los minutos.")
        else:
            print("Número de tarea inválido.")
    except ValueError:
        print("Error: Debes ingresar un número válido.")


if __name__ == "__main__":
    main()
