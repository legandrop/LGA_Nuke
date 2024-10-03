import hiero.core
import hiero.ui

def print_all_video_tracks():
    # Obtiene la secuencia activa
    seq = hiero.ui.activeSequence()
    
    if not seq:
        print("No hay una secuencia activa.")
        return
    
    # Itera sobre los tracks de video y los imprime
    for index, track in enumerate(seq.videoTracks()):
        print(f"Track de video en el indice {index}: {track.name()}")

# Llama a la funcion para imprimir todos los tracks de video
print_all_video_tracks()
