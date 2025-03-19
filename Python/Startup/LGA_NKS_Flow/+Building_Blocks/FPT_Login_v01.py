import shotgun_api3

# Tus datos de autenticacion
url = "https://wanka.shotgrid.autodesk.com"
script_name = "Support"
api_key = "blabla"

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
