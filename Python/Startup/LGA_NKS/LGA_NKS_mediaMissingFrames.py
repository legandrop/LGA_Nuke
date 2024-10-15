"""
________________________________________________________________________________

  LGA_NKS_mediaMissingFrames v1.5 | 2024 | Lega  
  Escanea los clips seleccionados en Hiero para secuencias EXR con frames faltantes o corruptos
________________________________________________________________________________

"""

import hiero.core
import hiero.ui
from PySide2.QtWidgets import QApplication, QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem, QHeaderView, QProgressDialog
from PySide2.QtGui import QScreen
from PySide2.QtCore import Qt, QThread, Signal, QTimer
import os
import re
import subprocess
import traceback

class WorkerThread(QThread):
    update_progress = Signal(int)
    update_table = Signal(list)
    finished = Signal()

    def __init__(self, selected_items):
        QThread.__init__(self)
        self.selected_items = selected_items

    def run(self):
        for index, item in enumerate(self.selected_items):
            if isinstance(item, hiero.core.TrackItem):
                try:
                    clip = item.source()
                    file_path = clip.mediaSource().fileinfos()[0].filename()
                    if file_path.endswith('.exr'):
                        clip_info = self.process_clip(clip, file_path)
                        self.update_table.emit(clip_info)
                except Exception as e:
                    print(f"Error procesando clip: {str(e)}")
                    print(traceback.format_exc())
            self.update_progress.emit(index + 1)
        self.finished.emit()

    def process_clip(self, clip, file_path):
        first_frame = int(clip.mediaSource().startTime())
        last_frame = int(clip.mediaSource().startTime() + clip.mediaSource().duration() - 1)
        total_frames = last_frame - first_frame + 1
        
        directory = os.path.dirname(file_path)
        filename_pattern = os.path.basename(file_path)
        filename_pattern = re.sub(r'%0\d+d', r'%d', filename_pattern)
        
        missing_frames, corrupt_frames = self.check_frames(directory, filename_pattern, first_frame, last_frame)
        
        return [file_path, clip.name(), str(first_frame), str(last_frame), str(total_frames),
                ", ".join(map(str, missing_frames)) if missing_frames else "Ninguno",
                ", ".join(map(str, corrupt_frames)) if corrupt_frames else "Ninguno"]

    def check_frames(self, directory, filename_pattern, first_frame, last_frame):
        missing_frames = []
        corrupt_frames = []
        try:
            for frame in range(first_frame, last_frame + 1):
                expected_filename = os.path.join(directory, filename_pattern % frame)
                if not os.path.exists(expected_filename):
                    missing_frames.append(frame)
                elif not self.is_exr_valid(expected_filename):
                    corrupt_frames.append(frame)
        except Exception as e:
            print(f"Error verificando frames: {str(e)}")
            print(traceback.format_exc())
        return missing_frames, corrupt_frames

    def is_exr_valid(self, file_path):
        exrheader_path = os.path.join(os.path.dirname(__file__), 'OpenEXR', 'exrheader.exe')
        try:
            result = subprocess.run([exrheader_path, file_path], capture_output=True, text=True, timeout=0.5)
            return result.returncode == 0 and "ERROR" not in result.stdout
        except subprocess.TimeoutExpired:
            print(f"Timeout al verificar el archivo: {file_path}")
            return False
        except Exception as e:
            print(f"Error al verificar el archivo {file_path}: {str(e)}")
            print(traceback.format_exc())
            return False

class ClipMediaInfo(QWidget):
    def __init__(self, parent=None):
        super(ClipMediaInfo, self).__init__(parent)
        self.initUI()

    def initUI(self):
        try:
            self.setWindowTitle("Información de Clips EXR")
            layout = QVBoxLayout(self)

            self.table = QTableWidget(0, 7, self)
            self.table.setHorizontalHeaderLabels(['Ruta', 'Nombre del Clip', 'IN', 'OUT', 'Frames', 'Frames Faltantes', 'Frames Corruptos'])
            self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
            
            layout.addWidget(self.table)
            self.setLayout(layout)
            
            QTimer.singleShot(0, self.load_data)
        except Exception as e:
            print(f"Error en initUI: {str(e)}")
            print(traceback.format_exc())

    def load_data(self):
        try:
            seq = hiero.ui.activeSequence()
            if seq:
                te = hiero.ui.getTimelineEditor(seq)
                selected_items = te.selection()

                self.progress = QProgressDialog("Verificando clips...", "Cancelar", 0, len(selected_items), self)
                self.progress.setWindowModality(Qt.WindowModal)

                self.worker = WorkerThread(selected_items)
                self.worker.update_progress.connect(self.update_progress)
                self.worker.update_table.connect(self.update_table)
                self.worker.finished.connect(self.on_finished)
                self.worker.start()

        except Exception as e:
            print(f"Error en load_data: {str(e)}")
            print(traceback.format_exc())

    def update_progress(self, value):
        self.progress.setValue(value)
        QApplication.processEvents()  # Permite que la interfaz de usuario se actualice

    def update_table(self, clip_info):
        row_count = self.table.rowCount()
        self.table.insertRow(row_count)
        for col, value in enumerate(clip_info):
            item = QTableWidgetItem(value)
            item.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(row_count, col, item)
        QApplication.processEvents()  # Permite que la interfaz de usuario se actualice

    def on_finished(self):
        self.progress.close()
        self.table.resizeColumnsToContents()
        self.adjust_window_size()

    def adjust_window_size(self):
        try:
            self.table.horizontalHeader().setStretchLastSection(False)
            self.table.resizeColumnsToContents()

            width = self.table.verticalHeader().width() - 40
            for i in range(self.table.columnCount()):
                width += self.table.columnWidth(i) + 20

            screen = QApplication.primaryScreen()
            screen_rect = screen.availableGeometry()
            max_width = screen_rect.width() * 0.8
            final_width = min(width, max_width)

            height = self.table.horizontalHeader().height() + 20
            for i in range(self.table.rowCount()):
                height += self.table.rowHeight(i) + 4

            max_height = screen_rect.height() * 0.8
            final_height = min(height, max_height)

            self.table.horizontalHeader().setStretchLastSection(True)

            self.resize(final_width, final_height)
            self.move((screen_rect.width() - final_width) // 2, (screen_rect.height() - final_height) // 2)
        except Exception as e:
            print(f"Error ajustando el tamaño de la ventana: {str(e)}")
            print(traceback.format_exc())

def showClipMediaInfo():
    try:
        global clipMediaInfoWindow
        clipMediaInfoWindow = ClipMediaInfo()
        clipMediaInfoWindow.show()
    except Exception as e:
        print(f"Error mostrando la ventana de información de clips: {str(e)}")
        print(traceback.format_exc())

def run_script():
    try:
        showClipMediaInfo()
    except Exception as e:
        print(f"Error ejecutando el script: {str(e)}")
        print(traceback.format_exc())

# Registrar la función como una acción en Hiero
action = hiero.ui.createMenuAction("Mostrar Información de Clips EXR", run_script)
hiero.ui.registerAction(action)

# Agregar la acción al menú de Hiero
menuBar = hiero.ui.menuBar()
toolsMenu = menuBar.addMenu("Herramientas")
toolsMenu.addAction(action)

# Ejecutar el script automáticamente al cargar
run_script()
