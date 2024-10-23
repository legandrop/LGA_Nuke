"""
__________________________________________________________

  LGA_NKS_Timeline_Refresh_Wrap v1.0 - 2024 - Lega
  
  Wrapper que ejecuta una secuencia de scripts para refrescar
  el timeline manteniendo el nivel de zoom original:
  
  1. Captura el estado actual del timeline
  2. Refresca el timeline
  3. Ajusta el tamaño de la ventana
  4. Scrollea al track superior
  5. Restaura el estado original
__________________________________________________________

"""

import hiero.core
import hiero.ui
import os
import importlib.util
from PySide2 import QtWidgets, QtCore

# Variable global para activar o desactivar los prints
DEBUG = True  # Cambiado a True para ver los estados

def debug_print(*message):
    if DEBUG:
        print(*message)

def import_script(script_name):
    """
    Importa un script desde la carpeta LGA_NKS
    """
    script_path = os.path.join(os.path.dirname(__file__), script_name + '.py')
    if os.path.exists(script_path):
        spec = importlib.util.spec_from_file_location(script_name, script_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module
    else:
        debug_print(f"Script no encontrado: {script_path}")
        return None

def main():
    """
    Función principal que coordina la ejecución de todos los scripts
    """
    try:
        # 1. Importar módulo de zoom y capturar estado actual
        zoom_module = import_script('LGA_NKS_Timeline_Zoom')
        if zoom_module:
            # Capturar el estado inicial
            original_state = zoom_module.get_timeline_state()
            print("\nEstado INICIAL del timeline:")
            print(original_state)

        # 2. Ejecutar Refresh Timeline
        refresh_module = import_script('LGA_NKS_Refresh_Timeline')
        if refresh_module:
            refresh_module.main()
            QtCore.QThread.msleep(100)
            QtCore.QCoreApplication.processEvents()

        # 3. Ejecutar Reduce SeqWin
        reduce_module = import_script('LGA_NKS_Reduce_SeqWin')
        if reduce_module:
            reduce_module.main()
            QtCore.QThread.msleep(100)
            QtCore.QCoreApplication.processEvents()

        # 4. Ejecutar ScrollTo TopTrack
        scroll_module = import_script('LGA_NKS_ScrollTo_TopTrack')
        if scroll_module:
            scroll_module.main()
            QtCore.QThread.msleep(100)
            QtCore.QCoreApplication.processEvents()

        # 5. Restaurar el estado original
        if original_state is not None:
            # Obtener estado actual antes de restaurar
            current_state = zoom_module.get_timeline_state()
            print("\nEstado ACTUAL antes de restaurar:")
            print(current_state)
            
            # Restaurar estado original
            if zoom_module.restore_timeline_state(original_state):
                # Obtener estado después de restaurar
                final_state = zoom_module.get_timeline_state()
                print("\nEstado FINAL después de restaurar:")
                print(final_state)
                
                # Comparar estados
                print("\nComparación de estados:")
                print(f"Original vs Final:")
                for key in original_state:
                    if original_state[key] != final_state[key]:
                        print(f"{key}: {original_state[key]} -> {final_state[key]}")
                    else:
                        print(f"{key}: {original_state[key]} (sin cambios)")

    except Exception as e:
        debug_print(f"Error en Timeline Refresh Wrap: {e}")
        import traceback
        debug_print(traceback.format_exc())

if __name__ == "__main__":
    main()
