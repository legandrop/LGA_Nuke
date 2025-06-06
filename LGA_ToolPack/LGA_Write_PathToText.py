"""
____________________________________________________________________________________

  LGA_Write_PathToText v0.2 | Lega
  Script para mostrar el path de un Write seleccionado, su evaluación y su versión normalizada en una ventana personalizada.
____________________________________________________________________________________
"""

import nuke
import os
from PySide2.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QPushButton
from PySide2.QtCore import Qt

# Variable global para activar o desactivar los prints de depuracion
debug = True  # Cambiar a False para ocultar los mensajes de debug

app = None
window = None


def debug_print(*message):
    if debug:
        print("[LGA_Write_PathToText]", *message)


class PathInfoWindow(QWidget):
    def __init__(self, write_file, evaluated_path, normalized_path):
        super().__init__()
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setWindowTitle("LGA Write PathToText")
        self.setStyleSheet("background-color: #232323; border-radius: 10px;")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(14)

        def add_block(title, value):
            title_label = QLabel(f"<b style='color:#fff;'>{title}</b>")
            title_label.setStyleSheet("font-size:14px;")
            value_label = QLabel(f"<span style='color:#AEAEAE;'>{value}</span>")
            value_label.setStyleSheet("font-size:14px;")
            value_label.setTextInteractionFlags(Qt.TextSelectableByMouse)
            layout.addWidget(title_label)
            layout.addWidget(value_label)

        add_block("Código original:", write_file)
        add_block(
            "Path evaluado:", evaluated_path if evaluated_path else "(No evaluado)"
        )
        add_block(
            "Path normalizado:",
            normalized_path if normalized_path else "(No normalizado)",
        )

        close_btn = QPushButton("Cerrar")
        close_btn.setStyleSheet(
            "background:#333;color:#fff;border-radius:5px;padding:6px 18px;font-size:13px;"
        )
        close_btn.clicked.connect(self.close)
        layout.addWidget(close_btn, alignment=Qt.AlignCenter)

        self.setLayout(layout)
        self.adjustSize()


def main():
    global app, window
    selected_nodes = nuke.selectedNodes()
    if not selected_nodes:
        debug_print("No hay nodos seleccionados. No se hace nada.")
        return
    write_node = None
    for node in selected_nodes:
        if node.Class() == "Write":
            write_node = node
            break
    if not write_node:
        debug_print("No hay ningun nodo Write seleccionado. No se hace nada.")
        return
    write_file = write_node["file"].value()
    evaluated_path = None
    normalized_path = None
    if "[" in write_file and "]" in write_file:
        try:
            evaluated_path = nuke.filename(write_node)
            if evaluated_path is None:
                evaluated_path = ""
            debug_print(f"Path evaluado: {evaluated_path}")
            normalized_path = os.path.normpath(evaluated_path)
            debug_print(f"Path normalizado: {normalized_path}")
        except Exception as e:
            debug_print(f"Error al evaluar el path: {e}")
    app = QApplication.instance() or QApplication([])
    window = PathInfoWindow(write_file, evaluated_path, normalized_path)
    window.show()


# --- Main Execution ---
if __name__ == "__main__":
    main()
