import hiero.core
import hiero.ui

def create_and_move_new_track():
    # Obtener la secuencia activa en el timeline
    seq = hiero.ui.activeSequence()
    if not seq:
        print("No active sequence found.")
        return
    
    # Encontrar el indice del track llamado "EXR"
    exr_index = -1
    for index, track in enumerate(seq.videoTracks()):
        if track.name() == "EXR":
            exr_index = index
            break
    
    if exr_index == -1:
        print("No se encontro un track llamado 'EXR'.")
        return
    
    # Obtener la lista de todos los tracks de video
    video_tracks = list(seq.videoTracks())
    print(f"Current video tracks: {[track.name() for track in video_tracks]}")

    # Iniciar una accion de undo
    project = seq.project()
    project.beginUndo("Move COMPARE Track Above EXR")

    try:
        # Primero remover todos los tracks
        for track in video_tracks:
            seq.removeTrack(track)
        
        # Crear el nuevo track llamado "COMPARE"
        new_track = hiero.core.VideoTrack("COMPARE")
        
        # Reinsertar los tracks en el orden deseado, incluyendo el nuevo track antes de "EXR"
        reordered_tracks = video_tracks[:exr_index] + [new_track] + video_tracks[exr_index:]
        for track in reordered_tracks:
            seq.addTrack(track)
        
        print(f"New track '{new_track.name()}' moved to index {exr_index}.")
        print(f"Reordered video tracks: {[track.name() for track in reordered_tracks]}")
    except Exception as e:
        print(f"Error while reordering tracks: {e}")
    finally:
        # Finalizar la accion de undo
        project.endUndo()

# Llamar a la funcion para crear y mover el nuevo track
create_and_move_new_track()
