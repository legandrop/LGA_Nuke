"""
__________________________________________________________

  LGA_NKS_Explore_Zoom_Scroll v1.1 - 2024 - Lega

  Explora y registra los valores actuales de zoom y posición
  del scrollbar horizontal en el timeline activo de Hiero.
  1. Obtiene el estado actual del zoom y scrollbar.
  2. Imprime los valores para análisis.
__________________________________________________________
"""

import hiero.core
import hiero.ui
from PySide2 import QtWidgets, QtCore

DEBUG = False

def debug_print(*message):
    if DEBUG:
        print(*message)

def get_timeline_widgets():
    """
    Obtiene los widgets necesarios del timeline.
    """
    try:
        t = hiero.ui.getTimelineEditor(hiero.ui.activeSequence())
        if not t:
            return None, None, None

        splitter = None
        for child in t.window().children():
            if isinstance(child, QtWidgets.QSplitter):
                splitter = child
                break

        if not splitter:
            debug_print("No se pudo encontrar el QSplitter")
            return None, None, None

        timeline_view = None
        for child in splitter.children():
            if isinstance(child, QtWidgets.QWidget):
                for subchild in child.children():
                    if isinstance(subchild, QtWidgets.QAbstractScrollArea):
                        timeline_view = subchild
                        break
                if timeline_view:
                    break

        if not timeline_view:
            debug_print("No se pudo encontrar el TimelineView")
            return None, None, None

        viewport = None
        h_container = None
        for child in timeline_view.children():
            if hasattr(child, 'objectName'):
                if child.objectName() == "qt_scrollarea_viewport":
                    viewport = child
                elif child.objectName() == "qt_scrollarea_hcontainer":
                    h_container = child

        if not all([viewport, h_container]):
            debug_print("No se pudieron encontrar todos los widgets necesarios")
            return None, None, None

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
        h_container = timeline_view.children()[6]  # qt_scrollarea_hcontainer
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

        debug_print(f"Estado del timeline: {state}")
        return state

    except Exception as e:
        debug_print(f"Error al obtener el estado del timeline: {e}")
        return None

def main():
    """
    Función principal que explora los valores de zoom y scrollbar.
    """
    get_timeline_state()

if __name__ == "__main__":
    main()
