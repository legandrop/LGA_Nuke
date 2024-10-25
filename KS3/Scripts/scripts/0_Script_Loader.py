import sys
import os
import hiero.core
import importlib

# Variable global para activar o desactivar los prints de depuración
DEBUG = False

def debug_print(*message):
    if DEBUG:
        print(*message)

# Definir la ruta del script que quieres ejecutar
ScriptPath = "Python/Startup/LGA_NKS/LGA_NKS_InOut_Editref.py"

def ejecutar_script(script_path):
    # Obtener la ruta del directorio de plugins de Hiero
    hiero_plugin_paths = hiero.core.pluginPath()

    # Asumimos que el primer path en la tupla es el que necesitamos
    if isinstance(hiero_plugin_paths, tuple) and len(hiero_plugin_paths) > 0:
        hiero_plugin_path = hiero_plugin_paths[0]
    else:
        hiero_plugin_path = hiero_plugin_paths  # En caso de que sea una cadena

    # Construir la ruta al directorio que contiene nuestro script
    script_parts = script_path.split('/')
    script_dir = os.path.join(os.path.dirname(hiero_plugin_path), *script_parts[:-1])
    
    # Añadir el directorio al path de Python si no está ya
    if script_dir not in sys.path:
        sys.path.insert(0, script_dir)

    debug_print("Python path:", sys.path)
    debug_print("Script directory:", script_dir)
    debug_print("")

    # Obtener el nombre del módulo del script
    module_name = os.path.splitext(script_parts[-1])[0]
    package_name = script_parts[-2]

    try:
        # Importar el módulo
        debug_print(f"Intentando importar el módulo: {package_name}.{module_name}")
        module = importlib.import_module(f"{package_name}.{module_name}")
        
        # Recargar el módulo
        debug_print(f"Recargando el módulo: {package_name}.{module_name}")
        module = importlib.reload(module)
        
        debug_print(f"Módulo importado y recargado: {module}")
        
        # Si el módulo tiene una función main(), ejecutarla
        if hasattr(module, 'main') and callable(module.main):
            debug_print("Función main() encontrada. Ejecutando...")
            module.main()
        else:
            debug_print(f"El módulo {module_name} no tiene una función main() ejecutable.")
            debug_print("Contenido del módulo:")
            for attr in dir(module):
                debug_print(f"  {attr}")
    except Exception as e:
        debug_print(f"Error al importar o ejecutar el módulo: {e}")
        import traceback
        traceback.print_exc()
        
        debug_print(f"Asegúrate de que el archivo {script_parts[-1]} está en {script_dir}")
        
        # Listar los contenidos del directorio para depuración
        debug_print("Contenidos del directorio:")
        for root, dirs, files in os.walk(script_dir):
            for file in files:
                debug_print(os.path.join(root, file))

# Ejecutar el script
ejecutar_script(ScriptPath)