"""
__________________________________________________________

  LGA_NKS_Timeline_Zoom v1.0 - 2024 - Lega

  Hace un zoom temporal en el timeline activo de Hiero:
  1. Captura el estado actual del timeline
  2. Incrementa el zoom usando la rueda del mouse
  3. Espera 1 segundo
  4. Restaura el estado original usando el valor exacto
     del slider y scrollbar
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
    Obtiene los widgets necesarios del timeline usando la ruta directa.
    """
    try:
        # Obtener el editor de la secuencia activa
        t = hiero.ui.getTimelineEditor(hiero.ui.activeSequence())
        if not t:
            return None, None, None
        
        # Obtener los widgets necesarios
        timeline_view = t.window().children()[3].children()[0].children()[0]
        viewport = timeline_view.children()[0]  # qt_scrollarea_viewport
        h_container = timeline_view.children()[6]  # qt_scrollarea_hcontainer
        h_scrollbar = h_container.children()[0]  # QScrollBar
        
        return timeline_view, viewport, h_scrollbar
            
    except Exception as e:
        debug_print(f"Error al obtener los widgets: {e}")
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
        # Obtener el slider
        h_container = timeline_view.children()[6]  # qt_scrollarea_hcontainer
        h_slider = h_container.children()[2]     # QSlider
        
        viewport_width = viewport.width()
        scrollbar_range = h_scrollbar.maximum() - h_scrollbar.minimum() + h_scrollbar.pageStep()
        zoom_factor = viewport_width / scrollbar_range
        
        # Agregar el valor del slider al estado
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

def apply_zoom_steps(viewport, steps=1, zoom_in=True):
    """
    Aplica múltiples pasos de zoom.
    """
    for _ in range(steps):
        success = apply_wheel_zoom(viewport, zoom_in)
        if not success:
            debug_print("Fallo al aplicar un paso de zoom.")
        time.sleep(0.05)  # Pequeña pausa para permitir que el zoom se aplique

def restore_timeline_state(state):
    """
    Restaura el estado del timeline usando acceso directo al scrollbar y slider.
    """
    try:
        # Obtener el editor de la secuencia activa
        t = hiero.ui.getTimelineEditor(hiero.ui.activeSequence())
        if not t:
            return False
        
        # Acceder directamente a los widgets usando la ruta específica
        h_container = t.window().children()[3].children()[0].children()[0].children()[6]
        h_scrollbar = h_container.children()[0]  # QScrollBar
        h_slider = h_container.children()[2]     # QSlider
        
        print("\nRestaurando estado del timeline...")
        print(f"Usando scrollbar y slider para restaurar zoom_factor: {state['zoom_factor']}")
        
        # 1. Primero restaurar el valor del slider y esperar
        if state['slider_value'] is not None:
            print(f"Restaurando valor del slider: {state['slider_value']}")
            h_slider.setValue(state['slider_value'])
            QtCore.QCoreApplication.processEvents()
            time.sleep(0.1)  # Dar tiempo a que el slider afecte el zoom
            
            # Verificar estado intermedio después del slider
            intermediate_state = get_timeline_state()
            print("\nEstado después de restaurar slider:")
            print(intermediate_state)
        
        # 2. Luego restaurar valores del scrollbar
        print("\nRestaurando valores del scrollbar...")
        h_scrollbar.setPageStep(state['page_step'])
        QtCore.QCoreApplication.processEvents()
        time.sleep(0.1)
        
        h_scrollbar.setMaximum(state['scroll_max'])
        QtCore.QCoreApplication.processEvents()
        time.sleep(0.1)
        
        h_scrollbar.setMinimum(state['scroll_min'])
        QtCore.QCoreApplication.processEvents()
        time.sleep(0.1)
        
        h_scrollbar.setValue(state['scroll_value'])
        QtCore.QCoreApplication.processEvents()
        
        # Verificar el estado final
        final_state = get_timeline_state()
        print("\nEstado FINAL después de restaurar:")
        print(final_state)
        
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
            
        # 2. Hacer zoom in usando la rueda del mouse
        zoom_steps = 8  # Número fijo de pasos para un zoom in más notorio
        print(f"\nAplicando {zoom_steps} pasos de zoom in...")
        apply_zoom_steps(viewport, steps=zoom_steps, zoom_in=True)
        zoom_state = get_timeline_state()
        print("\nEstado después de ZOOM IN:")
        print(zoom_state)
        
        # 3. Esperar 1 segundo
        time.sleep(1.0)
        
        # 4. Restaurar el estado original directamente
        restore_timeline_state(original_state)
        
    except Exception as e:
        debug_print(f"Error en la operación de zoom: {e}")

if __name__ == "__main__":
    main()
