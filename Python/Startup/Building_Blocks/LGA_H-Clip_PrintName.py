import hiero.core
import hiero.ui
import os
import re

# Funcion para extraer el nombre base del archivo EXR y el numero de version
def parse_exr_name(file_name):
    # Usar regex para encontrar y extraer el numero de version
    version_match = re.search(r'_v(\d+)', file_name)
    if version_match:
        version_number = version_match.group(1)
    else:
        version_number = 'Unknown'  # Por si no se encuentra la version

    # Remover la parte de version y secuencia de frames del nombre del archivo
    base_name = re.sub(r'_v\d+_%04d\.exr', '', file_name)
    return base_name, version_number

# Obtener la secuencia activa y el editor de linea de tiempo
seq = hiero.ui.activeSequence()
if seq:  # Asegurarse de que hay una secuencia activa
    te = hiero.ui.getTimelineEditor(seq)
    selected_clips = te.selection()

    # Iterar sobre los clips seleccionados para obtener el nombre base y la version del EXR
    if selected_clips:
        for clip in selected_clips:
            file_path = clip.source().mediaSource().fileinfos()[0].filename()
            print("Original file path:", file_path)

            # Extraer el nombre del archivo EXR del path
            exr_name = os.path.basename(file_path)
            print("Full EXR name:", exr_name)

            # Parse the EXR name to extract the base name and version number
            base_name, version_number = parse_exr_name(exr_name)
            print("Base EXR name:", base_name)
            print("Version number:", version_number)
    else:
        print("No clips selected on the timeline.")
else:
    print("No active sequence found.")
