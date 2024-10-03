
import tkinter as tk
# version comparacion local de jsons
from tkinter import ttk
from ttkthemes import ThemedTk
import json
import os
import sys
import schedule
import time
import threading
import shotgun_api3
import logging
import sv_ttk
from datetime import datetime, timedelta
from deepdiff import DeepDiff  # Para comparar diccionarios de JSON
from datetime import datetime
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
    def __init__(self, root, shotgrid_manager):
        self.root = root  # Utiliza la ventana raiz proporcionada
        self.sg_manager = shotgrid_manager
        center_window(self.root, 800, 600)

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
        self.show_initial_dialog(versions_uploaded, self.root)

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

    def show_initial_dialog(self, versions, root):
    ### Ventana que muestra cuantas versiones nuevas hay
        dialog = tk.Toplevel(self.root)
        dialog.title("FPT Pull Cache")
        dialog.configure(bg='#333333')
        center_window(dialog, 400, 300)
        dialog.attributes('-topmost', True)  # Asegura que la ventana se mantenga en el frente
        dialog.overrideredirect(True)  # Aplica overrideredirect tambien aqui si es necesario

        font_family = "Segoe UI"
        font_size = 10
        message_frame = tk.Frame(dialog, bg='#333333', padx=20, pady=20)
        message_frame.pack(fill=tk.BOTH, expand=True)

        count = len(versions)
        message = f"{count} new versions pulled from FPT"
        tk.Label(message_frame, text=message, fg='#E0E0E0', bg='#333333', font=(font_family, font_size)).pack()

        button_frame = tk.Frame(dialog, bg='#333333', pady=10)
        button_frame.pack(fill=tk.X)

        # Almacena el ID del evento after para poder cancelarlo mas tarde
        self.after_id = None

        ok_button = tk.Button(button_frame, text="OK (30)", command=lambda: self.close_dialog_with_countdown(dialog),
                              bg='#333333', fg='#E0E0E0', font=(font_family, font_size))
        ok_button.pack(side=tk.RIGHT, padx=10)

        details_button = tk.Button(button_frame, text="Details",
                                   command=lambda: [dialog.destroy(), self.show_uploaded_versions(versions, root)],
                                   bg='#333333', fg='#E0E0E0', font=(font_family, font_size))
        details_button.pack(side=tk.RIGHT, padx=10)

        def countdown(count=30):
            if dialog.winfo_exists():  # Verifica si el dialogo aun existe
                ok_button.config(text=f"OK ({count})")
                if count > 0:
                    self.after_id = dialog.after(1000, lambda: countdown(count-1))
                else:
                    dialog.destroy()

        countdown()

    def close_dialog_with_countdown(self, dialog):
        if self.after_id:
            dialog.after_cancel(self.after_id)
        dialog.destroy()

    def show_uploaded_versions(self, versions):
    ### Ventana que muestra el detalle de versiones
        details_window = tk.Toplevel(root)
        details_window.title("New versions pulled from FPT")
        details_window.configure(bg='#333333')
        center_window(details_window, 500, 400)
        details_window.overrideredirect(True)  # Aplicar overrideredirect tambien a esta ventana

        st = scrolledtext.ScrolledText(details_window, bg='#333333', fg='#E0E0E0')
        for version in versions:
            st.insert(tk.END, version + '\n')

        st.pack(fill=tk.BOTH, expand=True)

        # Asegurarse de limpiar cualquier after pendiente al cerrar la ventana
        details_window.protocol("WM_DELETE_WINDOW", lambda: self.close_uploaded_versions(details_window))

    def close_uploaded_versions(self, window):
        # Cancelar todos los eventos after pendientes antes de cerrar la ventana
        if hasattr(self, 'after_ids'):
            for after_id in self.after_ids:
                window.after_cancel(after_id)
            self.after_ids.clear()
        window.destroy()

    def close_root(self):
        self.root.destroy()

class SyncApp:
    def __init__(self, root, shotgrid_manager):
        self.root = root
        self.root.title("ShotGrid Sync Manager")

        self.sg_manager = shotgrid_manager
        self.hiero_ops = HieroOperations(self.root, self.sg_manager)  # Pasa self.root como argumento

        self.auto_sync = tk.BooleanVar(value=False)  # Inicializa aqui

        #self.setup_custom_title_bar()
        self.create_widgets()
        self.adjust_window_size()
        self.scheduler_thread = None
        self.running = False
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def create_widgets(self):
       
        control_frame = ttk.Frame(self.root)  # Usar ttk.Frame
        control_frame.pack(pady=50, padx=40)

        # Checkbox para Auto-Sync
        self.auto_sync_check = ttk.Checkbutton(control_frame, text="Auto-Sync", variable=self.auto_sync)
        self.auto_sync_check.pack(side=tk.LEFT, padx=10)

        # Dropdown para seleccionar el intervalo
        self.interval_option = tk.StringVar()
        self.interval_option.set("15")  # default value
        self.interval_dropdown = ttk.OptionMenu(control_frame, self.interval_option, "1", "15")
        self.interval_dropdown.pack(side=tk.LEFT, padx=5)

        # Boton Sync Now
        self.sync_now_button = ttk.Button(control_frame, text="Sync Now", command=self.sync_now)
        self.sync_now_button.pack(side=tk.LEFT, padx=10)

        # Etiqueta de estado
        self.status_label = ttk.Label(self.root, text="Status: Sync Deactivated", foreground="red")
        self.status_label.pack(pady=10)

        # Etiqueta para la cuenta regresiva
        self.countdown_label = ttk.Label(self.root, text="Next Sync: -- sec", foreground='#E0E0E0')
        self.countdown_label.pack(pady=10)

    def on_interval_change(self, *args):
        if self.running:
            self.stop_sync()
            self.start_sync()
            self.update_countdown()


    def toggle_auto_sync(self):
        if self.auto_sync.get():
            self.start_sync()
            self.update_countdown()  # Inicia la cuenta regresiva
        else:
            self.stop_sync()
            self.update_countdown()  # Actualiza el label para mostrar "--"

    def sync_now(self):
        self.job()
        # Actualiza el tiempo de la proxima ejecucion despues de la sincronizacion
        interval = int(self.interval_option.get())
        self.next_run_time = datetime.now() + timedelta(minutes=interval)
        self.update_countdown()  # Reinicia la cuenta regresiva despues de la ejecucion


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
        self.status_label.config(text="Status: Sync Activated", fg="green")

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
                self.countdown_label.config(text=f"Next Sync: {remaining_seconds} sec")
                self.root.after(1000, self.update_countdown)  # Programa la proxima actualizacion en un segundo
            elif remaining_seconds <= 0:
                self.countdown_label.config(text="Syncing now...")
                # Cancelar cualquier after_id anterior antes de configurar uno nuevo
                if hasattr(self, 'sync_after_id') and self.sync_after_id:
                    self.root.after_cancel(self.sync_after_id)
                self.sync_after_id = self.root.after(1000, self.sync_now)  # Espera un segundo antes de ejecutar la sincronizacion
        else:
            self.countdown_label.config(text="Next Sync: -- sec")
        
    def stop_sync(self):
        if self.running:
            schedule.clear()
            self.running = False
            self.status_label.config(text="Status: Sync Deactivated", fg="red")

    def run_scheduler(self):
        while self.running:
            schedule.run_pending()
            time.sleep(1)

    def adjust_window_size(self):
        self.root.update()  # Importante: actualiza el estado de la ventana
        width = self.root.winfo_reqwidth() + 200  # Ancho requerido mas 200 pixeles
        height = self.root.winfo_reqheight() + 50  # Altura requerida mas 50 pixeles
        self.root.geometry(f"{width}x{height}")  # Establece la nueva geometria

        # Centrar la ventana despues de ajustar el tamano
        center_window(self.root, width, height)

    def job(self):
        output_file = 'T:/LGA_Cache-Local.json'
        self.hiero_ops.process_all_shots(output_file)
        print("Sincronizacion completada.")

    def on_closing(self):
        if self.running:
            self.stop_sync()
            if self.scheduler_thread and self.scheduler_thread.is_alive():
                self.scheduler_thread.join()  # Espera a que el hilo termine
        self.root.quit()  # Finaliza mainloop
        self.root.destroy()  # Destruye la ventana principal y todas las ventanas derivadas
        self.hiero_ops.close_root()  # Cierra la ventana raiz de HieroOperations
        
    def setup_custom_title_bar(self):
        title_bar = ttk.Frame(self.root, style="TitleBar.TFrame")
        title_bar.pack(side="top", fill="x")
        title_label = ttk.Label(title_bar, text="ShotGrid Sync Manager", style="TitleBar.TLabel")
        title_label.pack(side="left", padx=10)
        close_button = ttk.Button(title_bar, text="X", command=self.close_app, style="CloseButton.TButton")
        close_button.pack(side="right", padx=5)
        title_bar.bind("<Button-1>", self.start_move)
        title_bar.bind("<ButtonRelease-1>", self.stop_move)
        title_bar.bind("<B1-Motion>", self.on_move)

    def close_app(self):
        self.root.destroy()

    def start_move(self, event):
        self.root.x = event.x
        self.root.y = event.y

    def stop_move(self, event):
        self.root.x = None
        self.root.y = None

    def on_move(self, event):
        deltax = event.x - self.root.x
        deltay = event.y - self.root.y
        x = self.root.winfo_x() + deltax
        y = self.root.winfo_y() + deltay
        self.root.geometry(f"+{x}+{y}")

# Configuracion para mantener coherencia con el tema oscuro
style = ttk.Style()
style.configure("TitleBar.TFrame", background="#333333")
style.configure("TitleBar.TLabel", background="#333333", foreground="white")
style.configure("CloseButton.TButton", background="#333333", foreground="white")

def center_window(window, width=400, height=200):
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()
    x = int((screen_width / 2) - (width / 2))
    y = int((screen_height / 2) - (height / 2))
    window.geometry(f'{width}x{height}+{x}+{y}')

def main():
    root = ThemedTk(theme="sun-valley")
    root.title("ShotGrid Sync Manager")

    # Configurar tamano y posicion antes de overrideredirect
    #root.geometry("800x600")  # Ajusta esto segun tus necesidades
    #center_window(root, 800, 600)
    
    # Ahora aplicar overrideredirect
    #root.overrideredirect(True)
    
    sg_manager = ShotGridManager('T:/LGA_Cache-SG.json')
    app = SyncApp(root, sg_manager)
    root.mainloop()



if __name__ == "__main__":
    main()

