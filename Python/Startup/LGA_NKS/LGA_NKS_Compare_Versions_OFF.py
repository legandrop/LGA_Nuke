import hiero.core
import hiero.ui

def remove_compare_track(seq):
    # Verificar si existe un track llamado "COMPARE" y eliminarlo
    for track in seq.videoTracks():
        if track.name() == "COMPARE":
            seq.removeTrack(track)
            print("Track 'COMPARE' removed.")
            return True
    print("Track 'COMPARE' not found.")
    return False

def disable_difference_mode_for_exr(seq):
    # Iterar sobre los tracks de video para encontrar el que se llama "EXR"
    for track in seq.videoTracks():
        if track.name() == "EXR":
            # Verificar si el blend mode esta activado
            if track.isBlendEnabled() and track.blendMode() == "difference":
                track.setBlendEnabled(False)
                print(f"Blend mode 'Difference' disabled for track 'EXR'.")
            else:
                print(f"Blend mode 'Difference' is not enabled for track 'EXR'.")
            return True
    print("Track 'EXR' not found.")
    return False

def main():
    # Obtener la secuencia activa en el timeline
    seq = hiero.ui.activeSequence()
    if not seq:
        print("No active sequence found.")
        return

    # Iniciar una accion de undo para las operaciones
    project = seq.project()
    project.beginUndo("Remove COMPARE Track and Disable EXR Difference Mode")

    try:
        # Remover el track "COMPARE"
        remove_compare_track(seq)

        # Desactivar el modo "Difference" para el track "EXR"
        disable_difference_mode_for_exr(seq)
    except Exception as e:
        print(f"Error during operation: {e}")
    finally:
        # Finalizar la accion de undo
        project.endUndo()

# Llamar a la funcion principal
if __name__ == "__main__":
    main()
