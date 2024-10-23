"""
________________________________________________________________

  LGA_ViewerPanel v1.3 - 2024 - Lega Pugliese
  Panel con herramientas para el viewer y el timeline de Hiero
________________________________________________________________

"""

import hiero.ui
import hiero.core
import os
import subprocess
import socket
from PySide2.QtWidgets import *
from PySide2.QtGui import QIcon, QKeySequence
from PySide2.QtCore import *
from PySide2 import QtWidgets, QtCore

# Variable global para activar o desactivar los prints
DEBUG = False

def debug_print(*message):
    if DEBUG:
        print(*message)

class ViewerPanel(QWidget):
    def __init__(self):
        super(ViewerPanel, self).__init__()

        self.setObjectName("com.lega.ViewerPanel")
        self.setWindowTitle("ViewerTL")
        self.setStyleSheet("QToolTip { color: #ffffff; background-color: #2a2a2a; border: 1px solid white; }")

        self.layout = QGridLayout(self)
        self.setLayout(self.layout)

        # Crear botones y agregarlos al layout
        self.buttons = [
            ("&Viewer | Rec709", self.rec709_viewer, "#311840", "Shift+V", "Shift+V"),
            ("Viewer | 2.35:1 ", self.viewer_235, "#311840"),
            ("Refresh Timeline", self.refresh_timeline, "#4c4350"),
            ("Top Track ", self.top_track, "#4c4350", "Ctrl+Shift+T"),
            ("In Out Editref", self.in_out_editref, "#4d462b", "Ctrl+Shift+U", "Ctrl+Shift+U")
        ]

        self.num_columns = 1  # Inicialmente una columna
        self.create_buttons()

        # Conectar la senal de cambio de tamano del widget al metodo correspondiente
        self.adjust_columns_on_resize()
        self.resizeEvent = self.adjust_columns_on_resize

    def create_buttons(self):
        for index, button_info in enumerate(self.buttons):
            name = button_info[0]
            handler = button_info[1]
            style = button_info[2]
            shortcut = button_info[3] if len(button_info) > 3 else None
            tooltip = button_info[4] if len(button_info) > 4 else None

            button = QPushButton(name)
            button.setStyleSheet(f"background-color: {style}")
            button.clicked.connect(handler)
            if shortcut:
                button.setShortcut(QKeySequence(shortcut))
            if tooltip:
                button.setToolTip(tooltip)

            row = index // self.num_columns
            column = index % self.num_columns
            self.layout.addWidget(button, row, column)

    def adjust_columns_on_resize(self, event=None):
        # Obtener el ancho actual del widget
        panel_width = self.width()
        button_width = 140  # Reducido el ancho aproximado de cada boton
        min_button_spacing = 5  # Reducido el espacio minimo entre botones

        # Calcular el numero de columnas en funcion del ancho del widget
        self.num_columns = max(1, (panel_width + min_button_spacing) // (button_width + min_button_spacing))

        # Limpiar el layout actual y eliminar widgets solo si existen
        while self.layout.count():
            item = self.layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

        # Volver a crear los botones con el nuevo numero de columnas
        self.create_buttons()

        # Calcular el numero de filas usadas
        num_rows = (len(self.buttons) + self.num_columns - 1) // self.num_columns

        # Anadir el espaciador vertical
        spacer = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)
        self.layout.addItem(spacer, num_rows, 0, 1, self.num_columns)

    ##### Rec709 en Viewer
    def rec709_viewer(self):
        try:
            current_viewer = hiero.ui.currentViewer()
            if current_viewer:
                current_viewer.player().setLUT('ACES/Rec.709')
                debug_print("LUT set to ACES/Rec.709")
            else:
                debug_print("No active viewer found.")
        except Exception as e:
            debug_print(f"Error setting Rec.709 LUT: {e}")

    def viewer_235(self):
        try:
            script_path = os.path.join(os.path.dirname(__file__), 'LGA_NKS', 'LGA_NKS_Viewer_235.py')
            if os.path.exists(script_path):
                import importlib.util
                spec = importlib.util.spec_from_file_location("LGA_NKS_Viewer_235", script_path)
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)

                # Llamar a la funcion main del script
                module.main()
                debug_print("Executed LGA_NKS_Viewer_235 script.")
            else:
                debug_print(f"Script not found at path: {script_path}")
        except Exception as e:
            debug_print(f"Error during running Viewer 2.35 script: {e}")

    ###### Refresh timeline
    def refresh_timeline(self):
        try:
            script_path = os.path.join(os.path.dirname(__file__), 'LGA_NKS', 'LGA_NKS_Timeline_Refresh_Wrap.py')
            if os.path.exists(script_path):
                import importlib.util
                spec = importlib.util.spec_from_file_location("LGA_NKS_Timeline_Refresh_Wrap", script_path)
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)

                # Llamar a la función main del script wrapper
                module.main()
                debug_print("Executed Timeline Refresh Wrap script.")
            else:
                debug_print(f"Script not found at path: {script_path}")
        except Exception as e:
            debug_print(f"Error during Timeline Refresh: {e}")

    ###### Top Track
    def top_track(self):
        # Ruta al script dentro de la subcarpeta LGA_NKS
        script_path = os.path.join(os.path.dirname(__file__), 'LGA_NKS', 'LGA_NKS_ScrollTo_TopTrack.py')
        if os.path.exists(script_path):
            import importlib.util
            spec = importlib.util.spec_from_file_location("LGA_NKS_ScrollTo_TopTrack", script_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

            # Llamar a la funcion principal del script
            module.main()
        else:
            debug_print(f"Script not found at path: {script_path}")            

    ###### In Out Editref
    def in_out_editref(self):
        try:
            script_path = os.path.join(os.path.dirname(__file__), 'LGA_NKS', 'LGA_NKS_InOut_Editref.py')
            if os.path.exists(script_path):
                import importlib.util
                spec = importlib.util.spec_from_file_location("LGA_NKS_InOut_Editref", script_path)
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)

                # Llamar a la funcion principal del script
                module.set_in_out_from_edit_ref_track()
                debug_print("Ejecutado LGA_NKS_InOut_Editref script.")
            else:
                debug_print(f"Script no encontrado en la ruta: {script_path}")
        except Exception as e:
            debug_print(f"Error al ejecutar el script In Out Editref: {e}")

# Crear la instancia del widget y anadirlo al gestor de ventanas de Hiero
viewerPanel = ViewerPanel()
wm = hiero.ui.windowManager()
wm.addWindow(viewerPanel)
