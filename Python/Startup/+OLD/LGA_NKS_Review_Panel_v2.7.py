"""
_______________________________________

  LGA_ReviewPanel v2.6 - 2024 - Lega
  Tools panel for Hiero / Nuke Studio
_______________________________________

""" 


import hiero.ui
import hiero.core
import os
import re
import subprocess
import socket
import importlib.util
from PySide2.QtWidgets import *
from PySide2.QtGui import QIcon
from PySide2.QtCore import *
from PySide2 import QtWidgets, QtCore

# Variable global para activar o desactivar los prints
DEBUG = False

def debug_print(*message):
    if DEBUG:
        print(*message)

class ReviewPanel(QWidget):
    def __init__(self):
        super(ReviewPanel, self).__init__()

        self.setObjectName("com.lega.RevtoolPanel")
        self.setWindowTitle("Review")
        self.setStyleSheet("QToolTip { color: #ffffff; background-color: #2a2a2a; border: 1px solid white; }")

        self.layout = QGridLayout(self)  # Usamos QGridLayout en lugar de QVBoxLayout
        self.setLayout(self.layout)

        # Crear botones y agregarlos al layout
        self.buttons = [
            ("Self ReplaceClip", self.execute_SelfReplaceClip, "#0e1f3a"),
            ("ON Clips | OFF v00", self.execute_EnableOrDisableClips, "#0e1f3a"), 
            ("EXR Track Difference", self.execute_ToggleBlendModeForEXRTrack, "#283526"),
            ("Compare Versions", self.execute_CompareVersions, "#273c24"),
            ("Compare OFF", self.execute_CompareVersionsOff, "#273c24"),
            ("Reveal in &Explorer", self.execute_RevealInExplorer, "#321a1a", "Shift+E", "Shift+E"),
            ("Reveal NKS Project", self.execute_RevealNKSProject, "#321a1a"),
            ("Reveal NK Sc&ript", self.execute_RevealNKScript, "#321a1a", "Shift+R", "Shift+R"),
            ("OpenInNuke&X", self.execute_OpenInNukeX, "#493800", "Shift+X", "Shift+X")
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
                button.setShortcut(shortcut)
            if tooltip:
                button.setToolTip(tooltip)

            row = index // self.num_columns
            column = index % self.num_columns
            self.layout.addWidget(button, row, column)

    def adjust_columns_on_resize(self, event=None):
        # Obtener el ancho actual del widget
        panel_width = self.width()
        button_width = 120  # Ancho aproximado de cada boton
        min_button_spacing = 10  # Espacio minimo entre botones

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

    # Metodo generico para ejecutar scripts externos
    def execute_external_script(self, script_name):
        script_path = os.path.join(os.path.dirname(__file__), 'LGA_NKS', script_name)
        if os.path.exists(script_path):
            try:
                spec = importlib.util.spec_from_file_location(script_name[:-3], script_path)
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                module.main()
            except Exception as e:
                debug_print(f"Error ejecutando el script {script_name}: {e}")
        else:
            debug_print(f"Script no encontrado en la ruta: {script_path}")

    # Handlers para cada boton que ejecutan scripts externos
    def execute_SelfReplaceClip(self):
        self.execute_external_script('LGA_NKS_SelfReplaceClip.py')

    def execute_EnableOrDisableClips(self):
        self.execute_external_script('LGA_NKS_ON_Clips_OFF_v00-Clips.py')

    def execute_ToggleBlendModeForEXRTrack(self):
        self.execute_external_script('LGA_NKS_EXRTrack_Difference.py')

    def execute_CompareVersions(self):
        self.execute_external_script('LGA_NKS_Compare_Versions.py')

    def execute_CompareVersionsOff(self):
        self.execute_external_script('LGA_NKS_Compare_Versions_OFF.py')

    def execute_RevealInExplorer(self):
        self.execute_external_script('LGA_NKS_RevealInExplorer.py')

    def execute_RevealNKSProject(self):
        self.execute_external_script('LGA_NKS_RevealNKS_Project.py')

    def execute_RevealNKScript(self):
        self.execute_external_script('LGA_NKS_RevealNK_Script.py')

    def execute_OpenInNukeX(self):
        self.execute_external_script('LGA_NKS_OpenInNukeX.py')


# Crear la instancia del widget y anadirlo al gestor de ventanas de Hiero
reconnectWidget = ReviewPanel()
wm = hiero.ui.windowManager()
wm.addWindow(reconnectWidget)
