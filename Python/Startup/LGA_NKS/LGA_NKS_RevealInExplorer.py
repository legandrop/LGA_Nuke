"""
______________________________________________________________________

  LGA_NKS_RevealInExplorer v1.0 - 2024 - Lega
  Revela los clips seleccionados en el explorador de archivos
______________________________________________________________________

"""

import hiero.core
import hiero.ui
import os
import subprocess

DEBUG = True

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

def reveal_project():
    """
    Revela el directorio del proyecto activo en el explorador de archivos.
    """
    project = get_active_project()
    if project:
        project_path = project.path()
        debug_print(f"El directorio del proyecto activo es: {project_path}")
        open_file_explorer(project_path)
    else:
        debug_print("No se encontro un proyecto activo en Hiero.")

def main():
    try:
        seq = hiero.ui.activeSequence()
        if not seq:
            debug_print("No hay una secuencia activa.")
            return

        te = hiero.ui.getTimelineEditor(seq)
        selected_clips = te.selection()

        if len(selected_clips) == 0:
            debug_print("*** No hay clips seleccionados en la pista ***")
            reveal_project()
        else:
            for shot in selected_clips:
                if isinstance(shot, hiero.core.EffectTrackItem):  # Verificar si es un efecto
                    pass  
                else:
                    # Obtener el file path del clip seleccionado
                    file_path = shot.source().mediaSource().fileinfos()[0].filename() if shot.source().mediaSource().fileinfos() else None
                    if file_path:
                        debug_print(f"Path original del archivo: {file_path}")
                        open_file_explorer(file_path)
    except Exception as e:
        debug_print(f"Error: {e}")
