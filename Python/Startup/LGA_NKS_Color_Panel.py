"""
_______________________

  LGA_colorPanel v1.8
_______________________
"""


import hiero.ui
import hiero.core
from PySide2.QtWidgets import QWidget, QPushButton, QGridLayout, QSpacerItem, QSizePolicy
from PySide2.QtGui import QColor

class ColorChangeWidget(QWidget):
    def __init__(self):
        super(ColorChangeWidget, self).__init__()

        self.setObjectName("com.lega.colorChangePanel")
        self.setWindowTitle("ClipColor")

        self.layout = QGridLayout()  # Usamos QGridLayout
        self.setLayout(self.layout)

        # Crear botones y agregarlos al layout con coordenadas especificas
        self.buttons = [
            ("v_00", QColor(138, 138, 138), "#8a8a8a"),
            ("Plate", QColor(66, 97, 109), "#42616d"),
            ("EditRef", QColor(170, 158, 84), "#aa9e54"),
            ("Reference", QColor(128, 83, 61), "#80533d"),
            ("Error", QColor(194, 82, 82), "#c25252")
        ]
        
        self.num_columns = 1  # Inicialmente una columna
        self.create_buttons()

        # Conectar la senal de cambio de tamano del widget al metodo correspondiente
        self.adjust_columns_on_resize()
        self.resizeEvent = self.adjust_columns_on_resize

    def create_buttons(self):
        for index, (name, color, style) in enumerate(self.buttons):
            button = QPushButton(name)
            button.setStyleSheet(f"background-color: {style}")
            button.clicked.connect(self.create_button_click_handler(color))
            row = index // self.num_columns
            column = index % self.num_columns
            self.layout.addWidget(button, row, column)


    def create_button_click_handler(self, color):
        def button_click_handler(_):
            self.change_clip_color(color)
        return button_click_handler



    def adjust_columns_on_resize(self, event=None):
        # Obtener el ancho actual del widget
        panel_width = self.width()
        button_width = 90  # Ancho aproximado de cada boton
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

    def change_clip_color(self, color):
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
                #print("No active sequence found.")
                pass
        except Exception as e:
            #print(f"\nError during operation: {e}")
            pass

# Crear la instancia del widget y anadirlo al gestor de ventanas de Hiero
colorChanger = ColorChangeWidget()
wm = hiero.ui.windowManager()
wm.addWindow(colorChanger)
