# Chequea que exista un script con el mismo nombre que el clip selecionado

import hiero.core
import hiero.ui
import os
import re  # Importar el modulo de expresiones regulares

# Funcion para obtener la ruta del proyecto
def get_project_path(file_path):
    # Dividir el path en partes usando '/' como separador
    path_parts = file_path.split('/')
    # Construir la nueva ruta agregando '/Comp/1_projects'
    project_path = '/'.join(path_parts[:4]) + '/Comp/1_projects'
    return project_path

# Funcion para obtener el nombre del archivo del script relacionado con el clip
def get_script_name(file_path):
    # Extraer el nombre del archivo del path completo
    script_name = os.path.basename(file_path)
    # Eliminar la extension y cualquier secuencia de frame como %04d
    script_name = re.sub(r'_%\d+?d\.exr$', '', script_name)  # Ajusta la expresion regular segun necesidad
    return script_name + '.nk'  # Anadir la extension correcta de Nuke

# Funcion para verificar si el archivo existe y reportar
def check_file_existence(path, file_name):
    full_path = os.path.join(path, file_name)
    if os.path.exists(full_path):
        return f"El archivo {file_name} existe en {path}."
    else:
        return f"El archivo {file_name} no existe en {path}."

# Obtener la secuencia activa y el editor de linea de tiempo
seq = hiero.ui.activeSequence()
if seq:  # Asegurarse de que hay una secuencia activa
    te = hiero.ui.getTimelineEditor(seq)
    selected_clips = te.selection()

    # Iterar sobre los clips seleccionados
    for shot in selected_clips:
        file_path = shot.source().mediaSource().fileinfos()[0].filename()
        print("Original file path:", file_path)

        # Obtener la nueva ruta del proyecto
        project_path = get_project_path(file_path)
        print("Project path:", project_path)

        # Obtener e imprimir el nombre del script relacionado
        script_name = get_script_name(file_path)
        print("Script name:", script_name)

        # Verificar y reportar si el archivo existe
        existence_message = check_file_existence(project_path, script_name)
        print(existence_message)
else:
    print("No active sequence found.")
