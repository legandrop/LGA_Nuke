import hiero.core
import os

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

# Obtener el proyecto activo
project = get_active_project()

if project:
    # Obtener el directorio del proyecto activo
    project_path = project.path()

    # Imprimir el directorio del proyecto activo
    print("El directorio del proyecto activo es:", project_path)

    # Abre el explorador de archivos en el directorio del proyecto
    try:
        os.startfile(os.path.dirname(project_path))
        print("Revealed in explorer successfully.")
    except:
        print("Error revealing in explorer.")
else:
    print("No se encontro un proyecto activo en Hiero.")
