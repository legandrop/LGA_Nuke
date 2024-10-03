# Igual que el v02a pero Usando variables de entorno de usuario y pass en vez de script

import os
import shotgun_api3

# Recuperar datos de autenticacion de las variables de entorno
url = os.environ.get("SHOTGRID_URL")
login = os.environ.get("SHOTGRID_LOGIN")
password = os.environ.get("SHOTGRID_PASSWORD")

# Verificar que las variables de entorno se recuperen correctamente
print(f"URL: {url}")
print(f"Login: {login}")
print(f"Password: {password}")

# Crear una instancia de la API de ShotGrid usando login y password
sg = shotgun_api3.Shotgun(url, login=login, password=password)

# Intentar recuperar una lista de proyectos para probar la conexion
try:
    projects = sg.find("Project", [], ['id', 'name'])
    print("Conexion exitosa. Aqui estan algunos de tus proyectos:")
    for project in projects:
        print(f"{project['id']}: {project['name']}")
except Exception as e:
    print(f"Error al conectar con ShotGrid: {e}")
