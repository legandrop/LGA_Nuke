"""
__________________________________________________________

  LGA_NKS_Timeline_InOutFitv2 v2.2 - 2024 - Lega

  Determina el clip del track "EditRef" que más abarca los
  puntos In y Out actuales de la secuencia activa en Hiero.
  1. Obtiene los valores actuales de In y Out de la secuencia.
  2. Encuentra el clip en el track "EditRef" que más abarca
     estos puntos.
  3. Selecciona el clip y ajusta la vista para que se ajuste
     al clip seleccionado en el timeline.
__________________________________________________________
"""

import hiero.ui

DEBUG = True

def debug_print(*message):
    if DEBUG:
        print(*message)

def obtener_in_out():
    """
    Obtiene los valores actuales de In y Out de la secuencia activa.
    """
    seq = hiero.ui.activeSequence()
    if not seq:
        debug_print("No hay una secuencia activa.")
        return None, None

    in_time = seq.inTime()
    out_time = seq.outTime()

    if in_time is None or out_time is None:
        debug_print("No se encontraron valores de In y Out.")
        return None, None

    debug_print(f"Valores actuales de In: {in_time}, Out: {out_time}")
    return in_time, out_time

def encontrar_clip_editref(in_time, out_time):
    """
    Encuentra el clip en el track "EditRef" que más abarca los puntos In y Out.
    """
    seq = hiero.ui.activeSequence()
    if not seq:
        debug_print("No hay una secuencia activa.")
        return None

    # Buscar el track llamado "EditRef"
    edit_ref_track = None
    for track in seq.videoTracks():
        if track.name() == "EditRef":
            edit_ref_track = track
            break

    if not edit_ref_track:
        debug_print("No se encontró un track llamado 'EditRef'.")
        return None

    # Buscar el clip que más abarca los puntos In y Out
    mejor_clip = None
    max_abarcado = 0
    for item in edit_ref_track.items():
        abarcado = min(out_time, item.timelineOut()) - max(in_time, item.timelineIn())
        if abarcado > max_abarcado:
            max_abarcado = abarcado
            mejor_clip = item

    if mejor_clip:
        debug_print(f"Clip seleccionado: {mejor_clip.name()}")
        return mejor_clip
    else:
        debug_print("No se encontró un clip que abarque los puntos In y Out.")
        return None

def ajustar_vista_al_clip():
    """
    Ajusta la vista para que se ajuste al clip seleccionado usando el comando de menú.
    """
    try:
        # Buscar y ejecutar el comando "Zoom to Fit"
        action = hiero.ui.findMenuAction("Zoom to Fit")
        if action:
            debug_print("Ejecutando comando Zoom to Fit")
            action.trigger()
        else:
            debug_print("No se encontró el comando Zoom to Fit")
    except Exception as e:
        debug_print(f"Error al ajustar la vista: {e}")

def main():
    """
    Función principal que encuentra y selecciona el clip del track "EditRef".
    """
    in_time, out_time = obtener_in_out()
    if in_time is None or out_time is None:
        debug_print("No se puede proceder sin valores de In y Out.")
        return

    clip = encontrar_clip_editref(in_time, out_time)
    if clip:
        # Seleccionar el clip usando setSelection
        timeline_editor = hiero.ui.getTimelineEditor(hiero.ui.activeSequence())
        if timeline_editor:
            timeline_editor.setSelection([clip])
            debug_print(f"Clip seleccionado: {clip.name()}")
            ajustar_vista_al_clip()
        else:
            debug_print("No se pudo obtener el timeline editor.")

if __name__ == "__main__":
    main()
