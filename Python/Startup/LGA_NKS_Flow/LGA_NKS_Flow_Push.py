"""
_____________________________________________________________

  LGA_NKS_Flow_Push v3.1 - Lega Pugliese
  Envia a flow nuevos estados de las tasks comps.
  En algunos estados permite enviar un mensaje a la version
  También actualiza la base de datos local para mantenerla sincronizada
_____________________________________________________________

"""

import os
import re
import shotgun_api3
import sqlite3
import platform
from PySide2.QtCore import QRunnable, Slot, QThreadPool, Signal, QObject, Qt
import datetime

# from PySide2.QtCore import QWaitCondition, QMutex
from PySide2.QtWidgets import (
    QApplication,
    QMessageBox,
    QDialog,
    QVBoxLayout,
    QPlainTextEdit,
    QPushButton,
    QLabel,
    QShortcut,
)
from PySide2.QtGui import QKeySequence

# Diccionario de traduccion de estados
status_translation = {
    "Corrections": "corr",
    "Corrs_Lega": "revleg",
    "Rev_Sup": "rev_su",
    "Rev_Lega": "revleg",
    "Rev_Dir": "rev_di",
    "Approved": "pubsh",
    "Rev_Sup_D": "rev_su",
    "Rev_Dir_D": "rev_di",
    "Rev_Hold": "revhld",
}

# Variable global para activar o desactivar los prints // En esta version el Debug se imprime al final del script
DEBUG = True
debug_messages = []


def debug_print(message):
    if DEBUG:
        debug_messages.append(message)


class DBManager:
    """Clase para manejar operaciones con la base de datos SQLite local."""

    def __init__(self):
        # Selecciona la ruta de la base de datos segun el sistema operativo
        if platform.system() == "Windows":
            self.db_path = r"C:/Portable/LGA/PipeSync/cache/pipesync.db"
        elif platform.system() == "Darwin":
            self.db_path = "/Users/leg4/Library/Caches/LGA/PipeSync/pipesync.db"
        else:
            debug_print(f"Sistema operativo no soportado: {platform.system()}")
            self.db_path = None

        if self.db_path and os.path.exists(self.db_path):
            try:
                self.conn = sqlite3.connect(self.db_path)
                self.conn.row_factory = sqlite3.Row
                debug_print(f"Conexión exitosa a la base de datos: {self.db_path}")
            except Exception as e:
                debug_print(f"Error al conectar a la base de datos: {e}")
                self.conn = None
        else:
            debug_print(f"DB file not found at path: {self.db_path}")
            self.conn = None

    def find_project(self, project_name):
        """Busca un proyecto por nombre en la base de datos."""
        if not self.conn:
            debug_print("No hay conexión a la base de datos")
            return None

        try:
            cur = self.conn.cursor()
            cur.execute(
                "SELECT * FROM projects WHERE project_name = ?", (project_name,)
            )
            return cur.fetchone()
        except Exception as e:
            debug_print(f"Error al buscar proyecto {project_name}: {e}")
            return None

    def find_shot(self, project_name, shot_code):
        """Busca un shot por nombre y código en la base de datos."""
        if not self.conn:
            debug_print("No hay conexión a la base de datos")
            return None

        try:
            cur = self.conn.cursor()
            cur.execute(
                """
                SELECT s.* FROM shots s
                JOIN projects p ON s.project_id = p.id
                WHERE p.project_name = ? AND s.shot_name = ?
                """,
                (project_name, shot_code),
            )
            return cur.fetchone()
        except Exception as e:
            debug_print(
                f"Error al buscar shot {shot_code} en proyecto {project_name}: {e}"
            )
            return None

    def find_task(self, shot_id, task_name):
        """Busca una tarea específica por nombre y shot_id."""
        if not self.conn:
            debug_print("No hay conexión a la base de datos")
            return None

        try:
            cur = self.conn.cursor()
            cur.execute(
                """
                SELECT * FROM tasks 
                WHERE shot_id = ? AND LOWER(task_type) = LOWER(?)
                """,
                (shot_id, task_name),
            )
            return cur.fetchone()
        except Exception as e:
            debug_print(
                f"Error al buscar tarea {task_name} para shot_id {shot_id}: {e}"
            )
            return None

    def update_task_status(self, task_id, status):
        """Actualiza el estado de una tarea en la base de datos."""
        if not self.conn:
            debug_print("No hay conexión a la base de datos")
            return False

        try:
            cur = self.conn.cursor()
            cur.execute(
                "UPDATE tasks SET task_status = ? WHERE id = ?", (status, task_id)
            )
            self.conn.commit()
            debug_print(
                f"Estado de la tarea (ID: {task_id}) actualizado a '{status}' en la base de datos local"
            )
            return True
        except Exception as e:
            debug_print(
                f"Error al actualizar el estado de la tarea en la DB local: {e}"
            )
            return False

    def update_version_status(self, task_id, version_number, status):
        """Actualiza el estado de una versión específica en la base de datos."""
        if not self.conn:
            debug_print("No hay conexión a la base de datos")
            return False

        try:
            cur = self.conn.cursor()
            cur.execute(
                "UPDATE versions SET status = ? WHERE task_id = ? AND version_number = ?",
                (status, task_id, version_number),
            )
            self.conn.commit()
            debug_print(
                f"Estado de la versión {version_number} (task_id: {task_id}) actualizado a '{status}' en la base de datos local"
            )
            return True
        except Exception as e:
            debug_print(
                f"Error al actualizar el estado de la versión en la DB local: {e}"
            )
            return False

    def get_user_name(self):
        """Obtiene el nombre del usuario actual desde app_settings."""
        if not self.conn:
            debug_print("No hay conexión a la base de datos para obtener user_name")
            return "Desconocido"
        try:
            cur = self.conn.cursor()
            cur.execute(
                "SELECT setting_value FROM app_settings WHERE setting_key = 'user_name'"
            )
            row = cur.fetchone()
            if row and row[0]:
                return row[0]
            else:
                return "Desconocido"
        except Exception as e:
            debug_print(f"Error al obtener user_name de app_settings: {e}")
            return "Desconocido"

    def add_version_note(self, version_id, content, created_by=None):
        """Añade una nota a una versión en la base de datos."""
        if not self.conn:
            debug_print("No hay conexión a la base de datos")
            return False
        if created_by is None:
            created_by = self.get_user_name()
        # Obtener fecha y hora local con zona horaria en formato igual a Flow
        created_on = (
            datetime.datetime.now().astimezone().isoformat(sep=" ", timespec="seconds")
        )
        try:
            cur = self.conn.cursor()
            cur.execute(
                """
                INSERT INTO version_notes (version_id, content, created_by, created_on) 
                VALUES (?, ?, ?, ?)
                """,
                (version_id, content, created_by, created_on),
            )
            self.conn.commit()
            debug_print(
                f"Nota añadida a la versión (ID: {version_id}) en la base de datos local por {created_by} en {created_on}"
            )
            return True
        except Exception as e:
            debug_print(f"Error al añadir nota a la versión en la DB local: {e}")
            return False

    def find_latest_version(self, task_id):
        """Encuentra la versión más reciente para una tarea específica."""
        if not self.conn:
            debug_print("No hay conexión a la base de datos")
            return None

        try:
            cur = self.conn.cursor()
            cur.execute(
                """
                SELECT * FROM versions 
                WHERE task_id = ? 
                ORDER BY version_number DESC 
                LIMIT 1
                """,
                (task_id,),
            )
            return cur.fetchone()
        except Exception as e:
            debug_print(
                f"Error al buscar la última versión para task_id {task_id}: {e}"
            )
            return None

    def close(self):
        """Cierra la conexión a la base de datos."""
        if hasattr(self, "conn") and self.conn:
            try:
                self.conn.close()
                self.conn = None
                debug_print("Conexión a la base de datos cerrada")
            except Exception as e:
                debug_print(f"Error al cerrar la conexión a la base de datos: {e}")


class InputDialog(QDialog):
    def __init__(self, base_name):
        super(InputDialog, self).__init__()
        self.setWindowTitle("Input Dialog")
        self.layout = QVBoxLayout(self)

        self.label = QLabel(f"Message for {base_name}:")
        self.layout.addWidget(self.label)

        self.text_edit = QPlainTextEdit(self)
        self.text_edit.setFixedHeight(120)  # Ajustar la altura de la caja de texto
        self.layout.addWidget(self.text_edit)

        self.ok_button = QPushButton("OK", self)
        self.ok_button.clicked.connect(self.accept)
        self.layout.addWidget(self.ok_button)

        # Conectar Ctrl+Enter al metodo accept
        shortcut = QShortcut(QKeySequence(Qt.CTRL + Qt.Key_Return), self)
        shortcut.activated.connect(self.accept)

    def get_text(self):
        if self.exec_() == QDialog.Accepted:
            return self.text_edit.toPlainText()
        else:
            return None


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
            debug_print("ShotGrid no inicializado")
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
            debug_print(
                f"Proyecto encontrado: {projects[0]['name']} (ID: {project_id})"
            )
            filters = [
                ["project", "is", {"type": "Project", "id": project_id}],
                ["code", "is", shot_code],
            ]
            fields = ["id", "code", "description"]
            try:
                shots = self.sg.find("Shot", filters, fields)
            except Exception as e:
                debug_print(f"Error buscando shot: {e}")
                return projects[0], None, None
            if shots:
                shot_id = shots[0]["id"]
                debug_print(f"Shot encontrado: {shots[0]['code']} (ID: {shot_id})")
                tasks = self.find_tasks_for_shot(shot_id)
                return projects[0], shots[0], tasks
            else:
                debug_print("No se encontro el Shot con el codigo especificado.")
                return projects[0], None, None
        else:
            debug_print("No se encontro el proyecto con el nombre especificado.")
            return None, None, None

    def find_tasks_for_shot(self, shot_id):
        if not self.sg:
            debug_print("ShotGrid no inicializado")
            return []
        filters = [["entity", "is", {"type": "Shot", "id": shot_id}]]
        fields = ["id", "content", "sg_status_list"]
        try:
            return self.sg.find("Task", filters, fields)
        except Exception as e:
            debug_print(f"Error buscando tareas para shot_id {shot_id}: {e}")
            return []

    def find_highest_version_for_shot(self, shot_id):
        if not self.sg:
            debug_print("ShotGrid no inicializado")
            return None, None, None
        filters = [["entity", "is", {"type": "Shot", "id": shot_id}]]
        fields = ["code", "created_at", "user", "sg_status_list", "description"]
        try:
            versions = self.sg.find("Version", filters, fields)
        except Exception as e:
            debug_print(f"Error buscando versiones para shot_id {shot_id}: {e}")
            return None, None, None
        comp_versions = [v for v in versions if "_comp_" in v["code"].lower()]
        if comp_versions:

            def safe_version_num(v):
                m = re.search(r"_v(\d+)", v["code"])
                return int(m.group(1)) if m else -1

            highest_version = max(comp_versions, key=safe_version_num)
            m = re.search(r"_v(\d+)", highest_version["code"])
            version_number = m.group(1) if m else "0"
            user_id = (
                highest_version["user"]["id"]
                if highest_version.get("user") and highest_version["user"].get("id")
                else None
            )
            return highest_version, version_number, user_id
        return None, None, None

    def update_task_status(self, task_id, new_status):
        if not self.sg:
            debug_print("ShotGrid no inicializado")
            return
        try:
            debug_print(
                f"Actualizando estado de la tarea (ID: {task_id}) a: {new_status}"
            )
            self.sg.update("Task", task_id, {"sg_status_list": new_status})
        except Exception as e:
            debug_print(f"Error al actualizar el estado de la tarea: {e}")

    def update_version_status(self, project_name, shot_code, version_str, new_status):
        if not self.sg:
            debug_print("ShotGrid no inicializado")
            return
        try:
            debug_print(
                f"Actualizando estado de la version para el Shot: {shot_code}, Version: {version_str} a: {new_status}"
            )
            filters = [
                ["project.Project.name", "is", project_name],
                ["entity.Shot.code", "is", shot_code],
                ["code", "contains", version_str],
            ]
            versions = self.sg.find("Version", filters, ["id"])
            for version in versions:
                debug_print(
                    f"Actualizando version (ID: {version['id']}) a estado: {new_status}"
                )
                self.sg.update("Version", version["id"], {"sg_status_list": new_status})
        except Exception as e:
            debug_print(f"Error al actualizar el estado de la version: {e}")

    def get_task_assignee(self, task_id):
        if not self.sg:
            debug_print("ShotGrid no inicializado")
            return None
        try:
            task = self.sg.find_one("Task", [["id", "is", task_id]], ["task_assignees"])
            if task and task["task_assignees"]:
                return task["task_assignees"][0]["id"]
            return None
        except Exception as e:
            debug_print(f"Error al obtener el asignado de la tarea: {e}")
            return None

    def add_comment_to_version(
        self, version_id, project_id, comment, user_id, task_assignee_id, shot_id=None
    ):
        if not self.sg:
            debug_print("ShotGrid no inicializado")
            return
        try:
            debug_print(
                f"Agregando comentario a la version (ID: {version_id}): {comment}"
            )
            addressings_to = [{"type": "HumanUser", "id": user_id}]
            if task_assignee_id and task_assignee_id != user_id:
                addressings_to.append({"type": "HumanUser", "id": task_assignee_id})
            note_data = {
                "project": {"type": "Project", "id": project_id},
                "content": comment,
                "note_links": [
                    {"type": "Version", "id": version_id},
                    {"type": "Shot", "id": shot_id},
                ],
                "addressings_to": addressings_to,
            }
            self.sg.create("Note", note_data)
        except Exception as e:
            debug_print(f"Error al agregar comentario a la version: {e}")


class WorkerSignals(QObject):
    result_ready = Signal(str, int, int)
    task_finished = Signal()
    debug_output = Signal()  # Nueva señal para imprimir logs


class Worker(QRunnable):
    def __init__(self, button_name, base_name, sg_manager, message):
        super(Worker, self).__init__()
        self.button_name = button_name
        self.base_name = base_name
        self.sg_manager = sg_manager
        self.message = message
        self.signals = WorkerSignals()

    @Slot()
    def run(self):
        db_manager = DBManager()  # Crear la conexión en el hilo correcto
        try:
            project_name = self.base_name.split("_")[0]
            parts = self.base_name.split("_")
            shot_code = "_".join(parts[:5])

            version_number_str = None
            for part in parts:
                if part.startswith("v") and part[1:].isdigit():
                    version_number_str = part
                    break

            if version_number_str:
                version_number = int(version_number_str.replace("v", ""))
                debug_print(f"Shot code: {shot_code}, Version number: {version_number}")
            else:
                debug_print(
                    "Error: No se encontro un numero de version valido en el nombre del archivo."
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

            if shot:
                debug_print(f"Shot encontrado: {shot['code']} (ID: {shot['id']})")

                # Realizar las actualizaciones en ShotGrid
                sg_status = status_translation.get(self.button_name, None)
                if sg_status:
                    task_id = None
                    task_assignee_id = None
                    for task in tasks:
                        if task["content"].lower() == task_name:
                            debug_print(
                                f"Actualizando tarea: {task['content']} (ID: {task['id']})"
                            )
                            self.sg_manager.update_task_status(task["id"], sg_status)
                            task_id = task["id"]
                            task_assignee_id = self.sg_manager.get_task_assignee(
                                task_id
                            )

                            # Actualizar en base de datos local si existe
                            db_shot = db_manager.find_shot(project_name, shot_code)
                            if db_shot:
                                db_task = db_manager.find_task(db_shot["id"], task_name)
                                if db_task:
                                    debug_print(
                                        f"Actualizando estado de tarea local (ID: {db_task['id']}) a: {sg_status}"
                                    )
                                    db_manager.update_task_status(
                                        db_task["id"], sg_status
                                    )

                                    # Obtener la última versión para esta tarea
                                    latest_version = db_manager.find_latest_version(
                                        db_task["id"]
                                    )
                                    if latest_version:
                                        # Decidir qué estado aplicar a la versión dependiendo del estado de la tarea
                                        version_status = None
                                        if sg_status == "rev_di" or sg_status == "corr":
                                            version_status = "vwd"
                                        elif sg_status == "rev_su":
                                            version_status = "rev"
                                        elif sg_status == "revleg":
                                            version_status = "unvleg"

                                        if version_status:
                                            debug_print(
                                                f"Actualizando estado de versión local (ID: {latest_version['id']}, version: {latest_version['version_number']}) a: {version_status}"
                                            )
                                            db_manager.update_version_status(
                                                db_task["id"],
                                                latest_version["version_number"],
                                                version_status,
                                            )

                                        # Añadir nota si hay mensaje
                                        if self.message:
                                            debug_print(
                                                f"Añadiendo nota a versión local (ID: {latest_version['id']})"
                                            )
                                            db_manager.add_version_note(
                                                latest_version["id"], self.message
                                            )
                                else:
                                    debug_print(
                                        f"No se encontró la tarea: {task_name} en la base de datos local"
                                    )
                            else:
                                debug_print(
                                    f"No se encontró el shot: {shot_code} en la base de datos local"
                                )
                            break

                    # Buscar la versión más alta para obtener su ID y usuario para los comentarios
                    sg_highest_version, sg_version_number, user_id = (
                        self.sg_manager.find_highest_version_for_shot(shot["id"])
                    )

                    if sg_status == "rev_di" or sg_status == "corr":
                        debug_print(
                            f"Actualizando version del Shot: {shot_code}, Version: {version_number_str} a: vwd"
                        )
                        self.sg_manager.update_version_status(
                            project_name, shot_code, version_number_str, "vwd"
                        )
                        project_id = project["id"]
                        try:
                            if self.message and sg_highest_version:
                                debug_print(
                                    f"Agregando comentario a la version (ID: {sg_highest_version['id']}): {self.message}"
                                )
                                self.sg_manager.add_comment_to_version(
                                    sg_highest_version["id"],
                                    project_id,
                                    self.message,
                                    user_id,
                                    task_assignee_id,
                                    shot["id"],
                                )
                        except Exception as e:
                            debug_print(f"Error while adding comment to version: {e}")
                    elif sg_status == "rev_su":
                        debug_print(
                            f"Actualizando version del Shot: {shot_code}, Version: {version_number_str} a: rev"
                        )
                        self.sg_manager.update_version_status(
                            project_name, shot_code, version_number_str, "rev"
                        )
                    elif sg_status == "revleg":
                        debug_print(
                            f"Actualizando version del Shot: {shot_code}, Version: {version_number_str} a: unvleg"
                        )
                        self.sg_manager.update_version_status(
                            project_name, shot_code, version_number_str, "unvleg"
                        )
                        project_id = project["id"]
                        try:
                            if self.message and sg_highest_version:
                                debug_print(
                                    f"Agregando comentario a la version (ID: {sg_highest_version['id']}): {self.message}"
                                )
                                self.sg_manager.add_comment_to_version(
                                    sg_highest_version["id"],
                                    project_id,
                                    self.message,
                                    user_id,
                                    task_assignee_id,
                                    shot["id"],
                                )
                        except Exception as e:
                            debug_print(f"Error while adding comment to version: {e}")
                else:
                    debug_print(
                        f"No se encontro un estado valido para: {self.button_name}"
                    )
            else:
                debug_print(f"No se encontro el Shot con el codigo: {shot_code}")
        except Exception as e:
            debug_print(f"Exception in Worker.run: {e}")
        finally:
            # Cerrar la conexión a la base de datos
            if db_manager:
                db_manager.close()
            self.signals.task_finished.emit()
            self.signals.debug_output.emit()  # Emitir señal al finalizar


class MessageBoxManager:
    def __init__(self):
        self.message_boxes = []

    def show_warning_message(self, info):
        app = QApplication.instance()
        if app is None:
            app = QApplication([])
        msg_box = QMessageBox()
        msg_box.setTextFormat(Qt.RichText)  # Permite el formato HTML
        msg_box.setText(info)
        msg_box.setWindowTitle("ShotGrid Version Warning")
        msg_box.setWindowModality(Qt.NonModal)
        msg_box.show()
        self.message_boxes.append(msg_box)


def show_version_dialog(base_name, local_version, flow_version):
    """Muestra un diálogo preguntando si se desea continuar cuando la versión local es más antigua."""
    app = QApplication.instance()
    if app is None:
        app = QApplication([])

    msgBox = QMessageBox()
    msgBox.setWindowTitle("Verificación de Versión")
    msgBox.setTextFormat(Qt.RichText)

    # Formatear el nombre base con la versión resaltada
    base_version_highlighted = re.sub(
        r"(_)(v\d+)", r'\1<span style="color: #ff9900;">\2</span>', base_name
    )

    msgBox.setText(
        f"<div style='text-align: center;'>"
        f"<span style='color: #ff9900;'><b>¡Atención!</b></span><br><br>"
        f"La versión que intentas actualizar no es la más reciente:<br><br>"
        f"<span style='font-weight: bold;'>{base_version_highlighted}</span><br><br>"
        f"Versión local: <span style='color: #ff9900;'>v{local_version}</span><br>"
        f"Última versión en Flow: <span style='color: #00ff00;'>v{flow_version}</span><br><br>"
        f"¿Deseas continuar de todos modos?</div>"
    )

    msgBox.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
    msgBox.setDefaultButton(QMessageBox.No)
    msgBox.button(QMessageBox.Yes).setText("Continuar de todos modos")
    msgBox.button(QMessageBox.No).setText("Cancelar")

    response = msgBox.exec_()
    return response == QMessageBox.Yes


def handle_results(info, sg_version_number, version_number):
    if sg_version_number > version_number:
        msg_manager.show_warning_message(info)


def Push_Task_Status(button_name, base_name, update_callback=None):
    global msg_manager

    # Obtener las credenciales del script desde las variables de entorno
    sg_url = os.getenv("SHOTGRID_URL")
    sg_script_name = os.getenv("SHOTGRID_SCRIPT_NAME")
    sg_api_key = os.getenv("SHOTGRID_API_KEY")
    sg_login = os.getenv("SHOTGRID_LOGIN")  # Para sudo_as_login

    if not sg_url or not sg_script_name or not sg_api_key or not sg_login:
        debug_print(
            "Las variables de entorno SHOTGRID_URL, SHOTGRID_SCRIPT_NAME, SHOTGRID_API_KEY y SHOTGRID_LOGIN deben estar configuradas."
        )
        return False  # Retornar False si faltan variables de entorno

    sg_manager = ShotGridManager(sg_url, sg_script_name, sg_api_key, sg_login)

    # Primero solicitar el mensaje al usuario para ciertos estados
    message = None
    sg_status = status_translation.get(button_name, None)
    if sg_status in ["rev_di", "corr", "revleg", "revhld"]:
        app = QApplication.instance()
        if app is None:
            app = QApplication([])

        input_dialog = InputDialog(base_name)
        message = input_dialog.get_text()
        if message is None:
            # Operación cancelada por el usuario al cerrar el diálogo de comentarios
            return False

    # Ahora extraer información del nombre base y verificar versiones
    try:
        project_name = base_name.split("_")[0]
        parts = base_name.split("_")
        shot_code = "_".join(parts[:5])

        # Extraer número de versión
        version_number_str = None
        for part in parts:
            if part.startswith("v") and part[1:].isdigit():
                version_number_str = part
                break

        if not version_number_str:
            debug_print(
                "Error: No se encontró un número de versión válido en el nombre del archivo."
            )
            return False

        local_version = int(version_number_str.replace("v", ""))

        # Verificar versión en Flow ANTES de hacer cualquier cambio
        project, shot, _ = sg_manager.find_shot_and_tasks(project_name, shot_code)
        if not shot:
            debug_print(f"No se encontró el Shot con el código: {shot_code}")
            return False

        sg_highest_version, sg_version_number, _ = (
            sg_manager.find_highest_version_for_shot(shot["id"])
        )
        if not sg_highest_version:
            debug_print(
                f"No se encontró la versión más alta para el Shot (ID: {shot['id']})"
            )
        elif sg_version_number and int(sg_version_number) > local_version:
            # Si la versión en Flow es mayor, mostrar el diálogo y preguntar si desea continuar
            debug_print(
                f"Versión local ({local_version}) es menor que la versión en Flow ({sg_version_number})"
            )
            if not show_version_dialog(base_name, local_version, sg_version_number):
                debug_print(
                    "Usuario canceló la operación debido a diferencia de versiones"
                )
                return False  # El usuario decidió no continuar
    except Exception as e:
        debug_print(f"Error durante la verificación de versiones: {e}")
        # Continuamos con el proceso aunque falle la verificación

    # Una vez que el usuario ha confirmado (o no hay problema de versiones), proceder con las actualizaciones
    if sg_status in ["rev_di", "corr", "revleg", "revhld"]:
        worker = Worker(button_name, base_name, sg_manager, message)
        worker.signals.result_ready.connect(handle_results)
        worker.signals.debug_output.connect(
            lambda: print_debug_messages()
        )  # Conectar nueva señal
        if update_callback:
            worker.signals.task_finished.connect(update_callback)
        QThreadPool.globalInstance().start(worker)
    else:
        worker = Worker(button_name, base_name, sg_manager, None)
        worker.signals.result_ready.connect(handle_results)
        worker.signals.debug_output.connect(lambda: print_debug_messages())
        if update_callback:
            worker.signals.task_finished.connect(update_callback)
        QThreadPool.globalInstance().start(worker)

    return True  # Retornar True indicando que la operación fue iniciada


def print_debug_messages():
    if DEBUG:
        print("\n".join(debug_messages))
        debug_messages.clear()  # Limpiar mensajes después de imprimir


msg_manager = MessageBoxManager()
