"""
Script para obtener la información completa de un shot específico en ShotGrid
Incluye: proyecto, estado, tareas, versiones y comentarios
solo la última versión.
sin optimizar
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

def get_shot_info(sg, shot_code):
    # Buscar información del shot
    filters = [['code', 'is', shot_code]]
    fields = [
        'id',
        'code',
        'description',
        'sg_status_list',
        'project.Project.name',
        'project.Project.sg_status'
    ]
    return sg.find_one("Shot", filters, fields)

def get_tasks_for_shot(sg, shot_id):
    # Obtener tareas asociadas al shot incluyendo los asignados
    filters = [['entity', 'is', {'type': 'Shot', 'id': shot_id}]]
    fields = [
        'id',
        'content',
        'sg_status_list',
        'sg_description',
        'sg_estimated_days',
        'task_assignees'  # Añadir este campo para obtener los asignados
    ]
    return sg.find("Task", filters, fields)

def get_latest_version_for_shot(sg, shot_id):
    # Obtener la última versión ordenando por fecha descendente
    filters = [['entity', 'is', {'type': 'Shot', 'id': shot_id}]]
    fields = [
        'id',
        'code',
        'sg_status_list',
        'description',
        'created_at',
        'user'
    ]
    # Ordenar por fecha de creación descendente y limitar a 1 resultado
    order = [{'field_name': 'created_at', 'direction': 'desc'}]
    return sg.find_one("Version", filters, fields, order)

def get_version_notes(sg, version_id):
    # Obtener notas asociadas a una versión
    filters = [['note_links', 'in', {'type': 'Version', 'id': version_id}]]
    fields = ['content', 'user']
    return sg.find("Note", filters, fields)

def print_task_info(task, sg):
    # Imprimir información de la tarea incluyendo los asignados
    print(f"  - Task: {task['content']}")
    print(f"    Status: {task['sg_status_list']}")
    print(f"    Description: {task.get('sg_description', 'No description available')}")
    print(f"    Estimated Duration: {task.get('sg_estimated_days', 'No estimate available')} days")
    
    # Imprimir asignados
    if task.get('task_assignees'):
        print("    Assigned To:")
        for assignee in task['task_assignees']:
            print(f"      - {assignee.get('name', 'Unknown')}")
    else:
        print("    No asignados encontrados.")
    
    print(f"    URL: {sg.base_url}/detail/Task/{task['id']}")

def print_shot_info(shot, tasks, version, sg):
    print(f"\nInformación del Shot:")
    print(f"Project: {shot['project.Project.name']}")
    print(f"Project Status: {shot['project.Project.sg_status']}")
    print(f"Shot: {shot['code']}")
    print(f"Shot Status: {shot['sg_status_list']}")
    print(f"Description: {shot.get('description', 'No description available')}")
    
    # Imprimir tareas
    if tasks:
        print("\nTareas asociadas:")
        for task in tasks:
            print_task_info(task, sg)
    else:
        print("\nNo se encontraron tareas asociadas.")
    
    # Imprimir la última versión
    if version:
        print("\nÚltima versión:")
        print(f"  - Version SG: {version.get('code', 'No version code')}")
        print(f"    Status: {version.get('sg_status_list', 'No status')}")
        print(f"    Description: {version.get('description', 'No description')}")
        print(f"    Created At: {version.get('created_at', 'No date available')}")
        print(f"    User: {version['user']['name'] if version.get('user') else 'No user available'}")
        
        # Obtener y mostrar notas
        notes = get_version_notes(sg, version['id'])
        if notes:
            print("    Comments:")
            for note in notes:
                print(f"      - {note['content']} (User: {note['user']['name']})")
        else:
            print("    No comments found.")
    else:
        print("\nNo se encontraron versiones asociadas.")

def main():
    # Iniciar el temporizador
    start_time = time.time()
    
    # Conectar a ShotGrid
    sg = connect_to_shotgrid()
    if not sg:
        return
    
    # Especificar el código del shot que queremos consultar
    shot_code = "EHQALPV_089_032_Luz_Reni"  # Cambiar por el shot que quieras consultar
    
    # Obtener la información
    shot = get_shot_info(sg, shot_code)
    if not shot:
        print(f"No se encontró el shot {shot_code}")
        return
    
    tasks = get_tasks_for_shot(sg, shot['id'])
    latest_version = get_latest_version_for_shot(sg, shot['id'])
    
    # Imprimir la información
    print_shot_info(shot, tasks, latest_version, sg)
    
    # Calcular y mostrar el tiempo de ejecución
    end_time = time.time()
    elapsed_time = end_time - start_time
    print(f"\nTiempo total de ejecución: {elapsed_time:.2f} segundos")

if __name__ == "__main__":
    main() 