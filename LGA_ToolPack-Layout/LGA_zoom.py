"""
_____________________________________________________________________________

  LGA_zoom v1.0 | 2024 | Lega  
  
  Alterna entre el zoom actual y un zoom que muestra todo el DAG.
  Permite volver al nivel de zoom anterior usando la posición del cursor
  como centro. Si pasan más de 5 segundos entre pulsaciones de la tecla H,
  se reinicia el ciclo.
_____________________________________________________________________________

"""

import nuke
import time
from PySide2.QtGui import QCursor, QMouseEvent
from PySide2.QtWidgets import QApplication
from PySide2.QtCore import Qt, QEvent, QPoint

# Estado del zoom
_zoom_state = {
    'zoom_level': None,
    'is_zoomed_out': False,
    'timestamp': None
}

# Tiempo máximo entre H's (en segundos)
MAX_TIME_BETWEEN_H = 5

def main():
    """
    Alterna entre el zoom guardado y zoom total del DAG
    """
    global _zoom_state
    
    current_time = time.time()
    
    # Si pasaron más de MAX_TIME_BETWEEN_H segundos, resetear el estado
    if _zoom_state['is_zoomed_out'] and _zoom_state['timestamp']:
        if current_time - _zoom_state['timestamp'] > MAX_TIME_BETWEEN_H:
            _zoom_state['is_zoomed_out'] = False
            _zoom_state['zoom_level'] = None
            _zoom_state['timestamp'] = None
    
    if not _zoom_state['is_zoomed_out']:
        # Guardar zoom actual y timestamp
        _zoom_state['zoom_level'] = nuke.zoom()
        _zoom_state['timestamp'] = current_time
        
        # Hacer zoom out a todo el DAG (deseleccionar todo primero)
        nuke.selectAll()
        nuke.invertSelection()
        nuke.zoomToFitSelected()
        _zoom_state['is_zoomed_out'] = True
        
    else:
        # Obtener el widget bajo el cursor
        widget = QApplication.widgetAt(QCursor.pos())
        cursor_before = QCursor.pos()
        
        if widget:
            # Simular un click completo (press y release) en el widget
            local_pos = widget.mapFromGlobal(cursor_before)
            
            # Mouse press
            press_event = QMouseEvent(QEvent.MouseButtonPress, 
                                    local_pos,  # Usar coordenadas locales del widget
                                    Qt.LeftButton, 
                                    Qt.LeftButton, 
                                    Qt.NoModifier)
            QApplication.sendEvent(widget, press_event)
            
            # Mouse release
            release_event = QMouseEvent(QEvent.MouseButtonRelease, 
                                      local_pos,  # Usar coordenadas locales del widget
                                      Qt.LeftButton, 
                                      Qt.LeftButton, 
                                      Qt.NoModifier)
            QApplication.sendEvent(widget, release_event)
            
            # Crear un NoOp temporal
            temp_node = nuke.createNode("NoOp", inpanel=False)
            
            # Obtener el centro del nodo temporal
            xC = temp_node.xpos() + temp_node.screenWidth()/2
            yC = temp_node.ypos() + temp_node.screenHeight()/2
            
            # Hacer zoom al nivel guardado usando el centro del nodo temporal
            nuke.zoom(_zoom_state['zoom_level'], [xC, yC])
            
            # Eliminar el nodo temporal
            nuke.delete(temp_node)
            
            # Resetear el estado
            _zoom_state['is_zoomed_out'] = False
            _zoom_state['timestamp'] = None