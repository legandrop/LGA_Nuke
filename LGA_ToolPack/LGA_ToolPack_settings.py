"""
_____________________________________________________________________________________________________

  LGA_ToolPack_settings v0.1 | 2025 | Lega
  Configuracion de la herramienta LGA_ToolPack
_____________________________________________________________________________________________________
"""

import sys
import os
import configparser
from PySide2.QtWidgets import (
    QApplication,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QGroupBox,
    QLabel,
    QLineEdit,
    QFormLayout,
    QPushButton,
)
from PySide2.QtCore import Qt

# Importar funciones y constantes desde LGA_Write_Focus
# Asumiendo que ambos scripts estan en el mismo directorio o en el sys.path
try:
    from LGA_Write_Focus import (
        get_config_path,
        ensure_config_exists,
        get_node_name_from_config,
        DEFAULT_NODE_NAME,  # Importar el valor por defecto tambien
        CONFIG_SECTION,  # Constante para la seccion
        CONFIG_NODE_NAME_KEY,  # Constante para la clave
    )
except ImportError:
    print(
        "Error: No se pudo importar LGA_Write_Focus.py. Asegurate de que este en la misma carpeta o en el PYTHONPATH."
    )

    # Definir funciones dummy o valores por defecto para que la UI no falle
    def ensure_config_exists():
        pass

    def get_node_name_from_config() -> str:
        return "Write_Pub"  # Usar valor por defecto

    DEFAULT_NODE_NAME = "Write_Pub"


class SettingsWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("LGA ToolPack Settings")
        self.setMinimumWidth(400)
        self.initUI()

    def initUI(self):
        main_layout = QVBoxLayout(self)

        # --- Write Presets Section ---
        write_presets_group = QGroupBox("Write Presets")
        write_presets_layout = QVBoxLayout()
        write_presets_layout.addWidget(
            QLabel("(Placeholder for Write Presets functionality)")
        )
        self.save_write_presets_button = QPushButton("Save")
        # self.save_write_presets_button.clicked.connect(self.save_write_presets) # Placeholder
        write_presets_layout.addWidget(self.save_write_presets_button, 0, Qt.AlignRight)
        write_presets_group.setLayout(write_presets_layout)
        main_layout.addWidget(write_presets_group)

        # --- Write Focus Section ---
        write_focus_group = QGroupBox("Write Focus")
        write_focus_layout_container = QVBoxLayout()  # Contenedor para Form y Boton
        write_focus_form_layout = QFormLayout()  # Layout para etiquetas y campos
        self.write_focus_input = QLineEdit()
        # --- Leer y mostrar el valor actual ---
        ensure_config_exists()  # Asegurarse de que el archivo .ini exista
        current_node_name = get_node_name_from_config()
        self.write_focus_input.setText(current_node_name)
        # --- Fin lectura ---
        write_focus_form_layout.addRow(
            "Name of the Write Node to Focus:", self.write_focus_input
        )

        # Anadir FormLayout al contenedor
        write_focus_layout_container.addLayout(write_focus_form_layout)

        # Boton Save
        self.save_write_focus_button = QPushButton("Save")
        self.save_write_focus_button.clicked.connect(self.save_write_focus_settings)
        write_focus_layout_container.addWidget(
            self.save_write_focus_button, 0, Qt.AlignRight
        )  # Anadir boton al contenedor

        write_focus_group.setLayout(
            write_focus_layout_container
        )  # Establecer layout del grupo
        main_layout.addWidget(write_focus_group)

        # --- Show in Flow Section ---
        show_flow_group = QGroupBox("Show in Flow")
        show_flow_layout_container = QVBoxLayout()  # Contenedor para Form y Boton
        show_flow_form_layout = QFormLayout()  # Layout para etiquetas y campos
        self.username_input = QLineEdit()
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)  # Mask password
        self.site_input = QLineEdit()
        show_flow_form_layout.addRow("Username:", self.username_input)
        show_flow_form_layout.addRow("Password:", self.password_input)
        show_flow_form_layout.addRow("Site:", self.site_input)

        # Anadir FormLayout al contenedor
        show_flow_layout_container.addLayout(show_flow_form_layout)

        # Boton Save
        self.save_show_flow_button = QPushButton("Save")
        # self.save_show_flow_button.clicked.connect(self.save_show_flow_settings) # Placeholder
        show_flow_layout_container.addWidget(
            self.save_show_flow_button, 0, Qt.AlignRight
        )  # Anadir boton al contenedor

        show_flow_group.setLayout(
            show_flow_layout_container
        )  # Establecer layout del grupo
        main_layout.addWidget(show_flow_group)

        # --- Color Space Favs Section ---
        color_space_group = QGroupBox("Color Space Favs")
        color_space_layout = QVBoxLayout()
        color_space_layout.addWidget(
            QLabel("(Placeholder for Color Space Favorites functionality)")
        )
        self.save_color_space_button = QPushButton("Save")
        # self.save_color_space_button.clicked.connect(self.save_color_space) # Placeholder
        color_space_layout.addWidget(self.save_color_space_button, 0, Qt.AlignRight)
        color_space_group.setLayout(color_space_layout)
        main_layout.addWidget(color_space_group)

        main_layout.addStretch()  # Push everything up

    def save_write_focus_settings(self):
        """Guarda el nombre del nodo de Write Focus en su archivo .ini."""
        config_file_path = get_config_path()
        if not config_file_path:
            print(
                "Error: No se pudo obtener la ruta del archivo de configuracion para Write Focus."
            )
            # Opcional: Mostrar mensaje en la UI
            return

        new_node_name = self.write_focus_input.text().strip()
        if not new_node_name:
            print("Error: El nombre del nodo para Write Focus no puede estar vacio.")
            # Opcional: Mostrar mensaje en la UI y quizas revertir al valor anterior
            current_node_name = get_node_name_from_config()  # Releer por si acaso
            self.write_focus_input.setText(current_node_name)
            return

        config = configparser.ConfigParser()
        try:
            # Leer la configuracion existente para preservar otras posibles claves/secciones
            config.read(config_file_path)

            # Asegurarse de que la seccion exista
            if not config.has_section(CONFIG_SECTION):
                config.add_section(CONFIG_SECTION)

            # Establecer el nuevo valor
            config.set(CONFIG_SECTION, CONFIG_NODE_NAME_KEY, new_node_name)

            # Escribir los cambios de vuelta al archivo
            with open(config_file_path, "w") as configfile:
                config.write(configfile)

            print(
                f"Configuracion de Write Focus guardada: {CONFIG_NODE_NAME_KEY} = {new_node_name} en {config_file_path}"
            )
            # Opcional: Mostrar mensaje de exito en la UI (ej. status bar)

        except IOError as e:
            print(
                f"Error de I/O al guardar la configuracion de Write Focus en {config_file_path}: {e}"
            )
            # Opcional: Mostrar mensaje de error en la UI
        except configparser.Error as e:
            print(
                f"Error de formato ConfigParser al guardar la configuracion de Write Focus: {e}"
            )
            # Opcional: Mostrar mensaje de error en la UI
        except Exception as e:
            print(f"Error inesperado al guardar la configuracion de Write Focus: {e}")
            # Opcional: Mostrar mensaje de error en la UI


# --- Main Execution ---
if __name__ == "__main__":
    # Solo se necesita una instancia de QApplication por script
    app = QApplication.instance() or QApplication(sys.argv)

    settings_window = SettingsWindow()
    settings_window.show()

    # Mantener el bucle para ejecucion standalone
    try:
        sys.exit(app.exec_())
    except SystemExit:
        pass  # Evitar error si ya existe una instancia de app (ej. dentro de Nuke)
