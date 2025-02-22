import os
import shotgun_api3

# Recuperar datos de autenticacion de las variables de entorno
url = os.environ.get("SHOTGRID_URL")
login = os.environ.get("SHOTGRID_LOGIN")
password = os.environ.get("SHOTGRID_PASSWORD")

# Crear instancia de la API de ShotGrid
sg = shotgun_api3.Shotgun(url, login=login, password=password)

# Buscar el proyecto ETDM
try:
    # Filtrar por nombre del proyecto y obtener ID y estado
    filters = [['name', 'is', 'ETDM']]
    fields = ['id', 'sg_project_status']
    
    # Obtener el proyecto
    project = sg.find_one("Project", filters, fields)
    
    if project:
        print(f"ID del proyecto ETDM: {project['id']}")
        print(f"Estado del proyecto ETDM: {project.get('sg_project_status', 'Estado no disponible')}")
    else:
        print("Proyecto ETDM no encontrado")
except Exception as e:
    print(f"Error al buscar el proyecto: {e}") 