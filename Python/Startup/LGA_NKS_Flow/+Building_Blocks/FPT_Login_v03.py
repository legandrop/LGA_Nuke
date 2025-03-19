# Igual que el v02a pero Usando variables de entorno de usuario y pass en vez de script
# y con la posibilidad de obtener el grupo de permisos del usuario

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
    
    # Obtener informacion del usuario actual
    current_user = sg.find_one("HumanUser", [['login', 'is', login]], ['permission_rule_set'])
    
    if current_user and 'permission_rule_set' in current_user:
        # Obtener el nombre del grupo de permisos
        permission_group = sg.find_one("PermissionRuleSet", 
                                     [['id', 'is', current_user['permission_rule_set']['id']]], 
                                     ['code'])
        if permission_group:
            print(f"\nTu grupo de permisos es: {permission_group['code']}")
        else:
            print("\nNo se pudo determinar tu grupo de permisos")
    else:
        print("\nNo se encontraron grupos de permisos para este usuario")

except Exception as e:
    print(f"Error al conectar con ShotGrid: {e}")
