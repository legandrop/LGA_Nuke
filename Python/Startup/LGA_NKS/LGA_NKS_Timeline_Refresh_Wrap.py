"""
__________________________________________________________

  LGA_NKS_Timeline_Refresh_Wrap v1.0 - 2024 - Lega
  
  Wrapper que ejecuta una secuencia de scripts para refrescar
  el timeline manteniendo el nivel de zoom original:
  
  1. Captura el estado actual del timeline (zoom y scroll)
  2. Refresca el timeline
  3. Ajusta el tamaño de la ventana
  4. Scrollea al track superior
  5. Re-Fetchea los widgets del timeline
  6. Restaura el estado original usando los valores exactos
     del slider y scrollbar
__________________________________________________________
"""

import hiero.core
import hiero.ui
import os
import importlib.util
from PySide2 import QtWidgets, QtCore
import time

# Variable global para activar o desactivar los prints
DEBUG = False

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
        start_total = time.time()
        
        # 1. Importar y utilizar el módulo de Zoom para capturar el estado inicial
        start_time = time.time()
        zoom_module = import_script('LGA_NKS_Timeline_Zoom')
        if not zoom_module:
            return
        debug_print(f"Tiempo importando módulo zoom: {time.time() - start_time:.3f} segundos")
            
        start_time = time.time()
        timeline_view, viewport, h_scrollbar = zoom_module.get_timeline_widgets()
        if not all([timeline_view, viewport, h_scrollbar]):
            debug_print("No se pudieron obtener los widgets del timeline.")
            return
        debug_print(f"Tiempo obteniendo widgets: {time.time() - start_time:.3f} segundos")
            
        # 2. Obtener estado inicial
        start_time = time.time()
        original_state = zoom_module.get_timeline_state()
        if original_state is None:
            debug_print("No se pudo capturar el estado inicial del timeline.")
            return
        debug_print("\nEstado INICIAL:")
        debug_print(original_state)
        debug_print(f"Tiempo capturando estado inicial: {time.time() - start_time:.3f} segundos")

        # 3. Ejecutar los scripts que pueden alterar el estado del timeline
        start_time = time.time()
        refresh_module = import_script('LGA_NKS_Refresh_Timeline')
        if refresh_module:
            refresh_module.main()
            QtCore.QThread.msleep(10)
            QtCore.QCoreApplication.processEvents()
        debug_print(f"Tiempo ejecutando refresh timeline: {time.time() - start_time:.3f} segundos")

        start_time = time.time()
        reduce_module = import_script('LGA_NKS_Reduce_SeqWin')
        if reduce_module:
            reduce_module.main()
            QtCore.QThread.msleep(10)
            QtCore.QCoreApplication.processEvents()
        debug_print(f"Tiempo ejecutando reduce window: {time.time() - start_time:.3f} segundos")

        start_time = time.time()
        scroll_module = import_script('LGA_NKS_ScrollTo_TopTrack')
        if scroll_module:
            scroll_module.main()
            QtCore.QThread.msleep(10)
            QtCore.QCoreApplication.processEvents()
        debug_print(f"Tiempo ejecutando scroll to top: {time.time() - start_time:.3f} segundos")
        
        # 4. Re-Fetcheo de los widgets después de ejecutar los scripts
        start_time = time.time()
        timeline_view, viewport, h_scrollbar = zoom_module.get_timeline_widgets()
        if not all([timeline_view, viewport, h_scrollbar]):
            debug_print("No se pudieron re-obtener los widgets del timeline después de ejecutar los scripts.")
            return
        debug_print(f"Tiempo re-obteniendo widgets: {time.time() - start_time:.3f} segundos")

        # 5. Primer intento de restauración
        start_time = time.time()
        debug_print("\nPrimer intento de restauración...")
        success = zoom_module.restore_timeline_state(original_state)
        debug_print(f"Tiempo primera restauración: {time.time() - start_time:.3f} segundos")
        
        # 6. Segundo intento de restauración
        start_time = time.time()
        debug_print("\nSegundo intento de restauración...")
        success = zoom_module.restore_timeline_state(original_state)
        debug_print(f"Tiempo segunda restauración: {time.time() - start_time:.3f} segundos")

        # 7. Procesar eventos y permitir que el GUI se actualice
        QtCore.QCoreApplication.processEvents()
        time.sleep(0.2)

        debug_print(f"\nTiempo total de operación: {time.time() - start_total:.3f} segundos")

    except Exception as e:
        debug_print(f"Error en Timeline Refresh Wrap: {e}")
        import traceback
        debug_print(traceback.format_exc())

if __name__ == "__main__":
    main()
