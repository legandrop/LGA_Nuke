"""
___________________________________________________________________________________

  LGA_viewer_SnapShot_Gallery v0.02 - Lega
  Crea una ventana que muestra los snapshots guardados organizados por proyecto
  con thumbnails redimensionables
___________________________________________________________________________________

"""

import nuke
import os
import glob
from PySide2.QtWidgets import (
    QApplication,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QScrollArea,
    QFrame,
    QSlider,
    QToolBar,
    QSizePolicy,
)
from PySide2.QtCore import Qt, QSize, Signal
from PySide2.QtGui import QPixmap, QFont, QCursor

# Variable global para activar o desactivar los prints de depuracion
debug = False  # Cambiar a False para ocultar los mensajes de debug

# Variables para personalizar el slider
SLIDER_BAR_WIDTH = 100  # Ancho de la barra del slider
SLIDER_BAR_HEIGHT = 4  # Alto de la barra del slider
SLIDER_HANDLE_SIZE = 9  # Diametro de la bolita del slider

app = None
window = None


def debug_print(*message):
    if debug:
        print("[LGA_viewer_SnapShot_Gallery]", *message)


class ThumbnailWidget(QLabel):
    """Widget personalizado para mostrar un thumbnail"""

    def __init__(self, image_path, size=150):
        super().__init__()
        self.image_path = image_path
        self.original_pixmap = None
        self.load_image()
        self.update_size(size)
        self.setAlignment(Qt.AlignCenter)
        self.setStyleSheet(
            """
            QLabel {
                border: 0px
                background-color: #2a2a2a;
                margin: 2px;
            }
            QLabel:hover {
                border: 0px
            }
        """
        )

    def load_image(self):
        """Carga la imagen original"""
        try:
            self.original_pixmap = QPixmap(self.image_path)
            if self.original_pixmap.isNull():
                debug_print(f"No se pudo cargar la imagen: {self.image_path}")
                # Crear un pixmap de placeholder
                self.original_pixmap = QPixmap(150, 100)
                self.original_pixmap.fill(Qt.gray)
        except Exception as e:
            debug_print(f"Error al cargar imagen {self.image_path}: {e}")
            self.original_pixmap = QPixmap(150, 100)
            self.original_pixmap.fill(Qt.gray)

    def update_size(self, width):
        """Actualiza el tamaño del thumbnail manteniendo la relación de aspecto"""
        if self.original_pixmap and not self.original_pixmap.isNull():
            scaled_pixmap = self.original_pixmap.scaledToWidth(
                width, Qt.SmoothTransformation
            )
            self.setPixmap(scaled_pixmap)
            self.setFixedSize(scaled_pixmap.size())


class ClickableLabel(QLabel):
    """Label clickeable para el titulo de las carpetas"""

    clicked = Signal()

    def __init__(self, text):
        super().__init__(text)
        self.setCursor(QCursor(Qt.PointingHandCursor))

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.clicked.emit()
        super().mousePressEvent(event)


class ProjectFolderWidget(QFrame):
    """Widget que contiene los thumbnails de un proyecto"""

    def __init__(self, project_name, image_paths, thumbnail_size=150):
        super().__init__()
        self.project_name = project_name
        self.image_paths = image_paths
        self.thumbnails = []
        self.thumbnail_size = thumbnail_size
        self.is_expanded = True
        self.thumbnails_widget = None
        self.arrow_label = None

        self.setFrameStyle(QFrame.Box)
        self.setStyleSheet(
            """
            QFrame {
                border: 0px solid #444444;
                border-radius: 2px;
                background-color: #1d1d1d;
                margin: 0px;
                padding: 0px;
            }
        """
        )

        self.setup_ui()

    def setup_ui(self):
        """Configura la interfaz del widget del proyecto"""
        layout = QVBoxLayout(self)
        layout.setSpacing(10)

        # Header con titulo y flecha
        header_layout = QHBoxLayout()
        header_layout.setSpacing(5)
        header_layout.setAlignment(Qt.AlignLeft)

        # Flecha desplegable
        self.arrow_label = QLabel()
        self.load_arrow_icon()
        self.arrow_label.setCursor(QCursor(Qt.PointingHandCursor))
        self.arrow_label.mousePressEvent = self.toggle_expanded
        header_layout.addWidget(self.arrow_label)

        # Título del proyecto (clickeable)
        self.title_label = ClickableLabel(
            f"<b style='color:#cccccc; font-size:13px;'>{self.project_name}</b>"
        )
        self.title_label.clicked.connect(self.toggle_expanded)
        header_layout.addWidget(self.title_label)

        layout.addLayout(header_layout)

        # Contenedor para los thumbnails
        self.thumbnails_widget = QWidget()
        thumbnails_layout = QHBoxLayout(self.thumbnails_widget)
        thumbnails_layout.setSpacing(5)
        thumbnails_layout.setAlignment(Qt.AlignLeft)
        thumbnails_layout.setContentsMargins(20, 0, 0, 0)  # Indentacion

        # Crear thumbnails para cada imagen
        for image_path in self.image_paths:
            thumbnail = ThumbnailWidget(image_path, self.thumbnail_size)
            self.thumbnails.append(thumbnail)
            thumbnails_layout.addWidget(thumbnail)

        # Si no hay imágenes, mostrar mensaje
        if not self.image_paths:
            no_images_label = QLabel(
                "<i style='color:#888888;'>No hay snapshots en este proyecto</i>"
            )
            thumbnails_layout.addWidget(no_images_label)

        layout.addWidget(self.thumbnails_widget)

    def load_arrow_icon(self):
        """Carga el icono de la flecha"""
        if self.arrow_label is None:
            return

        try:
            script_dir = os.path.dirname(__file__)
            icon_path = os.path.join(script_dir, "icons", "dropdown_arrow.png")

            if os.path.exists(icon_path):
                pixmap = QPixmap(icon_path)
                if not pixmap.isNull():
                    # Escalar el icono a un tamaño apropiado
                    scaled_pixmap = pixmap.scaledToWidth(12, Qt.SmoothTransformation)
                    self.arrow_label.setPixmap(scaled_pixmap)
                    self.arrow_label.setFixedSize(scaled_pixmap.size())
                    return

            # Si no se puede cargar el icono, usar texto como fallback
            self.arrow_label.setText("▼")
            self.arrow_label.setStyleSheet("color: #cccccc; font-size: 10px;")
            self.arrow_label.setFixedSize(12, 12)

        except Exception as e:
            debug_print(f"Error al cargar icono de flecha: {e}")
            # Fallback a texto
            if self.arrow_label is not None:
                self.arrow_label.setText("▼")
                self.arrow_label.setStyleSheet("color: #cccccc; font-size: 10px;")
                self.arrow_label.setFixedSize(12, 12)

    def toggle_expanded(self, event=None):
        """Alterna entre expandido y colapsado"""
        self.is_expanded = not self.is_expanded

        if self.thumbnails_widget is None or self.arrow_label is None:
            return

        if self.is_expanded:
            self.thumbnails_widget.show()
            # Rotar flecha hacia abajo
            if self.arrow_label.pixmap():
                # Si tiene pixmap, intentar rotarlo
                transform = self.arrow_label.pixmap().transformed(
                    self.arrow_label.pixmap().transform()
                )
            else:
                # Si es texto, cambiar simbolo
                self.arrow_label.setText("▼")
        else:
            self.thumbnails_widget.hide()
            # Rotar flecha hacia la derecha
            if self.arrow_label.pixmap():
                # Si tiene pixmap, intentar rotarlo
                pass  # Por simplicidad, mantenemos el mismo icono
            else:
                # Si es texto, cambiar simbolo
                self.arrow_label.setText("►")

    def update_thumbnail_size(self, size):
        """Actualiza el tamaño de todos los thumbnails"""
        self.thumbnail_size = size
        for thumbnail in self.thumbnails:
            thumbnail.update_size(size)


class SnapshotGalleryWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.project_widgets = []
        self.current_thumbnail_size = 150

        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setWindowTitle("LGA SnapShot Gallery")
        self.setStyleSheet("background-color: #1d1d1d; border-radius: 10px;")
        self.setMinimumSize(800, 600)

        self.setup_ui()
        self.load_gallery_content()

    def setup_ui(self):
        """Configura la interfaz principal"""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)

        # Toolbar superior con fondo #2a2a2a
        toolbar_frame = QFrame()
        toolbar_frame.setStyleSheet(
            """
            QFrame {
                background-color: #2a2a2a;
                border-radius: 5px;
                padding: 8px;
            }
        """
        )
        toolbar_layout = QHBoxLayout(toolbar_frame)
        toolbar_layout.setSpacing(10)
        toolbar_layout.setContentsMargins(10, 5, 10, 5)

        # Spacer para empujar el slider a la derecha
        toolbar_layout.addStretch()

        # Label para el slider
        size_label = QLabel("Thumbnail Size:")
        size_label.setStyleSheet("color: #cccccc; font-size: 12px;")
        toolbar_layout.addWidget(size_label)

        # Slider para controlar el tamaño de los thumbnails
        self.size_slider = QSlider(Qt.Horizontal)
        self.size_slider.setMinimum(50)
        self.size_slider.setMaximum(500)
        self.size_slider.setValue(150)
        self.size_slider.setFixedWidth(SLIDER_BAR_WIDTH)

        # Calcular el margen para centrar el handle
        handle_margin = -(SLIDER_HANDLE_SIZE - SLIDER_BAR_HEIGHT) // 2
        handle_radius = SLIDER_HANDLE_SIZE // 2

        self.size_slider.setStyleSheet(
            f"""
            QSlider::groove:horizontal {{
                border: 0px;
                height: {SLIDER_BAR_HEIGHT}px;
                background: #333333;
                border-radius: {SLIDER_BAR_HEIGHT // 2}px;
            }}
            QSlider::handle:horizontal {{
                background: #666666;
                border: 0px;
                width: {SLIDER_HANDLE_SIZE}px;
                height: {SLIDER_HANDLE_SIZE}px;
                margin: {handle_margin}px 0;
                border-radius: {handle_radius}px;
            }}
            QSlider::handle:horizontal:hover {{
                background: #888888;
            }}
        """
        )
        self.size_slider.valueChanged.connect(self.on_size_changed)
        toolbar_layout.addWidget(self.size_slider)

        main_layout.addWidget(toolbar_frame)

        # Área de scroll para el contenido
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet(
            """
            QScrollArea {
                border: none;
                background-color: #232323;
            }
            QScrollBar:vertical {
                background-color: #333333;
                width: 12px;
                border-radius: 6px;
            }
            QScrollBar::handle:vertical {
                background-color: #666666;
                border-radius: 6px;
                min-height: 20px;
            }
            QScrollBar::handle:vertical:hover {
                background-color: #888888;
            }
        """
        )

        # Widget contenedor para el scroll
        self.scroll_content = QWidget()
        self.scroll_layout = QVBoxLayout(self.scroll_content)
        self.scroll_layout.setSpacing(15)
        self.scroll_layout.setAlignment(Qt.AlignTop)

        scroll_area.setWidget(self.scroll_content)
        main_layout.addWidget(scroll_area)

    def on_size_changed(self, value):
        """Se ejecuta cuando cambia el valor del slider"""
        self.current_thumbnail_size = value

        # Actualizar el tamaño de todos los thumbnails
        for project_widget in self.project_widgets:
            project_widget.update_thumbnail_size(value)

    def load_gallery_content(self):
        """Carga el contenido de la galería organizando por proyectos"""
        gallery_path = self.get_gallery_path()

        if not gallery_path or not os.path.exists(gallery_path):
            # Mostrar mensaje si no existe la galería
            no_gallery_label = QLabel(
                f"<div style='text-align: center; color: #888888; font-size: 14px;'>"
                f"<b>No se encontró la carpeta de galería</b><br><br>"
                f"Ruta esperada: {gallery_path if gallery_path else 'No definida'}<br><br>"
                f"Toma algunos snapshots para crear la galería automáticamente."
                f"</div>"
            )
            no_gallery_label.setAlignment(Qt.AlignCenter)
            self.scroll_layout.addWidget(no_gallery_label)
            return

        # Obtener todas las subcarpetas (proyectos)
        project_folders = []
        try:
            for item in os.listdir(gallery_path):
                item_path = os.path.join(gallery_path, item)
                if os.path.isdir(item_path):
                    project_folders.append(item)
        except Exception as e:
            debug_print(f"Error al leer carpeta de galería: {e}")
            return

        if not project_folders:
            # No hay proyectos
            no_projects_label = QLabel(
                "<div style='text-align: center; color: #888888; font-size: 14px;'>"
                "<b>No hay proyectos en la galería</b><br><br>"
                "Toma algunos snapshots para empezar a llenar la galería."
                "</div>"
            )
            no_projects_label.setAlignment(Qt.AlignCenter)
            self.scroll_layout.addWidget(no_projects_label)
            return

        # Ordenar proyectos alfabéticamente
        project_folders.sort()

        # Crear widget para cada proyecto
        for project_name in project_folders:
            project_path = os.path.join(gallery_path, project_name)

            # Buscar todas las imágenes en la carpeta del proyecto
            image_extensions = ["*.jpg", "*.jpeg", "*.png", "*.tiff", "*.tif", "*.exr"]
            image_paths = []

            for extension in image_extensions:
                pattern = os.path.join(project_path, extension)
                image_paths.extend(glob.glob(pattern))

            # Ordenar imágenes alfabéticamente
            image_paths.sort()

            # Crear widget del proyecto
            project_widget = ProjectFolderWidget(
                project_name, image_paths, self.current_thumbnail_size
            )
            self.project_widgets.append(project_widget)
            self.scroll_layout.addWidget(project_widget)

        debug_print(f"Cargados {len(project_folders)} proyectos en la galería")

    def get_gallery_path(self):
        """Obtiene la ruta de la carpeta snapshot_gallery"""
        try:
            script_dir = os.path.dirname(__file__)
            gallery_path = os.path.join(script_dir, "snapshot_gallery")
            return gallery_path
        except Exception as e:
            debug_print(f"Error al obtener gallery path: {e}")
            return None


def open_snapshot_gallery():
    """Función principal que abre la ventana de galería de snapshots"""
    global app, window

    debug_print("Abriendo galería de snapshots...")

    app = QApplication.instance() or QApplication([])
    window = SnapshotGalleryWindow()
    window.show()


# --- Main Execution ---
if __name__ == "__main__":
    open_snapshot_gallery()
