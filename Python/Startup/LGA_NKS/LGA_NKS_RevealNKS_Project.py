"""
______________________________________________________________

  LGA_NKS_RevealNKS_Project v1.0 - 2024 - Lega
  Revela el proyecto NKS activo en el explorador de archivos
______________________________________________________________

"""

import hiero.core
import hiero.ui
import os
import subprocess

DEBUG = False

def debug_print(*message):
    if DEBUG:
        print(*message)

def open_file_explorer(path):
    if os.name == 'nt':  # Windows
        os.startfile(os.path.dirname(path))
    elif os.name == 'posix':  # macOS
        subprocess.Popen(['open', os.path.dirname(path)])
    else:
        debug_print("Sistema operativo no soportado para abrir el explorador de archivos.")

def get_active_project():
    """
    Obtiene el proyecto activo en Hiero.

    Returns:
    - hiero.core.Project o None: El proyecto activo, o None si no se encuentra ningun proyecto activo.
    """
    projects = hiero.core.projects()
    if projects:
        return projects[0]  # Devuelve el primer proyecto en la lista
    else:
        return None

def main():
    try:
        # Obtener el proyecto activo
        project = get_active_project()
        if project:
            # Obtener el directorio del proyecto activo
            project_path = project.path()

            # Imprimir el directorio del proyecto activo
            debug_print(f"El directorio del proyecto activo es: {project_path}")
            open_file_explorer(project_path)
        else:
            debug_print("No se encontro un proyecto activo en Hiero.")
    except Exception as e:
        debug_print(f"Error: {e}")
