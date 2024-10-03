import hiero.core
import hiero.ui

def activate_blend_mode_for_exr_track():
    # Obtiene la secuencia activa
    seq = hiero.ui.activeSequence()
    
    if not seq:
        print("No hay una secuencia activa.")
        return
    
    # Itera sobre los tracks de video para encontrar el que se llama "EXR"
    for index, track in enumerate(seq.videoTracks()):
        if track.name() == "EXR":
            # Activa el blend mode para el track "EXR"
            track.setBlendEnabled(True)
            track.setBlendMode("over")  # Puedes ajustar el modo de blend segun sea necesario
            print(f"Blend mode activado para el track 'EXR' en el indice: {index}")
            break
    else:
        print("No se encontro un track llamado 'EXR'.")

# Llama a la funcion para activar el blend mode del track "EXR"
activate_blend_mode_for_exr_track()
