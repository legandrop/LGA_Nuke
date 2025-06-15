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
    import PySide.QtGui as QtGui
    import PySide.QtCore as QtCore
    import PySide.QtWidgets as QtWidgets
    from PySide.QtGui import QImage, QClipboard, QIcon
    from PySide.QtWidgets import QApplication, QPushButton, QDialog, QHBoxLayout
except:
    # nuke>=11
    import PySide2.QtGui as QtGui
    import PySide2.QtCore as QtCore
    import PySide2.QtWidgets as QtWidgets
    from PySide2.QtGui import QImage, QClipboard, QIcon
    from PySide2.QtWidgets import QApplication, QPushButton, QDialog, QHBoxLayout


def launch():
    """Funcion principal que inserta los botones en el viewer"""

    class CustomButton(QPushButton):
        def __init__(self, _text, parent=None):
            super(CustomButton, self).__init__()
            self.setText(_text)
            self.setAcceptDrops(True)
            self.mineData = None
            self._parent = parent

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
            """Ejecuta la funcion take_snapshot del script LGA_viewer_SnapShot.py"""
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

                        # Llamar a la funcion take_snapshot del script
                        module.take_snapshot()
                    else:
                        nuke.message("Error: No se pudo cargar el modulo de SnapShot")
                else:
                    nuke.message(f"Error: Script no encontrado en {script_path}")
            except Exception as e:
                nuke.message(f"Error al ejecutar SnapShot: {str(e)}")
                print(f"Error en take_snapshot: {e}")

    class SwitchButton(QDialog):
        """Boton para mostrar snapshot"""

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
            self.addShortcutButton.clicked.connect(self.show_snapshot)
            self.addShortcutButton.setFixedWidth(30)
            self.addShortcutButton.setToolTip("Mostrar ultimo SnapShot tomado")
            self.addShortcutButton.setFlat(True)
            self.generalLayout.addWidget(self.addShortcutButton)

        def show_snapshot(self):
            """Ejecuta la funcion show_snapshot del script LGA_viewer_SnapShot.py"""
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

                        # Llamar a la funcion show_snapshot del script
                        module.show_snapshot()
                    else:
                        nuke.message("Error: No se pudo cargar el modulo de SnapShot")
                else:
                    nuke.message(f"Error: Script no encontrado en {script_path}")
            except Exception as e:
                nuke.message(f"Error al mostrar SnapShot: {str(e)}")
                print(f"Error en show_snapshot: {e}")

    class HoldTestButton(QDialog):
        """Botón de test hold (con mismo icono de snapshot)"""

        def __init__(self):
            super(HoldTestButton, self).__init__()
            self.generalLayout = QHBoxLayout(self)
            self.generalLayout.setMargin(0)
            self.generalLayout.setSpacing(0)
            self.addShortcutButton = CustomButton("", self)
            self.icon_size = 20
            self.btn_size = 30
            self.qt_icon_size = QtCore.QSize(self.icon_size, self.icon_size)
            self.qt_btn_size = QtCore.QSize(self.btn_size, self.btn_size)

            # Usar el mismo icono que el de snapshot
            icon_path = os.path.join(icons_path, "sanp_picture.png")
            self.addShortcutButton.setIcon(QtGui.QIcon(icon_path))
            self.addShortcutButton.setIconSize(self.qt_icon_size)
            self.addShortcutButton.setFixedSize(self.qt_btn_size)
            self.addShortcutButton.setFixedWidth(30)
            self.addShortcutButton.setToolTip("Test Hold Button - Mantener presionado")
            self.addShortcutButton.setFlat(True)
            self.generalLayout.addWidget(self.addShortcutButton)

            # Conectar eventos de press y release
            self.addShortcutButton.pressed.connect(self.on_pressed)
            self.addShortcutButton.released.connect(self.on_released)

        def on_pressed(self):
            """Se ejecuta cuando se presiona el boton"""
            print("🔽 Boton presionado - creando nodo NoOp")
            self.call_test_hold(start=True)

        def on_released(self):
            """Se ejecuta cuando se suelta el boton"""
            print("🔼 Boton liberado - eliminando nodo NoOp")
            self.call_test_hold(start=False)

        def call_test_hold(self, start):
            """Llama a la funcion test_hold del script LGA_viewer_SnapShot.py"""
            try:
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
                        module.test_hold(start)
                    else:
                        print("Error: No se pudo cargar el módulo SnapShot")
                else:
                    print(f"Error: Script no encontrado en {script_path}")
            except Exception as e:
                print(f"Error al ejecutar test_hold: {str(e)}")

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
                    # Crear los tres botones
                    snapshot_btn = SnapShotButton()
                    switch_btn = SwitchButton()
                    hold_test_btn = HoldTestButton()

                    # Limpiar botones existentes si los hay
                    wdgets = c.parentWidget().children()
                    if len(wdgets) >= 3:
                        for x in range(3, len(wdgets)):
                            widget_to_remove = c.parentWidget().children()[x]
                            c.parentWidget().layout().removeWidget(widget_to_remove)
                            widget_to_remove.deleteLater()

                    # Agregar los tres botones al layout
                    c.parentWidget().layout().addWidget(snapshot_btn)
                    c.parentWidget().layout().addWidget(switch_btn)
                    c.parentWidget().layout().addWidget(hold_test_btn)

                    print(
                        "✅ Botones LGA SnapShot agregados al viewer (incluyendo Hold Test)"
                    )
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
