"""
________________________________________________________________________________

  LGA_NKS_mediaMissingFrames v1.0 | 2024 | Lega  
  Escanea los clips seleccionados en Hiero para secuencias EXR con frames faltantes
________________________________________________________________________________

"""

import hiero.core
import hiero.ui
from PySide2.QtWidgets import QApplication, QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem, QHeaderView
from PySide2.QtGui import QScreen
from PySide2.QtCore import Qt
import os
import re

class ClipMediaInfo(QWidget):
    def __init__(self, parent=None):
        super(ClipMediaInfo, self).__init__(parent)
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Información de Clips EXR")
        layout = QVBoxLayout(self)

        self.table = QTableWidget(0, 6, self)
        self.table.setHorizontalHeaderLabels(['Ruta', 'Nombre del Clip', 'IN', 'OUT', 'Frames', 'Estado'])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        
        self.load_data()

        layout.addWidget(self.table)
        self.setLayout(layout)
        
        self.adjust_window_size()

    def load_data(self):
        seq = hiero.ui.activeSequence()
        if seq:
            te = hiero.ui.getTimelineEditor(seq)
            selected_items = te.selection()

            for item in selected_items:
                if isinstance(item, hiero.core.TrackItem):
                    clip = item.source()
                    file_path = clip.mediaSource().fileinfos()[0].filename()
                    if file_path.endswith('.exr'):
                        row_count = self.table.rowCount()
                        self.table.insertRow(row_count)
                        
                        self.table.setItem(row_count, 0, QTableWidgetItem(file_path))
                        clip_name_item = QTableWidgetItem(clip.name())
                        clip_name_item.setTextAlignment(Qt.AlignCenter)
                        self.table.setItem(row_count, 1, clip_name_item)
                        
                        # Obtener el rango de frames correcto
                        first_frame = clip.mediaSource().startTime()
                        last_frame = clip.mediaSource().startTime() + clip.mediaSource().duration() - 1
                        in_frame_item = QTableWidgetItem(str(first_frame))
                        in_frame_item.setTextAlignment(Qt.AlignCenter)
                        self.table.setItem(row_count, 2, in_frame_item)
                        out_frame_item = QTableWidgetItem(str(last_frame))
                        out_frame_item.setTextAlignment(Qt.AlignCenter)
                        self.table.setItem(row_count, 3, out_frame_item)
                        
                        total_frames = last_frame - first_frame + 1
                        frames_item = QTableWidgetItem(str(total_frames))
                        frames_item.setTextAlignment(Qt.AlignCenter)
                        self.table.setItem(row_count, 4, frames_item)
                        
                        directory = os.path.dirname(file_path)
                        filename_pattern = os.path.basename(file_path)
                        filename_pattern = re.sub(r'%0\d+d', r'%d', filename_pattern)
                        
                        missing_frames = []
                        for frame in range(int(first_frame), int(last_frame) + 1):
                            expected_filename = os.path.join(directory, filename_pattern % frame)
                            if not os.path.exists(expected_filename):
                                missing_frames.append(str(frame))
                        
                        if missing_frames:
                            if len(missing_frames) == total_frames:
                                status_item = QTableWidgetItem("OFFLINE")
                            else:
                                status_item = QTableWidgetItem("MISSING")
                                print(f"Ruta del archivo: {file_path}")
                                print(f"Faltantes: {', '.join(missing_frames)}")
                        else:
                            status_item = QTableWidgetItem("OK")
                            
                        status_item.setTextAlignment(Qt.AlignCenter)
                        self.table.setItem(row_count, 5, status_item)
                    
            self.table.resizeColumnsToContents()

    def adjust_window_size(self):
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

def showClipMediaInfo():
    global clipMediaInfoWindow
    clipMediaInfoWindow = ClipMediaInfo()
    clipMediaInfoWindow.show()

# Función para ejecutar el script
def run_script():
    showClipMediaInfo()

# Registrar la función como una acción en Hiero
action = hiero.ui.createMenuAction("Mostrar Información de Clips EXR", run_script)
hiero.ui.registerAction(action)

# Agregar la acción al menú de Hiero
menuBar = hiero.ui.menuBar()
toolsMenu = menuBar.addMenu("Herramientas")
toolsMenu.addAction(action)

# Ejecutar el script automáticamente al cargar
run_script()
