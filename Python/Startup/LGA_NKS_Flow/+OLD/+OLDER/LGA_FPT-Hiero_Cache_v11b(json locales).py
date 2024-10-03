import json
import os
import sys
from datetime import datetime
import shotgun_api3
from deepdiff import DeepDiff  # Para comparar diccionarios de JSON
import logging
from datetime import datetime
import tkinter as tk
from tkinter import messagebox, simpledialog, scrolledtext

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
        self.root = tk.Tk()
        self.root.withdraw()  # Oculta la ventana raiz

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
        versions_uploaded = []
        
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
            logging.info("Changes detected.")
            for change_type, details in diff.items():
                if change_type in ['values_changed', 'type_changes']:  # Estos tipos devuelven diccionarios
                    for item_key, item_value in details.items():
                        logging.info(f"{change_type} detected at {item_key}: {item_value}")
                        if 'new_value' in item_value:
                            new_value = item_value['new_value']
                            if isinstance(new_value, dict) and 'versions' in new_value:
                                for version in new_value['versions']:
                                    versions_uploaded.append(version['version_number'])

                                # Log this change
                                shot_index = item_key.split("root['shots'][")[1].split(']')[0]  # Extracting index
                                shot_name = project_data['shots'][int(shot_index)]['shot_name']
                                logging.info(f"Shot name: {shot_name}")

                                for task in project_data['shots'][int(shot_index)]['tasks']:
                                    logging.info(f"Task: {task['task_type']}")
                                    logging.info(f"Task_status: {task['task_status']}")
                                    for version in task['versions']:
                                        logging.info(f"Version uploaded: {version['version_number']}")
                                        logging.info(f"Version description: {version['version_description'] or 'None'}")
                                        logging.info(f"Version status: {version['version_status']}")
                                        logging.info("____________________________\n")
                elif change_type in ['item_added', 'item_removed']:  # Estos tipos pueden devolver listas
                    for change in details:
                        path = change.get('path', 'No path available')
                        item = change.get('item')
                        logging.info(f"{change_type} at {path}: {item}")
                else:
                    # General log for other types of changes
                    logging.info(f"{change_type}: {details}")
        else:
            logging.info("No changes detected.")


 
        with open(output_file, 'w') as file:
            json.dump(project_data, file, indent=4)

        end_time = datetime.now()
        elapsed_time = end_time - start_time
        logging.info("Finished synchronization with SG. Current date and time: {}".format(end_time.strftime("%Y-%m-%d %H:%M:%S")))
        logging.info(f"Total sync time: {elapsed_time}")
        logging.info("____________________________\n")

        # Mostrar la ventana con las versiones cargadas
        self.show_initial_dialog(versions_uploaded)

    def show_initial_dialog(self, versions):
        dialog = tk.Toplevel(self.root)
        dialog.title("FPT Pull Cache")
        dialog.configure(bg='#333333')
        dialog.attributes('-topmost', True)  # Asegura que la ventana se mantenga en el frente

        font_family = "Segoe UI"
        font_size = 10
        message_frame = tk.Frame(dialog, bg='#333333', padx=20, pady=20)
        message_frame.pack(fill=tk.BOTH, expand=True)

        count = len(versions)
        message = f"{count} new versions pulled from FPT"
        tk.Label(message_frame, text=message, fg='#E0E0E0', bg='#333333', font=(font_family, font_size)).pack()

        button_frame = tk.Frame(dialog, bg='#333333', pady=10)
        button_frame.pack(fill=tk.X)

        ok_button = tk.Button(button_frame, text="OK (30)", command=lambda: [dialog.destroy(), self.close_application()],
                              bg='#333333', fg='#E0E0E0', font=(font_family, font_size))
        ok_button.pack(side=tk.RIGHT, padx=10)
        
        details_button = tk.Button(button_frame, text="Details",
                                   command=lambda: [dialog.destroy(), self.show_uploaded_versions(versions)],
                                   bg='#333333', fg='#E0E0E0', font=(font_family, font_size))
        details_button.pack(side=tk.RIGHT, padx=10)


        def countdown(count=30):
            if count > 0:
                ok_button.config(text=f"OK ({count})")
                dialog.after(1000, countdown, count-1)
            else:
                dialog.destroy()
                self.close_application()

        countdown()

    def show_uploaded_versions(self, versions):
        details_window = tk.Toplevel(self.root)
        details_window.title("New versions pulled from FPT")
        details_window.configure(bg='#333333')

        st = scrolledtext.ScrolledText(details_window, bg='#333333', fg='#E0E0E0')
        for version in versions:
            st.insert(tk.END, version + '\n')

        st.pack(fill=tk.BOTH, expand=True)
        details_window.protocol("WM_DELETE_WINDOW", self.close_application)  # Maneja el cierre con el boton de cierre de ventana

    def close_application(self):
        """ Cierra todas las ventanas y termina la aplicacion """
        self.root.destroy()

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
    hiero_ops.root.mainloop()

if __name__ == "__main__":
    main()

