"""
_____________________________________________________________________________________________________

  LGA_ToolPack_settings v0.4 | Lega
  Configuracion de la herramienta LGA_ToolPack
_____________________________________________________________________________________________________
"""

import sys
import os
import configparser
import typing  # Importar typing
from typing import Optional, Tuple

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
    QTextEdit,  # Importar QTextEdit
    QMessageBox,  # Importar QMessageBox
    QCheckBox,
    QFileDialog,
)
from PySide2.QtCore import Qt

# Importar funciones y constantes desde LGA_Write_Focus
# Asumiendo que ambos scripts estan en el mismo directorio o en el sys.path
try:
    from LGA_Write_Focus import (
        get_config_path as wf_get_config_path,  # Renombrar para claridad
        ensure_config_exists as wf_ensure_config_exists,
        get_node_name_from_config as wf_get_node_name_from_config,
        DEFAULT_NODE_NAME as WF_DEFAULT_NODE_NAME,  # Renombrar constante
        CONFIG_SECTION as WF_CONFIG_SECTION,  # Renombrar constante
        CONFIG_NODE_NAME_KEY as WF_CONFIG_NODE_NAME_KEY,  # Renombrar constante
    )
except ImportError as e_wf:
    print(f"Error al importar LGA_Write_Focus.py: {e_wf}. Funcionalidad limitada.")

    # Definir funciones dummy y valores por defecto
    def wf_ensure_config_exists():
        pass

    def wf_get_node_name_from_config() -> str:
        return "Write_Pub"

    def wf_get_config_path() -> typing.Optional[str]:
        return None

    WF_DEFAULT_NODE_NAME = "Write_Pub"
    WF_CONFIG_SECTION = "Settings"
    WF_CONFIG_NODE_NAME_KEY = "node_name"

# --- Importaciones de LGA_showInlFlow ---
try:
    from LGA_showInlFlow import (
        get_config_path as sif_get_config_path,
        ensure_config_exists as sif_ensure_config_exists,
        get_credentials_from_config as sif_get_credentials_from_config,
        CONFIG_SECTION as SIF_CONFIG_SECTION,
        CONFIG_URL_KEY as SIF_CONFIG_URL_KEY,
        CONFIG_LOGIN_KEY as SIF_CONFIG_LOGIN_KEY,
        CONFIG_PASSWORD_KEY as SIF_CONFIG_PASSWORD_KEY,
    )
except ImportError as e_sif:
    print(f"Error al importar LGA_showInlFlow.py: {e_sif}. Funcionalidad limitada.")

    # Definir funciones dummy y valores por defecto
    def sif_ensure_config_exists():
        pass

    def sif_get_credentials_from_config() -> (
        typing.Tuple[typing.Optional[str], typing.Optional[str], typing.Optional[str]]
    ):
        return None, None, None

    def sif_get_config_path() -> typing.Optional[str]:
        return None

    SIF_CONFIG_SECTION = "Credentials"
    SIF_CONFIG_URL_KEY = "shotgrid_url"
    SIF_CONFIG_LOGIN_KEY = "shotgrid_login"
    SIF_CONFIG_PASSWORD_KEY = "shotgrid_password"

# --- Importaciones de LGA_RnW_ColorSpace_Favs --- Nuevo
try:
    from LGA_RnW_ColorSpace_Favs import (
        get_colorspace_ini_path,
        read_colorspaces_from_ini,
        save_colorspaces_to_ini,
        COLORSPACE_SECTION,  # Importar tambien la constante de seccion
    )
except ImportError as e_csf:
    print(
        f"Error al importar LGA_RnW_ColorSpace_Favs.py: {e_csf}. Funcionalidad limitada."
    )

    # Definir funciones dummy
    def get_colorspace_ini_path(create_if_missing: bool = True) -> typing.Optional[str]:
        return None

    def read_colorspaces_from_ini(ini_path: typing.Optional[str]) -> typing.List[str]:
        return []

    def save_colorspaces_to_ini(
        ini_path: typing.Optional[str], colorspaces_list: typing.List[str]
    ) -> bool:
        return False

    COLORSPACE_SECTION = "ColorSpaces"

# --- Importaciones de LGA_Render_Complete --- NUEVO
try:
    from LGA_Render_Complete import (
        get_config_path as rc_get_config_path,
        ensure_config_exists as rc_ensure_config_exists,
        get_mail_settings_from_config as rc_get_mail_settings_from_config,
        save_mail_settings_to_config as rc_save_mail_settings_to_config,
        CONFIG_SECTION as RC_CONFIG_SECTION,
        CONFIG_FROM_KEY as RC_CONFIG_FROM_KEY,
        CONFIG_PASS_KEY as RC_CONFIG_PASS_KEY,
        CONFIG_TO_KEY as RC_CONFIG_TO_KEY,
    )
except ImportError as e_rc:
    print(f"Error al importar LGA_Render_Complete.py: {e_rc}. Funcionalidad limitada.")

    def rc_ensure_config_exists() -> None:
        pass

    def rc_get_mail_settings_from_config() -> (
        Tuple[Optional[str], Optional[str], Optional[str]]
    ):
        return None, None, None

    def rc_save_mail_settings_to_config(from_email, from_password, to_email) -> bool:
        return False

    def rc_get_config_path() -> Optional[str]:
        return None

    RC_CONFIG_SECTION = "Mail"
    RC_CONFIG_FROM_KEY = "from_email"
    RC_CONFIG_PASS_KEY = "from_password"
    RC_CONFIG_TO_KEY = "to_email"


class SettingsWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("LGA ToolPack Settings")
        self.setMinimumWidth(450)  # Un poco mas ancho para el QTextEdit
        self.initUI()

    def initUI(self):
        main_layout = QVBoxLayout(self)

        # --- Write Presets Section (Placeholder) ---
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
        write_focus_layout_container = QVBoxLayout()
        write_focus_form_layout = QFormLayout()
        self.write_focus_input = QLineEdit()
        try:
            wf_ensure_config_exists()  # Usar funcion importada
            current_node_name = wf_get_node_name_from_config()  # Usar funcion importada
            self.write_focus_input.setText(current_node_name or WF_DEFAULT_NODE_NAME)
        except Exception as e:
            print(f"Error al cargar config de Write Focus: {e}")
            self.write_focus_input.setText(WF_DEFAULT_NODE_NAME)

        write_focus_form_layout.addRow(
            "Name of the Write Node to Focus:", self.write_focus_input
        )
        write_focus_layout_container.addLayout(write_focus_form_layout)
        self.save_write_focus_button = QPushButton("Save")
        self.save_write_focus_button.clicked.connect(self.save_write_focus_settings)
        write_focus_layout_container.addWidget(
            self.save_write_focus_button, 0, Qt.AlignRight
        )
        write_focus_group.setLayout(write_focus_layout_container)
        main_layout.addWidget(write_focus_group)

        # --- Show in Flow Section ---
        show_flow_group = QGroupBox("Show in Flow")
        show_flow_layout_container = QVBoxLayout()
        show_flow_form_layout = QFormLayout()
        self.username_input = QLineEdit()
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        self.site_input = QLineEdit()
        # Placeholders para los campos de ShotGrid
        self.site_input.setPlaceholderText("e.g., https://studio.shotgrid.autodesk.com")
        self.username_input.setPlaceholderText("e.g., artist@studio.com")
        self.password_input.setPlaceholderText("")
        show_flow_form_layout.addRow(
            "ShotGrid URL:",
            self.site_input,
        )
        show_flow_form_layout.addRow("ShotGrid Login:", self.username_input)
        show_flow_form_layout.addRow("ShotGrid Password:", self.password_input)

        try:
            sif_ensure_config_exists()  # Usar funcion importada
            sif_url, sif_login, sif_password = (
                sif_get_credentials_from_config()
            )  # Usar funcion importada
            self.site_input.setText(sif_url or "")
            self.username_input.setText(sif_login or "")
            self.password_input.setText(sif_password or "")
        except Exception as e:
            print(f"Error al cargar credenciales de Show in Flow: {e}")

        show_flow_layout_container.addLayout(show_flow_form_layout)
        self.save_show_flow_button = QPushButton("Save")
        self.save_show_flow_button.clicked.connect(self.save_show_flow_settings)
        show_flow_layout_container.addWidget(
            self.save_show_flow_button, 0, Qt.AlignRight
        )
        show_flow_group.setLayout(show_flow_layout_container)
        main_layout.addWidget(show_flow_group)

        # --- Color Space Favs Section --- Modificado
        color_space_group = QGroupBox("Color Space Favorites")  # Titulo mas descriptivo
        color_space_layout = QVBoxLayout()
        color_space_layout.addWidget(
            QLabel(
                "Enter favorite OCIO color spaces (one per line):"
            )  # Label explicativo
        )
        # Crear el QTextEdit
        self.color_space_edit = QTextEdit()
        self.color_space_edit.setPlaceholderText(
            "e.g.,\nOutput - sRGB\nUtility - Raw\nACES - ACEScg"
        )
        self.color_space_edit.setMinimumHeight(80)  # Altura minima
        color_space_layout.addWidget(self.color_space_edit)

        # --- Cargar favoritos existentes --- Nuevo
        try:
            self.colorspace_ini_path = get_colorspace_ini_path(create_if_missing=True)
            if self.colorspace_ini_path:
                fav_list = read_colorspaces_from_ini(self.colorspace_ini_path)
                self.color_space_edit.setText("\n".join(fav_list))
            else:
                print("Advertencia: No se pudo obtener la ruta del INI de ColorSpaces.")
                # Podriamos deshabilitar el campo/boton si no hay ruta
                # self.color_space_edit.setEnabled(False)
        except Exception as e:
            print(f"Error al cargar Color Space Favs: {e}")
            QMessageBox.warning(
                self, "Error", f"Could not load Color Space Favorites:\n{e}"
            )
        # ---------------------------------

        self.save_color_space_button = QPushButton("Save")
        self.save_color_space_button.clicked.connect(
            self.save_color_space_settings
        )  # Conectar al nuevo metodo
        color_space_layout.addWidget(self.save_color_space_button, 0, Qt.AlignRight)
        color_space_group.setLayout(color_space_layout)
        main_layout.addWidget(color_space_group)

        # --- Render Complete Mail Settings Section --- NUEVO
        render_mail_group = QGroupBox("Render Complete Mail Settings")
        render_mail_layout_container = QVBoxLayout()
        render_mail_form_layout = QFormLayout()
        self.render_mail_from_input = QLineEdit()
        self.render_mail_pass_input = QLineEdit()
        self.render_mail_pass_input.setEchoMode(QLineEdit.Password)
        self.render_mail_to_input = QLineEdit()
        # Placeholders para los campos de mail
        self.render_mail_from_input.setPlaceholderText("e.g., tuMail@outlook.com")
        self.render_mail_pass_input.setPlaceholderText("")
        self.render_mail_to_input.setPlaceholderText("e.g., tuMail@gmail.com")
        # Cargar valores actuales
        try:
            rc_ensure_config_exists()
            from_email, from_password, to_email = rc_get_mail_settings_from_config()
            self.render_mail_from_input.setText(from_email or "")
            self.render_mail_pass_input.setText(from_password or "")
            self.render_mail_to_input.setText(to_email or "")
        except Exception as e:
            print(f"Error al cargar config de Render Complete Mail: {e}")
        render_mail_form_layout.addRow("From (Outlook):", self.render_mail_from_input)
        render_mail_form_layout.addRow("Password:", self.render_mail_pass_input)
        render_mail_form_layout.addRow("To (Recipient):", self.render_mail_to_input)
        render_mail_layout_container.addLayout(render_mail_form_layout)
        # --- NUEVOS SETTINGS ---
        self.cb_enable_mail = QCheckBox("Enable mail sending")
        self.cb_enable_render_time = QCheckBox("Enable render time calculation")
        self.cb_enable_sound = QCheckBox("Enable sound notification")
        render_mail_layout_container.addWidget(self.cb_enable_mail)
        render_mail_layout_container.addWidget(self.cb_enable_render_time)
        render_mail_layout_container.addWidget(self.cb_enable_sound)
        # Selector de archivo .wav
        wav_layout = QHBoxLayout()
        self.wav_path_input = QLineEdit()
        self.wav_path_input.setPlaceholderText("Select .wav file...")
        self.wav_browse_btn = QPushButton("Browse")
        self.wav_browse_btn.clicked.connect(self.browse_wav_file)
        wav_layout.addWidget(self.wav_path_input)
        wav_layout.addWidget(self.wav_browse_btn)
        render_mail_layout_container.addLayout(wav_layout)
        # ---

        self.save_render_mail_button = QPushButton("Save")
        self.save_render_mail_button.clicked.connect(self.save_render_mail_settings)
        render_mail_layout_container.addWidget(
            self.save_render_mail_button, 0, Qt.AlignRight
        )
        render_mail_group.setLayout(render_mail_layout_container)
        main_layout.addWidget(render_mail_group)
        # ---
        main_layout.addStretch()

    def save_write_focus_settings(self):
        """Guarda el nombre del nodo de Write Focus en su archivo .ini."""
        config_file_path = wf_get_config_path()
        if not config_file_path:
            print("Error: No se pudo obtener la ruta para guardar Write Focus.")
            QMessageBox.critical(
                self,
                "Error",
                "Could not determine the configuration file path for Write Focus.",
            )
            return

        new_node_name = self.write_focus_input.text().strip()
        if not new_node_name:
            QMessageBox.warning(
                self, "Input Error", "Write Focus node name cannot be empty."
            )
            # Revertir al valor anterior o al por defecto
            try:
                current_node_name = wf_get_node_name_from_config()
                self.write_focus_input.setText(
                    current_node_name or WF_DEFAULT_NODE_NAME
                )
            except Exception:
                self.write_focus_input.setText(WF_DEFAULT_NODE_NAME)
            return

        config = configparser.ConfigParser()
        try:
            # Leer existente para preservar otras secciones/claves
            if os.path.exists(config_file_path):
                config.read(config_file_path)

            if not config.has_section(WF_CONFIG_SECTION):
                config.add_section(WF_CONFIG_SECTION)

            config.set(WF_CONFIG_SECTION, WF_CONFIG_NODE_NAME_KEY, new_node_name)

            with open(config_file_path, "w") as configfile:
                config.write(configfile)

            print(f"Configuracion de Write Focus guardada: {new_node_name}")
            QMessageBox.information(self, "Success", "Write Focus settings saved.")

        except Exception as e:
            print(f"Error al guardar la configuracion de Write Focus: {e}")
            QMessageBox.critical(
                self, "Save Error", f"Could not save Write Focus settings:\n{e}"
            )

    def save_show_flow_settings(self):
        """Guarda las credenciales de Show in Flow en su archivo .ini."""
        config_file_path = sif_get_config_path()
        if not config_file_path:
            print("Error: No se pudo obtener la ruta para guardar Show in Flow.")
            QMessageBox.critical(
                self,
                "Error",
                "Could not determine the configuration file path for Show in Flow.",
            )
            return

        new_url = self.site_input.text().strip()
        new_login = self.username_input.text().strip()
        new_password = self.password_input.text()  # No hacer strip a la password

        if not new_url or not new_login or not new_password:
            QMessageBox.warning(
                self,
                "Input Error",
                "Show in Flow URL, Login, and Password cannot be empty.",
            )
            # No revertimos aqui, dejamos que el usuario corrija
            return

        config = configparser.ConfigParser()
        try:
            # Leer existente
            if os.path.exists(config_file_path):
                config.read(config_file_path, encoding="utf-8")

            if not config.has_section(SIF_CONFIG_SECTION):
                config.add_section(SIF_CONFIG_SECTION)

            config.set(SIF_CONFIG_SECTION, SIF_CONFIG_URL_KEY, new_url)
            config.set(SIF_CONFIG_SECTION, SIF_CONFIG_LOGIN_KEY, new_login)
            config.set(SIF_CONFIG_SECTION, SIF_CONFIG_PASSWORD_KEY, new_password)

            with open(config_file_path, "w", encoding="utf-8") as configfile:
                config.write(configfile)

            print("Configuracion de Show in Flow guardada.")
            QMessageBox.information(self, "Success", "Show in Flow settings saved.")

        except Exception as e:
            print(f"Error al guardar la configuracion de Show in Flow: {e}")
            QMessageBox.critical(
                self, "Save Error", f"Could not save Show in Flow settings:\n{e}"
            )

    def save_color_space_settings(self):  # Nuevo metodo
        """Guarda la lista de Color Space Favorites en su archivo .ini."""
        # Re-obtener la ruta por si acaso, pero no forzar creacion/copia aqui
        ini_path = getattr(
            self,
            "colorspace_ini_path",
            get_colorspace_ini_path(create_if_missing=False),
        )

        if not ini_path:
            print("Error: No se pudo obtener la ruta para guardar Color Space Favs.")
            QMessageBox.critical(
                self,
                "Error",
                "Could not determine the configuration file path for Color Space Favorites.",
            )
            return

        # Obtener texto del QTextEdit
        text = self.color_space_edit.toPlainText()
        # Dividir en lineas, quitar espacios y filtrar vacias/solo espacios
        favorites_list = [line.strip() for line in text.split("\n") if line.strip()]

        # Usar la funcion importada para guardar
        try:
            success = save_colorspaces_to_ini(ini_path, favorites_list)
            if success:
                print("Configuracion de Color Space Favorites guardada.")
                QMessageBox.information(self, "Success", "Color Space Favorites saved.")
            else:
                # El error especifico ya deberia haberse impreso en la funcion save_colorspaces_to_ini
                QMessageBox.critical(
                    self,
                    "Save Error",
                    "Could not save Color Space Favorites. Check console for details.",
                )

        except Exception as e:
            # Captura por si save_colorspaces_to_ini lanza una excepcion inesperada
            print(f"Error inesperado al llamar a save_colorspaces_to_ini: {e}")
            QMessageBox.critical(
                self,
                "Save Error",
                f"Unexpected error saving Color Space Favorites:\n{e}",
            )

    def save_render_mail_settings(self):
        """Guarda los datos de mail de Render Complete en su archivo .ini."""
        config_file_path = rc_get_config_path()
        if not config_file_path:
            print(
                "Error: No se pudo obtener la ruta para guardar Render Complete Mail."
            )
            QMessageBox.critical(
                self,
                "Error",
                "Could not determine the configuration file path for Render Complete Mail.",
            )
            return
        from_email = self.render_mail_from_input.text().strip()
        from_password = self.render_mail_pass_input.text()
        to_email = self.render_mail_to_input.text().strip()
        if not from_email or not from_password or not to_email:
            QMessageBox.warning(
                self,
                "Input Error",
                "All mail fields must be filled (From, Password, To).",
            )
            # No revertimos, dejamos que el usuario corrija
            return
        try:
            success = rc_save_mail_settings_to_config(
                from_email, from_password, to_email
            )
            if success:
                print("Configuracion de Render Complete Mail guardada.")
                QMessageBox.information(
                    self, "Success", "Render Complete Mail settings saved."
                )
            else:
                QMessageBox.critical(
                    self,
                    "Save Error",
                    "Could not save Render Complete Mail settings. Check console for details.",
                )
        except Exception as e:
            print(f"Error al guardar la configuracion de Render Complete Mail: {e}")
            QMessageBox.critical(
                self,
                "Save Error",
                f"Could not save Render Complete Mail settings:\n{e}",
            )

    def browse_wav_file(self):
        """Abre un diálogo para seleccionar un archivo .wav y lo pone en el QLineEdit."""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select WAV file", "", "WAV Files (*.wav)"
        )
        if file_path:
            self.wav_path_input.setText(file_path)


# --- Main Execution ---
if __name__ == "__main__":
    # Necesario para ejecucion standalone fuera de Nuke
    app = QApplication.instance() or QApplication(sys.argv)

    settings_window = SettingsWindow()
    settings_window.show()

    # Mantener el bucle para ejecucion standalone
    if not QApplication.instance():  # Solo si no estamos en Nuke
        sys.exit(app.exec_())
    # Si estamos en Nuke, no llamamos a sys.exit()
