"""
FPT_Print_EveryShot_Info.py
Script para obtener todos los tasks asignados al usuario actual en ShotGrid
Incluye: shot, proyecto, estado, descripción y asignados
"""

import os
import shotgun_api3
import time

def connect_to_shotgrid():
    # Obtener credenciales de las variables de entorno
    sg_url = os.getenv('SHOTGRID_URL')
    sg_login = os.getenv('SHOTGRID_LOGIN')
    sg_password = os.getenv('SHOTGRID_PASSWORD')
    
    if not sg_url or not sg_login or not sg_password:
        print("Las variables de entorno SHOTGRID_URL, SHOTGRID_LOGIN y SHOTGRID_PASSWORD deben estar configuradas.")
        return None
    
    return shotgun_api3.Shotgun(sg_url, login=sg_login, password=sg_password)

def get_user_id(sg, user_login):
    # Obtener el ID del usuario usando su login
    filters = [['login', 'is', user_login]]
    fields = ['id']
    user = sg.find_one("HumanUser", filters, fields)
    return user['id'] if user else None

def get_assigned_tasks(sg, user_id):
    # Obtener todos los tasks asignados al usuario usando su ID
    # Excluyendo proyectos archivados
    filters = [
        ['task_assignees', 'is', {'type': 'HumanUser', 'id': user_id}]
    ]
    fields = [
        'id',
        'content',
        'sg_status_list',
        'sg_description',
        'sg_estimated_days',
        'entity',  # Para obtener el shot asociado
        'entity.Shot.code',  # Código del shot
        'entity.Shot.sg_status_list',  # Estado del shot
        'entity.Shot.project.Project.name',  # Nombre del proyecto
        'entity.Shot.project.Project.sg_project_status',  # Estado del proyecto
        'entity.Shot.image',  # Thumbnail del shot
        'task_assignees'  # Asignados (por si hay más de uno)
    ]
    # Excluir proyectos archivados
    return sg.find("Task", filters, fields, include_archived_projects=False)

def get_latest_version_and_notes(sg, shot_id):
    # Obtener la última versión y sus notas en un solo request
    filters = [['entity', 'is', {'type': 'Shot', 'id': shot_id}]]
    fields = [
        'id',
        'code',
        'sg_status_list',
        'description',
        'created_at',
        'user',
        'notes.content',  # Obtener notas directamente
        'notes.user'
    ]
    # Ordenar por fecha descendente y limitar a 1 resultado
    order = [{'field_name': 'created_at', 'direction': 'desc'}]
    version = sg.find_one("Version", filters, fields, order)
    
    if version:
        # Extraer notas de la versión
        version['notes'] = version.get('notes', [])
    return version

def print_task_info(task, sg):
    # Imprimir información del task
    print(f"\nTask: {task['content']}")
    print(f"  Status: {task['sg_status_list']}")
    print(f"  Description: {task.get('sg_description', 'No description available')}")
    print(f"  Estimated Duration: {task.get('sg_estimated_days', 'No estimate available')} days")
    
    # Imprimir asignados
    if task.get('task_assignees'):
        print("  Assigned To:")
        for assignee in task['task_assignees']:
            print(f"    - {assignee.get('name', 'Unknown')}")
    else:
        print("  No asignados encontrados.")
    
    # Imprimir información del shot
    if task.get('entity') and task['entity'].get('type') == 'Shot':
        shot_code = task.get('entity.Shot.code', 'No shot code')
        shot_status = task.get('entity.Shot.sg_status_list', 'No status')
        project_name = task.get('entity.Shot.project.Project.name', 'No project')
        project_status = task.get('entity.Shot.project.Project.sg_project_status', 'No status')
        shot_description = task.get('entity.Shot.description', 'No description available')
        shot_thumbnail = task.get('entity.Shot.image', None)
        
        print(f"  Shot: {shot_code}")
        print(f"    Shot Status: {shot_status}")
        print(f"    Project: {project_name}")
        print(f"    Project Status: {project_status}")
        print(f"    Description: {shot_description}")
        
        # Mostrar el thumbnail si está disponible
        if shot_thumbnail:
            print(f"    Thumbnail: {shot_thumbnail}")
        else:
            print("    No thumbnail disponible.")
        
        # Obtener la última versión y sus notas
        latest_version = get_latest_version_and_notes(sg, task['entity']['id'])
        if latest_version:
            print("\n  Última versión:")
            print(f"    - Version SG: {latest_version.get('code', 'No version code')}")
            print(f"      Status: {latest_version.get('sg_status_list', 'No status')}")
            print(f"      Description: {latest_version.get('description', 'No description')}")
            print(f"      Created At: {latest_version.get('created_at', 'No date available')}")
            print(f"      User: {latest_version['user']['name'] if latest_version.get('user') else 'No user available'}")
            
            # Mostrar notas
            if latest_version.get('notes'):
                print("      Comments:")
                for note in latest_version['notes']:
                    print(f"        - {note['content']} (User: {note['user']['name']})")
            else:
                print("      No comments found.")
        else:
            print("\n  No se encontraron versiones asociadas.")
    else:
        print("  No se encontró un shot asociado.")
    
    print(f"  URL: {sg.base_url}/detail/Task/{task['id']}")

def main():
    # Iniciar el temporizador
    start_time = time.time()
    
    # Conectar a ShotGrid
    sg = connect_to_shotgrid()
    if not sg:
        return
    
    # Especificar el login del usuario que queremos consultar
    user_login = os.getenv('SHOTGRID_LOGIN')  # Usar el mismo login que para la conexión
    
    # Obtener el ID del usuario
    user_id = get_user_id(sg, user_login)
    if not user_id:
        print(f"No se encontró el usuario con login {user_login}")
        return
    
    # Obtener todos los tasks asignados al usuario
    tasks = get_assigned_tasks(sg, user_id)
    if not tasks:
        print(f"No se encontraron tasks asignados a {user_login}")
        return
    
    # Contador de shots
    shot_count = 0
    
    # Imprimir la información de cada task
    print(f"\nTasks asignados a {user_login}:")
    for task in tasks:
        print_task_info(task, sg)
        if task.get('entity') and task['entity'].get('type') == 'Shot':
            shot_count += 1
    
    # Calcular y mostrar el tiempo de ejecución
    end_time = time.time()
    elapsed_time = end_time - start_time
    print(f"\nTiempo total de ejecución: {elapsed_time:.2f} segundos")
    print(f"Total de shots encontrados: {shot_count}")

if __name__ == "__main__":
    main() 