import hiero.core
import hiero.ui
import os
import re
import shotgun_api3

class ShotGridManager:
    """Clase para manejar operaciones en ShotGrid."""

    def __init__(self, url, login, password):
        self.sg = shotgun_api3.Shotgun(url, login=login, password=password)
        self.task_status_dict = {
            'apr': 'Approved', 'enviad': 'Enviado', 'wts': 'Waiting to start',
            'corr': 'Corrections', 'progre': 'In Progress', 'noread': 'Not Ready To Start',
            'rev': 'Pending Review', 'pubsh': 'Publish', 'pbshed': 'Published',
            'ready': 'Ready To Start', 'rev_di': 'Review Dir', 'rev_su': 'Review Sup',
            'vwd': 'Viewed', 'check': 'Delivery Checked'
        }

    def find_project(self, project_name):
        """Busca un proyecto por nombre."""
        return self.sg.find("Project", [['name', 'is', project_name]], ['id', 'name'])

    def find_shot(self, project_id, shot_code):
        """Busca un shot en un proyecto especifico."""
        filters = [['project', 'is', {'type': 'Project', 'id': project_id}], ['code', 'is', shot_code]]
        return self.sg.find("Shot", filters, ['id', 'code', 'description'])

    def find_task(self, shot_id, task_name):
        """Busca una tarea especifica asociada a un shot."""
        filters = [['entity', 'is', {'type': 'Shot', 'id': shot_id}], ['content', 'is', task_name]]
        return self.sg.find("Task", filters, ['id', 'content', 'sg_status_list'])

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
                    task_name = parts[5].lower()

                    projects = self.sg_manager.find_project(project_name)
                    if projects:
                        project_id = projects[0]['id']
                        shots = self.sg_manager.find_shot(project_id, shot_code)
                        if shots:
                            shot_id = shots[0]['id']
                            tasks = self.sg_manager.find_task(shot_id, task_name)
                            if tasks:
                                task_status = tasks[0]['sg_status_list']
                                full_status_name = self.sg_manager.task_status_dict.get(task_status, "Estado desconocido")
                                print(f"Tarea encontrada: {tasks[0]['content']}, Estado: {full_status_name}")
                            else:
                                print("No hay tareas asignadas a este shot que coincidan con el nombre.")
                        else:
                            print("No se encontro el shot.")
                    else:
                        print("No se encontro el proyecto.")
            else:
                print("No clips selected on the timeline.")
        else:
            print("No active sequence found.")

# Configuracion de acceso a ShotGrid
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
