import hiero.core
import hiero.ui

def print_exr_track_index():
    # Obtiene la secuencia activa
    seq = hiero.ui.activeSequence()
    
    if not seq:
        print("No hay una secuencia activa.")
        return
    
    # Itera sobre los tracks de video para encontrar el que se llama "EXR"
    for index, track in enumerate(seq.videoTracks()):
        if track.name() == "EXR":
            print(f"Track 'EXR' encontrado en el indice: {index}")
            break
    else:
        print("No se encontro un track llamado 'EXR'.")

# Llama a la funcion para imprimir el indice del track "EXR"
print_exr_track_index()
