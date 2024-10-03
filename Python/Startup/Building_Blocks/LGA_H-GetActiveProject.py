import hiero.core

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
    # Obtener el nombre del proyecto activo
    proj_name = project.name()

    # Imprimir el nombre del proyecto activo
    print("El proyecto activo es:", proj_name)
else:
    print("No se encontro un proyecto activo en Hiero.")
