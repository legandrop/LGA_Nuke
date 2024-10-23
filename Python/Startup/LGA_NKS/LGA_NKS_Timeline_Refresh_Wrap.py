"""
__________________________________________________________

  LGA_NKS_Timeline_Refresh_Wrap v1.0 - 2024 - Lega
  
  Wrapper que ejecuta una secuencia de scripts para refrescar
  el timeline manteniendo el nivel de zoom original:
  
  1. Captura el estado actual del timeline (zoom y scroll)
  2. Refresca el timeline
  3. Ajusta el tamaño de la ventana
  4. Scrollea al track superior
  5. Restaura el estado original usando los valores exactos
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
DEBUG = True

def debug_print(*message):
    if DEBUG:
        print(*message)

def get_timeline_state():
    """
    Obtiene el estado actual del timeline.
    """
    try:
        t = hiero.ui.getTimelineEditor(hiero.ui.activeSequence())
        if not t:
            return None
            
        # Obtener los widgets necesarios
        timeline_view = t.window().children()[3].children()[0].children()[0]
        viewport = timeline_view.children()[0]  # qt_scrollarea_viewport
        h_container = timeline_view.children()[6]  # qt_scrollarea_hcontainer
        h_scrollbar = h_container.children()[0]  # QScrollBar
        h_slider = h_container.children()[2]     # QSlider
        
        viewport_width = viewport.width()
        scrollbar_range = h_scrollbar.maximum() - h_scrollbar.minimum() + h_scrollbar.pageStep()
        zoom_factor = viewport_width / scrollbar_range
        
        state = {
            'scroll_value': h_scrollbar.value(),
            'scroll_min': h_scrollbar.minimum(),
            'scroll_max': h_scrollbar.maximum(),
            'page_step': h_scrollbar.pageStep(),
            'viewport_width': viewport_width,
            'zoom_factor': zoom_factor,
            'slider_value': h_slider.value() if hasattr(h_slider, 'value') else None
        }
        
        return state
            
    except Exception as e:
        debug_print(f"Error al obtener el estado del timeline: {e}")
        return None

def restore_timeline_state(state):
    """
    Restaura el estado del timeline usando acceso directo al scrollbar y slider.
    """
    try:
        t = hiero.ui.getTimelineEditor(hiero.ui.activeSequence())
        if not t:
            return False
        
        # Acceder directamente a los widgets
        h_container = t.window().children()[3].children()[0].children()[0].children()[6]
        h_scrollbar = h_container.children()[0]  # QScrollBar
        h_slider = h_container.children()[2]     # QSlider
        
        debug_print("\nRestaurando estado del timeline...")
        debug_print(f"Usando scrollbar y slider para restaurar zoom_factor: {state['zoom_factor']}")
        
        # 1. Primero restaurar el valor del slider
        if state['slider_value'] is not None:
            debug_print(f"Restaurando valor del slider: {state['slider_value']}")
            h_slider.setValue(state['slider_value'])
            QtCore.QCoreApplication.processEvents()
            
            # Verificar estado intermedio
            intermediate_state = get_timeline_state()
            debug_print("\nEstado después de restaurar slider:")
            debug_print(intermediate_state)
        
        # 2. Luego restaurar valores del scrollbar
        debug_print("\nRestaurando valores del scrollbar...")
        h_scrollbar.setPageStep(state['page_step'])
        h_scrollbar.setMaximum(state['scroll_max'])
        h_scrollbar.setMinimum(state['scroll_min'])
        h_scrollbar.setValue(state['scroll_value'])
        
        QtCore.QCoreApplication.processEvents()
        
        # Verificar el estado final
        final_state = get_timeline_state()
        debug_print("\nEstado FINAL después de restaurar:")
        debug_print(final_state)
        
        return True
            
    except Exception as e:
        debug_print(f"Error al restaurar el estado: {e}")
        return False

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
        
        # 1. Capturar estado inicial
        start_time = time.time()
        original_state = get_timeline_state()
        if original_state is None:
            debug_print("No se pudo capturar el estado inicial del timeline.")
            return
        debug_print("\nEstado INICIAL:")
        debug_print(original_state)
        debug_print(f"Tiempo capturando estado inicial: {time.time() - start_time:.3f} segundos")

        # 2. Ejecutar Clear Cache Playback
        start_time = time.time()
        cache_module = import_script('LGA_NKS_ClearCachePlayback')
        if cache_module:
            cache_module.main()
            QtCore.QThread.msleep(10)
            QtCore.QCoreApplication.processEvents()
        debug_print(f"Tiempo ejecutando clear cache: {time.time() - start_time:.3f} segundos")

        # 3. Ejecutar los scripts
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

        # 4. Primer intento de restauración
        start_time = time.time()
        debug_print("\nPrimer intento de restauración...")
        success = restore_timeline_state(original_state)
        debug_print(f"Tiempo primera restauración: {time.time() - start_time:.3f} segundos")
        
        # 5. Segundo intento de restauración
        start_time = time.time()
        debug_print("\nSegundo intento de restauración...")
        success = restore_timeline_state(original_state)
        debug_print(f"Tiempo segunda restauración: {time.time() - start_time:.3f} segundos")

        # 6. Procesar eventos finales
        QtCore.QCoreApplication.processEvents()
        time.sleep(0.2)

        debug_print(f"\nTiempo total de operación: {time.time() - start_total:.3f} segundos")

    except Exception as e:
        debug_print(f"Error en Timeline Refresh Wrap: {e}")
        import traceback
        debug_print(traceback.format_exc())

if __name__ == "__main__":
    main()
