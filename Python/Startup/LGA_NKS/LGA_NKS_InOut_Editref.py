"""
__________________________________________________________

  LGA_NKS_InOut_Editref v1.2 - 2024 - Lega

  Establece los puntos In y Out de la secuencia activa
  basándose en el clip más cercano del track "EditRef".
  1. Obtiene la secuencia activa y la posición del playhead.
  2. Encuentra el clip más cercano en el track "EditRef".
  3. Establece los puntos In y Out basados en ese clip.
  4. Selecciona el clip y ajusta la vista para que se ajuste
     al clip seleccionado en el timeline.
__________________________________________________________
"""

import hiero.core
import hiero.ui

DEBUG = True

def debug_print(*message):
    if DEBUG:
        print(*message)

def set_in_out_from_edit_ref_track():
    """
    Establece los puntos In y Out basándose en el clip más cercano del track EditRef.
    """
    # Obtener la secuencia activa
    seq = hiero.ui.activeSequence()
    if not seq:
        debug_print("No hay una secuencia activa.")
        return None

    # Obtener la posicion del playhead
    te = hiero.ui.getTimelineEditor(seq)
    current_viewer = hiero.ui.currentViewer()
    player = current_viewer.player() if current_viewer else None
    playhead_frame = player.time() if player else None

    if playhead_frame is None:
        debug_print("No se pudo obtener la posicion del playhead.")
        return None

    # Buscar el track llamado "EditRef"
    edit_ref_track = None
    for track in seq.videoTracks():
        if track.name() == "EditRef":
            edit_ref_track = track
            break

    if not edit_ref_track:
        debug_print("No se encontro un track llamado 'EditRef'.")
        return None

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
        debug_print("No se encontro ningun clip en el track EditRef.")
        return None

    # Obtener el in y out del clip de referencia
    ref_in = edit_ref_clip.timelineIn()
    ref_out = edit_ref_clip.timelineOut()

    # Establecer el in y out de la secuencia
    seq.setInTime(ref_in)
    seq.setOutTime(ref_out)

    debug_print(f"Se ha establecido el in/out de la secuencia a [{ref_in}, {ref_out}] basado en el clip de EditRef mas cercano.")
    
    return edit_ref_clip

def seleccionar_y_ajustar_clip(clip):
    """
    Selecciona el clip y ajusta la vista para que se ajuste al clip seleccionado.
    """
    if not clip:
        return

    try:
        # Seleccionar el clip
        timeline_editor = hiero.ui.getTimelineEditor(hiero.ui.activeSequence())
        if timeline_editor:
            timeline_editor.setSelection([clip])
            debug_print(f"Clip seleccionado: {clip.name()}")

            # Ejecutar el comando Zoom to Fit
            action = hiero.ui.findMenuAction("Zoom to Fit")
            if action:
                debug_print("Ejecutando comando Zoom to Fit")
                action.trigger()
            else:
                debug_print("No se encontró el comando Zoom to Fit")
        else:
            debug_print("No se pudo obtener el timeline editor.")
    except Exception as e:
        debug_print(f"Error al seleccionar y ajustar el clip: {e}")

def main():
    """
    Función principal que establece los puntos In/Out y ajusta la vista.
    """
    print("LGA_NKS_InOut_Editref v1.1 - 2024 - Lega")
    clip = set_in_out_from_edit_ref_track()
    if clip:
        seleccionar_y_ajustar_clip(clip)

if __name__ == "__main__":
    main()
