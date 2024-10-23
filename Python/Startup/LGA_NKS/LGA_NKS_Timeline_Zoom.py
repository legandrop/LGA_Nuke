"""
__________________________________________________________

  LGA_NKS_Timeline_Zoom v1.0 - 2024 - Lega
  
  Hace un zoom temporal en el timeline activo de Hiero:
  1. Captura el estado actual del timeline
  2. Incrementa el zoom usando la rueda del mouse
  3. Espera 1 segundo
  4. Restaura el estado original
__________________________________________________________

"""

import hiero.core
import hiero.ui
from PySide2 import QtWidgets, QtCore, QtGui
import time

# Variable global para activar o desactivar los prints
DEBUG = True

def debug_print(*message):
    if DEBUG:
        print(*message)

def get_timeline_widgets():
    """
    Obtiene los widgets necesarios del timeline.
    """
    timeline_editor = hiero.ui.getTimelineEditor(hiero.ui.activeSequence())
    if not timeline_editor:
        return None, None, None
        
    try:
        window = timeline_editor.window()
        timeline_view = window.children()[3].children()[0].children()[0]
        viewport = timeline_view.viewport()
        h_scrollbar = timeline_view.horizontalScrollBar()
        
        return timeline_view, viewport, h_scrollbar
    except:
        return None, None, None

def get_timeline_state():
    """
    Obtiene el estado actual del timeline.
    """
    timeline_view, viewport, h_scrollbar = get_timeline_widgets()
    if not all([timeline_view, viewport, h_scrollbar]):
        debug_print("No se pudieron obtener los widgets del timeline.")
        return None
        
    try:
        viewport_width = viewport.width()
        scrollbar_range = h_scrollbar.maximum() - h_scrollbar.minimum() + h_scrollbar.pageStep()
        zoom_factor = viewport_width / scrollbar_range
        
        return {
            'scroll_value': h_scrollbar.value(),
            'scroll_min': h_scrollbar.minimum(),
            'scroll_max': h_scrollbar.maximum(),
            'page_step': h_scrollbar.pageStep(),
            'viewport_width': viewport_width,
            'zoom_factor': zoom_factor
        }
            
    except Exception as e:
        debug_print(f"Error al obtener el estado del timeline: {e}")
        if DEBUG:
            import traceback
            debug_print(traceback.format_exc())
        
    return None

def apply_wheel_zoom(viewport, zoom_in=True):
    """
    Aplica zoom usando un evento de rueda del mouse.
    """
    try:
        delta = 120 if zoom_in else -120
        wheel_event = QtGui.QWheelEvent(
            QtCore.QPointF(viewport.rect().center()),
            QtCore.QPointF(viewport.rect().center()),
            QtCore.QPoint(0, delta),
            QtCore.QPoint(0, delta),
            QtCore.Qt.MouseButton.NoButton,
            QtCore.Qt.KeyboardModifier.ControlModifier,
            QtCore.Qt.ScrollPhase.NoScrollPhase,
            False,
            QtCore.Qt.MouseEventSource.MouseEventSynthesizedByApplication
        )
        
        QtCore.QCoreApplication.sendEvent(viewport, wheel_event)
        QtCore.QCoreApplication.processEvents()
        return True
        
    except Exception as e:
        debug_print(f"Error al aplicar zoom: {e}")
        return False

def restore_timeline_state(state):
    """
    Restaura el estado del timeline usando los métodos documentados del scrollbar.
    """
    timeline_view, viewport, h_scrollbar = get_timeline_widgets()
    if not all([timeline_view, viewport, h_scrollbar]):
        return False
            
    try:
        # Obtener valores actuales antes de cambiarlos
        current_page_step = h_scrollbar.pageStep()
        current_min = h_scrollbar.minimum()
        current_max = h_scrollbar.maximum()
        current_value = h_scrollbar.value()
        
        # 1. Primero establecer el page_step
        print(f"\nCambiando page_step de {current_page_step} a {state['page_step']}")
        h_scrollbar.setPageStep(state['page_step'])
        
        # 2. Establecer el rango completo de una vez
        print(f"Cambiando scroll_min de {current_min} a {state['scroll_min']}")
        print(f"Cambiando scroll_max de {current_max} a {state['scroll_max']}")
        h_scrollbar.setRange(state['scroll_min'], state['scroll_max'])
        
        # 3. Finalmente establecer el valor
        print(f"Cambiando scroll_value de {current_value} a {state['scroll_value']}")
        h_scrollbar.setValue(state['scroll_value'])
        
        # Verificar los cambios
        print("\nValores después de los cambios:")
        print(f"page_step: {h_scrollbar.pageStep()} (esperado: {state['page_step']})")
        print(f"scroll_min: {h_scrollbar.minimum()} (esperado: {state['scroll_min']})")
        print(f"scroll_max: {h_scrollbar.maximum()} (esperado: {state['scroll_max']})")
        print(f"scroll_value: {h_scrollbar.value()} (esperado: {state['scroll_value']})")
        
        QtCore.QCoreApplication.processEvents()
        return True
            
    except Exception as e:
        debug_print(f"Error al restaurar el estado: {e}")
        return False

def main():
    """
    Función principal que hace un zoom temporal en el timeline.
    """
    try:
        timeline_view, viewport, h_scrollbar = get_timeline_widgets()
        if not all([timeline_view, viewport, h_scrollbar]):
            return
            
        # 1. Estado inicial
        original_state = get_timeline_state()
        if original_state is None:
            return
        print("\nEstado INICIAL:")
        print(original_state)
            
        # 2. Hacer zoom in y capturar estado
        if apply_wheel_zoom(viewport, zoom_in=True):
            apply_wheel_zoom(viewport, zoom_in=True)
            apply_wheel_zoom(viewport, zoom_in=True)
            zoom_state = get_timeline_state()
            print("\nEstado después de ZOOM IN:")
            print(zoom_state)
            
            time.sleep(1.0)
            
            # 3. Restaurar y mostrar estado final
            if restore_timeline_state(original_state):
                final_state = get_timeline_state()
                print("\nEstado FINAL después de restaurar:")
                print(final_state)
        
    except Exception as e:
        debug_print(f"Error en la operación de zoom: {e}")

if __name__ == "__main__":
    main()
