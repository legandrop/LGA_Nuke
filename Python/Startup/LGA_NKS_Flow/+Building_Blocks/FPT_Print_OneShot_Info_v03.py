"""
Script para obtener la información completa de un shot específico en ShotGrid
Incluye: proyecto, estado, tareas, versiones y comentarios
optimizado v01 (no esta bajando las tasks)
"""

import os
import shotgun_api3
import time  # Para medir el tiempo de ejecución

def connect_to_shotgrid():
    # Obtener credenciales de las variables de entorno
    sg_url = os.getenv('SHOTGRID_URL')
    sg_login = os.getenv('SHOTGRID_LOGIN')
    sg_password = os.getenv('SHOTGRID_PASSWORD')
    
    if not sg_url or not sg_login or not sg_password:
        print("Las variables de entorno SHOTGRID_URL, SHOTGRID_LOGIN y SHOTGRID_PASSWORD deben estar configuradas.")
        return None
    
    return shotgun_api3.Shotgun(sg_url, login=sg_login, password=sg_password)

def get_shot_and_tasks(sg, shot_code):
    # Obtener el shot y sus tareas en un solo request
    filters = [['code', 'is', shot_code]]
    fields = [
        'id',
        'code',
        'description',
        'sg_status_list',
        'project.Project.name',
        'project.Project.sg_status',  # Cambiado de sg_status_list a sg_status
        'image',  # Thumbnail del shot
        'tasks.content',  # Obtener el contenido de las tareas
        'tasks.sg_status_list',
        'tasks.sg_description',
        'tasks.sg_estimated_days',
        'tasks.task_assignees'
    ]
    return sg.find_one("Shot", filters, fields)

def get_latest_version(sg, shot_id):
    # Obtener la última versión asociada al shot
    filters = [['entity', 'is', {'type': 'Shot', 'id': shot_id}]]
    fields = [
        'id',
        'code',
        'sg_status_list',
        'description',
        'created_at',
        'user'
    ]
    # Ordenar por fecha descendente y limitar a 1 resultado
    order = [{'field_name': 'created_at', 'direction': 'desc'}]
    return sg.find_one("Version", filters, fields, order)

def get_version_notes(sg, version_id):
    # Obtener notas asociadas a una versión
    filters = [['note_links', 'in', {'type': 'Version', 'id': version_id}]]
    fields = ['content', 'user']
    return sg.find("Note", filters, fields)

def print_shot_info(shot_data, latest_version, sg):
    print(f"\nInformación del Shot:")
    print(f"Project: {shot_data['project.Project.name']}")
    print(f"Project Status: {shot_data['project.Project.sg_status']}")  # Status del proyecto
    print(f"Shot: {shot_data['code']}")
    print(f"Shot Status: {shot_data['sg_status_list']}")
    print(f"Description: {shot_data.get('description', 'No description available')}")
    
    # Mostrar el thumbnail si está disponible
    if shot_data.get('image'):
        print(f"Thumbnail: {shot_data['image']}")
    else:
        print("No thumbnail disponible.")
    
    # Imprimir tareas
    if shot_data.get('tasks'):
        print("\nTareas asociadas:")
        for task in shot_data['tasks']:
            print(f"  - Task: {task.get('content', 'No task name')}")
            print(f"    Status: {task.get('sg_status_list', 'No status')}")
            print(f"    Description: {task.get('sg_description', 'No description available')}")
            print(f"    Estimated Duration: {task.get('sg_estimated_days', 'No estimate available')} days")
            if task.get('task_assignees'):
                print("    Assigned To:")
                for assignee in task['task_assignees']:
                    print(f"      - {assignee.get('name', 'Unknown')}")
            else:
                print("    No asignados encontrados.")
            print(f"    URL: {sg.base_url}/detail/Task/{task['id']}")
    else:
        print("\nNo se encontraron tareas asociadas.")
    
    # Imprimir la última versión
    if latest_version:
        print("\nÚltima versión:")
        print(f"  - Version SG: {latest_version.get('code', 'No version code')}")
        print(f"    Status: {latest_version.get('sg_status_list', 'No status')}")
        print(f"    Description: {latest_version.get('description', 'No description')}")
        print(f"    Created At: {latest_version.get('created_at', 'No date available')}")
        print(f"    User: {latest_version['user']['name'] if latest_version.get('user') else 'No user available'}")
        
        # Obtener notas de la versión
        notes = get_version_notes(sg, latest_version['id'])
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
    
    # Obtener el shot y sus tareas
    shot_data = get_shot_and_tasks(sg, shot_code)
    if not shot_data:
        print(f"No se encontró el shot {shot_code}")
        return
    
    # Obtener la última versión
    latest_version = get_latest_version(sg, shot_data['id'])
    
    # Imprimir la información
    print_shot_info(shot_data, latest_version, sg)
    
    # Calcular y mostrar el tiempo de ejecución
    end_time = time.time()
    elapsed_time = end_time - start_time
    print(f"\nTiempo total de ejecución: {elapsed_time:.2f} segundos")

if __name__ == "__main__":
    main() 