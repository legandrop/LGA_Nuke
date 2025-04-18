"""
_____________________________________________________________

  LGA_NKS_Flow_Push v1.6 - 2024 - Lega Pugliese
  Envia a flow nuevos estados de las tasks comps. 
  En algunos estados permite enviar un mensaje a la version
_____________________________________________________________

"""

import os
import re
import shotgun_api3
from PySide2.QtCore import QRunnable, Slot, QThreadPool, Signal, QObject, Qt
from PySide2.QtWidgets import QApplication, QMessageBox, QDialog, QVBoxLayout, QPlainTextEdit, QPushButton, QLabel, QShortcut
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
    "Rev_Dir_D": "rev_di"
}

# Variable global para activar o desactivar los prints
DEBUG = False

def debug_print(message):
    if DEBUG:
        print(message)


class InputDialog(QDialog):
    def __init__(self, base_name):
        super(InputDialog, self).__init__()
        self.setWindowTitle('Input Dialog')
        self.layout = QVBoxLayout(self)

        self.label = QLabel(f'Message for {base_name}:')
        self.layout.addWidget(self.label)

        self.text_edit = QPlainTextEdit(self)
        #self.text_edit.setPlaceholderText(f'Ctrl+Enter = OK')
        self.text_edit.setFixedHeight(120)  # Ajustar la altura de la caja de texto
        self.layout.addWidget(self.text_edit)

        self.ok_button = QPushButton('OK', self)
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
    def __init__(self, url, login, password):
        self.sg = shotgun_api3.Shotgun(url, login=login, password=password)

    def find_shot_and_tasks(self, project_name, shot_code):
        projects = self.sg.find("Project", [['name', 'is', project_name]], ['id', 'name'])
        if projects:
            project_id = projects[0]['id']
            filters = [
                ['project', 'is', {'type': 'Project', 'id': project_id}],
                ['code', 'is', shot_code]
            ]
            fields = ['id', 'code', 'description']
            shots = self.sg.find("Shot", filters, fields)
            if shots:
                shot_id = shots[0]['id']
                tasks = self.find_tasks_for_shot(shot_id)
                return projects[0], shots[0], tasks  # Return the project info as well
            else:
                return None, None, None
        else:
            return None, None, None

    def find_tasks_for_shot(self, shot_id):
        filters = [['entity', 'is', {'type': 'Shot', 'id': shot_id}]]
        fields = ['id', 'content', 'sg_status_list']
        return self.sg.find("Task", filters, fields)

    def find_highest_version_for_shot(self, shot_id):
        filters = [['entity', 'is', {'type': 'Shot', 'id': shot_id}]]
        fields = ['code', 'created_at', 'user', 'sg_status_list', 'description']
        versions = self.sg.find("Version", filters, fields)
        comp_versions = [v for v in versions if "_comp_" in v['code'].lower()]
        if comp_versions:
            highest_version = max(comp_versions, key=lambda v: int(re.search(r'_v(\d+)', v['code']).group(1)))
            version_number = re.search(r'_v(\d+)', highest_version['code']).group(1)
            return highest_version, version_number
        return None, None

    def update_task_status(self, task_id, new_status):
        try:
            self.sg.update('Task', task_id, {'sg_status_list': new_status})
        except Exception as e:
            debug_print(f"Error updating task status: {e}")

    def update_version_status(self, project_name, shot_code, version_str, new_status):
        try:
            filters = [
                ['project.Project.name', 'is', project_name],
                ['entity.Shot.code', 'is', shot_code],
                ['code', 'contains', version_str]
            ]
            versions = self.sg.find('Version', filters, ['id'])
            for version in versions:
                self.sg.update('Version', version['id'], {'sg_status_list': new_status})
        except Exception as e:
            debug_print(f"Error updating version status: {e}")

    def add_comment_to_version(self, version_id, project_id, comment):
        try:
            self.sg.create('Note', {
                'project': {'type': 'Project', 'id': project_id},
                'note_links': [{'type': 'Version', 'id': version_id}],
                'content': comment,
            })
        except Exception as e:
            debug_print(f"Error adding comment to version: {e}")
            


class WorkerSignals(QObject):
    result_ready = Signal(str, int, int)

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
        project_name = self.base_name.split('_')[0]
        parts = self.base_name.split('_')
        shot_code = '_'.join(parts[:5])
        task_name = parts[5].lower()
        version_number_str = parts[6].lower()
        version_number = int(version_number_str.replace('v', ''))

        project, shot, tasks = self.sg_manager.find_shot_and_tasks(project_name, shot_code)
        if shot:
            sg_highest_version, sg_version_number = self.sg_manager.find_highest_version_for_shot(shot['id'])
            if sg_highest_version:
                base_version_highlighted = re.sub(r'(_)(v\d+)', r'\1<span style="color: yellow;">\2</span>', self.base_name)
                base_name_styled = f'<span style="color: white; font-weight: bold;">{base_version_highlighted}</span>'
                sg_version_highlighted = f'<span style="color: yellow;">v{sg_version_number}</span>'
                info = (f"Warning: Changing task status on outdated version<br><br>"
                        f"{base_name_styled}<br><br>"
                        f"Version in SG: {sg_version_highlighted}")
                self.signals.result_ready.emit(info, int(sg_version_number), version_number)
                
                # Translate the button name to the corresponding SG status
                sg_status = status_translation.get(self.button_name, None)
                if sg_status:
                    # Find the task and update its status
                    for task in tasks:
                        if task['content'].lower() == task_name:
                            self.sg_manager.update_task_status(task['id'], sg_status)
                            break
                    # Update the version status and add comment if the status is "rev_di" or "corr"
                    if sg_status == "rev_di" or sg_status == "corr":
                        self.sg_manager.update_version_status(project_name, shot_code, version_number_str, "vwd")
                        project_id = project['id']
                        try:
                            if self.message:
                                self.sg_manager.add_comment_to_version(sg_highest_version['id'], project_id, self.message)
                        except Exception as e:
                            debug_print(f"Error while adding comment to version: {e}")
                    elif sg_status == "rev_su":
                        self.sg_manager.update_version_status(project_name, shot_code, version_number_str, "rev")
                    elif sg_status == "revleg":
                        self.sg_manager.update_version_status(project_name, shot_code, version_number_str, "unvleg")
                        project_id = project['id']
                        try:
                            if self.message:
                                self.sg_manager.add_comment_to_version(sg_highest_version['id'], project_id, self.message)
                        except Exception as e:
                            debug_print(f"Error while adding comment to version: {e}")

                        

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

def handle_results(info, sg_version_number, version_number):
    if sg_version_number > version_number:
        msg_manager.show_warning_message(info)

def Push_Task_Status(button_name, base_name):
    global msg_manager
    # Obtener el usuario y la contrasena de las variables de entorno
    sg_url = os.getenv('SHOTGRID_URL')
    sg_login = os.getenv('SHOTGRID_LOGIN')
    sg_password = os.getenv('SHOTGRID_PASSWORD')

    if not sg_url or not sg_login or not sg_password:
        debug_print("Las variables de entorno SHOTGRID_URL, SHOTGRID_LOGIN y SHOTGRID_PASSWORD deben estar configuradas.")
        return

    sg_manager = ShotGridManager(sg_url, sg_login, sg_password)

    # Verificar si el boton presionado es "Rev_Dir" o "Corrections"
    sg_status = status_translation.get(button_name, None)
    if sg_status in ["rev_di", "corr", "revleg"]:
        # Abrir la ventana de entrada de texto antes de iniciar el thread
        app = QApplication.instance()
        if app is None:
            app = QApplication([])

        input_dialog = InputDialog(base_name)  # Pasa base_name aqui
        message = input_dialog.get_text()
        if message is not None:
            worker = Worker(button_name, base_name, sg_manager, message)
            worker.signals.result_ready.connect(handle_results)
            QThreadPool.globalInstance().start(worker)
    else:
        # Si no es "Rev_Dir" o "Corrections", continuar sin abrir la ventana de entrada de texto
        worker = Worker(button_name, base_name, sg_manager, None)
        worker.signals.result_ready.connect(handle_results)
        QThreadPool.globalInstance().start(worker)




# Crear una instancia de MessageBoxManager globalmente para gestionar los cuadros de mensaje
msg_manager = MessageBoxManager()
                                                  