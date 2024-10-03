import shotgun_api3

# Configuracion de acceso a ShotGrid
# Obtener el usuario y la contrasena de las variables de entorno
sg_url = os.getenv('SHOTGRID_URL')
sg_login = os.getenv('SHOTGRID_LOGIN')
sg_password = os.getenv('SHOTGRID_PASSWORD')

if not sg_url or not sg_login or not sg_password:
    print("Las variables de entorno SHOTGRID_URL, SHOTGRID_LOGIN y SHOTGRID_PASSWORD deben estar configuradas.")
    exit()

sg = shotgun_api3.Shotgun(sg_url, login=sg_login, password=sg_password)

# Nombre del proyecto
project_name = "EHQALPV"  # Ajusta esto si el nombre de tu proyecto es diferente

# Buscar informacion del proyecto
projects = sg.find("Project", [['name', 'is', project_name]], ['id', 'name'])
if not projects:
    print("No se encontro el proyecto.")
else:
    project_id = projects[0]['id']
    print(f"Proyecto encontrado: ID={project_id}, Nombre={projects[0]['name']}")

    # Imprimir informacion adicional sobre el proyecto si necesaria
    project_info = sg.find_one("Project", [['id', 'is', project_id]], ['sg_description', 'sg_status'])
    if project_info:
        print(f"Descripcion: {project_info.get('sg_description', 'No especificada')}")
        print(f"Estado: {project_info.get('sg_status', 'No especificado')}")

    # Listar todos los shots asociados a este proyecto
    print("\nShots en el proyecto:")
    shots = sg.find("Shot", [['project', 'is', {'type': 'Project', 'id': project_id}]], ['id', 'code', 'description'])
    if shots:
        for shot in shots:
            print(f"ID: {shot['id']}, Codigo: {shot['code']}, Descripcion: {shot['description']}")
    else:
        print("No se encontraron shots en este proyecto.")