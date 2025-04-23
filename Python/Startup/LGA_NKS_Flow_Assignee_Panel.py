"""
____________________________________________________________________________________

  LGA_NKS_Flow_Assignee_Panel v0.1 - 2025 - Lega Pugliese
  Panel para obtener los asignados de la tarea del clip seleccionado en Flow
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
)
from PySide2.QtCore import Qt


def debug_print(*message):
    print(*message)


class AssigneePanel(QWidget):
    def __init__(self):
        super(AssigneePanel, self).__init__()
        self.setObjectName("com.lega.FPTAssigneePanel")
        self.setWindowTitle("Flow Assignee")
        self.layout = QGridLayout()
        self.setLayout(self.layout)

        self.get_assignees_button = QPushButton("Get Assignees")
        self.get_assignees_button.clicked.connect(self.get_assignees_for_selected_clip)
        self.layout.addWidget(self.get_assignees_button, 0, 0)

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
        # Importar y ejecutar la función del script LGA_NKS_Flow_Assignee.py directamente
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


# Crear la instancia del panel y agregarlo al windowManager de Hiero
assigneePanel = AssigneePanel()
wm = hiero.ui.windowManager()
wm.addWindow(assigneePanel)
