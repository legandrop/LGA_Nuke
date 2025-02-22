import os
import shotgun_api3

# Recuperar datos de autenticacion de las variables de entorno
url = os.environ.get("SHOTGRID_URL")
login = os.environ.get("SHOTGRID_LOGIN")
password = os.environ.get("SHOTGRID_PASSWORD")

# Crear instancia de la API de ShotGrid
sg = shotgun_api3.Shotgun(url, login=login, password=password)

# Listar todos los campos disponibles para el proyecto
try:
    fields = sg.schema_field_read("Project")
    print("Campos disponibles para Project:")
    for field_name, field_info in fields.items():
        print(f"- {field_name} ({field_info['data_type']['value']})")
except Exception as e:
    print(f"Error al obtener los campos: {e}")