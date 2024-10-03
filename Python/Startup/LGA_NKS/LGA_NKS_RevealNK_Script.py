"""
___________________________________________________________________________________

  LGA_NKS_RevealNK_Script v1.0 - 2024 - Lega
  Revela el script NKS asociado al clip seleccionado en el explorador de archivos
___________________________________________________________________________________

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

def get_project_path(file_path):
    # Dividir el path en partes usando '/' como separador
    path_parts = file_path.split('/')
    # Construir la nueva ruta agregando '/Comp/1_projects'
    project_path = '/'.join(path_parts[:4]) + '/Comp/1_projects'
    return project_path

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
            return
        else:
            for shot in selected_clips:
                if isinstance(shot, hiero.core.EffectTrackItem):  # Verificar si es un efecto
                    pass  
                else:
                    # Obtener el file path del clip seleccionado
                    file_path = shot.source().mediaSource().fileinfos()[0].filename() if shot.source().mediaSource().fileinfos() else None
                    if file_path:
                        debug_print(f"Path original del archivo: {file_path}")

                        # Obtener la nueva ruta del proyecto
                        project_path = get_project_path(file_path)
                        
                        # Asegurarnos de que la ruta termina con '/'
                        if not project_path.endswith('/'):
                            project_path += '/'
                        
                        debug_print(f"Ruta del proyecto: {project_path}")

                        # Abre el explorador de archivos en la nueva ruta del proyecto
                        open_file_explorer(project_path)
    except Exception as e:
        debug_print(f"Error: {e}")
