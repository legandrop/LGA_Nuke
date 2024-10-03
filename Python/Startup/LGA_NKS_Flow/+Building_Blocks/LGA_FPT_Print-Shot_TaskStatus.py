import os
import shotgun_api3

# Obtener el usuario y la contrasena de las variables de entorno
sg_url = os.getenv('SHOTGRID_URL')
sg_login = os.getenv('SHOTGRID_LOGIN')
sg_password = os.getenv('SHOTGRID_PASSWORD')

if not sg_url or not sg_login or not sg_password:
    print("Las variables de entorno SHOTGRID_URL, SHOTGRID_LOGIN y SHOTGRID_PASSWORD deben estar configuradas.")
    exit()

sg = shotgun_api3.Shotgun(sg_url, login=sg_login, password=sg_password)

# Nombre del archivo EXR
exr = "EHQALPV_001_010_SombraOvni_Aparece_comp_v05"

# Extraer el codigo del shot del nombre del archivo EXR
parts = exr.split('_')
shot_code = '_'.join(parts[:5])  # Esto construira "EHQALPV_001_010_SombraOvni_Aparece"

# Encuentra el proyecto por nombre
project_name = "EHQALPV"  # Asumiendo que el nombre del proyecto es el prefijo comun
projects = sg.find("Project", [['name', 'is', project_name]], ['id', 'name'])
if not projects:
    print("No se encontro el proyecto.")
else:
    project_id = projects[0]['id']

    # Buscar el shot correspondiente
    filters = [
        ['project', 'is', {'type': 'Project', 'id': project_id}],
        ['code', 'is', shot_code]
    ]
    fields = ['id', 'code', 'description']
    shots = sg.find("Shot", filters, fields)
    if not shots:
        print("No se encontro el shot.")
    else:
        shot_id = shots[0]['id']
        print(f"Encontrado shot: {shots[0]['code']} con descripcion: {shots[0]['description']}")

        # Obtener todas las tareas asociadas a ese shot
        task_filters = [
            ['entity', 'is', {'type': 'Shot', 'id': shot_id}]
        ]
        task_fields = ['id', 'content', 'sg_status_list']
        tasks = sg.find("Task", task_filters, task_fields)
        if tasks:
            print("Tareas encontradas:")
            for task in tasks:
                print(f"Task: {task['content']}, Estado: {task['sg_status_list']}")
        else:
            print("No hay tareas asignadas a este shot.")
