import hiero.core
import os
import re
import shotgun_api3
import sys
from PySide2.QtCore import QCoreApplication, Qt
from PySide2.QtWidgets import QWidget, QVBoxLayout, QTextEdit, QApplication

app = None
window = None

class ShotGridManager:
    """Clase para manejar operaciones en ShotGrid."""
    def __init__(self, url, login, password):
        self.sg = shotgun_api3.Shotgun(url, login=login, password=password)

    def find_shot_and_tasks(self, project_name, shot_code):
        """Encuentra el shot en ShotGrid."""
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
                return shots[0]
            else:
                return None
        else:
            return None

    def find_tasks_for_shot(self, shot_id):
        """Encuentra las tareas asociadas a un shot."""
        filters = [['entity', 'is', {'type': 'Shot', 'id': shot_id}]]
        fields = ['id', 'content', 'sg_status_list']
        return self.sg.find("Task", filters, fields)


class HieroOperations:
    """Clase para manejar operaciones en Hiero."""
    def __init__(self, shotgrid_manager):
        self.sg_manager = shotgrid_manager

    def parse_exr_name(self, file_name):
        """Extrae el nombre base del archivo EXR y el numero de version."""
        base_name = re.sub(r'_%04d\.exr$', '', file_name)
        version_match = re.search(r'_v(\d+)', base_name)
        version_number = version_match.group(1) if version_match else 'Unknown'
        return base_name, version_number

    def process_selected_clips(self):
        """Procesa los clips seleccionados en el timeline de Hiero."""
        seq = hiero.ui.activeSequence()
        if seq:
            te = hiero.ui.getTimelineEditor(seq)
            selected_clips = te.selection()
            results = []

            if selected_clips:
                for clip in selected_clips:
                    file_path = clip.source().mediaSource().fileinfos()[0].filename()
                    exr_name = os.path.basename(file_path)
                    base_name, version_number = self.parse_exr_name(exr_name)

                    project_name = base_name.split('_')[0]
                    parts = base_name.split('_')
                    shot_code = '_'.join(parts[:5])

                    # Realizar operacion intensiva en ShotGrid
                    QCoreApplication.processEvents()
                    shot = self.sg_manager.find_shot_and_tasks(project_name, shot_code)
                    
                    QCoreApplication.processEvents()
                    if shot:
                        shot_info = {
                            "shot_code": shot['code'],
                            "description": shot['description']
                        }
                        print(f"Proc Shot encontrado: {shot_info}")  # Print de informacion recopilada
                        results.append(shot_info)
                    QCoreApplication.processEvents()
            #print(f"Resultados finales: {results}")  # Print de los resultados finales
            return results
        else:
            print("No se encontro una secuencia activa en Hiero.")
            return []


class GUIWindow(QWidget):
    def __init__(self, hiero_ops, parent=None):
        super(GUIWindow, self).__init__(parent)
        self.hiero_ops = hiero_ops
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Info")
        layout = QVBoxLayout(self)
        self.text_edit = QTextEdit()
        self.text_edit.setReadOnly(True)
        layout.addWidget(self.text_edit)
        self.setLayout(layout)

    def display_results(self, results):
        """Muestra los resultados recopilados en una ventana independiente."""
        #print(f"Mostrando resultados: {results}")  # Print de los resultados recibidos
        message = """
        <style>
            p { line-height: 1.5; margin: 0; padding: 0; }
            b { color: #CCCC00; }
        </style>
        """
        for result in results:
            description = result['description'] if result['description'] is not None else "No info available"
            message += f"<p><b>{result['shot_code']}</b><br>{description}</p><br>"

        self.text_edit.setHtml(message)
        self.adjustSize()  # Ajusta el tamano del dialogo segun su contenido

        # Obtener el tamano ajustado y sumar pixeles al ancho
        width = self.sizeHint().width() + 10
        height = self.sizeHint().height()

        self.resize(width, height)  # Redimensiona el dialogo con el nuevo ancho

        self.setWindowFlags(self.windowFlags() | Qt.Window)  # Asegurarse de que la ventana sea independiente
        self.show()  # Mostrar la ventana




def main():
    global app, window

    sg_url = os.getenv('SHOTGRID_URL')
    sg_login = os.getenv('SHOTGRID_LOGIN')
    sg_password = os.getenv('SHOTGRID_PASSWORD')

    if not sg_url or not sg_login or not sg_password:
        print("Las variables de entorno SHOTGRID_URL, SHOTGRID_LOGIN y SHOTGRID_PASSWORD deben estar configuradas.")
        return

    sg_manager = ShotGridManager(sg_url, sg_login, sg_password)
    hiero_ops = HieroOperations(sg_manager)

    if not QApplication.instance():
        app = QApplication(sys.argv)
    else:
        app = QApplication.instance()

    window = GUIWindow(hiero_ops)
    results = hiero_ops.process_selected_clips()
    #print(f"Main Resultados obtenidos: {results}")  # Print para verificar los resultados
    window.display_results(results)
    window.show()
    app.exec_()



if __name__ == "__main__":
    main()
