import hiero.core
import os
import re
import shotgun_api3
import sys

class ShotGridManager:
    """Clase para manejar operaciones en ShotGrid."""
    def __init__(self, url, login, password):
        self.sg = shotgun_api3.Shotgun(url, login=login, password=password)

    def find_shot_and_tasks(self, project_name, shot_code):
        """Encuentra el shot en ShotGrid y sus tareas asociadas."""
        projects = self.sg.find("Project", [['name', 'is', project_name]], ['id', 'name'])
        if projects:
            project_id = projects[0]['id']
            filters = [
                ['project', 'is', {'type': 'Project', 'id': project_id}],
                ['code', 'is', shot_code]
            ]
            fields = ['id', 'code', 'description']
            shots = self.sg.find("Shot", filters, fields)
            if shots:
                shot_id = shots[0]['id']
                tasks = self.find_tasks_for_shot(shot_id)
                return shots[0], tasks
            else:
                print("No se encontro el shot.")
        else:
            print("No se encontro el proyecto en ShotGrid.")
        return None, None

    def find_tasks_for_shot(self, shot_id):
        """Encuentra las tareas asociadas a un shot."""
        filters = [['entity', 'is', {'type': 'Shot', 'id': shot_id}]]
        fields = ['id', 'content', 'sg_status_list']
        return self.sg.find("Task", filters, fields)

    def find_versions_for_shot(self, shot_id):
        """Encuentra todas las versiones asociadas a un shot."""
        filters = [['entity', 'is', {'type': 'Shot', 'id': shot_id}]]
        fields = ['code', 'created_at', 'user', 'sg_status_list']
        versions = self.sg.find("Version", filters, fields)
        filtered_versions = [v for v in versions if "_comp_" in v['code'].lower()]  # Filtra por nombre
        return filtered_versions
        


class HieroOperations:
    """Clase para manejar operaciones en Hiero."""
    def __init__(self, shotgrid_manager):
        self.sg_manager = shotgrid_manager

    def parse_exr_name(self, file_name):
        """Extrae el nombre base del archivo EXR y el numero de version."""
        base_name = re.sub(r'_%04d\.exr$', '', file_name)
        version_match = re.search(r'_v(\d+)', base_name)
        version_number = version_match.group(1) if version_match else 'Unknown'
        return base_name, version_number

    def process_selected_clips(self):
        """Procesa los clips seleccionados en el timeline de Hiero."""
        seq = hiero.ui.activeSequence()
        if seq:
            te = hiero.ui.getTimelineEditor(seq)
            selected_clips = te.selection()
            if selected_clips:
                for clip in selected_clips:
                    file_path = clip.source().mediaSource().fileinfos()[0].filename()
                    exr_name = os.path.basename(file_path)
                    base_name, version_number = self.parse_exr_name(exr_name)
                    project_name = base_name.split('_')[0]
                    parts = base_name.split('_')
                    shot_code = '_'.join(parts[:5])

                    shot, tasks = self.sg_manager.find_shot_and_tasks(project_name, shot_code)
                    if shot:
                        print("Clip seleccionado:", base_name)
                        print("Shot de SG encontrado:", shot['code'])
                        print("Descripcion del shot:", shot['description'])
                        print("Tareas asociadas:")
                        if tasks:
                            for task in tasks:
                                print("- Nombre:", task['content'])
                                print("  Estado:", task['sg_status_list'])
                        versions = self.sg_manager.find_versions_for_shot(shot['id'])
                        print("Versiones asociadas al shot:")
                        for version in versions:
                            version_number = re.search(r'_v(\d+)', version['code']).group(1)
                            print("- Version:", version['code'], "Numero de version:", version_number, "Creada el:", version['created_at'], "Por:", version['user']['name'], "Estado:", version['sg_status_list'])
                    else:
                        print("No se encontro el shot correspondiente en ShotGrid.")
            else:
                print("No se han seleccionado clips en el timeline.")
        else:
            print("No se encontro una secuencia activa en Hiero.")


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
    hiero_ops.process_selected_clips()


if __name__ == "__main__":
    main()
