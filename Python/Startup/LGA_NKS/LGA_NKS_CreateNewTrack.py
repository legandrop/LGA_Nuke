"""
______________________________________________________

  LGA_NKS_CreateNewTrack v1.2 - 2025 - Lega
  Crea un nuevo track de video encima del track actualmente seleccionado
  y mantiene la posicion del scroll vertical
______________________________________________________

"""

import hiero.core
import hiero.ui
from PySide2 import QtWidgets, QtCore

DEBUG = False

def debug_print(*message):
    if DEBUG:
        print(*message)

def print_tracks(seq, message):
    """Imprime los tracks en orden"""
    debug_print(f"\n{message}")
    debug_print("Tracks (de abajo hacia arriba):")
    for i, track in enumerate(seq.videoTracks()):
        debug_print(f"{i}: {track.name()}")

def get_selected_track_index(seq):
    """Obtiene el indice del track actualmente seleccionado"""
    te = hiero.ui.getTimelineEditor(seq)
    selected_items = te.selection()
    
    # Caso 1: Hay elementos seleccionados en la línea de tiempo
    if selected_items:
        for item in selected_items:
            # Verificar primero si el item seleccionado es un track
            if isinstance(item, hiero.core.TrackBase):
                selected_track = item
                debug_print("Track seleccionado directamente.")
                # Encontrar el índice del track en la secuencia
                for index, track in enumerate(seq.videoTracks()):
                    if track == selected_track:
                        return index
            # Si no es un track, verificar si es un clip (comportamiento original)
            elif hasattr(item, 'parentTrack'):
                selected_track = item.parentTrack()
                if selected_track:
                    debug_print("Track obtenido a partir de un clip seleccionado.")
                    # Encontrar el índice del track en la secuencia
                    for index, track in enumerate(seq.videoTracks()):
                        if track == selected_track:
                            return index
    
    # Caso 2: Verificar si hay un track seleccionado directamente
    # Esta es una ruta alternativa para detectar tracks seleccionados
    try:
        view = te.view()
        if view:
            selected_row = view.selectedRow()
            if selected_row >= 0:
                # Obtener el track correspondiente a la fila seleccionada
                # En Hiero, las filas del timeline view corresponden a tracks
                track_count = len(seq.videoTracks())
                if selected_row < track_count:
                    debug_print(f"Track seleccionado por fila: {selected_row}")
                    # La fila seleccionada corresponde a un índice de track
                    # (ajustar según sea necesario si el mapeo de filas a tracks es diferente)
                    return selected_row
    except Exception as e:
        debug_print(f"Error al intentar obtener el track por fila: {e}")
    
    debug_print("No hay tracks seleccionados en la línea de tiempo.")
    return None

def get_vertical_scroll_state():
    """
    Obtiene el estado actual del scroll vertical del timeline.
    """
    try:
        t = hiero.ui.getTimelineEditor(hiero.ui.activeSequence())
        if not t:
            return None
            
        # Buscar el QSplitter primero
        splitter = None
        for child in t.window().children():
            if isinstance(child, QtWidgets.QSplitter):
                splitter = child
                break
                
        if not splitter:
            debug_print("No se pudo encontrar el QSplitter")
            return None
            
        # Buscar el TimelineView dentro del primer widget del QSplitter
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
            return None
            
        # Buscar v_container por nombre
        v_container = None
        for child in timeline_view.children():
            if hasattr(child, 'objectName'):
                if child.objectName() == "qt_scrollarea_vcontainer":
                    v_container = child
                    break
        
        if not v_container:
            debug_print("No se pudo encontrar el contenedor vertical")
            return None
            
        # Obtener scrollbar vertical
        v_scrollbar = v_container.children()[0]  # QScrollBar vertical
        
        state = {
            'v_scroll_value': v_scrollbar.value(),
            'v_scroll_min': v_scrollbar.minimum(),
            'v_scroll_max': v_scrollbar.maximum(),
            'v_page_step': v_scrollbar.pageStep()
        }
        
        debug_print(f"Estado del scroll vertical capturado: {state['v_scroll_value']}")
        return state
            
    except Exception as e:
        debug_print(f"Error al obtener el estado del scroll vertical: {e}")
        import traceback
        debug_print(traceback.format_exc())
        
    return None

def restore_vertical_scroll_state(state):
    """
    Restaura el estado del scroll vertical del timeline.
    """
    if not state:
        debug_print("No hay estado de scroll vertical para restaurar")
        return False
        
    try:
        t = hiero.ui.getTimelineEditor(hiero.ui.activeSequence())
        if not t:
            return False
            
        # Buscar el QSplitter primero
        splitter = None
        for child in t.window().children():
            if isinstance(child, QtWidgets.QSplitter):
                splitter = child
                break
                
        if not splitter:
            debug_print("No se pudo encontrar el QSplitter")
            return False
            
        # Buscar el TimelineView dentro del primer widget del QSplitter
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
            return False
            
        # Buscar v_container por nombre
        v_container = None
        for child in timeline_view.children():
            if hasattr(child, 'objectName'):
                if child.objectName() == "qt_scrollarea_vcontainer":
                    v_container = child
                    break
        
        if not v_container:
            debug_print("No se pudo encontrar el contenedor vertical")
            return False
            
        # Obtener scrollbar vertical
        v_scrollbar = v_container.children()[0]  # QScrollBar vertical
        
        debug_print(f"Restaurando valor del scroll vertical a: {state['v_scroll_value']}")
        v_scrollbar.setPageStep(state['v_page_step'])
        v_scrollbar.setMaximum(state['v_scroll_max'])
        v_scrollbar.setMinimum(state['v_scroll_min'])
        v_scrollbar.setValue(state['v_scroll_value'])
        
        # Procesar eventos
        QtCore.QCoreApplication.processEvents()
        
        return True
            
    except Exception as e:
        debug_print(f"Error al restaurar el scroll vertical: {e}")
        import traceback
        debug_print(traceback.format_exc())
        
    return False

def create_new_track(seq, track_index):
    """Crea un nuevo track y lo inserta en la posicion especificada"""
    if track_index is None:
        debug_print("No se pudo determinar la posicion del nuevo track.")
        return None
        
    # Crear el nuevo track
    new_track = hiero.core.VideoTrack("New")
    
    # Obtener todos los tracks de video
    video_tracks = list(seq.videoTracks())
    
    # Imprimir tracks antes de la operación
    print_tracks(seq, "ANTES DE LA OPERACIÓN")
    
    # Remover todos los tracks existentes
    for track in video_tracks:
        seq.removeTrack(track)
    
    # Insertar el nuevo track en la posicion deseada (encima del track seleccionado)
    # Insertamos en track_index + 1 para que aparezca encima del track seleccionado
    new_tracks = video_tracks[:track_index+1] + [new_track] + video_tracks[track_index+1:]
    
    # Imprimir el orden que vamos a insertar
    debug_print("\nORDEN DE INSERCIÓN:")
    for i, track in enumerate(new_tracks):
        debug_print(f"{i}: {track.name()}")
    
    # Reinsertar todos los tracks en el orden correcto
    for track in new_tracks:
        seq.addTrack(track)
    
    # Imprimir tracks después de la operación
    print_tracks(seq, "DESPUÉS DE LA OPERACIÓN")
        
    debug_print(f"Nuevo track creado encima del track en la posicion {track_index}")
    return new_track

def main():
    try:
        # Obtener la secuencia activa
        seq = hiero.ui.activeSequence()
        if not seq:
            debug_print("No se encontro una secuencia activa en Hiero.")
            return
            
        # Iniciar una accion de undo
        project = seq.project()
        project.beginUndo("Crear Nuevo Track")


        # Capturar el estado del scroll vertical
        vertical_scroll_state = get_vertical_scroll_state()
        if vertical_scroll_state:
            debug_print("Estado del scroll vertical capturado correctamente")
        else:
            debug_print("No se pudo capturar el estado del scroll vertical")

        
        try:
            # Obtener el indice del track seleccionado
            track_index = get_selected_track_index(seq)
            
            # Crear el nuevo track
            new_track = create_new_track(seq, track_index)
            
            if new_track:
                debug_print("Operacion completada exitosamente.")
            else:
                debug_print("No se pudo crear el nuevo track.")
                
        except Exception as e:
            debug_print(f"Error durante la operacion: {e}")
        finally:
            # Restaurar el estado del scroll vertical
            if vertical_scroll_state:
                # Pequeño retraso para asegurar que la UI se actualice
                QtCore.QTimer.singleShot(100, lambda: restore_vertical_scroll_state(vertical_scroll_state))
                debug_print("Restauración del scroll vertical programada")

            # Finalizar la accion de undo
            project.endUndo()
            

            
    except Exception as e:
        debug_print(f"Error general: {e}")

if __name__ == "__main__":
    main() 