import hiero.core
import os
import re
import json
import sys
from PySide2.QtCore import QCoreApplication, Qt
from PySide2.QtWidgets import QWidget, QVBoxLayout, QTextEdit, QApplication

app = None
window = None

class ShotGridManager:
    """Clase para manejar operaciones con datos de un archivo JSON en lugar de ShotGrid."""
    def __init__(self, json_path):
        with open(json_path, 'r', encoding='utf-8') as file:
            self.data = json.load(file)


    def find_project(self, project_name):
        """Busca un proyecto por nombre en el JSON."""
        return next((p for p in self.data['projects'] if p['project_name'] == project_name), None)

    def find_shot(self, project_name, shot_code):
        """Busca un shot por nombre y codigo en el JSON."""
        project = self.find_project(project_name)
        if project:
            return next((s for s in project['shots'] if s['shot_name'] == shot_code), None)
        return None

    def find_task(self, shot, task_name):
        """Busca una tarea especifica por nombre en un shot."""
        return next((t for t in shot['tasks'] if t['task_type'].lower() == task_name.lower()), None)


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

                    # Realizar operacion intensiva en el JSON
                    QCoreApplication.processEvents()
                    shot = self.sg_manager.find_shot(project_name, shot_code)
                    
                    QCoreApplication.processEvents()
                    if shot:
                        task = self.sg_manager.find_task(shot, "comp")
                        task_description = task['task_description'] if task else "No info available"
                        shot_info = {
                            "shot_code": shot['shot_name'],
                            "description": task_description
                        }
                        results.append(shot_info)
                    QCoreApplication.processEvents()
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

    # Obten el path del script actual
    script_path = os.path.dirname(__file__)

    # Genera la ruta relativa para el archivo JSON
    json_path = os.path.join(script_path, 'Data', 'LGA_NKS_Flow_Downloader_Local.json')

    # Verifica si el archivo JSON existe
    if not os.path.exists(json_path):
        print(f"JSON file not found at path: {json_path}")
        return

    sg_manager = ShotGridManager(json_path)
    hiero_ops = HieroOperations(sg_manager)

    if not QApplication.instance():
        app = QApplication(sys.argv)
    else:
        app = QApplication.instance()

    window = GUIWindow(hiero_ops)
    results = hiero_ops.process_selected_clips()
    window.display_results(results)
    window.show()
    app.exec_()


if __name__ == "__main__":
    main()
