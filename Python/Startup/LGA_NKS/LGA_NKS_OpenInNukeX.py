"""
_________________________________________________________________________

  LGA_NKS_OpenInNukeX v1.1 - 2024 - Lega
  Abre el script asociado al clip seleccionado en NukeX
  Verifica si hay una version mas reciente y pregunta si desea abrirla
_________________________________________________________________________

"""

import hiero.core
import hiero.ui
import os
import re
import subprocess
import socket
from PySide2 import QtWidgets, QtCore

DEBUG = False

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

def show_version_dialog(current_version, latest_version, current_path, latest_path):
    msgBox = QtWidgets.QMessageBox()
    msgBox.setWindowTitle("Verificacion de Version")
    msgBox.setText(
        f"<div style='text-align: center;'>"
        f"<span style='color: #ff9900;'><b>¡Atencion!</b></span><br><br>"
        f"La version que intentas abrir no es la mas reciente:<br><br>"
        f"Version actual: <span style='color: #ff9900;'>{current_version}</span><br>"
        f"Ultima version: <span style='color: #00ff00;'>{latest_version}</span><br><br>"
        f"¿Deseas abrir la ultima version en su lugar?</div>"
    )
    msgBox.setStandardButtons(QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
    msgBox.setDefaultButton(QtWidgets.QMessageBox.Yes)
    msgBox.button(QtWidgets.QMessageBox.Yes).setText("Abrir ultima version")
    msgBox.button(QtWidgets.QMessageBox.No).setText("Abrir version actual")
    
    response = msgBox.exec_()
    return response == QtWidgets.QMessageBox.Yes

def get_version_from_filename(filename):
    debug_print(f"Analizando version del archivo: {filename}")
    # Busca patrones como _v00, _v01, etc. antes de la extension
    match = re.search(r'_v(\d{2})\.nk$', filename)
    if match:
        version = int(match.group(1))
        debug_print(f"Version encontrada: {version}")
        return version
    debug_print("No se encontro version en el nombre del archivo")
    return 0

def find_latest_version(script_path):
    debug_print(f"Buscando versiones en: {script_path}")
    directory = os.path.dirname(script_path)
    base_name = os.path.splitext(os.path.basename(script_path))[0]
    debug_print(f"Nombre base del archivo: {base_name}")
    
    # Eliminar la version actual del nombre base si existe
    base_name = re.sub(r'_v\d{2}$', '', base_name)
    debug_print(f"Nombre base sin version: {base_name}")
    
    # Buscar todos los archivos que coincidan con el patrón
    pattern = re.compile(f"{base_name}_v\\d{{2}}\\.nk$")
    versions = []
    
    debug_print(f"Buscando archivos en directorio: {directory}")
    for file in os.listdir(directory):
        debug_print(f"Archivo encontrado: {file}")
        if pattern.match(file):
            version = get_version_from_filename(file)
            full_path = os.path.join(directory, file)
            versions.append((version, full_path))
            debug_print(f"Version valida encontrada: {version} en {full_path}")
    
    if not versions:
        debug_print("No se encontraron versiones validas")
        return None, None
    
    # Ordenar por version y obtener la mas alta
    versions.sort(key=lambda x: x[0], reverse=True)
    latest = versions[0]
    debug_print(f"Version mas alta encontrada: {latest[0]} en {latest[1]}")
    return latest

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
    debug_print(f"Obteniendo project path de: {file_path}")
    # Dividir el path en partes usando '/' como separador
    path_parts = file_path.split('/')
    debug_print(f"Partes del path: {path_parts}")
    # Construir la nueva ruta agregando '/Comp/1_projects'
    project_path = '/'.join(path_parts[:4]) + '/Comp/1_projects'
    debug_print(f"Project path construido: {project_path}")
    return project_path

def get_script_name(file_path):
    debug_print(f"Obteniendo script name de: {file_path}")
    # Extraer el nombre del archivo del path completo
    script_name = os.path.basename(file_path)
    debug_print(f"Nombre base del archivo: {script_name}")
    # Eliminar la extension y cualquier secuencia de frame como %04d
    script_name = re.sub(r'_%\d+?d\.exr$', '', script_name)
    debug_print(f"Nombre sin secuencia de frame: {script_name}")
    script_name = script_name + '.nk'
    debug_print(f"Nombre final del script: {script_name}")
    return script_name

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
            # Esperar una respuesta para confirmar que NukeX esta operativo
            response = s.recv(1024).decode()
            if "pong" in response:
                debug_print("NukeX esta activo y respondiendo.")
                # Cerrar el socket anterior y abrir uno nuevo para enviar el comando de ejecucion
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
                raise Exception("NukeX no esta respondiendo como se esperaba.")
    except (socket.timeout, ConnectionRefusedError, Exception) as e:
        # Si no se puede establecer la conexion o no se recibe la respuesta esperada, intentar abrir NukeX directamente
        command = f'"{nuke_path}" --nukex "{nk_filepath}"'
        subprocess.Popen(command, shell=True)
        show_timed_message(
            "Error", 
            (
                f"<span style='color:white;'><b>Fallo la conexion con NukeX</b></span><br><br>"
                f"Abriendo una nueva instancia de NukeX<br>"
                f"<span style='font-style: italic; color: #9f9f9f; font-size: 0.9em;'>{nuke_path}</span>"
            ), 
            5000
        )
    except ConnectionResetError:
        show_message("Error", "La conexion fue cerrada por el servidor.")

def main():
    try:
        debug_print("Iniciando main()")
        seq = hiero.ui.activeSequence()
        if not seq:
            debug_print("No hay una secuencia activa.")
            show_message("Error", "No hay una secuencia activa.")
            return

        te = hiero.ui.getTimelineEditor(seq)
        selected_clips = te.selection()
        debug_print(f"Clips seleccionados: {len(selected_clips)}")

        if len(selected_clips) == 0:
            debug_print("*** No hay clips seleccionados en la pista ***")
            show_message("Error", "No hay clips seleccionados.")
            return

        for shot in selected_clips:
            if isinstance(shot, hiero.core.EffectTrackItem):
                debug_print("Ignorando clip de tipo EffectTrackItem")
                continue
            try:
                debug_print("Procesando clip...")
                file_path = shot.source().mediaSource().fileinfos()[0].filename() if shot.source().mediaSource().fileinfos() else None
                if not file_path:
                    debug_print("No se encontro el path del archivo del clip.")
                    continue
                debug_print(f"Path del archivo encontrado: {file_path}")
                
                project_path = get_project_path(file_path)
                script_name = get_script_name(file_path)
                script_full_path = os.path.join(project_path, script_name)
                debug_print(f"Ruta completa del script: {script_full_path}")

                if os.path.exists(script_full_path):
                    debug_print("El script existe, verificando versiones...")
                    # Verificar si hay una version mas reciente
                    latest_version, latest_path = find_latest_version(script_full_path)
                    current_version = get_version_from_filename(script_name)
                    debug_print(f"Version actual: {current_version}, Version mas reciente: {latest_version}")
                    
                    if latest_version and latest_version > current_version:
                        debug_print("Se encontro una version mas reciente")
                        if show_version_dialog(f"v{current_version:02d}", f"v{latest_version:02d}", script_full_path, latest_path):
                            debug_print("Usuario eligio abrir la version mas reciente")
                            script_full_path = latest_path
                    
                    debug_print(f"Abriendo script: {script_full_path}")
                    open_nuke_script(script_full_path)
                else:
                    debug_print(f"El script no existe en: {script_full_path}")
                    formatted_message = "<div style='text-align: left;'><b>Archivo no encontrado</b><br><br>" + script_full_path + "</div>"
                    show_message("Error", formatted_message)
                return
            except AttributeError as e:
                debug_print(f"El clip no tiene una fuente valida: {e}")
            except Exception as e:
                debug_print(f"Error procesando el clip: {e}")

        show_message("Error", "No se encontro un clip valido.")
    except Exception as e:
        debug_print(f"Error durante la operacion: {e}")

if __name__ == "__main__":
    main()
