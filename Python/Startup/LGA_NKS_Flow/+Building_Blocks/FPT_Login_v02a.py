# Usando variables de entorno

import os
import shotgun_api3

# Configurar las variables de entorno manualmente para esta prueba
os.environ['SHOTGRID_URL'] = "https://wanka.shotgrid.autodesk.com"
os.environ['SHOTGRID_SCRIPT_NAME'] = "Support"
os.environ['SHOTGRID_API_KEY'] = "blabla"

# Recuperar datos de autenticacion de las variables de entorno
url = os.environ.get("SHOTGRID_URL")
script_name = os.environ.get("SHOTGRID_SCRIPT_NAME")
api_key = os.environ.get("SHOTGRID_API_KEY")

# Crear una instancia de la API de ShotGrid
sg = shotgun_api3.Shotgun(url, script_name, api_key)

# Intentar recuperar una lista de proyectos para probar la conexion
try:
    projects = sg.find("Project", [], ['id', 'name'])
    print("Conexion exitosa. Aqui estan algunos de tus proyectos:")
    for project in projects:
        print(f"{project['id']}: {project['name']}")
except Exception as e:
    print(f"Error al conectar con ShotGrid: {e}")
