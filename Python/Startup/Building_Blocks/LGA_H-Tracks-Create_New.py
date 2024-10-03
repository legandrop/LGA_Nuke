import hiero.ui
import hiero.core

def create_new_track():
    # Obtener la secuencia activa en el timeline
    seq = hiero.ui.activeSequence()
    if not seq:
        print("No active sequence found.")
        return

    # Crear un nuevo track de video
    new_track = hiero.core.VideoTrack("New Video Track")
    
    # Agregar el nuevo track a la secuencia activa
    seq.addTrack(new_track)
    
    print(f"New track '{new_track.name()}' added to the sequence.")

# Llamar a la funcion para crear el nuevo track
create_new_track()
