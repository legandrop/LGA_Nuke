"""
____________________________________________________________________________________

  LGA_NKS_Flow_Assignee_Panel v1.0 - 2025 - Lega Pugliese
  Panel para obtener los asignados de la tarea del clip seleccionado en Flow,
  limpiarlos o sumar asignados a la tarea comp.
____________________________________________________________________________________
"""

import hiero.ui
import hiero.core
import sys
import os
from PySide2.QtWidgets import (
    QWidget,
    QPushButton,
    QGridLayout,
    QMessageBox,
    QSpacerItem,
    QSizePolicy,
)
from PySide2.QtCore import Qt
from PySide2.QtGui import QColor


def debug_print(*message):
    print(*message)


class AssigneePanel(QWidget):
    def __init__(self):
        super(AssigneePanel, self).__init__()
        self.setObjectName("com.lega.FPTAssigneePanel")
        self.setWindowTitle("Assignees")
        self.layout = QGridLayout()
        self.setLayout(self.layout)

        # Definir los botones y sus colores/estilos
        self.buttons = [
            {
                "name": "Get Assignees",
                "color": QColor(46, 119, 212),
                "style": "#202233",
                "callback": self.get_assignees_for_selected_clip,
            },
            {
                "name": "Clear Assignees",
                "color": QColor(36, 76, 25),
                "style": "#202233",
                "callback": self.clear_assignees_for_selected_clip,
            },
            {
                "name": "Lega Pugliese",
                "color": QColor(105, 19, 94),
                "style": "#69135e",
                "callback": lambda: self.assign_assignee_for_selected_clip(
                    "Lega Pugliese"
                ),
            },
            {
                "name": "Sebas Romano",
                "color": QColor(163, 85, 126),
                "style": "#a3557e",
                "callback": lambda: self.assign_assignee_for_selected_clip(
                    "Sebas Romano"
                ),
            },
            {
                "name": "Patricio Barreiro",
                "color": QColor(152, 192, 84),
                "style": "#19335D",
                "callback": lambda: self.assign_assignee_for_selected_clip(
                    "Patricio Barreiro"
                ),
            },
            {
                "name": "Mariel Falco",
                "color": QColor(82, 61, 128),
                "style": "#665621",
                "callback": lambda: self.assign_assignee_for_selected_clip(
                    "Mariel Falco"
                ),
            },
        ]

        self.num_columns = 1  # Inicialmente una columna
        self.create_buttons()

        # Conectar la senal de cambio de tamano del widget al metodo correspondiente
        self.adjust_columns_on_resize()
        self.resizeEvent = self.adjust_columns_on_resize

    def create_buttons(self):
        # Limpiar el layout actual antes de crear nuevos botones
        while self.layout.count():
            item = self.layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

        for index, button_info in enumerate(self.buttons):
            name = button_info["name"]
            style = button_info["style"]
            callback = button_info["callback"]
            button = QPushButton(name)
            # Aplicar solo el color de fondo, sin negrita ni color de texto blanco
            button.setStyleSheet(f"background-color: {style}")
            button.clicked.connect(callback)
            row = index // self.num_columns
            column = index % self.num_columns
            self.layout.addWidget(button, row, column)

        # Calcular el numero de filas usadas
        num_rows = (len(self.buttons) + self.num_columns - 1) // self.num_columns

        # Anadir el espaciador vertical al final
        spacer = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)
        self.layout.addItem(spacer, num_rows, 0, 1, self.num_columns)

    def adjust_columns_on_resize(self, event=None):
        # Obtener el ancho actual del widget
        panel_width = self.width()
        button_width = 100  # Ancho aproximado de cada boton
        min_button_spacing = 10  # Espacio minimo entre botones

        # Calcular el numero de columnas en funcion del ancho del widget
        new_num_columns = max(
            1, (panel_width + min_button_spacing) // (button_width + min_button_spacing)
        )

        if new_num_columns != self.num_columns:
            self.num_columns = new_num_columns
            # Volver a crear los botones con el nuevo numero de columnas
            self.create_buttons()

    def parse_exr_name(self, exr_name):
        # Ajustar el manejo del formato del nombre del archivo EXR
        if "%04d" in exr_name:
            exr_name = exr_name.replace(".%", "_%")  # Reemplazar patron para analisis
        parts = exr_name.split("_")
        if len(parts) < 7 or not parts[-2].startswith("v"):
            raise ValueError(
                f"Nombre del archivo EXR no tiene el formato esperado: {exr_name}"
            )
        base_name = "_".join(parts[:-1])
        return base_name

    def get_assignees_for_selected_clip(self):
        seq = hiero.ui.activeSequence()
        if not seq:
            QMessageBox.warning(self, "No Sequence", "No hay una secuencia activa.")
            return
        te = hiero.ui.getTimelineEditor(seq)
        selected_items = te.selection()
        if not selected_items:
            QMessageBox.warning(
                self, "No Selection", "Selecciona un clip en el timeline."
            )
            return
        for item in selected_items:
            if not isinstance(item, hiero.core.EffectTrackItem):
                if item.source().mediaSource().isMediaPresent():
                    fileinfos = item.source().mediaSource().fileinfos()
                    if not fileinfos:
                        continue
                    file_path = fileinfos[0].filename()
                    exr_name = os.path.basename(file_path)
                    exr_name = exr_name.replace(".%", "_%")
                    try:
                        base_name = self.parse_exr_name(exr_name)
                        self.call_assignee_script(base_name)
                    except Exception as e:
                        QMessageBox.warning(self, "Formato Incorrecto", str(e))
                else:
                    QMessageBox.warning(
                        self, "Media Missing", "El clip no tiene media presente."
                    )

    def call_assignee_script(self, base_name):
        # Importar y ejecutar la funcion del script LGA_NKS_Flow_Assignee.py directamente
        script_path = os.path.join(
            os.path.dirname(__file__), "LGA_NKS_Flow", "LGA_NKS_Flow_Assignee.py"
        )
        if not os.path.exists(script_path):
            QMessageBox.warning(
                self,
                "Script no encontrado",
                f"No se encontró el script en la ruta: {script_path}",
            )
            return
        try:
            import importlib.util

            spec = importlib.util.spec_from_file_location(
                "LGA_NKS_Flow_Assignee", script_path
            )
            if spec is None or spec.loader is None:
                raise ImportError(
                    "No se pudo cargar el módulo LGA_NKS_Flow_Assignee.py"
                )
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            # Llamar a la función principal pasando el base_name
            module.show_task_assignees_from_base_name(base_name)
        except Exception as e:
            QMessageBox.warning(self, "Error al ejecutar", str(e))

    def clear_assignees_for_selected_clip(self):
        seq = hiero.ui.activeSequence()
        if not seq:
            QMessageBox.warning(self, "No Sequence", "No hay una secuencia activa.")
            return
        te = hiero.ui.getTimelineEditor(seq)
        selected_items = te.selection()
        if not selected_items:
            QMessageBox.warning(
                self, "No Selection", "Selecciona un clip en el timeline."
            )
            return
        for item in selected_items:
            if not isinstance(item, hiero.core.EffectTrackItem):
                if item.source().mediaSource().isMediaPresent():
                    fileinfos = item.source().mediaSource().fileinfos()
                    if not fileinfos:
                        continue
                    file_path = fileinfos[0].filename()
                    exr_name = os.path.basename(file_path)
                    exr_name = exr_name.replace(".%", "_%")
                    try:
                        base_name = self.parse_exr_name(exr_name)
                        self.call_clear_assignees_script(base_name)
                    except Exception as e:
                        QMessageBox.warning(self, "Formato Incorrecto", str(e))
                else:
                    QMessageBox.warning(
                        self, "Media Missing", "El clip no tiene media presente."
                    )

    def call_clear_assignees_script(self, base_name):
        script_path = os.path.join(
            os.path.dirname(__file__), "LGA_NKS_Flow", "LGA_NKS_Flow_Clear_Assignees.py"
        )
        if not os.path.exists(script_path):
            QMessageBox.warning(
                self,
                "Script no encontrado",
                f"No se encontró el script en la ruta: {script_path}",
            )
            return
        try:
            import importlib.util

            spec = importlib.util.spec_from_file_location(
                "LGA_NKS_Flow_Clear_Assignees", script_path
            )
            if spec is None or spec.loader is None:
                raise ImportError(
                    "No se pudo cargar el módulo LGA_NKS_Flow_Clear_Assignees.py"
                )
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            # Llamar a la función principal pasando el base_name
            module.clear_task_assignees_from_base_name(base_name)
        except Exception as e:
            QMessageBox.warning(self, "Error al ejecutar", str(e))

    def assign_assignee_for_selected_clip(self, user_name):
        seq = hiero.ui.activeSequence()
        if not seq:
            QMessageBox.warning(self, "No Sequence", "No hay una secuencia activa.")
            return
        te = hiero.ui.getTimelineEditor(seq)
        selected_items = te.selection()
        if not selected_items:
            QMessageBox.warning(
                self, "No Selection", "Selecciona un clip en el timeline."
            )
            return
        for item in selected_items:
            if not isinstance(item, hiero.core.EffectTrackItem):
                if item.source().mediaSource().isMediaPresent():
                    fileinfos = item.source().mediaSource().fileinfos()
                    if not fileinfos:
                        continue
                    file_path = fileinfos[0].filename()
                    exr_name = os.path.basename(file_path)
                    exr_name = exr_name.replace(".%", "_%")
                    try:
                        base_name = self.parse_exr_name(exr_name)
                        self.call_assign_assignee_script(base_name, user_name)
                    except Exception as e:
                        QMessageBox.warning(self, "Formato Incorrecto", str(e))
                else:
                    QMessageBox.warning(
                        self, "Media Missing", "El clip no tiene media presente."
                    )

    def call_assign_assignee_script(self, base_name, user_name):
        script_path = os.path.join(
            os.path.dirname(__file__), "LGA_NKS_Flow", "LGA_NKS_Flow_Assign_Assignee.py"
        )
        if not os.path.exists(script_path):
            QMessageBox.warning(
                self,
                "Script no encontrado",
                f"No se encontró el script en la ruta: {script_path}",
            )
            return
        try:
            import importlib.util

            spec = importlib.util.spec_from_file_location(
                "LGA_NKS_Flow_Assign_Assignee", script_path
            )
            if spec is None or spec.loader is None:
                raise ImportError(
                    "No se pudo cargar el módulo LGA_NKS_Flow_Assign_Assignee.py"
                )
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            # Llamar a la función principal pasando el base_name y el nombre del usuario
            module.assign_assignee_to_task(base_name, user_name)
        except Exception as e:
            QMessageBox.warning(self, "Error al ejecutar", str(e))


# Crear la instancia del panel y agregarlo al windowManager de Hiero
assigneePanel = AssigneePanel()
wm = hiero.ui.windowManager()
wm.addWindow(assigneePanel)
