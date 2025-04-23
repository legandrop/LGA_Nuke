"""
________________________________________________________________

  LGA_NKS_Flow_Clear_Assignees v1.0 - 2025 - Lega Pugliese
  Elimina los asignados de una tarea en ShotGrid (Flow) a partir del base_name
________________________________________________________________
"""

import os
import shotgun_api3
from PySide2.QtCore import QRunnable, Slot, QThreadPool, Signal, QObject
from PySide2.QtWidgets import QApplication, QMessageBox

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
        debug_print("Inicializando conexion a ShotGrid para eliminar asignados")
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
            [
                "content",
                "is",
                task_name_lower,
            ],  # ShotGrid parece distinguir mayus/minus en 'is'
        ]
        fields_task = ["id", "content"]
        tasks = self.sg.find("Task", filters_task, fields_task)

        # Fallback si no encuentra por 'is', intenta con 'contains' o iterando
        if not tasks:
            filters_task_all = [["entity", "is", {"type": "Shot", "id": shot_id}]]
            fields_task_all = ["id", "content"]
            all_tasks = self.sg.find("Task", filters_task_all, fields_task_all)
            for task in all_tasks:
                if task["content"].lower() == task_name_lower:
                    tasks = [task]
                    break

        if tasks:
            task_id = tasks[0]["id"]
            debug_print(f"Task encontrada: {tasks[0]['content']} (ID: {task_id})")
            return shot_code_found, task_id
        else:
            debug_print(
                f"No se encontro la tarea '{task_name_lower}' para el shot {shot_code_found}."
            )
            return shot_code_found, None

    def clear_task_assignees(self, task_id):
        if not self.sg:
            debug_print("Conexion a ShotGrid no esta inicializada")
            return False, "Conexion a ShotGrid no inicializada"
        try:
            debug_print(f"Eliminando asignados de la tarea ID: {task_id}")
            result = self.sg.update("Task", task_id, {"task_assignees": []})
            if result:
                debug_print(
                    f"Asignados eliminados exitosamente para la tarea {task_id}"
                )
                return True, f"Asignados eliminados para la tarea ID {task_id}"
            else:
                debug_print(f"Fallo al eliminar asignados para la tarea {task_id}")
                return False, f"Fallo al actualizar la tarea ID {task_id}"
        except Exception as e:
            debug_print(f"Error al eliminar los asignados de la tarea: {e}")
            return False, f"Error al eliminar asignados: {e}"


class WorkerSignals(QObject):
    finished = Signal(bool, str, str)  # success, shot_name, message
    debug_output = Signal()


class ClearAssigneeWorker(QRunnable):
    def __init__(self, sg_manager, base_name):
        super(ClearAssigneeWorker, self).__init__()
        self.sg_manager = sg_manager
        self.base_name = base_name
        self.signals = WorkerSignals()

    @Slot()
    def run(self):
        success = False
        message = "Error desconocido"
        shot_name = "-"
        try:
            # Extraer datos del base_name
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
                message = "Error: No se encontro un numero de version valido en el nombre base."
                debug_print(message)
                self.signals.finished.emit(success, shot_name, message)
                self.signals.debug_output.emit()
                return

            version_index = parts.index(version_number_str)
            task_name = parts[version_index - 1].lower()  # Asegurarse que sea lowercase

            debug_print(
                f"Buscando shot y tarea para el proyecto: {project_name}, Shot: {shot_code}, Tarea: {task_name}"
            )
            shot_name_found, task_id = self.sg_manager.find_shot_and_task_id(
                project_name, shot_code, task_name
            )
            shot_name = (
                shot_name_found if shot_name_found else shot_code
            )  # Usar el encontrado o el extraido

            if not task_id:
                message = (
                    f"No se encontro la tarea '{task_name}' para el shot {shot_name}."
                )
                debug_print(message)
                self.signals.finished.emit(success, shot_name, message)
                self.signals.debug_output.emit()
                return

            debug_print(
                f"Task ID encontrado: {task_id}. Intentando eliminar asignados..."
            )
            success, message = self.sg_manager.clear_task_assignees(task_id)

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


def show_result_dialog(success, shot_name, message):
    """
    Muestra una ventana con el resultado de la operacion.
    """
    app = QApplication.instance() or QApplication([])
    msg = QMessageBox()
    if success:
        msg.setWindowTitle("Operacion Exitosa")
        msg.setIcon(QMessageBox.Information)
        msg.setText(f"Shot: {shot_name}\n\nResultado: {message}")
    else:
        msg.setWindowTitle("Error en la Operacion")
        msg.setIcon(QMessageBox.Warning)
        msg.setText(f"Shot: {shot_name}\n\nError: {message}")
    msg.setStandardButtons(QMessageBox.Ok)
    msg.exec_()


def clear_task_assignees_from_base_name(base_name):
    sg_url, sg_script_name, sg_api_key, sg_login = get_env_credentials()
    if not all([sg_url, sg_script_name, sg_api_key, sg_login]):
        show_result_dialog(
            False, "-", "Faltan credenciales de ShotGrid en variables de entorno."
        )
        print_debug_messages()
        return

    sg_manager = ShotGridManager(sg_url, sg_script_name, sg_api_key, sg_login)
    worker = ClearAssigneeWorker(sg_manager, base_name)

    # Conectar la senal finished al dialogo de resultado
    worker.signals.finished.connect(show_result_dialog)
    # Conectar la senal debug_output para imprimir mensajes de debug
    worker.signals.debug_output.connect(print_debug_messages)

    # Ejecutar el worker en un hilo separado
    QThreadPool.globalInstance().start(worker)


if __name__ == "__main__":
    import sys

    # Asegurarse que QApplication exista si se ejecuta standalone
    app = QApplication.instance()
    if not app:
        app = QApplication(sys.argv)

    if len(sys.argv) < 2:
        print("Uso: python LGA_NKS_Flow_Clear_Assignees.py <base_name>")
    else:
        base_name_arg = sys.argv[1]
        clear_task_assignees_from_base_name(base_name_arg)
        # Mantener la aplicacion corriendo si es necesario para que el dialogo aparezca
        if "__main__" == __name__ and not QApplication.instance():
            sys.exit(app.exec_())  # Solo si no hay instancia previa
