"""
_____________________________________________________________________________________________________

  LGA_showInFlow v2.3 | 2024 | Lega
  Abre la URL de la task Comp del shot, tomando la informacion del nombre del script


_____________________________________________________________________________________________________
"""

import os
import sys
import re
import platform
import nuke
import webbrowser
import threading
import subprocess
import configparser

# Agregar la ruta de la carpeta shotgun_api3 al sys.path
script_dir = os.path.dirname(os.path.abspath(__file__))
shotgun_api_path = os.path.join(script_dir, "shotgun_api3")
sys.path.append(shotgun_api_path)

# Ahora importamos shotgun_api3
import shotgun_api3

# Constantes para el archivo de configuracion (adaptadas del ejemplo)
CONFIG_FILE_NAME = "ShowInFlow.ini"
CONFIG_SECTION = "Credentials"
CONFIG_URL_KEY = "shotgrid_url"
CONFIG_LOGIN_KEY = "shotgrid_login"
CONFIG_PASSWORD_KEY = "shotgrid_password"

# --- Inicio: Funciones de manejo de configuracion (basadas en LGA_Write_Focus.py) ---


def get_config_path():
    """Devuelve la ruta completa al archivo de configuracion."""
    try:
        appdata_path = os.getenv("APPDATA")
        if not appdata_path:
            print("Error: No se pudo encontrar la variable de entorno APPDATA.")
            return None
        config_dir = os.path.join(appdata_path, "LGA", "ToolPack")
        return os.path.join(config_dir, CONFIG_FILE_NAME)
    except Exception as e:
        print(f"Error al obtener la ruta de configuracion: {e}")
        return None


def ensure_config_exists():
    """
    Asegura que el directorio de configuracion y el archivo .ini existan.
    Si no existen, los crea con valores vacios.
    """
    config_file_path = get_config_path()
    if not config_file_path:
        return  # Salir si no se pudo obtener la ruta

    config_dir = os.path.dirname(config_file_path)

    try:
        # Crear el directorio si no existe
        if not os.path.exists(config_dir):
            os.makedirs(config_dir)
            print(f"Directorio de configuracion creado: {config_dir}")

        # Crear el archivo .ini si no existe
        if not os.path.exists(config_file_path):
            config = configparser.ConfigParser()
            config[CONFIG_SECTION] = {
                CONFIG_URL_KEY: "",
                CONFIG_LOGIN_KEY: "",
                CONFIG_PASSWORD_KEY: "",
            }
            with open(config_file_path, "w", encoding="utf-8") as configfile:
                config.write(configfile)
            print(
                f"Archivo de configuración creado: {config_file_path}. Por favor, complételo con sus credenciales."
            )
        # else: # Debugging opcional como en el ejemplo
        #     print(f"Archivo de configuración ya existe: {config_file_path}")

    except Exception as e:
        print(f"Error al asegurar la configuración: {e}")


def get_credentials_from_config():
    """
    Lee las credenciales de ShotGrid desde el archivo .ini.
    Devuelve (url, login, password) o (None, None, None) si hay errores o faltan datos.
    Usa print para errores internos, similar al ejemplo.
    """
    config_file_path = get_config_path()
    if not config_file_path or not os.path.exists(config_file_path):
        print(
            f"Archivo de configuración no encontrado en la ruta esperada: {config_file_path}"
        )
        return None, None, None

    try:
        config = configparser.ConfigParser()
        config.read(config_file_path, encoding="utf-8")

        # Verificar si la seccion y las claves existen
        if (
            config.has_section(CONFIG_SECTION)
            and config.has_option(CONFIG_SECTION, CONFIG_URL_KEY)
            and config.has_option(CONFIG_SECTION, CONFIG_LOGIN_KEY)
            and config.has_option(CONFIG_SECTION, CONFIG_PASSWORD_KEY)
        ):

            sg_url = config.get(CONFIG_SECTION, CONFIG_URL_KEY).strip()
            sg_login = config.get(CONFIG_SECTION, CONFIG_LOGIN_KEY).strip()
            sg_password = config.get(CONFIG_SECTION, CONFIG_PASSWORD_KEY).strip()

            # Validar que los valores no esten vacios
            if sg_url and sg_login and sg_password:
                return sg_url, sg_login, sg_password
            else:
                print(f"Una o más credenciales en {config_file_path} están vacías.")
                return None, None, None
        else:
            missing = []
            if not config.has_section(CONFIG_SECTION):
                missing.append(f"Seccion [{CONFIG_SECTION}]")
            if not config.has_option(CONFIG_SECTION, CONFIG_URL_KEY):
                missing.append(f"Clave {CONFIG_URL_KEY}")
            if not config.has_option(CONFIG_SECTION, CONFIG_LOGIN_KEY):
                missing.append(f"Clave {CONFIG_LOGIN_KEY}")
            if not config.has_option(CONFIG_SECTION, CONFIG_PASSWORD_KEY):
                missing.append(f"Clave {CONFIG_PASSWORD_KEY}")
            print(
                f"Configuración incompleta en {config_file_path}. Falta: {', '.join(missing)}"
            )
            return None, None, None

    except configparser.Error as e:
        print(f"Error al leer el archivo de configuración {config_file_path}: {e}.")
        return None, None, None
    except Exception as e:
        print(f"Error inesperado al leer la configuración: {e}.")
        return None, None, None


# --- Fin: Funciones de manejo de configuracion ---

# Asegurarse de que el archivo de configuracion existe al iniciar (como en el ejemplo)
ensure_config_exists()

# Verificacion del sistema operativo y configuracion de la ruta del navegador
if platform.system() == "Windows":
    # print("Windows")
    browser_path = "C:/Program Files/Google/Chrome/Application/chrome.exe %s"
elif platform.system() == "Darwin":  # macOS
    # print("mac")
    browser_path = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
else:
    browser_path = ""  # Ruta del navegador para otros sistemas, si aplica
    # debug_print ("No se detecto el OS") # Corregido: Eliminado/Comentado

use_default_browser = False  # Si esta en True, usa el navegador por defecto, si esta en False, usa browser_path

DEBUG = True


# Definir debug_print aqui para que siempre exista
def debug_print(*message):
    if DEBUG:
        print(*message)


class ShotGridManager:
    def __init__(self, url, login, password):
        self.sg = shotgun_api3.Shotgun(url, login=login, password=password)

    def find_shot_and_tasks(self, project_name, shot_code):
        debug_print(f"Buscando proyecto: {project_name}, shot: {shot_code}")
        projects = self.sg.find(
            "Project", [["name", "is", project_name]], ["id", "name"]
        )
        if projects:
            project_id = projects[0]["id"]
            debug_print(f"Proyecto encontrado: {project_id}")
            filters = [
                ["project", "is", {"type": "Project", "id": project_id}],
                ["code", "is", shot_code],
            ]
            fields = ["id", "code", "description"]
            shots = self.sg.find("Shot", filters, fields)
            if shots:
                shot_id = shots[0]["id"]
                debug_print(f"Shot encontrado: {shot_id}")
                tasks = self.find_tasks_for_shot(shot_id)
                return shots[0], tasks
            else:
                debug_print("No se encontro el shot.")
        else:
            debug_print("No se encontro el proyecto en ShotGrid.")
        return None, None

    def find_tasks_for_shot(self, shot_id):
        debug_print(f"Buscando tareas para el shot: {shot_id}")
        filters = [["entity", "is", {"type": "Shot", "id": shot_id}]]
        fields = ["id", "content", "sg_status_list"]
        tasks = self.sg.find("Task", filters, fields)
        debug_print(f"Tareas encontradas: {tasks}")
        return tasks

    def get_task_url(self, task_id):
        return f"{self.sg.base_url}/detail/Task/{task_id}"


class NukeOperations:
    def __init__(self, shotgrid_manager):
        self.sg_manager = shotgrid_manager

    def parse_nuke_script_name(self, file_name):
        base_name = re.sub(r"_%04d\.nk$", "", file_name)
        version_match = re.search(r"_v(\d+)", base_name)
        version_number = version_match.group(1) if version_match else "Unknown"
        return base_name, version_number

    def process_current_script(self):
        file_path = nuke.root().name()
        debug_print(f"Nuke script file path: {file_path}")
        if file_path:
            nuke_script_name = os.path.basename(file_path)
            debug_print(f"Nuke script name: {nuke_script_name}")
            base_name, nuke_version_number = self.parse_nuke_script_name(
                nuke_script_name
            )
            debug_print(
                f"Parsed base name: {base_name}, version number: {nuke_version_number}"
            )
            project_name = base_name.split("_")[0]
            parts = base_name.split("_")
            shot_code = "_".join(parts[:5])
            debug_print(f"Project name: {project_name}, shot code: {shot_code}")

            shot, tasks = self.sg_manager.find_shot_and_tasks(project_name, shot_code)
            if shot:
                for task in tasks:
                    if task["content"] == "Comp":
                        task_url = self.sg_manager.get_task_url(task["id"])
                        debug_print(
                            f"  - Task: {task['content']} (Status: {task['sg_status_list']}) URL: {task_url}"
                        )
                        if use_default_browser:
                            webbrowser.open(task_url)
                        else:
                            self.open_url_in_browser(task_url)
            else:
                debug_print("No se encontro el shot correspondiente en ShotGrid.")
        else:
            debug_print("No se encontro un script activo en Nuke.")

    def open_url_in_browser(self, url):
        if platform.system() == "Darwin":  # macOS
            try:
                subprocess.run([browser_path, url])
                debug_print(f"Opening {url} in specified browser on macOS...")
            except Exception as e:
                debug_print(f"Failed to open URL in specified browser on macOS: {e}")
        elif platform.system() == "Windows":
            debug_print("Windows")
            try:
                webbrowser.get(browser_path).open(url)
                debug_print(f"Opening {url} in specified browser on Windows...")
            except Exception as e:
                debug_print(f"Failed to open URL in specified browser on Windows: {e}")


def threaded_function():
    # Leer credenciales desde el archivo .ini usando la funcion adaptada
    sg_url, sg_login, sg_password = get_credentials_from_config()

    # Verificar si las credenciales se leyeron correctamente
    if not sg_url or not sg_login or not sg_password:
        # Si fallo, get_credentials_from_config ya imprimio el error.
        # Preparar mensaje de error para devolver.
        config_path = get_config_path() or "AppData\\LGA\\ToolPack\\ShowInFlow.ini"
        error_message = f"No se pudieron leer las credenciales de ShotGrid desde:\n{config_path}\n\nRevise la consola para detalles y asegúrese de que el archivo esté completo."
        # print(f"Debug: Devolviendo error - {error_message}") # Debug opcional
        return error_message  # Devolver el mensaje de error

    # Si las credenciales son validas, proceder con la logica original
    try:
        debug_print(f"Conectando a ShotGrid URL: {sg_url} con login: {sg_login}")
        sg_manager = ShotGridManager(sg_url, sg_login, sg_password)
        nuke_ops = NukeOperations(sg_manager)
        nuke_ops.process_current_script()  # Ejecutar la lógica principal
        return None  # Indicar éxito

    except shotgun_api3.AuthenticationFault:
        # Error especifico de autenticacion
        error_message = f"Error de autenticación con ShotGrid.\nVerifique las credenciales en:\n{get_config_path()}"
        debug_print("Error de autenticación con ShotGrid.")
        return error_message  # Devolver el mensaje de error

    except Exception as e:
        # Otros errores durante la conexion o procesamiento
        error_message = (
            f"Ocurrió un error al conectar o procesar la información de ShotGrid: {e}"
        )
        debug_print(f"Error detallado: {e}")
        return error_message  # Devolver el mensaje de error


def main():
    # Crear un objeto para almacenar el resultado del hilo
    result_container = {}

    def run_in_thread():
        result_container["error"] = threaded_function()

    thread = threading.Thread(target=run_in_thread)
    thread.start()
    thread.join()  # Esperar a que el hilo termine (bloquea UI)

    # Verificar si hubo un error devuelto por el hilo
    error_message = result_container["error"]
    if error_message:
        nuke.message(error_message)  # Mostrar el error en el hilo principal

    # El join del comentario original ya no es necesario aquí
    # # Este join lo tuve que agregar en MAC. Volver a probar en mac y si es necesario agregarlo,
    # # entonces le ponemos un IF porque me cuelga la interface en windows mientras se ejecuta:
    # #thread.join() #


if __name__ == "__main__":
    main()
