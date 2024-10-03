"""
   
   Imprime la version en Hiero, version en ShotGrid (SG), estado de la version en SG, 
   descripcion y URLs de las tareas asociadas para los clips seleccionados en el timeline.
   Tambien imprime los comentarios que haya en la version del clip seleccionado
   
"""


import hiero.core
import os
import re
import shotgun_api3
import sys

class ShotGridManager:
    def __init__(self, url, login, password):
        self.sg = shotgun_api3.Shotgun(url, login=login, password=password)

    def find_shot_and_tasks(self, project_name, shot_code):
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
        filters = [['entity', 'is', {'type': 'Shot', 'id': shot_id}]]
        fields = ['id', 'content', 'sg_status_list']
        return self.sg.find("Task", filters, fields)

    def find_version_by_code(self, shot_id, version_code):
        filters = [
            ['entity', 'is', {'type': 'Shot', 'id': shot_id}],
            ['code', 'contains', version_code]
        ]
        fields = ['id', 'code', 'created_at', 'user', 'sg_status_list', 'description']
        versions = self.sg.find("Version", filters, fields)
        return versions

    def get_task_url(self, task_id):
        return f"{self.sg.base_url}/detail/Task/{task_id}"

    def get_version_notes(self, version_id):
        filters = [['note_links', 'in', {'type': 'Version', 'id': version_id}]]
        fields = ['content', 'user']
        return self.sg.find("Note", filters, fields)

class HieroOperations:
    def __init__(self, shotgrid_manager):
        self.sg_manager = shotgrid_manager

    def parse_exr_name(self, file_name):
        base_name = re.sub(r'_%04d\.exr$', '', file_name)
        version_match = re.search(r'_v(\d+)', base_name)
        version_number = version_match.group(1) if version_match else 'Unknown'
        return base_name, version_number

    def process_selected_clips(self):
        seq = hiero.ui.activeSequence()
        if seq:
            te = hiero.ui.getTimelineEditor(seq)
            selected_clips = te.selection()
            if selected_clips:
                for clip in selected_clips:
                    file_path = clip.source().mediaSource().fileinfos()[0].filename()
                    exr_name = os.path.basename(file_path)
                    base_name, hiero_version_number = self.parse_exr_name(exr_name)
                    project_name = base_name.split('_')[0]
                    parts = base_name.split('_')
                    shot_code = '_'.join(parts[:5])

                    shot, tasks = self.sg_manager.find_shot_and_tasks(project_name, shot_code)
                    if shot:
                        versions = self.sg_manager.find_version_by_code(shot['id'], f"_v{hiero_version_number}")
                        if versions:
                            version = versions[0]  # Assuming the first match is the correct version
                            print(f"- Shot name: {shot['code']}")
                            print(f"- Version Hiero: v{hiero_version_number}")
                            print(f"- Version SG: {version['code']}")
                            print(f"- Version SG status: {version['sg_status_list']}")
                            print(f"- Description: {version['description']}")

                            notes = self.sg_manager.get_version_notes(version['id'])
                            if notes:
                                print("  - Comments:")
                                for note in notes:
                                    print(f"    - {note['content']} (User: {note['user']['name']})")
                            else:
                                print("  - No comments found.")
                            
                            for task in tasks:
                                task_url = self.sg_manager.get_task_url(task['id'])
                                print(f"  - Task: {task['content']} (Status: {task['sg_status_list']}) URL: {task_url}")
                        else:
                            print(f"No versions found for Hiero version v{hiero_version_number} in ShotGrid.")
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
