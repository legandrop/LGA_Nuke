# Script para listar todos los campos de Task en ShotGrid
# Con énfasis en campos de estimación de tiempo/duración

import os
import shotgun_api3
import pprint

# Recuperar datos de autenticación de las variables de entorno
url = os.environ.get("SHOTGRID_URL")
login = os.environ.get("SHOTGRID_LOGIN")
password = os.environ.get("SHOTGRID_PASSWORD")

# Crear una instancia de la API de ShotGrid usando login y password
sg = shotgun_api3.Shotgun(url, login=login, password=password)


def listar_campos_task():
    """
    Lista todos los campos de la entidad Task en ShotGrid,
    con énfasis en campos relacionados con estimaciones.
    """
    print("\n=== CAMPOS DE TASK EN SHOTGRID ===\n")

    # Obtener todos los campos de Task
    fields = sg.schema_field_read("Task")

    # Primero mostrar campos relacionados con estimaciones
    print("--- CAMPOS RELACIONADOS CON ESTIMACIONES ---")
    estimation_fields = {}
    keywords = ["estimat", "duration", "time", "hour", "día", "day", "week", "fecha"]

    for field_name, field_data in fields.items():
        field_display = field_data.get("name", {}).get("value", "Sin nombre")

        # Buscar campos relacionados con estimaciones
        if any(
            keyword.lower() in field_name.lower()
            or keyword.lower() in field_display.lower()
            for keyword in keywords
        ):
            estimation_fields[field_name] = field_data
            print(f"Campo: {field_name}")
            print(f"  Nombre visible: {field_display}")
            print(f"  Editable: {field_data.get('editable', False)}")
            print(
                f"  Tipo: {field_data.get('data_type', {}).get('value', 'Desconocido')}"
            )

            # Si es una lista, mostrar valores posibles
            if field_data.get("data_type", {}).get("value") == "list":
                valores = (
                    field_data.get("properties", {})
                    .get("valid_values", {})
                    .get("value", [])
                )
                print(
                    f"  Valores permitidos: {', '.join(valores) if valores else 'Ninguno'}"
                )
            print()

    # Mostrar resto de campos
    print("\n--- TODOS LOS CAMPOS DE TASK ---")
    for field_name, field_data in fields.items():
        if field_name not in estimation_fields:
            field_display = field_data.get("name", {}).get("value", "Sin nombre")
            print(
                f"{field_name} → {field_display} | Editable: {field_data.get('editable', False)}"
            )


def ver_ejemplo_tarea(task_id=None):
    """
    Muestra un ejemplo de una tarea para ver sus valores actuales.
    Si no se proporciona task_id, busca la primera tarea disponible.
    """
    print("\n=== EJEMPLO DE TAREA ===\n")

    if not task_id:
        # Obtener una tarea cualquiera como ejemplo
        result = sg.find_one("Task", [], ["id"])
        if result:
            task_id = result["id"]
        else:
            print("No se encontró ninguna tarea en el proyecto.")
            return

    # Obtener todos los campos de la tarea
    task = sg.find_one("Task", [["id", "is", task_id]], fields=None)

    if task:
        print(f"Tarea ID: {task.get('id')}")
        print(f"Nombre: {task.get('content')}")

        # Mostrar campos relacionados con estimaciones
        keywords = [
            "estimat",
            "duration",
            "time",
            "hour",
            "día",
            "day",
            "week",
            "fecha",
        ]
        estimation_data = {}

        for field, value in task.items():
            if (
                any(keyword.lower() in field.lower() for keyword in keywords)
                and value is not None
            ):
                estimation_data[field] = value

        if estimation_data:
            print("\nCampos de estimación:")
            for field, value in estimation_data.items():
                print(f"  {field}: {value}")
        else:
            print("\nNo se encontraron campos de estimación con valores.")

        # Opcional: Mostrar los primeros 5 campos genéricos
        print("\nOtros campos de ejemplo:")
        count = 0
        for field, value in task.items():
            if (
                field not in estimation_data
                and field not in ["type", "id"]
                and value is not None
            ):
                print(f"  {field}: {value}")
                count += 1
                if count >= 5:
                    break
    else:
        print(f"No se encontró ninguna tarea con ID {task_id}")


def actualizar_campo_estimacion(task_id, campo, valor):
    """
    Actualiza un campo de estimación para una tarea específica.

    Args:
        task_id (int): ID de la tarea a actualizar
        campo (str): Nombre del campo a actualizar (ej: 'sg_estimated_time')
        valor: Valor a asignar al campo
    """
    try:
        result = sg.update("Task", task_id, {campo: valor})
        print(f"\nCampo '{campo}' de Tarea {task_id} actualizado con valor: {valor}")
        return result
    except Exception as e:
        print(f"\nError al actualizar el campo '{campo}': {e}")
        return None


def main():
    # Mostrar todos los campos de Task en ShotGrid
    listar_campos_task()

    # Mostrar ejemplo de una tarea (opcional)
    # Descomenta la siguiente línea para ver un ejemplo de tarea
    # ver_ejemplo_tarea()

    # Ejemplo de cómo actualizar un campo de estimación
    # (descomenta y modifica para probar)
    """
    task_id = 123  # Reemplaza con un ID de tarea válido
    campo_estimacion = "sg_estimated_time"  # Reemplaza con el nombre correcto del campo
    nuevo_valor = 2.5  # Reemplaza con el valor deseado
    actualizar_campo_estimacion(task_id, campo_estimacion, nuevo_valor)
    """


if __name__ == "__main__":
    main()
