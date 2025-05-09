import json
import os
import shotgun_api3
from datetime import datetime

class ShotGridManager:
    """Clase para manejar operaciones en ShotGrid."""
    def __init__(self, url, login, password):
        self.sg = shotgun_api3.Shotgun(url, login=login, password=password)

    def find_project_shots(self, project_name):
        """Encuentra todos los shots en un proyecto especifico."""
        projects = self.sg.find("Project", [['name', 'is', project_name]], ['id', 'name'])
        if projects:
            project_id = projects[0]['id']
            filters = [
                ['project', 'is', {'type': 'Project', 'id': project_id}]
            ]
            fields = ['id', 'code', 'sg_sequence.Sequence.code']
            return self.sg.find("Shot", filters, fields)
        else:
            return []

    def find_tasks_for_shot(self, shot_id):
        """Encuentra las tareas asociadas a un shot."""
        filters = [['entity', 'is', {'type': 'Shot', 'id': shot_id}]]
        fields = ['id', 'content', 'description', 'sg_status_list']
        return self.sg.find("Task", filters, fields)

    def find_versions_for_shot(self, shot_id):
        """Encuentra todas las versiones asociadas a un shot."""
        filters = [['entity', 'is', {'type': 'Shot', 'id': shot_id}]]
        fields = ['code', 'description', 'created_at', 'sg_status_list']
        versions = self.sg.find("Version", filters, fields)
        return [v for v in versions if "_comp_" in v['code'].lower()]

def main():
    project_names = ["EHQALPV", "PORH"]  # Lista de proyectos a procesar
    output_data = {"projects": []}

    for project_name in project_names:
        sg_url = os.getenv('SHOTGRID_URL')
        sg_login = os.getenv('SHOTGRID_LOGIN')
        sg_password = os.getenv('SHOTGRID_PASSWORD')

        if not sg_url or not sg_login or not sg_password:
            print("Las variables de entorno SHOTGRID_URL, SHOTGRID_LOGIN y SHOTGRID_PASSWORD deben estar configuradas.")
            return

        sg_manager = ShotGridManager(sg_url, sg_login, sg_password)
        shots = sg_manager.find_project_shots(project_name)

        project_data = {"project_name": project_name, "shots": []}
        
        for shot in shots:
            shot_data = {"shot_name": shot['code'], "sequence": shot['sg_sequence.Sequence.code'] if 'sg_sequence.Sequence.code' in shot else 'Unknown', "tasks": []}
            tasks = sg_manager.find_tasks_for_shot(shot['id'])
            
            for task in tasks:
                if 'Comp' in task['content']:
                    task_data = {"task_type": "Comp", "task_description": task.get('description', 'Sin descripcion'), "task_status": task.get('sg_status_list', 'Sin estado'), "versions": []}
                    versions = sg_manager.find_versions_for_shot(shot['id'])
                    
                    for version in versions:
                        version_data = {"version_number": version['code'], "version_description": version.get('description', 'Sin descripcion'), "version_status": version['sg_status_list'], "version_date": version['created_at'].isoformat() if version['created_at'] else "Unknown"}
                        task_data["versions"].append(version_data)
                    
                    shot_data["tasks"].append(task_data)
            
            project_data["shots"].append(shot_data)

        output_data["projects"].append(project_data)

    # Escribir los datos en un archivo JSON
    output_file = 'T:/LGA_Cache.json'
    with open(output_file, 'w') as file:
        json.dump(output_data, file, indent=4)

    print("Proceso completado. JSON generado con exito.")

if __name__ == "__main__":
    main()
