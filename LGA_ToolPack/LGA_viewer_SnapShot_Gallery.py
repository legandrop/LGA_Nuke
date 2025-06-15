"""
___________________________________________________________________________________

  LGA_viewer_SnapShot_Gallery v0.01 - Lega
  Crea una ventana que muestra los snapshots guardados en la carpeta de snapshots
___________________________________________________________________________________

"""

import nuke
import os
from PySide2.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QPushButton
from PySide2.QtCore import Qt

# Variable global para activar o desactivar los prints de depuracion
debug = False  # Cambiar a False para ocultar los mensajes de debug

app = None
window = None


def debug_print(*message):
    if debug:
        print("[LGA_viewer_SnapShot_Gallery]", *message)


class SnapshotGalleryWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setWindowTitle("LGA SnapShot Gallery")
        self.setStyleSheet("background-color: #232323; border-radius: 10px;")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(14)

        def add_block(title, value, rich=False):
            block_layout = QVBoxLayout()
            block_layout.setSpacing(2)  # Espacio reducido entre título y valor
            block_layout.setContentsMargins(0, 0, 0, 0)
            title_label = QLabel(f"<b style='color:#cccccc;'>{title}</b>")
            title_label.setStyleSheet("font-size:14px;")
            if rich:
                value_label = QLabel(value)
            else:
                value_label = QLabel(f"<span style='color:#AEAEAE;'>{value}</span>")
            value_label.setStyleSheet("font-size:13px;")
            value_label.setTextInteractionFlags(Qt.TextSelectableByMouse)
            block_layout.addWidget(title_label)
            block_layout.addWidget(value_label)
            layout.addLayout(block_layout)

        # Obtener la carpeta de snapshots
        gallery_path = get_gallery_path()

        add_block("Gallery Path:", gallery_path if gallery_path else "(No encontrada)")
        add_block("Status:", "En desarrollo - Próximamente galería completa")
        add_block("Info:", "Esta ventana mostrará los snapshots guardados")

        self.setLayout(layout)
        self.adjustSize()


def get_gallery_path():
    """Obtiene la ruta de la carpeta snapshot_gallery"""
    try:
        script_dir = os.path.dirname(__file__)
        gallery_path = os.path.join(script_dir, "snapshot_gallery")
        return gallery_path
    except Exception as e:
        debug_print(f"Error al obtener gallery path: {e}")
        return None


def open_snapshot_gallery():
    """Función principal que abre la ventana de galería de snapshots"""
    global app, window

    debug_print("Abriendo galería de snapshots...")

    app = QApplication.instance() or QApplication([])
    window = SnapshotGalleryWindow()
    window.show()


# --- Main Execution ---
if __name__ == "__main__":
    open_snapshot_gallery()
