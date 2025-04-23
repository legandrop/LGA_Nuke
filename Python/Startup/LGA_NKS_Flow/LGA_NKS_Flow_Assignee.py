"""
_____________________________________________________________

  LGA_NKS_Flow_Assignee v0.3 - 2025 - Lega Pugliese
  Imprime los asignados de una tarea en ShotGrid (Flow) a partir del base_name
_____________________________________________________________
"""

import os
import re
import shotgun_api3
from PySide2.QtCore import QRunnable, Slot, QThreadPool, Signal, QObject

# Variable global para debug
DEBUG = True

debug_messages = []


def debug_print(message):
    if DEBUG:
        debug_messages.append(str(message))


def print_debug_messages():
    if DEBUG and debug_messages:
        print("\n".join(debug_messages))
        debug_messages.clear()


class ShotGridManager:
    def __init__(self, url, script_name, api_key, sudo_login):
        debug_print("Inicializando conexion a ShotGrid")
        try:
            self.sg = shotgun_api3.Shotgun(
                url, script_name=script_name, api_key=api_key, sudo_as_login=sudo_login
            )
            debug_print("Conexion a ShotGrid inicializada exitosamente")
        except Exception as e:
            debug_print(f"Error al inicializar la conexion a ShotGrid: {e}")
            self.sg = None

    def find_shot_and_tasks(self, project_name, shot_code):
        if not self.sg:
            debug_print("Conexion a ShotGrid no esta inicializada")
            return None, None, None
        debug_print(f"Buscando proyecto con nombre: {project_name}")
        try:
            projects = self.sg.find(
                "Project", [["name", "is", project_name]], ["id", "name"]
            )
        except Exception as e:
            debug_print(f"Error buscando proyecto: {e}")
            return None, None, None
        if projects:
            project_id = projects[0]["id"]
            filters = [
                ["project", "is", {"type": "Project", "id": project_id}],
                ["code", "is", shot_code],
            ]
            fields = ["id", "code", "description"]
            shots = self.sg.find("Shot", filters, fields)
            if shots:
                shot_id = shots[0]["id"]
                debug_print(f"Shot encontrado: {shots[0]['code']} (ID: {shot_id})")
                tasks = self.find_tasks_for_shot(shot_id)
                return projects[0], shots[0], tasks
            else:
                debug_print("No se encontro el Shot con el codigo especificado.")
                return None, None, None
        else:
            debug_print("No se encontro el proyecto con el nombre especificado.")
            return None, None, None

    def find_tasks_for_shot(self, shot_id):
        filters = [["entity", "is", {"type": "Shot", "id": shot_id}]]
        fields = ["id", "content", "sg_status_list"]
        return self.sg.find("Task", filters, fields)

    def get_task_assignees(self, task_id):
        if not self.sg:
            debug_print("Conexion a ShotGrid no esta inicializada")
            return []
        try:
            task = self.sg.find_one("Task", [["id", "is", task_id]], ["task_assignees"])
            if task and task["task_assignees"]:
                return task["task_assignees"]
            else:
                debug_print(f"No hay asignados para la tarea {task_id}")
                return []
        except Exception as e:
            debug_print(f"Error al obtener los asignados de la tarea: {e}")
            return []


class WorkerSignals(QObject):
    finished = Signal()
    debug_output = Signal()


class AssigneeWorker(QRunnable):
    def __init__(self, sg_manager, base_name):
        super(AssigneeWorker, self).__init__()
        self.sg_manager = sg_manager
        self.base_name = base_name
        self.signals = WorkerSignals()

    @Slot()
    def run(self):
        try:
            # Extraer datos del base_name igual que en el script de push
            project_name = self.base_name.split("_")[0]
            parts = self.base_name.split("_")
            shot_code = "_".join(parts[:5])
            # Extraer nombre de la tarea
            version_number_str = None
            for part in parts:
                if part.startswith("v") and part[1:].isdigit():
                    version_number_str = part
                    break
            if not version_number_str:
                debug_print(
                    "Error: No se encontro un numero de version valido en el nombre base."
                )
                return
            version_index = parts.index(version_number_str)
            task_name = parts[version_index - 1].lower()
            debug_print(
                f"Buscando shot y tareas para el proyecto: {project_name}, Shot: {shot_code}"
            )
            project, shot, tasks = self.sg_manager.find_shot_and_tasks(
                project_name, shot_code
            )
            if not tasks:
                debug_print("No se encontraron tareas para el shot.")
                return
            # Buscar el task_id correcto
            task_id = None
            for task in tasks:
                if task["content"].lower() == task_name:
                    task_id = task["id"]
                    break
            if not task_id:
                debug_print(f"No se encontro la tarea '{task_name}' para el shot.")
                return
            debug_print(f"Task ID encontrado: {task_id}")
            # Obtener e imprimir los asignados
            assignees = self.sg_manager.get_task_assignees(task_id)
            if assignees:
                for user in assignees:
                    debug_print(
                        f"Asignado: {user.get('name', 'Sin nombre')} (ID: {user.get('id', '-')})"
                    )
            else:
                debug_print("No se encontraron asignados.")
        except Exception as e:
            debug_print(f"Error en el worker: {e}")
        finally:
            self.signals.finished.emit()
            self.signals.debug_output.emit()


def get_env_credentials():
    sg_url = os.getenv("SHOTGRID_URL")
    sg_script_name = os.getenv("SHOTGRID_SCRIPT_NAME")
    sg_api_key = os.getenv("SHOTGRID_API_KEY")
    sg_login = os.getenv("SHOTGRID_LOGIN")
    if not sg_url or not sg_script_name or not sg_api_key or not sg_login:
        debug_print(
            "Las variables de entorno SHOTGRID_URL, SHOTGRID_SCRIPT_NAME, SHOTGRID_API_KEY y SHOTGRID_LOGIN deben estar configuradas."
        )
        return None, None, None, None
    return sg_url, sg_script_name, sg_api_key, sg_login


def print_task_assignees_from_base_name(base_name):
    sg_url, sg_script_name, sg_api_key, sg_login = get_env_credentials()
    if not all([sg_url, sg_script_name, sg_api_key, sg_login]):
        print_debug_messages()
        return
    sg_manager = ShotGridManager(sg_url, sg_script_name, sg_api_key, sg_login)
    worker = AssigneeWorker(sg_manager, base_name)
    worker.signals.debug_output.connect(print_debug_messages)
    QThreadPool.globalInstance().start(worker)


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Uso: python LGA_NKS_Flow_Assignee.py <base_name>")
    else:
        base_name = sys.argv[1]
        print_task_assignees_from_base_name(base_name)
