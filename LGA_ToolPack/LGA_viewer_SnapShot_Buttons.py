"""
______________________________________________________

  LGA_NKS_SnapSho_Buttons v0.5 - Lega
  Crea botones en el viewer para snapshots
______________________________________________________

"""

import nuke
import os

# Obtener la ruta de los iconos
KS_DIR = os.path.dirname(__file__)
icons_path = os.path.join(KS_DIR, "icons")

try:
    # nuke <11
    import PySide
    from PySide import QtGui
    from PySide import QtCore
    from PySide.QtGui import *
    from PySide.QtCore import *
    from PySide.QtWidgets import *
except:
    # nuke>=11
    import PySide2
    from PySide2 import QtGui
    from PySide2 import QtCore
    from PySide2.QtGui import *
    from PySide2.QtCore import *
    from PySide2.QtWidgets import *


def launch():
    """Funcion principal que inserta los botones en el viewer"""

    class CustomButton(QPushButton):
        def __init__(self, _text, parent=None):
            super(CustomButton, self).__init__()
            self.setText(_text)
            self.setAcceptDrops(True)
            self.mineData = None
            self._parent = parent

        def dragEnterEvent(self, e):
            if e.mimeData().hasText():
                self.mineData = e.mimeData().text()
                self.setFlat(False)
                e.accept()
            else:
                e.ignore()

        def dragLeaveEvent(self, e):
            self.setFlat(True)

        def dropEvent(self, e):
            self._parent.addHotkey(self.mineData)
            self.setFlat(True)

    class SnapShotButton(QDialog):
        """Boton para tomar snapshot"""

        def __init__(self):
            super(SnapShotButton, self).__init__()
            self.generalLayout = QHBoxLayout(self)
            self.generalLayout.setMargin(0)
            self.generalLayout.setSpacing(0)
            self.addShortcutButton = CustomButton("", self)
            self.icon_size = 20
            self.btn_size = 30
            self.qt_icon_size = QtCore.QSize(self.icon_size, self.icon_size)
            self.qt_btn_size = QtCore.QSize(self.btn_size, self.btn_size)

            # Configurar icono y propiedades del boton
            icon_path = os.path.join(icons_path, "snap_camera.png")
            self.addShortcutButton.setIcon(QtGui.QIcon(icon_path))
            self.addShortcutButton.setIconSize(self.qt_icon_size)
            self.addShortcutButton.setFixedSize(self.qt_btn_size)
            self.addShortcutButton.clicked.connect(self.take_snapshot)
            self.addShortcutButton.setFixedWidth(30)
            self.addShortcutButton.setToolTip("Tomar SnapShot del viewer activo")
            self.addShortcutButton.setFlat(True)
            self.generalLayout.addWidget(self.addShortcutButton)

        def take_snapshot(self):
            """Ejecuta la funcion main del script LGA_viewer_SnapShot.py"""
            try:
                # Importar y ejecutar el script de snapshot
                script_path = os.path.join(
                    os.path.dirname(__file__), "LGA_viewer_SnapShot.py"
                )
                if os.path.exists(script_path):
                    import importlib.util

                    spec = importlib.util.spec_from_file_location(
                        "LGA_viewer_SnapShot", script_path
                    )
                    if spec and spec.loader:
                        module = importlib.util.module_from_spec(spec)
                        spec.loader.exec_module(module)

                        # Llamar a la funcion main del script
                        module.main()
                        print("✅ SnapShot ejecutado correctamente")
                    else:
                        nuke.message("Error: No se pudo cargar el modulo de SnapShot")
                else:
                    nuke.message(f"Error: Script no encontrado en {script_path}")
            except Exception as e:
                nuke.message(f"Error al ejecutar SnapShot: {str(e)}")
                print(f"Error en take_snapshot: {e}")

    class SwitchButton(QDialog):
        """Boton para cambiar viewer (funcionalidad futura)"""

        def __init__(self):
            super(SwitchButton, self).__init__()
            self.generalLayout = QHBoxLayout(self)
            self.generalLayout.setMargin(0)
            self.generalLayout.setSpacing(0)
            self.addShortcutButton = CustomButton("", self)
            self.icon_size = 20
            self.btn_size = 30
            self.qt_icon_size = QtCore.QSize(self.icon_size, self.icon_size)
            self.qt_btn_size = QtCore.QSize(self.btn_size, self.btn_size)

            # Configurar icono y propiedades del boton
            icon_path = os.path.join(icons_path, "sanp_picture.png")
            self.addShortcutButton.setIcon(QtGui.QIcon(icon_path))
            self.addShortcutButton.setIconSize(self.qt_icon_size)
            self.addShortcutButton.setFixedSize(self.qt_btn_size)
            self.addShortcutButton.clicked.connect(self.switch_viewer)
            self.addShortcutButton.setFixedWidth(30)
            self.addShortcutButton.setToolTip("Cambiar viewer (funcionalidad futura)")
            self.addShortcutButton.setFlat(True)
            self.generalLayout.addWidget(self.addShortcutButton)

        def switch_viewer(self):
            """Funcionalidad del segundo boton (por implementar)"""
            print("🔄 Switch viewer - Funcionalidad por implementar")
            nuke.message("Switch viewer - Funcionalidad por implementar")

    def find_viewer():
        """Encuentra el widget del viewer activo"""
        nuke.show(nuke.thisNode())
        for widget in QApplication.allWidgets():
            if widget.windowTitle() == nuke.activeViewer().node().name():
                return widget
        return False

    def find_framerange(qtObject):
        """Busca el frameslider y agrega los botones"""
        for c in qtObject.children():
            found = find_framerange(c)
            if found:
                return found
            try:
                tt = c.toolTip().lower()
                if tt.startswith("frameslider range"):
                    # Crear los botones
                    snapshot_btn = SnapShotButton()
                    switch_btn = SwitchButton()

                    # Limpiar botones existentes si los hay
                    wdgets = c.parentWidget().children()
                    if len(wdgets) >= 3:
                        for x in range(3, len(wdgets)):
                            widget_to_remove = c.parentWidget().children()[x]
                            c.parentWidget().layout().removeWidget(widget_to_remove)
                            widget_to_remove.deleteLater()

                    # Agregar los nuevos botones
                    c.parentWidget().layout().addWidget(snapshot_btn)
                    c.parentWidget().layout().addWidget(switch_btn)

                    print("✅ Botones LGA SnapShot agregados al viewer")
                    return c
            except:
                pass
        return None

    # Ejecutar la insercion de botones
    viewer_widget = find_viewer()
    if viewer_widget:
        find_framerange(viewer_widget)
    else:
        print("⚠️ No se pudo encontrar el widget del viewer")
