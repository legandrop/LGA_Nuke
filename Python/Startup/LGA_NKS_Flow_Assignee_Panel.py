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

        # Botón para limpiar asignees
        self.clear_assignees_button = QPushButton("Clear Assignees")
        self.clear_assignees_button.clicked.connect(
            self.clear_assignees_for_selected_clip
        )
        self.layout.addWidget(self.clear_assignees_button, 1, 0)

        # Botón para asignar a Lega Pugliese
        self.assign_lega_button = QPushButton("Lega Pugliese")
        self.assign_lega_button.clicked.connect(
            lambda: self.assign_assignee_for_selected_clip("Lega Pugliese")
        )
        self.layout.addWidget(self.assign_lega_button, 2, 0)

        # Botón para asignar a Sebas Romano
        self.assign_sebas_button = QPushButton("Sebas Romano")
        self.assign_sebas_button.clicked.connect(
            lambda: self.assign_assignee_for_selected_clip("Sebas Romano")
        )
        self.layout.addWidget(self.assign_sebas_button, 3, 0)

        # Botón para asignar a Patricio Barreiro
        self.assign_patricio_button = QPushButton("Patricio Barreiro")
        self.assign_patricio_button.clicked.connect(
            lambda: self.assign_assignee_for_selected_clip("Patricio Barreiro")
        )
        self.layout.addWidget(self.assign_patricio_button, 4, 0)

        # Botón para asignar a Mariel Falco
        self.assign_mariel_button = QPushButton("Mariel Falco")
        self.assign_mariel_button.clicked.connect(
            lambda: self.assign_assignee_for_selected_clip("Mariel Falco")
        )
        self.layout.addWidget(self.assign_mariel_button, 5, 0)

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
