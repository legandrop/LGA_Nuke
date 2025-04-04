"""
______________________________________________________

  LGA_NKS_CreateNewTrack v1.0 - 2024 - Lega
  Crea un nuevo track de video encima del track actualmente seleccionado
______________________________________________________

"""

import hiero.core
import hiero.ui

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
    
    if not selected_items:
        debug_print("No hay items seleccionados en la linea de tiempo.")
        return None
        
    # Obtener el track del primer item seleccionado
    selected_track = selected_items[0].parentTrack()
    if not selected_track:
        debug_print("No se pudo obtener el track seleccionado.")
        return None
        
    # Encontrar el indice del track en la secuencia
    for index, track in enumerate(seq.videoTracks()):
        if track == selected_track:
            return index
            
    return None

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
            # Finalizar la accion de undo
            project.endUndo()
            
    except Exception as e:
        debug_print(f"Error general: {e}")

if __name__ == "__main__":
    main() 