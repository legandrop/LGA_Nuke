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
    """Clase para manejar operaciones ahora con un archivo JSON en lugar de ShotGrid."""
    def __init__(self, file_path):
        # Cargamos el archivo JSON al iniciar la instancia
        with open(file_path, 'r') as file:
            loaded_data = json.load(file)
            self.data = loaded_data['project']  # Accediendo al nivel 'project'

    def find_project_shots(self, project_name):
        """Retorna todos los shots para un proyecto especifico basado en el JSON cargado."""
        # Verificar que el nombre del proyecto coincide
        if self.data['project_name'] == project_name:
            return self.data['shots']
        else:
            return []      

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

        # Generacion de datos de proyecto basada en los shots actuales
        for shot in shots:
            shot_data = self.generate_shot_data(shot)
            project_data["shots"].append(shot_data)

        # Verifica si el archivo existe y no esta vacio
        old_data = {}
        if os.path.exists(output_file) and os.path.getsize(output_file) > 0:
            with open(output_file, 'r') as file:
                old_data = json.load(file)
        else:
            # Si el archivo no existe o esta vacio, considera todas las versiones como nuevas
            logging.info("No existing cache or cache is empty. Considering all versions as new.")
            for shot in project_data['shots']:
                for task in shot['tasks']:
                    for version in task['versions']:
                        versions_uploaded.append(version['version_number'])
                        logging.info(f"Version added: {version['version_number']}")
                        logging.info(f"Version description: {version.get('version_description', 'No description provided')}")
                        logging.info(f"Version status: {version.get('version_status', 'No status provided')}")
                        logging.info(f"Version date: {version.get('version_date', 'No date provided')}")
                        logging.info("____________________________\n")

        # Comparacion de los datos nuevos con los antiguos
        if old_data:
            diff = DeepDiff(old_data, project_data, ignore_order=True)
            if diff:
                self.handle_differences(diff, project_data, versions_uploaded)
            else:
                logging.info("No differences detected")
        else:
            logging.info("All versions are treated as new due to missing or empty cache.")

        # Guardar los datos actualizados en el archivo JSON
        with open(output_file, 'w') as file:
            json.dump(project_data, file, indent=4)

        end_time = datetime.now()
        elapsed_time = end_time - start_time
        logging.info("Finished synchronization with SG. Current date and time: {}".format(end_time.strftime("%Y-%m-%d %H:%M:%S")))
        logging.info(f"Total sync time: {elapsed_time}")
        logging.info("____________________________\n")

        # Mostrar la ventana con las versiones cargadas
        self.show_initial_dialog(versions_uploaded)

    def generate_shot_data(self, shot):
        """Genera el diccionario de datos de un shot especifico, incluyendo tareas y versiones."""
        shot_data = {
            "shot_name": shot['shot_name'],
            "sequence": shot['sequence'],
            "tasks": []
        }
        for task in shot['tasks']:
            if 'Comp' in task['task_type']:
                task_data = {
                    "task_type": task['task_type'],
                    "task_description": task.get('task_description', 'Sin descripcion'),
                    "task_status": task.get('task_status', 'Sin estado'),
                    "versions": []
                }
                for version in task['versions']:
                    version_data = {
                        "version_number": version['version_number'],
                        "version_description": version.get('version_description', 'Sin descripcion'),
                        "version_status": version['version_status'],
                        "version_date": version['version_date']
                    }
                    task_data["versions"].append(version_data)
                shot_data["tasks"].append(task_data)
        return shot_data

    def handle_differences(self, diff, project_data, versions_uploaded):
        """Maneja las diferencias encontradas por DeepDiff y registra los cambios relevantes."""
        logging.info("Differences detected")
        logging.info(f"Full diff: {diff}")  # Imprime la diferencia completa para ver que se esta detectando
        for key, value in diff.items():
            logging.info(f"Key 1: {key}")  # Registro de la clave en el diccionario de diferencias
            if 'values_changed' in key:
                for item_key, item_value in value.items():
                    logging.info(f"Processing values_changed for: {item_key}")
                    new_value = item_value.get('new_value', {})
                    old_value = item_value.get('old_value', {})
                    shot_index = int(item_key.split('[')[2].split(']')[0])  # Asegurarse de obtener siempre el indice del shot
            # Verifica si el cambio involucra la lista de tareas
                    if isinstance(new_value, dict) and 'tasks' in new_value and isinstance(old_value, dict) and 'tasks' in old_value:
                        logging.info(f"task in item key")
                        new_tasks = new_value['tasks']
                        old_tasks = old_value['tasks']
                        if not old_tasks and new_tasks:
                            # Si no habia tareas anteriormente y ahora hay, se considera como tareas nuevas
                            logging.info(f"New tasks detected at shot index {shot_index}.")
                            for task in new_tasks:
                                self.log_new_task_details(shot_index, task, versions_uploaded, project_data)
                        for new_task, old_task in zip(new_tasks, old_tasks):
                            new_versions = new_task.get('versions', [])
                            old_versions = old_task.get('versions', [])
                            task_index = new_tasks.index(new_task)  # Obtener el indice de la tarea actual
                            if not old_versions and new_versions:
                                # Si no habia versiones anteriormente y ahora hay, se considera como versiones nuevas
                                logging.info(f"New versions detected in task {new_task['task_type']} at shot index {shot_index}, task index {task_index}.")
                                for version in new_versions:
                                    self.log_new_version_details(shot_index, task_index, version, versions_uploaded, project_data)
                    else:
                        self.log_change_details(key, item_key, item_value, project_data, versions_uploaded)
            else:
                # Manejar otros tipos de diferencias que no son values_changed
                for item_key, item_value in value.items():
                    logging.info(f"Else Item key: {item_key}, Item value processing under different key: {item_value}")
                    self.log_change_details(key, item_key, item_value, project_data, versions_uploaded)

    def log_new_version_details(self, shot_index, task_index, version, versions_uploaded, project_data):
        """Log details of a new version added to a task in a shot."""
        shot_name = project_data['shots'][shot_index]['shot_name']
        task_type = project_data['shots'][shot_index]['tasks'][task_index]['task_type']
        logging.info(f"New version detected in shot {shot_name}, task {task_type}: {version['version_number']}")
        versions_uploaded.append(version['version_number'])
        logging.info(f"Version added: {version['version_number']}")
        logging.info(f"Version description: {version.get('version_description', 'No description provided')}")
        logging.info(f"Version status: {version['version_status']}")
        logging.info(f"Version date: {version['version_date']}")
        logging.info("____________________________\n")



    def log_new_task_details(self, shot_index, task, versions_uploaded, project_data):
        """Log details of a new task added to a shot."""
        shot_name = project_data['shots'][shot_index]['shot_name']
        logging.info(f"New task detected in shot {shot_name}: {task['task_type']}")
        for version in task['versions']:
            versions_uploaded.append(version['version_number'])
            logging.info(f"Version added: {version['version_number']}")
            logging.info(f"Version description: {version.get('version_description', 'No description provided')}")
            logging.info(f"Version status: {version['version_status']}")
            logging.info(f"Version date: {version['version_date']}")
            logging.info("____________________________\n")



    def log_change_details(self, change_type, item_key, item_value, project_data, versions_uploaded):
        """Log the details of the changes based on the type of difference detected."""
        logging.info(f"Processing change type: {change_type}")  # Verificacion de que tipo de cambio se procesa
        if change_type == 'values_changed' and 'new_value' in item_value:
            # Extract and log the details for changed values
            new_value = item_value['new_value']
            logging.info(f"Values changed detected at {item_key}, new value: {new_value}")
            if isinstance(new_value, dict) and 'versions' in new_value:
                self.log_version_changes(item_key, new_value, project_data, versions_uploaded)
        elif change_type == 'iterable_item_added' and item_key.startswith("root['shots']"):
            # Log details for new shots added
            logging.info(f"New shot added: {item_key}")
            shot_info = item_value.get('item', {}) if 'item' in item_value else item_value
            logging.info(f"Shot details: {shot_info}")
            if 'tasks' in shot_info:
                for task in shot_info['tasks']:
                    for version in task['versions']:
                        versions_uploaded.append(version['version_number'])
                        logging.info(f"Version added: {version['version_number']}")
                        logging.info(f"Version description: {version.get('version_description', 'No description provided')}")
                        logging.info(f"Version status: {version.get('version_status', 'No status provided')}")
                        logging.info(f"Version date: {version.get('version_date', 'No date provided')}")
                        logging.info("____________________________\n")
        elif change_type == 'iterable_item_removed':
            logging.info(f"Removed item at {item_key}: {item_value}")
            # Log details for items removed
            self.log_added_or_removed_items(change_type, item_key, item_value, project_data, versions_uploaded)


    def log_version_changes(self, item_key, new_value, project_data, versions_uploaded):
        """Log changes in versions extracted from project data based on item keys."""
        shot_index = item_key.split("root['shots'][")[1].split(']')[0]  # Extracting index
        shot_name = project_data['shots'][int(shot_index)]['shot_name']
        logging.info(f"Shot name: {shot_name}")

        for task in project_data['shots'][int(shot_index)]['tasks']:
            logging.info(f"Task: {task['task_type']}")
            logging.info(f"Task_status: {task['task_status']}")
            for version in task['versions']:
                versions_uploaded.append(version['version_number'])
                logging.info(f"Version uploaded: {version['version_number']}")
                logging.info(f"Version description: {version['version_description'] or 'None'}")
                logging.info(f"Version status: {version['version_status']}")
                logging.info("____________________________\n")

    def log_added_or_removed_items(self, change_type, item_key, item_value, project_data, versions_uploaded):
        """Log details for added or removed items, specifically handling version details."""
        logging.info(f"Change type: {change_type}, Item Key: {item_key}")
        # Directamente maneja el valor de item_value, asumiendo que es la version anadida
        new_value = item_value
        if isinstance(new_value, dict) and 'version_number' in new_value:
            versions_uploaded.append(new_value['version_number'])
            logging.info(f"Version added/removed: {new_value['version_number']}")
            logging.info(f"Version description: {new_value.get('version_description', 'No description provided')}")
            logging.info(f"Version status: {new_value.get('version_status', 'No status provided')}")
            logging.info(f"Version date: {new_value.get('version_date', 'No date provided')}")
            logging.info("____________________________\n")
        else:
            # Si item_value no es un diccionario como se esperaba, manejar adecuadamente
            logging.error(f"Unexpected data format for added item: {item_value}")
            logging.info("____________________________\n")


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
    sg_manager = ShotGridManager('T:/LGA_Cache-SG.json')
    hiero_ops = HieroOperations(sg_manager)
    output_file = 'T:/LGA_Cache-Local.json'
    hiero_ops.process_all_shots(output_file)
    hiero_ops.root.mainloop()

if __name__ == "__main__":
    main()
