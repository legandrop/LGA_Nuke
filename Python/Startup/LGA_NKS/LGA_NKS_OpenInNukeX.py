"""
______________________________________________________________________

  LGA_NKS_OpenInNukeX v1.0 - 2024 - Lega
  Abre el script asociado al clip seleccionado en NukeX
______________________________________________________________________

"""

import hiero.core
import hiero.ui
import os
import re
import subprocess
import socket
from PySide2 import QtWidgets, QtCore

DEBUG = True

def debug_print(*message):
    if DEBUG:
        print(*message)

def show_message(title, message, duration=None):
    msgBox = QtWidgets.QMessageBox()
    msgBox.setWindowTitle(title)
    # Interpretar el mensaje como HTML si incluye etiquetas, de lo contrario como texto normal
    if '<' in message and '>' in message:
        msgBox.setTextFormat(QtCore.Qt.TextFormat.RichText)  # Interpretar como HTML
    else:
        msgBox.setTextFormat(QtCore.Qt.TextFormat.PlainText)  # Interpretar como texto normal
    msgBox.setText(message)
    msgBox.setStandardButtons(QtWidgets.QMessageBox.Ok)
    if duration:
        QtCore.QTimer.singleShot(duration, msgBox.close)
    msgBox.exec_()

def show_timed_message(title, message, duration):
    msgBox = TimedMessageBox(title, message, duration)
    msgBox.exec_()

class TimedMessageBox(QtWidgets.QMessageBox):
    def __init__(self, title, message, duration):
        super().__init__()
        self.setWindowTitle(title)
        self.setText(message)
        self.setStandardButtons(QtWidgets.QMessageBox.Ok)

        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.updateButton)
        self.timeLeft = duration // 1000  # Convert milliseconds to seconds
        self.timer.start(1000)  # Update every second

        self.updateButton()  # Initialize the button text

    def updateButton(self):
        if self.timeLeft > 0:
            self.button(QtWidgets.QMessageBox.Ok).setText(f"OK ({self.timeLeft})")
            self.timeLeft -= 1
        else:
            self.timer.stop()
            self.accept()  # Close the message box automatically

def get_project_path(file_path):
    # Dividir el path en partes usando '/' como separador
    path_parts = file_path.split('/')
    # Construir la nueva ruta agregando '/Comp/1_projects'
    project_path = '/'.join(path_parts[:4]) + '/Comp/1_projects'
    return project_path

def get_script_name(file_path):
    # Extraer el nombre del archivo del path completo
    script_name = os.path.basename(file_path)
    # Eliminar la extensión y cualquier secuencia de frame como %04d
    script_name = re.sub(r'_%\d+?d\.exr$', '', script_name)  # Ajusta la expresión regular según necesidad
    return script_name + '.nk'  # Añadir la extensión correcta de Nuke

def open_nuke_script(nk_filepath):
    host = 'localhost'
    port = 54325
    nuke_path = "C:/Program Files/Nuke15.0v4/Nuke15.0.exe"

    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(10)
            s.connect((host, port))
            # Enviar un comando 'ping'
            s.sendall("ping".encode())
            # Esperar una respuesta para confirmar que NukeX está operativo
            response = s.recv(1024).decode()
            if "pong" in response:
                debug_print("NukeX está activo y respondiendo.")
                # Cerrar el socket anterior y abrir uno nuevo para enviar el comando de ejecución
                s.close()
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as new_socket:
                    new_socket.connect((host, port))
                    normalized_path = os.path.normpath(nk_filepath).replace('\\', '/')
                    full_command = f"run_script||{normalized_path}"
                    new_socket.sendall(full_command.encode())
                    show_timed_message(
                        "OpenInNukeX", 
                        (
                            f"<div style='text-align: center;'>"
                            f"<span>Abriendo</span><br>"
                            f"<span style='font-style: italic; color: #9f9f9f; font-size: 0.9em;'>{os.path.basename(nk_filepath)}</span><br><br>"
                            f"<span style='color:white;'>Por favor, cambia a la ventana de NukeX...</span>"
                            f"</div>"
                        ),
                        5000
                    )
                    return

            else:
                raise Exception("NukeX no está respondiendo como se esperaba.")
    except (socket.timeout, ConnectionRefusedError, Exception) as e:
        # Si no se puede establecer la conexión o no se recibe la respuesta esperada, intentar abrir NukeX directamente
        command = f'"{nuke_path}" --nukex "{nk_filepath}"'
        subprocess.Popen(command, shell=True)
        show_timed_message(
            "Error", 
            (
                f"<span style='color:white;'><b>Falló la conexión con NukeX</b></span><br><br>"
                f"Abriendo una nueva instancia de NukeX<br>"
                f"<span style='font-style: italic; color: #9f9f9f; font-size: 0.9em;'>{nuke_path}</span>"
            ), 
            5000
        )
    except ConnectionResetError:
        show_message("Error", "La conexión fue cerrada por el servidor.")

def main():
    try:
        seq = hiero.ui.activeSequence()
        if not seq:
            debug_print("No hay una secuencia activa.")
            show_message("Error", "No hay una secuencia activa.")
            return

        te = hiero.ui.getTimelineEditor(seq)
        selected_clips = te.selection()

        if len(selected_clips) == 0:
            debug_print("*** No hay clips seleccionados en la pista ***")
            show_message("Error", "No hay clips seleccionados.")
            return

        for shot in selected_clips:
            if isinstance(shot, hiero.core.EffectTrackItem):
                continue  # Ignorar si es un efecto
            try:
                file_path = shot.source().mediaSource().fileinfos()[0].filename() if shot.source().mediaSource().fileinfos() else None
                if not file_path:
                    debug_print("No se encontró el path del archivo del clip.")
                    continue
                project_path = get_project_path(file_path)
                script_name = get_script_name(file_path)
                script_full_path = os.path.join(project_path, script_name)

                # Verificar si el archivo existe y abrir en Nuke si es así
                if os.path.exists(script_full_path):
                    open_nuke_script(script_full_path)
                else:
                    formatted_message = "<div style='text-align: left;'><b>Archivo no encontrado</b><br><br>" + script_full_path + "</div>"
                    show_message("Error", formatted_message)
                return  # Salir después de abrir el script
            except AttributeError as e:
                debug_print(f"El clip no tiene una fuente válida: {e}")

        show_message("Error", "No se encontró un clip válido.")
    except Exception as e:
        debug_print(f"Error durante la operación: {e}")
