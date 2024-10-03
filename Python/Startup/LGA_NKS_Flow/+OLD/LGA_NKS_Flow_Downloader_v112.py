"""
____________________________________________________________________________________

  LGA_NKS_Flow_Downloader v1.4 - Lega

  - Se conecta a Flow con las credenciales del script, 
  - Descarga la informacion de los proyectos agregados en los settings
  - Genera un JSON con la informacion descargada y la compara con el JSON descargado anteriormente
  - Reporta en un LOG y en una ventana de la UI las versiones nuevas encontradas en Flow
  
____________________________________________________________________________________
"""


"""

Para compilar:
1- Copiar el archivo a la carpeta compilar.
2- Renombrarlo para sacarle el numero de version (borrar el que ya existia ahi)
3- Si hice algun cambia en la carpeta Data, copiarlo a la carpeta Data de la carpeta Compilar

4- en CMD:
    cd C:/Users/leg4-pc/.nuke/Python/Startup/LGA_NKS_Flow/Compilar
    pyinstaller --onefile --add-data "Data/no_icon.ico;Data" --add-data "Data/LGA.ico;Data" --add-data "Data/settings_off.png;Data" --add-data "Data/settings_on.png;Data" --add-data "Data/CTkScrollableDropdown/ctk_scrollable_dropdown.py;Data/CTkScrollableDropdown" --add-data "Data/LGA_NKS_Flow_Downloader_CCTK_Theme.json;Data" -i "Data/LGA.ico" LGA_NKS_Flow_Downloader.py

4b- en Terminal: (se usa : en lugar de ; para separar rutas)
    cd /Users/leg4/.nuke/Python/Startup/LGA_NKS_Flow/Compilar
    pyinstaller --onefile --add-data "Data/no_icon.ico:Data" --add-data "Data/LGA.ico:Data" --add-data "Data/settings_off.png:Data" --add-data "Data/settings_on.png:Data" --add-data "Data/CTkScrollableDropdown/ctk_scrollable_dropdown.py:Data/CTkScrollableDropdown" --add-data "Data/LGA_NKS_Flow_Downloader_CCTK_Theme.json:Data" -i "Data/LGA.ico" LGA_NKS_Flow_Downloader.py


Antivirus, windows defender:
1- Search de windows
2- Virus protection
3- Mangage Settings
4- Exclusions (abajo de todo)
5- Agregar una exclusion

6- Si lo mando a cuarententa directo hay que ir a protection history


"""


import json
import os
import sys
import schedule
import time
import threading
import shotgun_api3
import logging
import sv_ttk
import customtkinter as ctk
import tkinter as tk
import pystray
from customtkinter import CTkImage
from PIL import Image, ImageTk
from pystray import MenuItem as item
from pystray import Menu
from datetime import datetime, timedelta
from deepdiff import DeepDiff  # Para comparar diccionarios de JSON
from datetime import datetime
from ttkthemes import ThemedTk
from tkinter import PhotoImage, filedialog
from tkinter import font as tkFont
from sys import platform
import platform
import subprocess  ##### Importacion para subprocess

try:
    from ctypes import windll, byref, sizeof, c_int
except:
    pass


data_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'Data', 'CTkScrollableDropdown')
if data_path not in sys.path:
    sys.path.append(data_path)
from ctk_scrollable_dropdown import CTkScrollableDropdown


def get_script_path():
    """Get the path of the currently executing script or executable."""
    if getattr(sys, 'frozen', False):
        # We are running in a bundle (PyInstaller)
        return os.path.dirname(sys.executable)
    else:
        # We are running in a normal Python environment
        return os.path.dirname(os.path.abspath(__file__))

# Obtener la ruta del directorio donde se encuentra este script o ejecutable
current_script_path = get_script_path()
# Cambiar Script_Path para que apunte a la subcarpeta 'Data'
Script_Path = os.path.join(current_script_path, 'Data')


BG_Color = "#26272b"  # Background color
BTN_Color = "#711ca1"  # Button color
TXT_Color = "#FFFFFF"  # Text color


class ShotGridDownloader:
    """Clase para manejar operaciones en ShotGrid."""
    def __init__(self, url, script_name, api_key):
        self.sg = shotgun_api3.Shotgun(url, script_name=script_name, api_key=api_key)
        self.cancel_download = False

    def find_project_shots(self, project_name):
        """Encuentra todos los shots en un proyecto especifico."""
        if self.cancel_download:
            return []
        try:
            projects = self.sg.find("Project", [['name', 'is', project_name]], ['id', 'name'])
        except Exception as e:
            current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            print(f"{current_time} - No se puede conectar a ShotGrid. Verifique su conexion a Internet.")
            print(f"{current_time} - find_project_shots error: {e}")
            return []

        if projects:
            project_id = projects[0]['id']
            filters = [
                ['project', 'is', {'type': 'Project', 'id': project_id}]
            ]
            fields = ['id', 'code', 'sg_sequence.Sequence.code']
            try:
                return self.sg.find("Shot", filters, fields)
            except Exception as e:
                current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                print(f"{current_time} - No se puede conectar a ShotGrid. Verifique su conexion a Internet.")
                print(f"{current_time} - find_project_shots error: {e}")
                return []
        else:
            return []

    def find_tasks_for_shot(self, shot_id):
        """Encuentra las tareas asociadas a un shot."""
        if self.cancel_download:
            return []
        filters = [['entity', 'is', {'type': 'Shot', 'id': shot_id}]]
        fields = ['id', 'content', 'description', 'sg_status_list', 'task_assignees']
        try:
            tasks = self.sg.find("Task", filters, fields)
        except Exception as e:
            current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            print(f"{current_time} - No se puede conectar a ShotGrid. Verifique su conexion a Internet.")
            print(f"{current_time} - find_tasks_for_shot error: {e}")
            return []

        for task in tasks:
            if task['task_assignees']:
                task['assigned_to'] = task['task_assignees'][0]['name']
            else:
                task['assigned_to'] = 'No asignado'
        return tasks

    def find_versions_for_shot(self, shot_id):
        """Encuentra todas las versiones asociadas a un shot."""
        if self.cancel_download:
            return []
        filters = [['entity', 'is', {'type': 'Shot', 'id': shot_id}]]
        fields = ['code', 'description', 'created_at', 'sg_status_list']
        try:
            versions = self.sg.find("Version", filters, fields)
        except Exception as e:
            current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            print(f"{current_time} - No se puede conectar a ShotGrid. Verifique su conexion a Internet.")
            print(f"{current_time} - find_versions_for_shot error: {e}")
            return []
        
        # Obtener comentarios para cada version
        for version in versions:
            version['comments'] = self.get_version_comments(version['id'])
        
        return [v for v in versions if "_comp_" in v['code'].lower()]

    def get_version_comments(self, version_id):
        """Obtiene los comentarios asociados a una version."""
        filters = [['note_links', 'in', {'type': 'Version', 'id': version_id}]]
        fields = ['content', 'user']
        try:
            notes = self.sg.find("Note", filters, fields)
            comments = [{"text": note['content'], "user": note['user']['name']} for note in notes]
            return comments
        except Exception as e:
            print("No se pueden obtener los comentarios de ShotGrid. Verifique su conexion a Internet.")
            print(f"Error: {e}")
            return []

    def download_and_save_data(self, project_names, json_SG_output_file):
        output_data = {"projects": []}

        for project_name in project_names:
            if self.cancel_download:
                break
            current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            print(f"{current_time} - Buscando shots en el proyecto '{project_name}'...")
            start_time = datetime.now()
            logging.info("____________________________+++++++ START +++++++____________________________\n")
            logging.info(f"Starting synchronization with SG. Current date and time: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
            logging.info("______________________________________________________________________________\n")

            try:
                start_time = time.time()
                shots = self.find_project_shots(project_name)
                end_time = time.time()
                time_elapsed = end_time - start_time

                for i in range(int(time_elapsed) + 1):
                    if self.cancel_download:
                        break
                    print(".", end="", flush=True)
                    time.sleep(1)

                if self.cancel_download:
                    break
                print()

                project_data = {"project_name": project_name, "shots": []}
                for shot in shots:
                    if self.cancel_download:
                        break
                    shot_data = {"shot_name": shot['code'], "sequence": shot.get('sg_sequence.Sequence.code', 'Unknown'), "tasks": []}
                    tasks = self.find_tasks_for_shot(shot['id'])
                    for task in tasks:
                        if 'Comp' in task['content']:
                            if self.cancel_download:
                                break
                            task_data = {
                                "task_type": "Comp",
                                "task_description": task.get('description', 'Sin descripcion'),
                                "task_status": task.get('sg_status_list', 'Sin estado'),
                                "task_assigned_to": task.get('assigned_to', 'No asignado'),
                                "versions": []
                            }
                            versions = self.find_versions_for_shot(shot['id'])
                            for version in versions:
                                if self.cancel_download:
                                    break
                                try:
                                    version_data = {
                                        "version_number": version.get('code', 'Sin numero de version'),
                                        "version_description": version.get('description', 'Sin descripcion'),
                                        "version_status": version.get('sg_status_list', 'Sin estado'),
                                        "version_date": version['created_at'].isoformat() if version['created_at'] else "Unknown",
                                        "comments": version.get('comments', [])
                                    }
                                    task_data["versions"].append(version_data)
                                except KeyError as e:
                                    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                                    logging.error(f"{current_time} - KeyError: {e} en version: {version}")
                            shot_data["tasks"].append(task_data)
                    project_data["shots"].append(shot_data)
                output_data["projects"].append(project_data)
            except Exception as e:
                current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                print(f"{current_time} - No se puede conectar a ShotGrid. Verifique su conexion a Internet.")
                print(f"{current_time} - download_and_save_data error: {e}")
                logging.error(f"Error in download_and_save_data: {e}", exc_info=True)
                break

        if not self.cancel_download:
            with open(json_SG_output_file, 'w', encoding='utf-8') as file:
                json.dump(output_data, file, ensure_ascii=False, indent=4)

        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        print(f"{current_time} - Proceso completado. JSON generado con exito." if not self.cancel_download else "Proceso cancelado.")



class ShotGridManager:
    """Clase para manejar operaciones con un archivo JSON en lugar de ShotGrid."""
    def __init__(self, file_path):
        # Cargamos el archivo JSON al iniciar la instancia
        with open(file_path, 'r', encoding='utf-8') as file:
            loaded_data = json.load(file)
            self.data = loaded_data['projects']  # Accediendo a la lista de proyectos

    def find_project_shots(self, project_names):
        """Retorna todos los shots para los proyectos especificados basado en el JSON cargado."""
        shots = []
        for project in self.data:
            if project['project_name'] in project_names:
                shots.extend(project['shots'])
        return shots

class HieroOperations:
    """Clase para manejar operaciones en Hiero."""
    def __init__(self, root, shotgrid_manager):
        self.sg_manager = shotgrid_manager
        self.root = ctk.CTkToplevel(root)  # Cambiado a Toplevel
        self.root.withdraw()  # Oculta la ventana raiz
        ctk.set_default_color_theme(resource_path("LGA_NKS_Flow_Downloader_CCTK_Theme.json"))
        set_title_bar_color(self.root, BG_Color, TXT_Color)  # Color de barra y texto personalizados

    def process_all_shots(self, output_file):
        """Procesa todos los shots en el proyecto especificado y guarda la informacion en un archivo JSON."""
        start_time = datetime.now()
        config = load_config()
        project_names = config.get('project_names', ['DefaultProjectName'])

        all_projects_data = {'projects': []}
        all_versions_uploaded = []

        old_data = {}
        if os.path.exists(output_file) and os.path.getsize(output_file) > 0:
            with open(output_file, 'r', encoding='utf-8') as file:  # Cambiado aqui
                old_data = json.load(file)

        #logging.info(f"Old data structure: {old_data}")

        for project_name in project_names:
            #logging.info(f"Searching project: {project_name}:\n")
            shots = self.sg_manager.find_project_shots([project_name])
            project_data = {
                "project_name": project_name,
                "shots": []
            }

            for shot in shots:
                shot_data = self.generate_shot_data(shot)
                project_data["shots"].append(shot_data)

            all_projects_data['projects'].append(project_data)

        #logging.info(f"New data structure: {all_projects_data}")

        if old_data:
            diff = DeepDiff(old_data, all_projects_data, ignore_order=True)
            if diff:
                self.handle_differences(diff, all_projects_data, all_versions_uploaded)
            else:
                logging.info("No differences detected")
        else:
            logging.info("No existing cache or cache is empty. Considering all versions as new.")
            for project in all_projects_data['projects']:
                for shot in project['shots']:
                    for task in shot['tasks']:
                        for version in task['versions']:
                            all_versions_uploaded.append(version['version_number'])
                            logging.info(f"Version added: {version['version_number']}")
                            logging.info(f"Version description: {version.get('version_description', 'No description provided')}")
                            logging.info(f"Version status: {version.get('version_status', 'No status provided')}")
                            logging.info(f"Version date: {version.get('version_date', 'No date provided')}")
                            logging.info("____________________________\n")

        with open(output_file, 'w', encoding='utf-8') as file:  # Cambiado aqui
            json.dump(all_projects_data, file, ensure_ascii=False, indent=4)

        if not all_versions_uploaded or not config.get('new_versions_popup', True):
            logging.info("No new versions found")

        end_time = datetime.now()
        elapsed_time = end_time - start_time
        logging.info("\nFinished synchronization with SG. Current date and time: {}".format(end_time.strftime("%Y-%m-%d %H:%M:%S")))
        logging.info(f"Total sync time: {elapsed_time}")
        logging.info("______________________________+++++++ END +++++++______________________________\n")

        if all_versions_uploaded and config.get('new_versions_popup', True):
            self.new_versions_window(all_versions_uploaded)

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
                    "task_assigned_to": task.get('task_assigned_to', 'No asignado'),
                    "versions": []
                }
                for version in task['versions']:
                    version_data = {
                        "version_number": version['version_number'],
                        "version_description": version.get('version_description', 'Sin descripcion'),
                        "version_status": version['version_status'],
                        "version_date": version['version_date'],
                        "comments": version.get('comments', [])
                    }
                    task_data["versions"].append(version_data)
                shot_data["tasks"].append(task_data)
        return shot_data

    def process_change(self, item, change_type):
        """Procesa un cambio individual de la lista de cambios detectados."""
        #logging.info(f"Processing {change_type} for item: {item}")
        pass

    def handle_differences(self, diff, project_data, versions_uploaded):
        """Maneja las diferencias encontradas por DeepDiff y registra los cambios relevantes."""
        #logging.info("Unusual differences detected")
        #logging.info(f"Processing differences: {diff}")

        for key, value in diff.items():
            #logging.info(f"Key 1: {key}")
            if 'values_changed' in key:
                for item_key, item_value in value.items():
                    #logging.info(f"Item key: {item_key}, Item value: {item_value}")
                    try:
                        shot_index = int(item_key.split('[')[2].split(']')[0])
                    except IndexError as e:
                        #logging.error(f"Error processing item key: {item_key}, Error: {e}")
                        continue

                    #logging.info(f"Processing values_changed for: {item_key}")
                    new_value = item_value.get('new_value', {})
                    old_value = item_value.get('old_value', {})

                    if isinstance(new_value, dict) and 'tasks' in new_value and isinstance(old_value, dict) and 'tasks' in old_value:
                        #logging.info(f"task in item key")
                        new_tasks = new_value['tasks']
                        old_tasks = old_value['tasks']

                        for new_task, old_task in zip(new_tasks, old_tasks):
                            new_versions = new_task.get('versions', [])
                            old_versions = old_task.get('versions', [])
                            task_index = new_tasks.index(new_task)

                            #logging.info(f"Comparing new_versions: {new_versions} with old_versions: {old_versions}")

                            # Detectar versiones nuevas
                            for new_version in new_versions:
                                if new_version not in old_versions:
                                    #logging.info(f"New version detected in 'values_changed': {new_version}")
                                    self.log_version_details(shot_index, task_index, new_version, versions_uploaded, project_data, added=True)

                            # Detectar versiones eliminadas
                            for old_version in old_versions:
                                if old_version not in new_versions:
                                    #logging.info(f"Removed version detected: {old_version}")
                                    self.log_version_details(shot_index, task_index, old_version, versions_uploaded, project_data, added=False)
                    else:
                        self.log_change_details(key, item_key, item_value, project_data, versions_uploaded)

            elif 'iterable_item_added' in key:
                added_versions = set()  # Usar un conjunto para evitar duplicados
                for item_key, item_value in value.items():
                    #logging.info(f"New item added: {item_key}")
                    #logging.info(f"item_value: {item_value}")
                    if 'versions' in item_key:
                        #logging.info("'versions' in item_key da verdadero")
                        version_info = item_value
                        #logging.info(f"Version details: {version_info}")
                        if isinstance(version_info, dict):
                            #logging.info("'if isinstance(version_info, dict) da verdadero")
                            version_number = version_info.get('version_number', 'Sin numero de version')
                            if version_number not in added_versions:
                                #logging.info(f"New version detected in 'iterable_item_added': {version_info}")
                                added_versions.add(version_number)
                                self.log_version_details(0, 0, version_info, versions_uploaded, project_data, added=True)
                    elif 'tasks' in item_key:
                        #logging.info("'tasks' in item_key da verdadero")
                        task_info = item_value
                        #logging.info(f"New task detected: {task_info}")
                        for version in task_info.get('versions', []):
                            version_number = version.get('version_number', 'Sin numero de version')
                            if version_number not in added_versions:
                                logging.info(f"New version detected in new task: {version}")
                                added_versions.add(version_number)
                                self.log_version_details(0, 0, version, versions_uploaded, project_data, added=True)
                    elif 'shots' in item_key:
                        #logging.info("'shots' in item_key da verdadero")
                        shot_info = item_value
                        #logging.info(f"New shot detected: {shot_info}")
                        for task in shot_info.get('tasks', []):
                            for version in task.get('versions', []):
                                version_number = version.get('version_number', 'Sin numero de version')
                                if version_number not in added_versions:
                                    #logging.info(f"New version detected in new shot: {version}")
                                    added_versions.add(version_number)
                                    self.log_version_details(0, 0, version, versions_uploaded, project_data, added=True)
                    elif 'projects' in item_key:
                        #logging.info("'projects' in item_key da verdadero")
                        project_info = item_value
                        logging.info(f"New project detected: {project_info}")
                        if 'shots' in project_info:
                            for shot in project_info['shots']:
                                for task in shot['tasks']:
                                    for version in task['versions']:
                                        version_number = version.get('version_number', 'Sin numero de version')
                                        if version_number not in added_versions:
                                            logging.info(f"New version detected in new project: {version}")
                                            added_versions.add(version_number)
                                            self.log_version_details(0, 0, version, versions_uploaded, project_data, added=True)
                    else:
                        #logging.info("'versions' in item_key da falso")
                        shot_info = item_value.get('item', {}) if 'item' in item_value else item_value
                        #logging.info(f"Shot details: {shot_info}")
                        if 'tasks' in shot_info:
                            for task in shot_info['tasks']:
                                for version in task['versions']:
                                    version_number = version.get('version_number', 'Sin numero de version')
                                    if version_number not in added_versions:
                                        logging.info(f"New version detected in shot_info: {version}")
                                        added_versions.add(version_number)
                                        self.log_version_details(0, 0, version, versions_uploaded, project_data, added=True)

            elif 'iterable_item_removed' in key:
                for item_key, item_value in value.items():
                    logging.info(f"Removed item at {item_key}: {item_value}")
                    self.log_added_or_removed_items(key, item_key, item_value, project_data, versions_uploaded)

            logging.info(f"Current state of versions_uploaded: {versions_uploaded}")

        logging.info("______________________________________________________________________________\n")

    def log_version_details(self, shot_index, task_index, version, versions_uploaded, project_data, added=True):
        """Log details of a version (new or removed) from a task in a shot."""
        action = "added" if added else "removed"
        
        version_number = version.get('version_number', None)
        if not version_number:
            logging.error(f"Missing 'version_number' in version data: {version}")
            return
        
        logging.info(f"Logging version {action}: {version_number} in shot index {shot_index}, task index {task_index}")
        if shot_index != 0 and task_index != 0:
            shot_name = project_data['projects'][0]['shots'][shot_index]['shot_name']
            task_type = project_data['projects'][0]['shots'][shot_index]['tasks'][task_index]['task_type']
            logging.info(f"Version {action} in shot {shot_name}, task {task_type}: {version_number}")
        if added:
            versions_uploaded.append(version_number)
        logging.info(f"Version {action}: {version_number}")
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
        #logging.info(f"Processing change type: {change_type}")
        if change_type == 'values_changed' and 'new_value' in item_value:
            new_value = item_value['new_value']
            #logging.info(f"Values changed detected at {item_key}, new value: {new_value}")
            if isinstance(new_value, dict) and 'versions' in new_value:
                self.log_version_changes(item_key, new_value, project_data, versions_uploaded)
        elif change_type == 'iterable_item_added' and item_key.startswith("root['shots']"):
            #logging.info(f"New shot added: {item_key}")
            shot_info = item_value.get('item', {}) if 'item' in item_value else item_value
            #logging.info(f"Shot details: {shot_info}")
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
            self.log_added_or_removed_items(change_type, item_key, item_value, project_data, versions_uploaded)

    def log_version_changes(self, item_key, new_value, project_data, versions_uploaded):
        """Log changes in versions extracted from project data based on item keys."""
        try:
            shot_index = int(item_key.split("root['shots'][")[1].split(']')[0])
            shot_name = project_data['shots'][shot_index]['shot_name']
            logging.info(f"Shot name: {shot_name}")

            for task in project_data['shots'][shot_index]['tasks']:
                logging.info(f"Task: {task['task_type']}")
                logging.info(f"Task_status: {task['task_status']}")
                for version in task['versions']:
                    versions_uploaded.append(version['version_number'])
                    logging.info(f"Version uploaded: {version['version_number']}")
                    logging.info(f"Version description: {version['version_description'] or 'None'}")
                    logging.info(f"Version status: {version['version_status']}")
                    logging.info("____________________________\n")
        except IndexError as e:
            logging.error(f"IndexError: {e} - Invalid shot_index in item_key: {item_key}")
        except KeyError as e:
            logging.error(f"KeyError: {e} - Missing key in project_data for item_key: {item_key}")

    def log_added_or_removed_items(self, change_type, item_key, item_value, project_data, versions_uploaded):
        """Log details for added or removed items, specifically handling version details."""
        logging.info(f"Change type: {change_type}, Item Key: {item_key}")
        new_value = item_value
        if isinstance(new_value, dict) and 'version_number' in new_value:
            versions_uploaded.append(new_value['version_number'])
            logging.info(f"Version added/removed: {new_value['version_number']}")
            logging.info(f"Version description: {new_value.get('version_description', 'No description provided')}")
            logging.info(f"Version status: {new_value.get('version_status', 'No status provided')}")
            logging.info(f"Version date: {new_value.get('version_date', 'No date provided')}")
            logging.info("____________________________\n")
        else:
            logging.error(f"Unexpected data format for added item: {item_value}")
            logging.info("____________________________\n")

    def new_versions_window(self, versions):
        ### Ventana que muestra cuantas versiones nuevas hay
        dialog = ctk.CTkToplevel(self.root)
        dialog.title(" ")

        # Establecer el icono, asegurandose de que el camino al archivo sea correcto
        icon_path = resource_path("no_icon.ico")
        setup_window_icon(dialog, icon_path) ##### Usar funcion para configurar el icono

        # Solucion para el problema en Windows con customtkinter
        if platform.system() == "Windows":
            dialog.after(200, lambda: setup_window_icon(dialog, icon_path))  ##### Usar funcion para configurar el icono con retraso en Windows        
            
        #center_window(dialog, 400, 300)
        
        set_title_bar_color(dialog, BG_Color, TXT_Color)  # Set title bar color

        # Configura el resto de los elementos de la ventana
        dialog.attributes('-topmost', True)  # Asegura que la ventana se mantenga en el frente

        
        # Se crea un marco sin padding y luego se configura el padding interno
        message_frame = ctk.CTkFrame(dialog)
        message_frame.pack(fill=ctk.BOTH, expand=True, padx=20, pady=(30, 10))

        count = len(versions)
        message = f"{count} new versions pulled from FPT"
        ctk.CTkLabel(message_frame, text=message).pack()

        button_frame = ctk.CTkFrame(dialog)
        button_frame.pack(fill=ctk.X, padx=(10, 20))

        # Almacena el ID del evento after para poder cancelarlo mas tarde
        self.after_id = None

        ok_button = ctk.CTkButton(button_frame, text="OK (30)", command=lambda: self.close_dialog_with_countdown(dialog), width=60)
        ok_button.pack(side=ctk.RIGHT, padx=10, pady=(10, 30))

        details_button = ctk.CTkButton(button_frame, text="Details",
                                        command=lambda: [dialog.destroy(), self.uploaded_versions_window(versions)], width=60)
        details_button.pack(side=ctk.RIGHT, padx=10, pady=(10, 30))
        
        # Configuracion para cerrar la ventana automaticamente despues de un tiempo
        def countdown(count=30):
            if dialog.winfo_exists():  # Verifica si el dialogo aun existe
                ok_button.configure(text=f"OK ({count})")  # Cambia config por configure aqui
                if count > 0:
                    self.after_id = dialog.after(1000, lambda: countdown(count-1))
                else:
                    dialog.destroy()

        self.adjust_window_size(dialog)

        countdown()

        # Vincular la tecla Esc para cerrar la ventana
        dialog.bind("<Escape>", lambda event: dialog.destroy())

    def uploaded_versions_window(self, versions):
        # Crear la ventana de detalles
        details_window = ctk.CTkToplevel(self.root)
        details_window.title("")
        
        # Configurar el icono y el color de la barra de titulo
        icon_path = resource_path("no_icon.ico")  # Obtener la ruta del icono
        setup_window_icon(details_window, icon_path) ##### Usar funcion para configurar el icono
        set_title_bar_color(details_window, BG_Color, TXT_Color)  # Configurar el color de la barra de titulo

        if platform.system() == "Windows":
            details_window.after(200, lambda: setup_window_icon(details_window, icon_path))  ##### Usar funcion para configurar el icono con retraso en Windows

        # Crear un frame para contener el texto y el scrollable frame
        container_frame = ctk.CTkFrame(details_window)
        container_frame.pack(padx=10, pady=0, fill="both", expand=True)

        # Definir el estilo del titulo
        title_font = ctk.CTkFont(size=15, weight="bold")  # Aumentar tamano y hacer negrita

        # Anadir el texto antes del scrollable frame
        label = ctk.CTkLabel(container_frame, text="  New versions pulled:", text_color=TXT_Color, anchor="w", font=title_font)

        label.pack(padx=10, pady=(0, 0), fill="x")

        # Crear inicialmente un CTkFrame normal
        initial_frame = ctk.CTkFrame(container_frame, corner_radius=10)
        initial_frame.pack(padx=10, pady=0, fill="both", expand=True)

        # Anadir etiquetas dentro del frame inicial para cada version
        for version in versions:
            version_label = ctk.CTkLabel(initial_frame, text=version, wraplength=initial_frame.winfo_width() - 20, anchor="w")
            version_label.pack(padx=10, pady=2, fill="x")

        # Actualizar la ventana para calcular el tamano necesario
        details_window.update_idletasks()

        # Almacenar las dimensiones antes de cambiar a scrollable
        initial_width = initial_frame.winfo_reqwidth() + 80
        initial_height = details_window.winfo_screenheight() * 0.9  # Establecer el alto al 90% de la altura de la pantalla

        # Comprobar si se necesita un scrollable frame
        if initial_frame.winfo_reqheight() > details_window.winfo_screenheight() * 0.9:
            # Si se excede el tamano, reemplazar con un CTkScrollableFrame
            initial_frame.pack_forget()  # Eliminar el frame inicial
            scrollable_frame = ctk.CTkScrollableFrame(container_frame, corner_radius=10)
            scrollable_frame.pack(padx=10, pady=0, fill="both", expand=True)

            # Volver a crear las etiquetas dentro del nuevo scrollable frame
            for version in versions:
                version_label = ctk.CTkLabel(scrollable_frame, text=version, wraplength=scrollable_frame.winfo_width() - 20, anchor="w")
                version_label.pack(padx=10, pady=2, fill="x")

            # Ajustar tamano de la ventana al usar scrollable
            details_window.geometry(f"{initial_width}x{int(initial_height)}")
            # Actualizar la ventana para calcular el tamano necesario
            details_window.update_idletasks()            
            center_window(details_window, initial_width, int(initial_height))
        else:
            self.adjust_window_size(details_window)

        # Vincular la tecla Esc para cerrar la ventana
        details_window.bind("<Escape>", lambda event: details_window.destroy())


    def close_dialog_with_countdown(self, dialog):
        if self.after_id:
            dialog.after_cancel(self.after_id)
        dialog.destroy()

    def close_uploaded_versions(self, window):
        # Cancelar todos los eventos after pendientes antes de cerrar la ventana
        if hasattr(self, 'after_ids'):
            for after_id in self.after_ids:
                window.after_cancel(after_id)
            self.after_ids.clear()
        window.destroy()

    def adjust_window_size(self, window):
        window.update_idletasks()  # Procesa los eventos pendientes para ajustar el layout correctamente
        width = window.winfo_reqwidth()  # Ancho requerido, ajustado despues de procesar idletasks
        height = window.winfo_reqheight()  # Altura requerida, ajustada de la misma forma
        window.geometry(f"{width}x{height}")  # Establece la nueva geometria con los valores ajustados
        center_window(window, width, height)  # Llama a un metodo para centrar la ventana correctamente


class SyncApp:
    def __init__(self, root, url, script_name, api_key):
        self.root = root
        self.url = url
        self.script_name = script_name
        self.api_key = api_key
        self.download_thread = None
        self.sg_downloader = None  
        self.sync_after_id = None        
        self.root.configure(fg_color=BG_Color)
        self.root.title(" ")
        self.tooltip_window = None
        self.running = False  # Variable para la cuenta regresiva
        self.progress_length = 0.35  # Longitud de la barra de progreso deslizante (35%)
        self.progress_position = 0.0  # Posicion inicial de la barra de progreso deslizante
        self.scheduler_thread = None

        # Ocultar la ventana inmediatamente despues de crearla para evitar parpadeos
        self.root.withdraw()  

        set_title_bar_color(self.root, BG_Color, TXT_Color)  # Cambiar title bar color

        # Reemplazo del icono del title bar con retardo
        icon_path = resource_path("no_icon.ico")
        setup_window_icon(self.root, icon_path)
        if platform.system() == "Windows":
            self.root.after(200, lambda: setup_window_icon(self.root, icon_path))

        self.sg_manager = None  # Inicializamos como None
        self.hiero_ops = None  # Inicializamos como None

        # Cargar la info del JSON de configuracion
        config = load_config() 
        self.auto_sync_var = tk.IntVar(value=config.get('auto_sync', 0))  
        self.sync_interval = config.get('sync_interval', '15') 
        self.start_minimized = config.get('start_minimized', False)
        self.close_to_tray = config.get('close_to_tray', True)    
        self.log_file_path = config.get('log_file_path', Script_Path)  # Default path si no esta especificado  
        self.project_names = config.get('project_names', ["", "", "", ""]) # Cargar nombres de proyectos o asignar una lista vacia si no hay        
        self.project_vars = [tk.StringVar(value=name) for name in self.project_names]

        # Contenido todo el contenido de la ventana
        self.create_widgets() 

        
        # Comprobar el estado del auto_sync y empezar a sincronizar si esta activado
        if self.auto_sync_var.get():
            self.start_sync()
            self.update_countdown()

        # Vincular la tecla Esc para cerrar la aplicacion
        self.root.bind("<Escape>", self.on_closing)

        self.adjust_window_size(self.root)  # Ajusta el tamano y posicion de la ventana antes de mostrarla
        
        # Configuracion del system tray
        self.image = Image.open(resource_path("LGA.ico")) 
         
        self.menu = (
            pystray.MenuItem('Show', self.show_window, default=True),
            pystray.MenuItem('Quit', self.quit_window)
        )
            
        # Definir accion del boton (la cruz) para cerrar la ventana
        self.root.protocol('WM_DELETE_WINDOW', self.close_action)
        
        # Abrir solo la ventana o solo el icono del tray dependiendo del setting de start minimized
        if self.start_minimized:
            self.icon = pystray.Icon("name", self.image, "title", self.menu)
            self.run_tray_icon()
        else:
            self.root.deiconify() # Muestra la ventana solo despues de que todo esta configurado y centrado


    def run_tray_icon(self):
        if platform.system() == "Darwin":
            threading.Thread(target=self.icon.run).start()
        else:
            self.icon.run()

    def create_widgets(self):
        # Frame de control principal
        control_frame = ctk.CTkFrame(self.root)
        control_frame.pack(pady=30, padx=40, fill=ctk.BOTH)

        # Checkbox para Auto-Sync
        self.auto_sync_check = ctk.CTkCheckBox(control_frame, text="Auto-Sync", variable=self.auto_sync_var, onvalue=1, offvalue=0, command=self.toggle_auto_sync)
        self.auto_sync_check.pack(side=ctk.LEFT, padx=10, anchor=ctk.W)

        # Mostrar de que el checkbox refleje el estado inicial correctamente
        self.auto_sync_check.select() if self.auto_sync_var.get() else self.auto_sync_check.deselect()

        # Etiqueta "every"
        every_label = ctk.CTkLabel(control_frame, text="every")
        every_label.pack(side=ctk.LEFT, padx=5, anchor=ctk.W)

        # Menu de opciones con valor predeterminado
        values = ["1", "15", "30", "60", "120"]
        self.interval_option = tk.StringVar()  # Inicializar interval_option como una StringVar
        self.interval_option_widget = ctk.CTkOptionMenu(control_frame, variable=self.interval_option, values=values, width=85)  # Usar interval_option_widget para el OptionMenu
        config = load_config()
        current_interval = config.get('sync_interval', '15')
        self.interval_option.set(current_interval)  # Establecer valor inicial desde configuracion
        self.interval_option_widget.pack(side=ctk.LEFT, padx=5, anchor=ctk.W)

        # Adaptar CTkScrollableDropdown solo cuando sea necesario
        self.interval_option_widget.bind("<Button-1>", self.create_dropdown)  # Enlazar evento al widget interval_option_widget

        # Etiqueta "minutes"
        minutes_label = ctk.CTkLabel(control_frame, text="minutes")
        minutes_label.pack(side=ctk.RIGHT, padx=20, anchor=ctk.W)

        # Etiqueta para la cuenta regresiva
        self.countdown_label = ctk.CTkLabel(self.root, text="Next Sync: -- sec")
        self.countdown_label.pack(pady=(10, 10))

        # Crear un frame para la barra de progreso con un tamano fijo
        self.progress_frame = ctk.CTkFrame(self.root, width=200, height=30)
        self.progress_frame.pack(pady=5)
        self.progress_frame.pack_propagate(False)  # Evitar que el frame cambie de tamano con el contenido

        self.progress_bar = ctk.CTkProgressBar(self.progress_frame, orientation="horizontal", mode="indeterminate", width=100, height=5)
        self.progress_bar.pack_forget()  # Asegurate de que este oculta inicialmente

        # Crear y configurar el boton Sync Now con la fuente personalizada
        self.sync_now_button = ctk.CTkButton(self.root, text="Sync Now", command=self.sync_now, text_color="#FFFFFF", width=60)
        self.sync_now_button.pack(pady=(0, 0))  # Ajustar el padding para dejar espacio para la barra de progreso

        # Bottom Frame para elementos alineados a izquierda y derecha
        bottom_frame = ctk.CTkFrame(self.root)
        bottom_frame.pack(fill=ctk.X, side=ctk.BOTTOM, pady=(0, 20))

        # Cargando las imagenes del boton de settings
        settings_off_ctk_image = ctk.CTkImage(dark_image=Image.open(resource_path("settings_off.png")), size=(16, 16))
        settings_on_ctk_image = ctk.CTkImage(dark_image=Image.open(resource_path("settings_on.png")), size=(16, 16))

        # Boton de configuracion
        self.settings_button = ctk.CTkButton(bottom_frame, text=" ", fg_color="#26272b", hover_color="#26272b", width=16, image=settings_off_ctk_image, command=self.settings_window)
        self.settings_button.image = settings_off_ctk_image  # Mantener una referencia
        self.settings_button.pack(side=ctk.LEFT, padx=24, pady=(16, 0))

        # Cambiar iconos en hover
        def on_enter(event):
            self.settings_button.configure(image=settings_on_ctk_image)
            self.settings_button.image = settings_on_ctk_image  # Actualizar referencia

        def on_leave(event):
            self.settings_button.configure(image=settings_off_ctk_image)
            self.settings_button.image = settings_off_ctk_image  # Actualizar referencia

        self.settings_button.bind("<Enter>", on_enter)
        self.settings_button.bind("<Leave>", on_leave)

        # Label de la version, alineado a la derecha
        version_label = ctk.CTkLabel(bottom_frame, text="v1.3", anchor="se")
        version_label.pack(side=ctk.RIGHT, padx=30)
        self.setup_tooltip(version_label, "Lega Pugliese - 2024")


    def create_dropdown(self, event):
        values = ["1", "15", "30", "60", "120"]
        dropdown = CTkScrollableDropdown(self.interval_option_widget, values=values, command=self.on_interval_change, scrollbar=False, frame_border_color="#443a91", button_color="#2a2a2a", fg_color="#2a2a2a")
        
        def on_focus_out(event):
            try:
                if dropdown.winfo_exists():
                    dropdown.destroy()
            except Exception as e:
                print(f"Error destroying dropdown: {e}")
        
        dropdown.bind("<FocusOut>", on_focus_out)
        self.dropdown = dropdown  # Guardar la referencia al dropdown

    def destroy_dropdown(self, dropdown):
        try:
            if dropdown.winfo_exists():
                dropdown.destroy()
        except Exception as e:
            print(f"Error destroying dropdown: {e}")


    def cancel_sync(self):
        if self.sg_downloader:
            self.sg_downloader.cancel_download = True

    def start_indeterminate_progress(self):
        self.progress_bar.configure(mode="indeterminate", indeterminate_speed=0.5)
        self.progress_bar.start()

    def stop_indeterminate_progress(self):
        self.progress_bar.stop()

    def show_progress_bar(self):
        self.progress_position = 0.0  # Reinicia la posicion de la barra de progreso deslizante
        self.progress_bar.pack(pady=(0, 0))
        self.root.update_idletasks()  # Actualiza la interfaz
        self.progress_bar.set(0)

    def hide_progress_bar(self):
        self.progress_bar.pack_forget()
        self.root.update_idletasks()  # Actualiza la interfaz
        self.progress_bar.set(0)

    def toggle_sync(self):
        if self.download_thread and self.download_thread.is_alive():
            # Si ya se esta ejecutando una sincronizacion, cancelala
            self.sg_downloader.cancel_download = True
            self.sync_now_button.configure(text="Sync Now", command=self.toggle_sync)
            self.progress_bar.set(0)  # Reiniciar la barra de progreso
        else:
            # Iniciar una nueva sincronizacion
            self.sg_downloader = ShotGridDownloader(self.url, self.script_name, self.api_key)
            self.progress_bar.set(0.1)  # Actualizar la barra de progreso
            self.sync_now_button.configure(text="Cancel Sync", command=self.toggle_sync)
            self.download_thread = threading.Thread(target=self.download_and_sync)
            self.download_thread.start()
            # Desactivar la tecla ESC durante la sincronizacion
            self.root.unbind("<Escape>")

    def settings_window(self):
        ### Ventana que muestra cuantas versiones nuevas hay
        config = load_config()
        self.settingsW = ctk.CTkToplevel(self.root)
        self.settingsW.title(" ")

        # Ocultar la ventana inmediatamente despues de crearla para evitar parpadeos
        self.settingsW.withdraw()

        # Establecer el icono, asegurandose de que el camino al archivo sea correcto
        icon_path = resource_path("no_icon.ico")
        setup_window_icon(self.settingsW, icon_path)

        # Solucion para el problema en Windows con customtkinter
        if platform.system() == "Windows":
            self.settingsW.after(200, lambda: setup_window_icon(self.settingsW, icon_path))

        set_title_bar_color(self.settingsW, BG_Color, TXT_Color)  # Set title bar color

        # Configura el resto de los elementos de la ventana
        self.settingsW.attributes('-topmost', True)  # Asegura que la ventana se mantenga en el frente

        # Se crea un marco sin padding y luego se configura el padding interno
        settings_frame = ctk.CTkFrame(self.settingsW)
        settings_frame.pack(fill=ctk.BOTH, expand=True, padx=20, pady=(10, 10))

        # Checkbox for Start Minimized
        self.start_minimized_var = tk.BooleanVar(value=self.start_minimized)
        start_minimized_check = ctk.CTkCheckBox(settings_frame, text="Start Minimized", variable=self.start_minimized_var, onvalue=True, offvalue=False, command=self.update_settings)
        start_minimized_check.pack(side=ctk.TOP, anchor=ctk.W, padx=30, pady=10)

        # Checkbox for Close to Tray
        self.close_to_tray_var = tk.BooleanVar(value=self.close_to_tray)
        close_to_tray_check = ctk.CTkCheckBox(settings_frame, text="Close to Tray", variable=self.close_to_tray_var, onvalue=True, offvalue=False, command=self.update_settings)
        close_to_tray_check.pack(side=ctk.TOP, anchor=ctk.W, padx=30, pady=10)

        # Checkbox for New Versions Pop-Up Windows
        self.new_versions_popup_var = tk.BooleanVar(value=config.get('new_versions_popup', True))
        new_versions_popup_check = ctk.CTkCheckBox(settings_frame, text="New versions pop-up windows", variable=self.new_versions_popup_var, onvalue=True, offvalue=False, command=self.update_settings)
        new_versions_popup_check.pack(side=ctk.TOP, anchor=ctk.W, padx=30, pady=10)

        # Frame para configuraciones de proyectos
        projects_frame = ctk.CTkFrame(settings_frame, border_width=0, border_color="#443a91")
        projects_frame.pack(fill=ctk.X, padx=(10, 20), pady=10)

        # Label para "Projects"
        projects_label = ctk.CTkLabel(projects_frame, text="Projects:")
        projects_label.pack(side=ctk.TOP, anchor=ctk.W, padx=(20, 0), pady=(10, 5))

        # Panel para contener los Entry widgets
        self.project_entries_frame = ctk.CTkFrame(projects_frame)
        self.project_entries_frame.pack(fill=ctk.X, expand=True, padx=(20, 20))

        # Metodo para agregar Entries inicialmente y luego dinamicamente
        self.refresh_project_entries()

        # Frame para los botones OK y Cancel debajo de los entries
        project_button_frame = ctk.CTkFrame(projects_frame)
        project_button_frame.pack(fill=ctk.X, padx=2, pady=(10, 10))

        # Boton OK para confirmar los cambios
        ok_project_button = ctk.CTkButton(project_button_frame, text="OK", width=20, command=self.save_projects)
        ok_project_button.pack(side=ctk.RIGHT, padx=(0, 20), pady=5)

        # Boton Cancel para cerrar la ventana de configuracion
        cancel_project_button = ctk.CTkButton(project_button_frame, text="Cancel", command=self.settingsW.destroy, width=20)
        cancel_project_button.pack(side=ctk.RIGHT, padx=10, pady=5)

        # Boton Add para anadir un nuevo proyecto
        add_button = ctk.CTkButton(project_button_frame, text="Add", width=20, command=self.add_project_entry)
        add_button.pack(side=ctk.RIGHT, padx=(0, 0), pady=5)

        # Crear frame para los settings del log
        logPath_frame = ctk.CTkFrame(settings_frame, border_width=0, border_color="#443a91")
        logPath_frame.pack(fill=ctk.X, padx=(10, 20), pady=10)

        # Frame para label y entry
        entry_frame = ctk.CTkFrame(logPath_frame)
        entry_frame.pack(fill=ctk.X, padx=2, pady=(10, 0))

        # Label para la ruta del archivo de log
        log_path_label = ctk.CTkLabel(entry_frame, text="Log file path:")
        log_path_label.pack(side=ctk.LEFT, padx=(20, 0), pady=5)

        # Entry para modificar la ruta del archivo de log
        self.log_path_var = tk.StringVar(value=self.log_file_path)
        log_path_entry = ctk.CTkEntry(entry_frame, textvariable=self.log_path_var, width=300)
        log_path_entry.pack(side=ctk.LEFT, fill=ctk.X, expand=True, padx=(10, 20), pady=5)

        # Frame para los botones
        button_frame = ctk.CTkFrame(logPath_frame)
        button_frame.pack(fill=ctk.X, padx=2, pady=(0, 10))

        # Boton OK para confirmar el cambio
        ok_button = ctk.CTkButton(button_frame, text="OK", width=20, command=lambda: self.update_log_path(log_path_entry.get(), self.settingsW))
        ok_button.pack(side=ctk.RIGHT, padx=(0, 20), pady=5)

        # Boton Cancel para cerrar la ventana
        cancel_button = ctk.CTkButton(button_frame, text="Cancel", command=self.settingsW.destroy, width=20)
        cancel_button.pack(side=ctk.RIGHT, padx=10, pady=5)

        # Boton Browse para abrir el cuadro de dialogo y seleccionar un path
        browse_button = ctk.CTkButton(button_frame, text="Browse", command=lambda: self.browse_log_path(log_path_entry), width=20)
        browse_button.pack(side=ctk.RIGHT, padx=0, pady=5)

        # Boton Open para abrir el archivo de log
        open_button = ctk.CTkButton(button_frame, text="Open", command=self.open_log_file, width=20)
        open_button.pack(side=ctk.RIGHT, padx=10, pady=5)

        # Boton Clear para borrar el contenido del log
        clear_button = ctk.CTkButton(button_frame, text="Clear", command=self.clear_log_file, width=20)
        clear_button.pack(side=ctk.RIGHT, padx=0, pady=5)

        # Almacena el ID del evento after para poder cancelarlo mas tarde
        self.after_id = None        

        self.adjust_window_size(self.settingsW)
        
        self.settingsW.deiconify()  # Muestra la ventana solo despues de que todo esta configurado y centrado
        self.settingsW.focus_force()  # Asegura que la ventana de configuraciones este enfocada y en el frente

        # Vincular la tecla Esc para cerrar la ventana
        self.settingsW.bind("<Escape>", lambda event: self.settingsW.destroy())

    def download_and_sync(self):
        # Detener las actualizaciones del contador
        if self.sync_after_id:
            self.root.after_cancel(self.sync_after_id)
            self.sync_after_id = None

        # Actualizar el label para mostrar que se esta sincronizando
        self.update_label_syncing()

        # Mostrar la barra de progreso
        self.show_progress_bar()
        self.start_indeterminate_progress()  # Iniciar la barra de progreso en modo indeterminado

        # Cambiar el boton a "Cancel Sync"
        self.sync_now_button.configure(text="Cancel Sync", command=self.cancel_sync)

        try:
            # Crear instancia de ShotGridDownloader
            self.sg_downloader = ShotGridDownloader(self.url, self.script_name, self.api_key)
            json_SG_output_file = os.path.join(Script_Path, 'LGA_NKS_Flow_Downloader_SG.json')

            # Crear y comenzar el hilo de descarga
            self.download_thread = threading.Thread(target=download_project_data, args=(self.sg_downloader, self.project_names, json_SG_output_file))
            self.download_thread.start()

            # Esperar a que el hilo de descarga termine
            self.download_thread.join()

            # Proceder con la sincronizacion despues de la descarga
            if not self.sg_downloader.cancel_download:
                current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                print(f"{current_time} - Termino el sync")
                self.initialize_sg_manager()
                self.job()
                self.sync_now_button.configure(text="Sync Now", command=self.sync_now)
                self.progress_bar.set(1.0)  # Completar la barra de progreso

                # Actualiza el tiempo de la proxima ejecucion despues de la sincronizacion
                interval = int(self.interval_option.get())  # Obtiene el valor actual del menu de opciones
                self.schedule_next_sync(interval)
            else:
                # Si se cancelo, reanudar el contador sin sincronizacion
                current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                print(f"{current_time} - Descarga cancelada.")
                self.update_label_cancelled()
                interval = int(self.interval_option.get())
                self.next_run_time = datetime.now() + timedelta(minutes=interval)
                self.update_countdown()

        except Exception as e:
            current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            print(f"{current_time} - Error en el hilo de descarga y sincronizacion: {e}")
            self.update_label_cancelled()
            interval = int(self.interval_option.get())
            self.next_run_time = datetime.now() + timedelta(minutes=interval)
            self.update_countdown()

        finally:
            self.sg_downloader = None  # Resetear la instancia de ShotGridDownloader
            self.download_thread = None  # Resetear el hilo de descarga
            self.stop_indeterminate_progress()  # Detener la barra de progreso indeterminado
            self.hide_progress_bar()  # Ocultar la barra de progreso
            self.sync_now_button.configure(text="Sync Now", command=self.sync_now)
            # Volver a habilitar la tecla ESC
            self.root.bind("<Escape>", self.on_closing)

    def update_progress_bar(self):
        if self.download_thread and self.download_thread.is_alive():
            self.progress_position += 0.01  # Incremento de la posicion
            if self.progress_position > 1.0:
                self.progress_position = 0.0  # Reinicia la posicion si se supera el 100%

            # Calcula el valor de la barra de progreso basado en la posicion y la longitud
            start = self.progress_position
            end = start + self.progress_length
            if end > 1.0:
                end = 1.0

            self.progress_bar.set(end)

            # Programa la proxima actualizacion
            self.root.after(100, self.update_progress_bar)
        else:
            self.progress_bar.set(1.0)  # Completa la barra de progreso si se ha terminado

    def open_log_file(self):
        log_file_path = os.path.join(self.log_path_var.get(), 'LGA_NKS_Flow_Downloader.log')
        # Abrir el archivo de log con la aplicacion predeterminada del sistema
        if os.path.exists(log_file_path):
            try:
                if platform.system() == "Windows":
                    os.startfile(log_file_path)
                elif platform.system() == "Darwin":
                    subprocess.call(("open", log_file_path))
                elif platform.system() == "Linux":
                    subprocess.call(("xdg-open", log_file_path))
            except Exception as e:
                print(f"Error al abrir el archivo de log: {e}")

    def clear_log_file(self):
        log_file_path = os.path.join(self.log_path_var.get(), 'LGA_NKS_Flow_Downloader.log')
        # Borrar el contenido del archivo de log
        try:
            with open(log_file_path, 'w', encoding='utf-8'):
                pass
            print("El archivo de log ha sido borrado.")
        except Exception as e:
            print(f"Error al borrar el archivo de log: {e}")

    def save_projects(self):
        # Recoger todos los valores no vacios de los Entry widgets
        project_names = [var.get().strip() for var in self.project_vars if var.get().strip()]
        # Actualizar la configuracion con los nombres de los proyectos
        new_config = {
            'auto_sync': self.auto_sync_var.get(),
            'sync_interval': self.interval_option.get(),
            'start_minimized': self.start_minimized_var.get(),
            'close_to_tray': self.close_to_tray_var.get(),
            'log_file_path': self.log_path_var.get(),
            'project_names': project_names
        }
        save_config(new_config)
        # Actualizar las variables de instancia segun el archivo de configuracion
        self.start_minimized = new_config['start_minimized']
        self.close_to_tray = new_config['close_to_tray']
        self.log_file_path = new_config['log_file_path']
        self.project_names = project_names  # Asegurarse de que la lista de proyectos se actualice en la interfaz de usuario
        self.settingsW.destroy()  # Cerrar la ventana de configuracion

    def refresh_project_entries(self):
        # Limpiar los widgets actuales
        for widget in self.project_entries_frame.winfo_children():
            widget.destroy()

        # Crear nuevos Entry widgets basados en project_vars
        for var in self.project_vars:
            entry = ctk.CTkEntry(self.project_entries_frame, textvariable=var, width=300)
            entry.pack(fill=ctk.X, expand=True, padx=(0, 0), pady=(5, 5))

    def add_project_entry(self):
        # Anadir una nueva StringVar vacia a la lista
        new_var = tk.StringVar(value="")
        self.project_vars.append(new_var)
        # Refrescar la lista de Entry widgets para incluir el nuevo
        self.refresh_project_entries()
        # Llamar al metodo para ajustar el tamano de la ventana
        self.adjust_window_size(self.settingsW)


    def browse_log_path(self, entry_widget):
        # Abrir el cuadro de dialogo para seleccionar un directorio, usando settingsW como el padre del dialogo
        directory = filedialog.askdirectory(parent=self.settingsW)  # Anade parent para asegurar que el dialogo aparezca encima
        if directory:  # Asegurate de que el usuario no haya cancelado el cuadro de dialogo
            entry_widget.delete(0, tk.END)  # Elimina el contenido actual del entry
            entry_widget.insert(0, directory)  # Inserta el directorio seleccionado en el entry

    def update_settings(self):
        new_config = {
            'auto_sync': self.auto_sync_var.get(),
            'sync_interval': self.interval_option.get(),
            'start_minimized': self.start_minimized_var.get(),
            'close_to_tray': self.close_to_tray_var.get(),
            'log_file_path': self.log_path_var.get(),
            'new_versions_popup': self.new_versions_popup_var.get()
        }
        save_config(new_config)
        # Actualizar las variables de instancia segun el archivo de configuracion
        self.start_minimized = new_config['start_minimized']
        self.close_to_tray = new_config['close_to_tray']
        logging.basicConfig(filename=new_config['log_file_path'], level=logging.INFO, format='%(message)s')

    def update_log_path(self, new_path, window):
        # Actualiza la configuracion del log path y guarda en el JSON
        self.log_file_path = new_path  # Actualiza la variable de instancia
        save_config({'log_file_path': new_path})  # Guarda la nueva configuracion

        # Actualizar la configuracion de logging al nuevo path
        log_file_path = os.path.join(new_path, 'LGA_NKS_Flow_Downloader.log')

        # Elimina todos los handlers antiguos para evitar duplicados
        for handler in logging.root.handlers[:]:
            logging.root.removeHandler(handler)

        # Configura un nuevo handler con codificacion UTF-8
        file_handler = logging.FileHandler(log_file_path, encoding='utf-8')
        file_handler.setLevel(logging.INFO)
        file_handler.setFormatter(logging.Formatter('%(asctime)s - %(message)s'))
        logging.root.addHandler(file_handler)

        window.destroy()  # Cierra la ventana de configuracion

    def close_action(self):
        # Accion del boton de cerrar ventana segun el setting de la configuracion
        if self.close_to_tray:
            self.withdraw_window()
        else:
            if platform.system() == "Darwin" and hasattr(self, 'icon') and self.icon:
                self.icon.stop()  # Detener el icono de pystray en macOS
            self.on_closing()


    def toggle_auto_sync(self):
        # Obtener el estado actual del checkbox y guardar en la configuracion
        current_state = self.auto_sync_var.get()  # Obtiene el estado actual del checkbox

        # Actualizar la configuracion de auto_sync
        config = load_config()
        config['auto_sync'] = current_state
        save_config(config)

        if current_state:
            self.start_sync()
            self.update_countdown()  # Asegurarse de que el contador se actualice al iniciar la sincronizacion
        else:
            self.stop_sync()
            self.update_countdown()  # Asegurarse de que el contador se actualice al detener la sincronizacion

    def quit_window(self):
        if self.download_thread and self.download_thread.is_alive():
            print("Cannot close the application while syncing.")
            return

        if platform.system() == "Darwin" and hasattr(self, 'icon') and self.icon is not None:
            self.icon.stop()  # Detener el icono de pystray en macOS
        self.root.quit()
        self.root.destroy()

    def show_window(self, icon=None, item=None):
        # Mostrar la ventana principal y ocultar el icono del system tray
        self.root.after(0, self.root.deiconify)
        if icon:
            icon.stop()
        elif platform.system() == "Darwin" and hasattr(self, 'icon') and self.icon is not None:
            self.icon.stop()  # Detener el icono de pystray en macOS

    def withdraw_window(self):
        self.root.withdraw()
        if platform.system() == "Darwin" and hasattr(self, 'icon') and self.icon is not None:
            self.icon.stop()  # Detener el icono de pystray en macOS
        self.icon = pystray.Icon("name", self.image, "title", self.menu)
        self.run_tray_icon()

    def setup_tooltip(self, widget, text):
        def on_enter(event):
            x = widget.winfo_rootx() + widget.winfo_width() - 155
            y = widget.winfo_rooty() + widget.winfo_height() + 17

            # Crear ventana Toplevel para el tooltip
            self.tooltip_window = tk.Toplevel(self.root)
            self.tooltip_window.wm_overrideredirect(True)
            self.tooltip_window.wm_geometry(f"+{x}+{y}")
            self.tooltip_window.config(bg='#26272a')  # Este color sera transparente

            # Aplicar transparencia
            self.tooltip_window.attributes('-transparentcolor', '#26272a')

            # Crear un CTkFrame dentro del Toplevel
            tooltip_frame = ctk.CTkFrame(self.tooltip_window, corner_radius=60, fg_color="#26272b")
            tooltip_frame.pack(padx=20, pady=10, fill="both", expand=True)

            # Agregar una etiqueta dentro del CTkFrame
            label = ctk.CTkLabel(tooltip_frame, text=text, fg_color="#26272b", text_color="gray84")
            label.pack(padx=20, pady=5)

        def on_leave(event):
            if self.tooltip_window:
                self.tooltip_window.destroy()
                self.tooltip_window = None

        widget.bind('<Enter>', on_enter)
        widget.bind('<Leave>', on_leave)

    def on_interval_change(self, new_interval):
        self.interval_option.set(new_interval)  # Establece el nuevo valor en la interfaz
        save_config({'auto_sync': self.auto_sync_var.get(), 'sync_interval': new_interval})  # Guarda el nuevo estado y el intervalo

        # Re-inicia el proceso de sincronizacion con el nuevo intervalo si ya esta en ejecucion
        if self.running:
            self.stop_sync()
            self.start_sync()
            self.update_countdown()


    def start_sync(self):
        interval = int(self.interval_option.get())
        self.next_run_time = datetime.now() + timedelta(minutes=interval)
        schedule.every(interval).minutes.do(self.job_wrapper)
        self.update_countdown()
        if not self.running:
            self.scheduler_thread = threading.Thread(target=self.run_scheduler)
            self.scheduler_thread.daemon = True
            self.scheduler_thread.start()
        self.running = True

    def stop_sync(self):
        if self.running:
            schedule.clear()
            self.running = False
        
        # Cancelar la proxima sincronizacion programada
        if self.sync_after_id:
            self.root.after_cancel(self.sync_after_id)
            self.sync_after_id = None

    def initialize_sg_manager(self):
        json_file_path = os.path.join(Script_Path, 'LGA_NKS_Flow_Downloader_SG.json')
        if not os.path.exists(json_file_path):
            # Si el archivo no existe, crea uno con la estructura minima necesaria
            initial_data = {'project': {'project_name': '', 'shots': []}}
            with open(json_file_path, 'w') as file:
                json.dump(initial_data, file, indent=4)
        # Siempre inicializa el ShotGridManager, lo que implica volver a leer el JSON
        self.sg_manager = ShotGridManager(json_file_path)
        self.hiero_ops = HieroOperations(self.root, self.sg_manager)

    def sync_now(self):
        # Verifica si ya se esta ejecutando una sincronizacion
        if self.download_thread and self.download_thread.is_alive():
            return

        # Detener la sincronizacion automatica
        if self.sync_after_id:
            self.root.after_cancel(self.sync_after_id)
            self.sync_after_id = None

        # Ejecutar el proceso de sync en un hilo separado
        sync_thread = threading.Thread(target=self.download_and_sync)
        sync_thread.start()

    def update_label_syncing(self):
        self.countdown_label.configure(text="Syncing now...", text_color="#774dcb")
        self.progress_bar.set(0)  # Inicializar la barra de progreso a 0

    def job_wrapper(self):
        self.job()
        # Actualiza el tiempo de la proxima ejecucion despues de cada ejecucion
        interval = int(self.interval_option.get())
        self.next_run_time = datetime.now() + timedelta(minutes=interval)
        self.update_countdown()  # Reinicia la cuenta regresiva despues de la ejecucion

    def update_countdown(self):
        if self.running:
            current_time = datetime.now()
            remaining_seconds = int((self.next_run_time - current_time).total_seconds())
            if remaining_seconds > 0:
                self.countdown_label.configure(text=f"Next Sync: {remaining_seconds} sec", text_color="gray84")
                self.sync_after_id = self.root.after(1000, self.update_countdown)  # Programa la proxima actualizacion en un segundo
            elif remaining_seconds <= 0:
                self.countdown_label.configure(text="Syncing now...", text_color="#774dcb")
                # Cancelar cualquier after_id anterior antes de configurar uno nuevo
                if hasattr(self, 'sync_after_id') and self.sync_after_id:
                    self.root.after_cancel(self.sync_after_id)
                self.sync_after_id = self.root.after(1000, self.sync_now)  # Espera un segundo antes de ejecutar la sincronizacion
        else:
            self.countdown_label.configure(text="Next Sync: -- sec", text_color="gray84")  # Usa configure en lugar de config

    def run_scheduler(self):
        while self.running:
            schedule.run_pending()
            time.sleep(1)

    def adjust_window_size(self, window):
        window.update_idletasks()  # Procesa los eventos pendientes para ajustar el layout correctamente
        width = window.winfo_reqwidth() + 0  # Ancho requerido mas 200 pixeles
        height = window.winfo_reqheight() + 0  # Altura requerida mas 50 pixeles
        window.geometry(f"{width}x{height}")  # Establece la nueva geometria con los valores ajustados
        center_window(window, width, height)  # Llama a un metodo para centrar la ventana correctamente

    def job(self):
        # Usa la variable de instancia para construir el path completo del archivo de salida
        output_file = os.path.join(Script_Path, 'LGA_NKS_Flow_Downloader_Local.json')
        self.hiero_ops.process_all_shots(output_file)

    def on_closing(self, event=None):
        if self.download_thread and self.download_thread.is_alive():
            print("Cannot close the application while syncing.")
            return

        # Si hay una descarga en curso, cancelar la descarga
        if self.sg_downloader and self.download_thread and self.download_thread.is_alive():
            self.sg_downloader.cancel_download = True
            self.download_thread.join(timeout=5)  # Espera un maximo de 5 segundos a que el hilo de descarga termine

        if self.running:
            self.stop_sync()
            if self.scheduler_thread and self.scheduler_thread.is_alive():
                self.scheduler_thread.join(timeout=5)  # Espera un maximo de 5 segundos a que el hilo termine

        if platform.system() == "Darwin" and hasattr(self, 'icon') and self.icon is not None:
            self.icon.stop()  # Detener el icono de pystray en macOS
        self.root.quit()  # Finaliza mainloop
        self.root.destroy()  # Destruye la ventana principal y todas las ventanas derivadas




    def update_label_cancelled(self):
        # Actualizar el label para mostrar que la descarga fue cancelada
        self.countdown_label.configure(text="Sync Cancelled")

    def update_label_next_sync(self, seconds):
        # Actualizar el label para mostrar el tiempo restante para la proxima sincronizacion
        self.countdown_label.configure(text=f"Next Sync: {seconds} sec")

    def countdown(self, remaining_seconds):
        # Actualizar el contador y llamar a la funcion despues de 1 segundo
        if remaining_seconds <= 0:
            self.sync_now()
            return

        self.update_label_next_sync(remaining_seconds)
        self.sync_after_id = self.root.after(1000, lambda: self.countdown(remaining_seconds - 1))

    def schedule_next_sync(self, interval_minutes):
        # Programar la proxima sincronizacion despues del intervalo especificado
        interval_seconds = interval_minutes * 60  # Convertir minutos a segundos
        self.sync_after_id = self.root.after(interval_seconds * 1000, self.sync_now)

        # Actualizar el label para reflejar el tiempo restante para la proxima sincronizacion
        self.update_label_next_sync(interval_seconds)


def setup_window_icon(window, icon_path):
    try:
        icon = Image.open(icon_path)
        window.iconphoto(True, ImageTk.PhotoImage(icon))
    except Exception as e:
        print(f"Error setting window icon: {e}")

def center_window(window, width=400, height=200):
    window.update_idletasks()  # Procesa eventos pendientes para ajustar el layout correctamente
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()
    x = (screen_width // 2) - (width // 2)
    y = (screen_height // 2) - (height // 2) - 40  # Restar 40 pixeles a la coordenada 'y' para compensar la barra de tareas
    window.geometry(f'{width}x{height}+{x}+{y}')
    window.deiconify()  # Mostrar la ventana despues de centrarla

def adjust_window_size(window):
    window.update()  # Importante: actualiza el estado de la ventana
    width = window.winfo_reqwidth() + 300  # Ancho requerido mas 200 pixeles
    height = window.winfo_reqheight() + 300  # Altura requerida mas 50 pixeles
    window.geometry(f"{width}x{height}")  # Establece la nueva geometria

    # Centrar la ventana despues de ajustar el tamano
    center_window(window, width, height)

def set_title_bar_color(window, title_bar_color, title_text_color):
    if platform.system() == "Windows" and platform.release() == "10":
        window.update_idletasks()  # Asegurarse de que la ventana este completamente inicializada

        try:
            hwnd = windll.user32.GetParent(window.winfo_id())

            # Invertir los canales de color de RGB a BGR
            _title_bar_color = int(title_bar_color[1:], 16)  # Convertir de hex a int
            _title_text_color = int(title_text_color[1:], 16)  # Convertir de hex a int

            # Reorganizar los canales RGB a BGR
            _title_bar_color = ((_title_bar_color & 0xff) << 16) + (_title_bar_color & 0xff00) + ((_title_bar_color & 0xff0000) >> 16)
            _title_text_color = ((_title_text_color & 0xff) << 16) + (_title_text_color & 0xff00) + ((_title_text_color & 0xff0000) >> 16)

            set_window_attribute = windll.dwmapi.DwmSetWindowAttribute
            set_window_attribute(hwnd, 35, byref(c_int(_title_bar_color)), sizeof(c_int))
            set_window_attribute(hwnd, 36, byref(c_int(_title_text_color)), sizeof(c_int))
            window.wm_title(window.wm_title())  # Forzar una actualizacion de la barra de titulo
        except Exception as e:
            print(f"Failed to set title bar color: {e}")

def download_project_data(downloader, project_names, json_output_file):
    downloader.download_and_save_data(project_names, json_output_file)

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    if getattr(sys, 'frozen', False):
        # El ejecutable empaquetado por PyInstaller
        base_path = os.path.dirname(sys.executable)
    else:
        # En el entorno de desarrollo
        base_path = os.path.dirname(os.path.abspath(__file__))

    return os.path.join(base_path, "Data", relative_path)

def load_config():
    config_path = os.path.join(Script_Path, 'LGA_NKS_Flow_Downloader_Config.json')
    if os.path.exists(config_path):
        with open(config_path, 'r', encoding='utf-8') as config_file:
            try:
                return json.load(config_file)
            except json.JSONDecodeError:
                pass
    return {"auto_sync": False, "sync_interval": "15"}  # Valores predeterminados

def save_config(new_config):
    config_path = os.path.join(Script_Path, 'LGA_NKS_Flow_Downloader_Config.json')
    # Carga la configuracion existente o usa la predeterminada si el archivo no existe
    config = load_config()  
    # Actualiza la configuracion con los nuevos valores
    config.update(new_config)
    # Guarda la configuracion actualizada
    with open(config_path, 'w', encoding='utf-8') as config_file:
        json.dump(config, config_file, ensure_ascii=False, indent=4)

def main():
    # Obtener el usuario y la contrasena de las variables de entorno
    sg_url = os.getenv('SHOTGRID_URL')
    sg_script_name = os.getenv('SHOTGRID_SCRIPT_NAME')
    sg_api_key = os.getenv('SHOTGRID_API_KEY')

    if not sg_url or not sg_script_name or not sg_api_key:
        print("Las variables de entorno SHOTGRID_URL, SHOTGRID_SCRIPT_NAME y SHOTGRID_API_KEY deben estar configuradas.")
        return

    # Cargar info del archivo de config.json
    config = load_config()

    ####### Logging
    # Carga la configuracion o establece un valor predeterminado para el directorio
    log_file_directory = config.get('log_file_path', Script_Path)

    # Concatena el directorio con el nombre del archivo para formar la ruta completa del archivo de log
    log_file_path = os.path.join(log_file_directory, 'LGA_NKS_Flow_Downloader.log')

    # Configura el logger con codificacion UTF-8
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    # Elimina todos los handlers antiguos
    while logger.handlers:
        logger.removeHandler(logger.handlers[0])

    # Anade el nuevo FileHandler con codificacion UTF-8
    file_handler = logging.FileHandler(log_file_path, encoding='utf-8')
    file_handler.setFormatter(logging.Formatter('%(message)s'))
    logger.addHandler(file_handler)

    ######## Crear y cerrar la ventana master (root) de la app
    root = ctk.CTk()  # Crear instancia principal de Tk
    root.withdraw()  # Oculta la ventana principal para evitar mostrar la ventana en blanco con titulo 'tk'

    # Cargar un custom theme
    ctk.set_default_color_theme(resource_path("LGA_NKS_Flow_Downloader_CCTK_Theme.json"))

    app = SyncApp(root, sg_url, sg_script_name, sg_api_key)
    root.mainloop()

if __name__ == "__main__":
    main()

