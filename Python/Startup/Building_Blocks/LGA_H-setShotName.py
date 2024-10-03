import hiero.core
import hiero.ui
import os

# Funcion para obtener el shot name a partir del path del clip
def get_shot_name(file_path):
    # Dividir el path en partes usando '/' como separador
    path_parts = file_path.split('/')
    # El shot name seria la tercera parte del path
    shot_name = path_parts[3]
    return shot_name

# Obtener la secuencia activa y el editor de linea de tiempo
seq = hiero.ui.activeSequence()
if seq:  # Asegurarse de que hay una secuencia activa
    te = hiero.ui.getTimelineEditor(seq)
    selected_clips = te.selection()

    # Iterar sobre los clips seleccionados para cambiar el nombre del plano
    for shot in selected_clips:
        file_path = shot.source().mediaSource().fileinfos()[0].filename()
        print("Original file path:", file_path)

        # Obtener el shot name del path del clip
        shot_name = get_shot_name(file_path)
        print("Shot name:", shot_name)

        # Cambiar el nombre del plano al clip seleccionado
        shot.setName(shot_name)
        print("Shot name changed successfully.")

else:
    print("No active sequence found.")
