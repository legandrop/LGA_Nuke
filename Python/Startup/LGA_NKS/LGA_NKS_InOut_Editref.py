import hiero.core
import hiero.ui

def set_in_out_from_edit_ref_track():
    # Obtener la secuencia activa
    seq = hiero.ui.activeSequence()
    if not seq:
        print("No hay una secuencia activa.")
        return

    # Obtener la posicion del playhead
    te = hiero.ui.getTimelineEditor(seq)
    current_viewer = hiero.ui.currentViewer()
    player = current_viewer.player() if current_viewer else None
    playhead_frame = player.time() if player else None

    if playhead_frame is None:
        print("No se pudo obtener la posicion del playhead.")
        return

    # Buscar el track llamado "EditRef"
    edit_ref_track = None
    for track in seq.videoTracks():
        if track.name() == "EditRef":
            edit_ref_track = track
            break

    if not edit_ref_track:
        print("No se encontro un track llamado 'EditRef'.")
        return

    # Buscar el clip mas cercano en el track EditRef
    edit_ref_clip = None
    min_distance = float('inf')
    for item in edit_ref_track.items():
        if item.timelineIn() <= playhead_frame < item.timelineOut():
            edit_ref_clip = item
            break
        else:
            # Calcular la distancia al playhead
            if playhead_frame < item.timelineIn():
                distance = item.timelineIn() - playhead_frame
            else:
                distance = playhead_frame - item.timelineOut()
            if distance < min_distance:
                min_distance = distance
                edit_ref_clip = item

    if not edit_ref_clip:
        print("No se encontro ningun clip en el track EditRef.")
        return

    # Obtener el in y out del clip de referencia
    ref_in = edit_ref_clip.timelineIn()
    ref_out = edit_ref_clip.timelineOut()

    # Establecer el in y out de la secuencia
    seq.setInTime(ref_in)
    seq.setOutTime(ref_out)

    print(f"Se ha establecido el in/out de la secuencia a [{ref_in}, {ref_out}] basado en el clip de EditRef mas cercano.")

# Ejecutar la funcion
set_in_out_from_edit_ref_track()