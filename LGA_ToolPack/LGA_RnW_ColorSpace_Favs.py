"""
________________________________________________________________________

  LGA_RnW_ColorSpace_Favs v1.4 | 2024 | Lega
  Tool for applying OCIO color spaces to selected Read and Write nodes
________________________________________________________________________

"""

from PySide2.QtWidgets import (
    QApplication,
    QWidget,
    QVBoxLayout,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QPushButton,
    QHBoxLayout,
)
from PySide2.QtCore import Qt, QRect
from PySide2.QtGui import QCursor, QPalette, QColor
import configparser
import nuke
import os
import shutil


class SelectedNodeInfo(QWidget):
    def __init__(self, selected_nodes, parent=None, initial_color_spaces=None):
        super(SelectedNodeInfo, self).__init__(parent)
        # Cargar color spaces solo si no se pasaron pre-cargados
        self.color_spaces = (
            initial_color_spaces
            if initial_color_spaces is not None
            else self.load_color_spaces()
        )
        self.selected_nodes = selected_nodes
        # Solo inicializar UI si hay color spaces (aunque main ya lo verifica)
        if self.color_spaces:
            self.initUI()
        else:
            # Este caso no debería ocurrir si main funciona, pero por seguridad:
            print("Error interno: __init__ llamado sin color spaces válidos.")
            # Considerar cerrar o no hacer nada
            # self.close()

    def initUI(self):
        self.setWindowFlags(
            Qt.FramelessWindowHint
        )  # Quitar la barra de titulo estandar

        # Verificar los tipos de nodos seleccionados y establecer el titulo apropiado
        node_classes = [node.Class() for node in self.selected_nodes]
        if "Write" in node_classes and "Read" in node_classes:
            self.setWindowTitle(" Input + Output Transform")
            header_label = "Input & Output Transform"
        elif "Write" in node_classes:
            self.setWindowTitle(" Output Transform")
            header_label = "Output Transform"
        elif "Read" in node_classes:
            self.setWindowTitle(" Input Transform")
            header_label = "Input Transform"
        else:
            self.setWindowTitle("Node Information")
            header_label = "Transform"

        layout = QVBoxLayout(self)

        # Crear una barra de titulo personalizada con el titulo y el boton de cierre en la misma linea
        title_bar = QWidget(self)
        title_bar.setFixedHeight(20)  # Ajustar el alto de la barra de titulo
        title_bar.setAutoFillBackground(
            True
        )  # Asegurar que el fondo se llene con el color especificado
        title_bar.setStyleSheet(
            "background-color: #323232;"
        )  # Establecer el color de fondo

        title_bar_layout = QHBoxLayout(title_bar)
        title_bar_layout.setContentsMargins(0, 0, 0, 0)  # Ajustar los margenes a cero

        # Anadir un expansor para centrar el titulo
        title_bar_layout.addStretch(1)

        # Crear el titulo de la ventana
        title_label = QPushButton(self.windowTitle(), self)
        title_label.setStyleSheet(
            "background-color: none; color: white; border: none; font-weight: bold;"
        )
        title_label.setEnabled(False)  # Hacer que el boton no sea clickeable
        title_bar_layout.addWidget(title_label)

        # Anadir otro expansor para centrar el titulo
        title_bar_layout.addStretch(1)

        # Agregar el boton de cierre personalizado al final
        close_button = QPushButton("X", self)
        close_button.setFixedSize(
            20, 20
        )  # Ajustar el tamano de la X para que sea consistente con la altura de la barra
        close_button.setStyleSheet(
            "background-color: none; color: white; border: none;"
        )
        close_button.clicked.connect(self.close)
        title_bar_layout.addWidget(close_button)

        # Mover el boton de cierre al final con espaciado
        title_bar_layout.setSpacing(0)

        layout.addWidget(title_bar)

        # Crear la tabla sin el horizontal header
        self.table = QTableWidget(len(self.color_spaces), 1, self)
        self.table.horizontalHeader().setVisible(
            False
        )  # Ocultar el encabezado horizontal

        # Eliminar numeros de las filas
        self.table.verticalHeader().setVisible(False)

        # Configurar la paleta de la tabla para cambiar el color de seleccion a gris claro
        palette = self.table.palette()
        palette.setColor(QPalette.Highlight, QColor(230, 230, 230))  # Gris claro
        palette.setColor(QPalette.HighlightedText, QColor(Qt.black))
        self.table.setPalette(palette)

        # Configurar el estilo de la tabla
        self.table.setStyleSheet(
            """
            QTableView::item:selected {
                background-color: rgb(230, 230, 230);  # Gris claro
                color: black;
            }
        """
        )

        # Configurar el comportamiento de seleccion para seleccionar filas enteras
        self.table.setSelectionBehavior(QTableWidget.SelectRows)

        # Cargar datos en la tabla
        self.load_data()

        # Conectar el evento de clic de la celda para cambiar el espacio de color
        self.table.cellClicked.connect(self.change_color_space)

        layout.addWidget(self.table)
        self.setLayout(layout)

        # Ajustar el tamano de la ventana y posicionarla en el centro
        self.adjust_window_size()

    def load_color_spaces(self):
        config = configparser.ConfigParser(allow_no_value=True)
        ini_path = None  # Inicializar ini_path a None
        fallback_list = []  # Lista vacía como fallback final si todo falla

        # Definir nombres de archivo INI
        ini_name_appdata = "ColorSpace_Favs.ini"  # Nombre en AppData
        ini_name_local = "LGA_RnW_ColorSpace_Favs.ini"  # Nombre junto al script

        # Definir rutas
        app_data_path = os.getenv("APPDATA")
        local_script_dir = os.path.dirname(os.path.realpath(__file__))
        local_ini_path = os.path.join(local_script_dir, ini_name_local)
        lga_toolpack_dir = None
        ini_path_appdata = None

        if app_data_path:
            lga_toolpack_dir = os.path.join(app_data_path, "LGA", "ToolPack")
            ini_path_appdata = os.path.join(lga_toolpack_dir, ini_name_appdata)

            # 1. Crear carpeta AppData si no existe
            if not os.path.exists(lga_toolpack_dir):
                try:
                    os.makedirs(lga_toolpack_dir)
                    print(f"Carpeta creada en: {lga_toolpack_dir}")
                except OSError as e:
                    print(
                        f"Error al crear la carpeta {lga_toolpack_dir}: {e}. Intentando usar INI local."
                    )
                    # Si falla la creación, intentaremos usar el local más adelante
                    pass

            # 2. Verificar/Copiar INI a AppData (con renombrado)
            if os.path.exists(lga_toolpack_dir):
                # Buscar el archivo con el nombre de AppData
                if not os.path.exists(ini_path_appdata):
                    # Si no existe, buscar el archivo local con su nombre original
                    if os.path.exists(local_ini_path):
                        try:
                            # Copiar desde local_ini_path a ini_path_appdata (renombrando)
                            shutil.copy2(local_ini_path, ini_path_appdata)
                            print(
                                f"Archivo INI copiado desde {ini_name_local} a {ini_path_appdata}"
                            )
                            ini_path = ini_path_appdata  # Usar el INI recién copiado/renombrado
                        except Exception as e:
                            print(
                                f"Error al copiar/renombrar el archivo INI a AppData: {e}. Intentando usar INI local."
                            )
                            pass
                    else:
                        print(
                            f"Error: El archivo INI no existe en AppData ({ini_name_appdata}) y el archivo fuente local ({ini_name_local}) tampoco existe para copiar."
                        )
                else:
                    # Si el INI (con nombre de AppData) ya existe en AppData, esa es la ruta a usar
                    print(
                        f"Usando archivo INI existente en AppData: {ini_path_appdata}"
                    )
                    ini_path = ini_path_appdata
            else:
                print(
                    f"La carpeta {lga_toolpack_dir} no existe y no pudo ser creada. Intentando usar INI local."
                )

        else:
            print(
                "Error: No se pudo obtener la ruta APPDATA. Intentando usar INI local ({ini_name_local})."
            )

        # 3. Intentar usar INI local si no se pudo usar/crear el de AppData
        if ini_path is None:  # Si no tenemos una ruta válida de AppData
            if os.path.exists(local_ini_path):
                print(f"Usando archivo INI local como fallback: {local_ini_path}")
                ini_path = local_ini_path  # Usar el local con su nombre original
            else:
                print(
                    f"Error: No se pudo determinar una ruta válida para el archivo INI (ni AppData [{ini_name_appdata}] ni local [{ini_name_local}])."
                )

        # 4. Leer la configuración desde la ruta INI determinada (si existe)
        if ini_path and os.path.exists(ini_path):
            try:
                print(
                    f"Leyendo configuracion desde: {ini_path}"
                )  # Indicar qué archivo se está leyendo
                config.optionxform = str  # type: ignore # Mantener mayusculas/minusculas
                config.read(ini_path)
                if "ColorSpaces" in config:
                    return [key for key in config["ColorSpaces"]]
                else:
                    print(
                        f"Error: La seccion 'ColorSpaces' no se encuentra en el archivo INI: {ini_path}"
                    )
                    return fallback_list
            except configparser.Error as e:
                print(f"Error al leer el archivo INI {ini_path}: {e}")
                return fallback_list
        else:
            print(
                "Error final: No se pudo encontrar o acceder a un archivo INI válido."
            )
            return fallback_list

    def load_data(self):
        for row, name in enumerate(self.color_spaces):
            node_item = QTableWidgetItem(name)
            self.table.setItem(row, 0, node_item)

        self.table.resizeColumnsToContents()

    def adjust_window_size(self):
        # Desactivar temporalmente el estiramiento de la ultima columna
        self.table.horizontalHeader().setStretchLastSection(False)

        # Ajustar las columnas al contenido
        self.table.resizeColumnsToContents()

        # Calcular el ancho de la ventana basado en el ancho de las columnas y el texto mas ancho
        width = self.table.verticalHeader().width()  # Un poco de relleno para estetica
        for i in range(self.table.columnCount()):
            width += (
                self.table.columnWidth(i) + 50
            )  # Un poco mas de relleno entre columnas

        # Ajustar el ancho adicional basado en el texto mas ancho
        longest_text = max(self.color_spaces, key=len)
        font_metrics = self.table.fontMetrics()
        text_width = (
            font_metrics.horizontalAdvance(longest_text) + 50
        )  # Un poco de relleno adicional
        width = max(width, text_width)

        # Asegurarse de que el ancho no supera el 80% del ancho de pantalla
        screen = QApplication.primaryScreen()
        screen_rect = screen.availableGeometry()
        max_width = screen_rect.width() * 0.8
        final_width = min(width, max_width)

        # Calcular la altura basada en la altura de los headers y las filas
        height = self.table.horizontalHeader().height() + 20
        for i in range(self.table.rowCount()):
            height += self.table.rowHeight(i)

        # Agregar un relleno total de 6 pixeles
        height += 10

        # Incluir la altura de la barra de titulo personalizada
        title_bar_height = 20
        height += title_bar_height

        # Asegurarse de que la altura no supera el 80% del alto de pantalla
        max_height = screen_rect.height() * 0.8
        final_height = min(height, max_height)

        # Reactivar el estiramiento de la ultima columna
        self.table.horizontalHeader().setStretchLastSection(True)

        # Ajustar el tamano de la ventana
        self.resize(final_width, final_height)

        # Obtener la posicion actual del puntero del mouse
        cursor_pos = QCursor.pos()

        # Mover la ventana para que se centre en la posicion actual del puntero del mouse
        self.move(cursor_pos.x() - final_width // 2, cursor_pos.y() - final_height // 2)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.close()
        elif event.key() in (Qt.Key_Return, Qt.Key_Enter):
            current_row = self.table.currentRow()
            if current_row >= 0:
                self.change_color_space(current_row, 0)
        else:
            super(SelectedNodeInfo, self).keyPressEvent(event)

    def change_color_space(self, row, column):
        selected_color_space = self.color_spaces[row]

        # Obtener los nodos seleccionados
        selected_nodes = nuke.selectedNodes()

        if selected_nodes:
            for node in selected_nodes:
                if node.Class() == "Read" or node.Class() == "Write":
                    try:
                        node["colorspace"].setValue(selected_color_space)
                    except Exception as e:
                        print(f"Error al cambiar el espacio de color: {e}")

        # Cerrar la ventana despues de aplicar los cambios
        self.close()


app = None
window = None


def main():
    global app, window
    selected_nodes = nuke.selectedNodes()

    # Verificar si hay algun nodo Read o Write seleccionado
    if any(node.Class() in ["Read", "Write"] for node in selected_nodes):

        # Intentar cargar los color spaces ANTES de crear la ventana principal
        temp_loader = SelectedNodeInfo(
            selected_nodes
        )  # Instancia temporal solo para cargar
        color_spaces = temp_loader.color_spaces  # Acceder a la lista cargada
        del temp_loader  # Eliminar instancia temporal

        if not color_spaces:
            nuke.message(
                "Error: No se pudieron cargar los espacios de color.\nVerifique que el archivo 'LGA_RnW_ColorSpace_Favs.ini' exista en\nAppData\\Roaming\\LGA\\ToolPack o junto al script."
            )
            return  # No continuar si no hay color spaces

        # Si hay color spaces, proceder a crear y mostrar la ventana
        app = QApplication.instance() or QApplication([])
        # Pasar los color_spaces ya cargados para evitar cargarlos de nuevo
        window = SelectedNodeInfo(selected_nodes, initial_color_spaces=color_spaces)
        window.show()
    else:
        nuke.message("Por favor seleccione al menos un nodo Read o Write.")


# Llamar a main() para iniciar la aplicacion
# main()
