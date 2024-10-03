"""
_______________________

  LGA_FlowNo_Panel v1.2
_______________________
"""


import hiero.ui
import hiero.core
import sys
import os
from PySide2.QtWidgets import QWidget, QPushButton, QGridLayout, QSpacerItem, QSizePolicy
from PySide2.QtGui import QColor

class ColorChangeWidget(QWidget):
    def __init__(self):
        super(ColorChangeWidget, self).__init__()

        self.setObjectName("com.lega.NoFPTPanel")
        self.setWindowTitle("NoFPT")

        self.layout = QGridLayout()  # Usamos QGridLayout
        self.setLayout(self.layout)

        # Crear botones y agregarlos al layout con coordenadas especificas
        self.buttons = [
            {"name": "-", "color": None, "style": "#1f1f1f", "action": None},
            {"name": "Clear Tag", "color": None, "style": "#1f1f1f", "action": None},  # Nuevo boton
            {"name": "Corrections", "color": QColor(46, 119, 212), "style": "#2e77d4", "action": "color"},
            {"name": "Corrs_Lega", "color": QColor(105, 19, 94), "style": "#69135e", "action": "color"},
            {"name": "Rev_Sup", "color": QColor(163, 85, 126), "style": "#a3557e", "action": "color"},
            {"name": "Rev_Dir", "color": QColor(199, 155, 183), "style": "#bf95b0", "action": "color"},
            {"name": "Approved", "color": QColor(36, 76, 25), "style": "#244c19", "action": "color"},
            {"name": "Rev_Sup_D", "color": QColor(82, 61, 128), "style": "#523d80", "action": "color"},
            {"name": "Rev_Dir_D", "color": QColor(77, 33, 168), "style": "#4d21a8", "action": "color"},
        ]

        
        self.num_columns = 1  # Inicialmente una columna
        self.create_buttons()

        # Conectar la senal de cambio de tamano del widget al metodo correspondiente
        self.adjust_columns_on_resize()
        self.resizeEvent = self.adjust_columns_on_resize

    def create_button_click_handler(self, color, button_name):
        def button_click_handler(_):
            self.change_clip_color_and_push_status(color, button_name)
        return button_click_handler

    def create_buttons(self):
        for index, button_info in enumerate(self.buttons):
            name = button_info["name"]
            color = button_info["color"]
            style = button_info["style"]
            action = button_info["action"]

            button = QPushButton(name)
            button.setStyleSheet(f"background-color: {style}")
            if action == "color":
                button.clicked.connect(self.create_button_click_handler(color, name))
            elif action == "fpt_pull":
                button.clicked.connect(self.run_FPT_pull)
            elif action == "clear_tag":
                button.clicked.connect(self.run_clear_tag_script)
            row = index // self.num_columns
            column = index % self.num_columns
            self.layout.addWidget(button, row, column)

    def push_task_status(self, button_name, base_name):
        try:
            script_path = os.path.join(os.path.dirname(__file__), 'LGA_FPT-Hiero', 'LGA_FPT-Hiero_Push.py')
            if os.path.exists(script_path):
                import importlib.util
                spec = importlib.util.spec_from_file_location("LGA_FPT_Hiero_Push", script_path)
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                module.Push_Task_Status(button_name, base_name)
            else:
                print(f"Script not found at path: {script_path}")
        except Exception as e:
            print(f"Error during push task status operation: {e}")

    def change_clip_color_and_push_status(self, color, button_name):
        try:
            seq = hiero.ui.activeSequence()
            if seq:
                te = hiero.ui.getTimelineEditor(seq)
                selected_items = te.selection()
                project = hiero.core.projects()[0]
                project.beginUndo("Change Clip Color")
                
                for item in selected_items:
                    if not isinstance(item, hiero.core.EffectTrackItem):
                        bin_item = item.source().binItem()
                        if item.source().mediaSource().isMediaPresent():
                            active_version = bin_item.activeVersion()
                            if active_version:
                                bin_item.setColor(color)
                project.endUndo()
            else:
                print("No active sequence found.")
        except Exception as e:
            print(f"\nError during operation: {e}")



    def adjust_columns_on_resize(self, event=None):
        # Obtener el ancho actual del widget
        panel_width = self.width()
        button_width = 100  # Ancho aproximado de cada boton
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


    def run_clear_tag_script(self):
        project = hiero.core.projects()[0] if hiero.core.projects() else None
        if project:
            project.beginUndo("Run External Script")
            try:
                seq = hiero.ui.activeSequence()
                if seq:
                    te = hiero.ui.getTimelineEditor(seq)
                    selected_items = te.selection()
                    found_valid_clip = False
                    for item in selected_items:
                        if not isinstance(item, hiero.core.EffectTrackItem):
                            found_valid_clip = True
                            break  # Salir del bucle despues de encontrar el primer clip valido
                    
                    if found_valid_clip:
                        # Importar y ejecutar el script de la subcarpeta
                        script_path = os.path.join(os.path.dirname(__file__), 'LGA_FPT-Hiero', 'LGA_H-DeleteClipTags.py')
                        if os.path.exists(script_path):
                            try:
                                import importlib.util
                                spec = importlib.util.spec_from_file_location("LGA_H_DeleteClipTags", script_path)
                                module = importlib.util.module_from_spec(spec)
                                spec.loader.exec_module(module)
                                module.delete_tags_from_selected_clips()
                                #print("Script ejecutado correctamente.")
                            except Exception as e:
                                pass  # Silenciar el error
                        else:
                            pass  # Silenciar el error si el script no se encuentra
            finally:
                project.endUndo()







# Crear la instancia del widget y anadirlo al gestor de ventanas de Hiero
colorChanger = ColorChangeWidget()
wm = hiero.ui.windowManager()
wm.addWindow(colorChanger)
