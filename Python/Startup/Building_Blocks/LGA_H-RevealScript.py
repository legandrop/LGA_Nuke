import hiero.core
import hiero.ui
import os

# Funcion para obtener la ruta del proyecto
def get_project_path(file_path):
    # Dividir el path en partes usando '/' como separador
    path_parts = file_path.split('/')
    # Construir la nueva ruta agregando '/Comp/1_projects'
    project_path = '/'.join(path_parts[:4]) + '/Comp/1_projects'
    return project_path

# Obtener la secuencia activa y el editor de linea de tiempo
seq = hiero.ui.activeSequence()
if seq:  # Asegurarse de que hay una secuencia activa
    te = hiero.ui.getTimelineEditor(seq)
    selected_clips = te.selection()

    # Iterar sobre los clips seleccionados para hacer el "reveal in explorer"
    for shot in selected_clips:
        file_path = shot.source().mediaSource().fileinfos()[0].filename()
        print("Original file path:", file_path)

        # Obtener la nueva ruta del proyecto
        project_path = get_project_path(file_path)
        print("Project path:", project_path)

        # Abre el explorador de archivos en la nueva ruta del proyecto
        try:
            os.startfile(project_path)
            print("Revealed in explorer successfully.")
        except:
            print("Error revealing in explorer.")
else:
    print("No active sequence found.")
