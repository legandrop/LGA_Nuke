"""
_____________________________________________________

  LGA_NKS_Flow_Shot_info v1.3 - 2024 - Lega Pugliese
  Imprime informacion del shot y las varsiones 
_____________________________________________________

"""

import hiero.core
import os
import re
import json
import sys
from PySide2.QtCore import QCoreApplication, Qt
from PySide2.QtGui import QFontMetrics, QKeySequence
from PySide2.QtWidgets import QWidget, QVBoxLayout, QTextEdit, QApplication, QShortcut


# Variable global para activar o desactivar los prints
DEBUG = False

def debug_print(*message):
    if DEBUG:
        print(*message)


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
        debug_print("Processing selected clips...")
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
                    debug_print(f"Shot found: {shot}")
                    
                    QCoreApplication.processEvents()
                    if shot:
                        task = self.sg_manager.find_task(shot, "comp")
                        debug_print(f"Task found: {task}")
                        task_description = task['task_description'] if task else "No info available"
                        assignee = task['task_assigned_to'] if task else "No assignee"
                        versions = task['versions'] if task else []
                        
                        # Obtener las tres ultimas versiones
                        last_versions = sorted(versions, key=lambda v: v['version_date'], reverse=True)[:3]
                        version_info = [{'version_number': re.search(r'v(\d+)', v['version_number']).group(), 'version_description': v['version_description'] or "No description", 'comments': v['comments']} for v in last_versions]
                        
                        shot_info = {
                            "shot_code": shot['shot_name'],
                            "description": task_description,
                            "assignee": assignee,
                            "versions": version_info
                        }
                        results.append(shot_info)
                    QCoreApplication.processEvents()
            debug_print("Processing completed.")
            return results
        else:
            debug_print("No se encontro una secuencia activa en Hiero.")
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

        # Anadir evento para cerrar la ventana con la tecla ESC
        shortcut = QShortcut(QKeySequence(Qt.Key_Escape), self)
        shortcut.activated.connect(self.close)


    def display_results(self, results):
        """Muestra los resultados recopilados en una ventana independiente."""
        debug_print("Displaying results...")
        message = """
        <style>
            p { line-height: 1.5; margin: 0; padding: 0; }
            b { color: #CCCC00; }
            .assignee { color: #007ACC; font-weight: bold; }
            .version { color: #007ACC; font-weight: bold; }
            .description-title { color: #009688; font-weight: bold; }
            .comment { display: inline; margin-left: 20px; }
            .comment-user { color: #AAAAAA; } /* Nuevo estilo para los nombres de comentaristas */
        </style>
        """
        lines = []
        total_lines = 0

        for result in results:
            debug_print(f"Processing result: {result}")
            description = result['description'] if result['description'] is not None else "Sin descripcion"
            assignee = result['assignee'] if result['assignee'] is not None else "No assignee"
            versions = result['versions']

            shot_code = f"<b>{result['shot_code']}</b>"
            assignee_formatted = f"<span class='assignee'>{assignee}</span>"

            lines.append(f"{shot_code} | {assignee_formatted}")
            message += f"<p>{shot_code} | {assignee_formatted}<br>"
            message += f"<span class='description-title'>Description:</span> {description}<br>"

            total_lines += 3  # Cada resultado tiene al menos 3 lineas
            for version in versions:
                version_number = version['version_number'].split('_')[-1]
                version_line = f"<span class='version'>{version_number}:</span> {version['version_description']}<br>"
                lines.append(version_line)
                message += version_line
                total_lines += 1

                for comment in version['comments']:
                    comment_user = comment['user']
                    comment_text = re.sub(r'\n\n+', '<br>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;', comment['text'])
                    comment_text = re.sub(r'\n', '<br>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;', comment_text)
                    comment_line = f"<b class='comment-user'>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;{comment_user}:</b> {comment_text}"
                    
                    # Usar span en lugar de div para evitar saltos de linea
                    lines.append(comment_line)
                    message += f"<span class='comment'>{comment_line}</span><br>"

                    # Contar el numero de <br> para calcular el numero de lineas
                    br_count = comment_text.count('<br>')
                    total_lines += br_count + 1  # Anadir el numero de <br> mas una linea por el comentario

            message += "</p>"
            total_lines += 4  # Anadir una linea adicional por el espacio del </p> y una mas por margen entre shots

        self.text_edit.setHtml(message.strip())  # Eliminar cualquier espacio en blanco al final
        self.adjustSize()  # Ajusta el tamano del dialogo segun su contenido

        # Encontrar la longitud de la linea mas larga en texto plano
        def strip_html_tags(text):
            clean = re.compile('<.*?>')
            return re.sub(clean, '', text)

        # Dividir las lineas que contienen <br> antes de quitar las etiquetas HTML
        plain_text_lines = []
        for line in lines:
            split_lines = line.split('<br>')
            for split_line in split_lines:
                plain_text_lines.append(strip_html_tags(split_line))

        longest_line = max(plain_text_lines, key=len)
        longest_line_length = len(longest_line)
        debug_print(f"Longest plain text line: {longest_line}")
        debug_print(f"Longest plain text line length (characters): {longest_line_length}")

        # Calcular el ancho basado en la longitud de la linea mas larga en texto plano
        font_metrics = QFontMetrics(self.text_edit.font())
        char_width = font_metrics.averageCharWidth()
        char_height = font_metrics.height()
        debug_print(f"Average character width (pixels): {char_width}")
        width = longest_line_length * char_width + 10  # Sumar un pequeno margen
        debug_print(f"Calculated width (pixels): {width}")
        height = total_lines * char_height + 40  # Sumar un margen adicional para evitar cortes

        # Limitar el tamano maximo de la ventana
        max_width = 1920
        max_height = 1080

        if width > max_width:
            width = max_width
        if height > max_height:
            height = max_height

        self.resize(width, height)  # Redimensiona el dialogo con el nuevo ancho y altura

        self.setWindowFlags(self.windowFlags() | Qt.Window)  # Asegurarse de que la ventana sea independiente
        self.show()  # Mostrar la ventana
        debug_print("Results displayed successfully.")
        debug_print(f"Final window size - Width: {width}, Height: {height}")

def main():
    global app, window

    # Obten el path del script actual
    script_path = os.path.dirname(__file__)

    # Genera la ruta relativa para el archivo JSON
    json_path = os.path.join(script_path, 'Data', 'LGA_NKS_Flow_Downloader_Local.json')

    # Verifica si el archivo JSON existe
    if not os.path.exists(json_path):
        debug_print(f"JSON file not found at path: {json_path}")
        return

    sg_manager = ShotGridManager(json_path)
    hiero_ops = HieroOperations(sg_manager)

    if not QApplication.instance():
        app = QApplication(sys.argv)
    else:
        app = QApplication.instance()

    window = GUIWindow(hiero_ops)
    results = hiero_ops.process_selected_clips()
    debug_print(f"Results: {results}")
    window.display_results(results)
    window.show()
    app.exec_()

if __name__ == "__main__":
    main()
