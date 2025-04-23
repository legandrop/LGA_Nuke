"""
________________________________________________________________

  LGA_NKS_Flow_Assign_Assignee v1.0 - 2025 - Lega Pugliese
  Asigna un usuario a una tarea en ShotGrid (Flow) a partir del base_name y nombre de usuario
________________________________________________________________
"""

import os
import shotgun_api3
from PySide2.QtCore import QRunnable, Slot, QThreadPool, Signal, QObject
from PySide2.QtWidgets import QApplication, QMessageBox

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
        debug_print("Inicializando conexion a ShotGrid para asignar usuario")
        try:
            self.sg = shotgun_api3.Shotgun(
                url, script_name=script_name, api_key=api_key, sudo_as_login=sudo_login
            )
            debug_print("Conexion a ShotGrid inicializada exitosamente")
        except Exception as e:
            debug_print(f"Error al inicializar la conexion a ShotGrid: {e}")
            self.sg = None

    def find_shot_and_task_id(self, project_name, shot_code, task_name_lower):
        if not self.sg:
            debug_print("Conexion a ShotGrid no esta inicializada")
            return None, None
        debug_print(f"Buscando proyecto con nombre: {project_name}")
        try:
            projects = self.sg.find(
                "Project", [["name", "is", project_name]], ["id", "name"]
            )
        except Exception as e:
            debug_print(f"Error buscando proyecto: {e}")
            return None, None
        if not projects:
            debug_print("No se encontro el proyecto con el nombre especificado.")
            return None, None
        project_id = projects[0]["id"]
        filters_shot = [
            ["project", "is", {"type": "Project", "id": project_id}],
            ["code", "is", shot_code],
        ]
        fields_shot = ["id", "code"]
        shots = self.sg.find("Shot", filters_shot, fields_shot)
        if not shots:
            debug_print("No se encontro el Shot con el codigo especificado.")
            return None, None
        shot_id = shots[0]["id"]
        shot_code_found = shots[0]["code"]
        debug_print(f"Shot encontrado: {shot_code_found} (ID: {shot_id})")
        filters_task = [
            ["entity", "is", {"type": "Shot", "id": shot_id}],
            ["content", "is", task_name_lower],
        ]
        fields_task = ["id", "content", "task_assignees"]
        tasks = self.sg.find("Task", filters_task, fields_task)
        if not tasks:
            filters_task_all = [["entity", "is", {"type": "Shot", "id": shot_id}]]
            fields_task_all = ["id", "content", "task_assignees"]
            all_tasks = self.sg.find("Task", filters_task_all, fields_task_all)
            for task in all_tasks:
                if task["content"].lower() == task_name_lower:
                    tasks = [task]
                    break
        if tasks:
            task = tasks[0]
            debug_print(f"Task encontrada: {task['content']} (ID: {task['id']})")
            return shot_code_found, task
        else:
            debug_print(
                f"No se encontro la tarea '{task_name_lower}' para el shot {shot_code_found}."
            )
            return shot_code_found, None

    def find_user_by_name(self, user_name):
        if not self.sg:
            debug_print("Conexion a ShotGrid no esta inicializada")
            return None
        try:
            users = self.sg.find(
                "HumanUser", [["name", "is", user_name]], ["id", "name"]
            )
            if users:
                debug_print(
                    f"Usuario encontrado: {users[0]['name']} (ID: {users[0]['id']})"
                )
                return users[0]
            else:
                debug_print(f"No se encontro el usuario '{user_name}' en ShotGrid.")
                return None
        except Exception as e:
            debug_print(f"Error buscando usuario: {e}")
            return None

    def add_assignee_to_task(self, task_id, current_assignees, user):
        if not self.sg:
            debug_print("Conexion a ShotGrid no esta inicializada")
            return False, "Conexion a ShotGrid no inicializada"
        try:
            # Evitar duplicados
            assignees = current_assignees or []
            if any(u["id"] == user["id"] for u in assignees):
                debug_print(f"El usuario ya es asignado de la tarea.")
                return True, "El usuario ya estaba asignado a la tarea."
            new_assignees = assignees + [user]
            result = self.sg.update("Task", task_id, {"task_assignees": new_assignees})
            if result:
                debug_print(f"Usuario asignado exitosamente a la tarea {task_id}")
                return True, f"Usuario asignado exitosamente."
            else:
                debug_print(f"Fallo al asignar usuario a la tarea {task_id}")
                return False, f"Fallo al actualizar la tarea."
        except Exception as e:
            debug_print(f"Error al asignar usuario: {e}")
            return False, f"Error al asignar usuario: {e}"


class WorkerSignals(QObject):
    finished = Signal(bool, str, str)  # success, shot_name, message
    debug_output = Signal()


class AssignAssigneeWorker(QRunnable):
    def __init__(self, sg_manager, base_name, user_name):
        super(AssignAssigneeWorker, self).__init__()
        self.sg_manager = sg_manager
        self.base_name = base_name
        self.user_name = user_name
        self.signals = WorkerSignals()

    @Slot()
    def run(self):
        success = False
        message = "Error desconocido"
        shot_name = "-"
        try:
            project_name = self.base_name.split("_")[0]
            parts = self.base_name.split("_")
            shot_code = "_".join(parts[:5])
            version_number_str = None
            for part in parts:
                if part.startswith("v") and part[1:].isdigit():
                    version_number_str = part
                    break
            if not version_number_str:
                message = "Error: No se encontro un numero de version valido en el nombre base."
                debug_print(message)
                self.signals.finished.emit(success, shot_name, message)
                self.signals.debug_output.emit()
                return
            version_index = parts.index(version_number_str)
            task_name = parts[version_index - 1].lower()
            debug_print(
                f"Buscando shot y tarea para el proyecto: {project_name}, Shot: {shot_code}, Tarea: {task_name}"
            )
            shot_name_found, task = self.sg_manager.find_shot_and_task_id(
                project_name, shot_code, task_name
            )
            shot_name = shot_name_found if shot_name_found else shot_code
            if not task:
                message = (
                    f"No se encontro la tarea '{task_name}' para el shot {shot_name}."
                )
                debug_print(message)
                self.signals.finished.emit(success, shot_name, message)
                self.signals.debug_output.emit()
                return
            user = self.sg_manager.find_user_by_name(self.user_name)
            if not user:
                message = f"No se encontro el usuario '{self.user_name}' en ShotGrid."
                debug_print(message)
                self.signals.finished.emit(success, shot_name, message)
                self.signals.debug_output.emit()
                return
            current_assignees = task.get("task_assignees", [])
            success, message = self.sg_manager.add_assignee_to_task(
                task["id"], current_assignees, user
            )
        except Exception as e:
            message = f"Error en el worker: {e}"
            debug_print(message)
        finally:
            self.signals.finished.emit(success, shot_name, message)
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


def show_result_dialog(success, shot_name, message, user_name=None):
    app = QApplication.instance() or QApplication([])
    msg = QMessageBox()
    if success:
        msg.setWindowTitle("Asignacion Exitosa")
        msg.setIcon(QMessageBox.Information)
        texto = f"Shot: {shot_name}\n\n{message}"
        if user_name:
            texto += f"\n\nAsignado: {user_name}"
        msg.setText(texto)
    else:
        msg.setWindowTitle("Error en la Asignacion")
        msg.setIcon(QMessageBox.Warning)
        msg.setText(f"Shot: {shot_name}\n\nError: {message}")
    msg.setStandardButtons(QMessageBox.Ok)
    msg.exec_()


def assign_assignee_to_task(base_name, user_name):
    sg_url, sg_script_name, sg_api_key, sg_login = get_env_credentials()
    if not all([sg_url, sg_script_name, sg_api_key, sg_login]):
        show_result_dialog(
            False,
            "-",
            "Faltan credenciales de ShotGrid en variables de entorno.",
            user_name,
        )
        print_debug_messages()
        return
    sg_manager = ShotGridManager(sg_url, sg_script_name, sg_api_key, sg_login)
    worker = AssignAssigneeWorker(sg_manager, base_name, user_name)

    def on_finished(success, shot_name, message):
        show_result_dialog(success, shot_name, message, user_name)

    worker.signals.finished.connect(on_finished)
    worker.signals.debug_output.connect(print_debug_messages)
    QThreadPool.globalInstance().start(worker)


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 3:
        print("Uso: python LGA_NKS_Flow_Assign_Assignee.py <base_name> <user_name>")
    else:
        base_name = sys.argv[1]
        user_name = sys.argv[2]
        assign_assignee_to_task(base_name, user_name)
