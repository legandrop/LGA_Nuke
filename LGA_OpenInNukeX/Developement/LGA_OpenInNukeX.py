import socket
import sys
import os
import subprocess
import tkinter as tk
from tkinter import messagebox

def show_message(message):
    root = tk.Tk()
    root.withdraw()  # Oculta la ventana raiz
    messagebox.showinfo("Resultado", message)
    root.destroy()


def get_nuke_path_from_file():
    # Obtiene la ruta del directorio donde se encuentra el ejecutable.
    directory_of_exe = os.path.dirname(sys.executable)
    filepath = os.path.join(directory_of_exe, 'nukeXpath.txt')
    
    try:
        with open(filepath, 'r') as file:
            return file.readline().strip()
    except FileNotFoundError as e:
        show_message(f"Error: Nuke path file not found in the executable's directory. {e}")
        return None
    except Exception as e:
        show_message(f"Error reading Nuke path from file: {e}")
        return None

def open_nuke_with_file(nuke_executable_path, nk_filepath):
    # Crea un comando para abrir Nuke con el archivo .nk
    command = f'"{nuke_executable_path}" --nukex "{nk_filepath}"'
    try:
        subprocess.Popen(command, shell=True)  # Abre NukeX con el archivo .nk
    except Exception as e:
        show_message(f"Failed to open Nuke with the file: {e}")



def send_to_nuke(filepath, host='localhost', port=54325):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(10)
        try:
            s.connect((host, port))
            # Normaliza la ruta del archivo
            normalized_path = os.path.normpath(filepath).replace('\\', '/')
            full_command = f"run_script||{normalized_path}"
            s.sendall(full_command.encode())
            response = []
            while True:
                part = s.recv(1024)
                if not part:
                    break
                response.append(part)
            #show_message(f"Received: {b''.join(response).decode()}")
        except socket.timeout:
            show_message("Connection to Nuke has expired.")
        except ConnectionRefusedError:
            nuke_executable_path = get_nuke_path_from_file()
            if nuke_executable_path:
                #show_message("Could not connect to Nuke. Attempting to open NukeX with the file.")
                open_nuke_with_file(nuke_executable_path, filepath)
            else:
                show_message("Nuke path file not found or unreadable.")
        except ConnectionResetError:
            show_message("The connection was closed by the server.")


# Comprueba si hay argumentos pasados al ejecutable
if len(sys.argv) > 1:
    # El primer argumento es la ruta del archivo
    send_to_nuke(sys.argv[1])
else:
    show_message("No .nk file path was provided.")



