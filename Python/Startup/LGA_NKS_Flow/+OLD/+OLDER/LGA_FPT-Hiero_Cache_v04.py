import json
import os
import sys
from datetime import datetime
import shotgun_api3
from deepdiff import DeepDiff  # Para comparar diccionarios de JSON
import logging
from datetime import datetime

# Configuracion de logging
logging.basicConfig(filename='T:/LGA_Cache.log', level=logging.INFO, format='%(message)s')
                    
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
            fields = ['id', 'code', 'description', 'sg_sequence.Sequence.code']
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
        fields = ['code', 'description', 'created_at', 'user', 'sg_status_list']
        versions = self.sg.find("Version", filters, fields)
        return [v for v in versions if "_comp_" in v['code'].lower()]

class HieroOperations:
    """Clase para manejar operaciones en Hiero."""
    def __init__(self, shotgrid_manager):
        self.sg_manager = shotgrid_manager

    def process_all_shots(self, output_file):
        """Procesa todos los shots en el proyecto especificado y guarda la informacion en un archivo JSON."""
        start_time = datetime.now()
        logging.info("____________________________\n")
        logging.info(f"Starting synchronization with SG. Current date and time: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        logging.info("____________________________\n")

        project_name = "EHQALPV"
        shots = self.sg_manager.find_project_shots(project_name)
        project_data = {
            "project_name": project_name,
            "shots": []
        }
        for shot in shots:
            shot_data = {
                "shot_name": shot['code'],
                "sequence": shot['sg_sequence.Sequence.code'] if 'sg_sequence.Sequence.code' in shot else 'Unknown',
                "tasks": []
            }
            tasks = self.sg_manager.find_tasks_for_shot(shot['id'])
            for task in tasks:
                if 'Comp' in task['content']:
                    task_data = {
                        "task_type": "Comp",
                        "task_description": task.get('description', 'Sin descripcion'),
                        "task_status": task.get('sg_status_list', 'Sin estado'),
                        "versions": []
                    }
                    versions = self.sg_manager.find_versions_for_shot(shot['id'])
                    for version in versions:
                        version_data = {
                            "version_number": version['code'],
                            "version_description": version.get('description', 'Sin descripcion'),
                            "version_status": version['sg_status_list'],
                            "version_date": version['created_at'].isoformat() if version['created_at'] else "Unknown"
                        }
                        task_data["versions"].append(version_data)
                    shot_data["tasks"].append(task_data)
            project_data["shots"].append(shot_data)
            
        # Cargar el archivo JSON existente si esta disponible
        old_data = {}
        if os.path.exists(output_file):
            with open(output_file, 'r') as file:
                old_data = json.load(file)

        diff = DeepDiff(old_data, project_data, ignore_order=True)
        if diff:
            for key, value in diff.items():
                if 'values_changed' in key:
                    for change in value:
                        path = change.split("root['shots'][")[1].split(']')[0]
                        change_desc = value[change]['new_value']
                        logging.info(f"Shot name: {project_data['shots'][int(path)]['shot_name']}")
                        for task in project_data['shots'][int(path)]['tasks']:
                            logging.info(f"Task: {task['task_type']}")
                            logging.info(f"Task_status: {task['task_status']}")
                            for version in task['versions']:
                                logging.info(f"Version uploaded: {version['version_number']}")
                                logging.info(f"Version description: {version['version_description'] or 'None'}")
                                logging.info(f"Version status: {version['version_status']}")
                                logging.info("____________________________\n")
        else:
            logging.info("No changes detected.\n")

        with open(output_file, 'w') as file:
            json.dump(project_data, file, indent=4)

        end_time = datetime.now()
        elapsed_time = end_time - start_time
        logging.info("Finished synchronization with SG. Current date and time: {}".format(end_time.strftime("%Y-%m-%d %H:%M:%S")))
        logging.info(f"Total sync time: {elapsed_time}")
        logging.info("____________________________\n")


def main():
    global msg_manager
    sg_url = os.getenv('SHOTGRID_URL')
    sg_login = os.getenv('SHOTGRID_LOGIN')
    sg_password = os.getenv('SHOTGRID_PASSWORD')

    if not sg_url or not sg_login or not sg_password:
        print("Las variables de entorno SHOTGRID_URL, SHOTGRID_LOGIN y SHOTGRID_PASSWORD deben estar configuradas.")
        return

    sg_manager = ShotGridManager(sg_url, sg_login, sg_password)
    hiero_ops = HieroOperations(sg_manager)
    output_file = 'T:/LGA_Cache.json'
    hiero_ops.process_all_shots(output_file)

if __name__ == "__main__":
    main()
