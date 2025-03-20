"""
__________________________________________________________

  LGA_NKS_Next_RevLega v1.2 - 2024 - Lega

  Busca el siguiente clip con estado Rev_Lega y ajusta la vista:
  1. Obtiene la posición actual del playhead.
   2. Encuentra el siguiente clip más cercano con color Rev_Lega.
  3. Establece los puntos In/Out basados en el clip EditRef
     correspondiente a esa posición.
  4. Mueve el playhead a la posición del In.
  5. Ajusta el zoom para que se ajuste al clip seleccionado.
__________________________________________________________
"""

import hiero.core
import hiero.ui
from PySide2.QtGui import QColor

DEBUG = False

def debug_print(*message):
    if DEBUG:
        print(*message)

# Definir el color que buscamos (Rev_Lega)
REV_LEGA_COLOR = QColor(105, 19, 94)  # #69135e

def get_current_playhead_position():
    """
    Obtiene la posición actual del playhead.
    """
    try:
        viewer = hiero.ui.currentViewer()
        if viewer:
            return viewer.time()
        return None
    except Exception as e:
        debug_print(f"Error al obtener la posición del playhead: {e}")
        return None

def find_next_revlega_clip():
    """
    Encuentra el siguiente clip con color Rev_Lega después del playhead.
    """
    seq = hiero.ui.activeSequence()
    if not seq:
        debug_print("No hay una secuencia activa.")
        return None

    playhead_pos = get_current_playhead_position()
    if playhead_pos is None:
        debug_print("No se pudo obtener la posición del playhead.")
        return None

    next_clip = None
    min_distance = float('inf')

    # Buscar en todas las pistas de video
    for track in seq.videoTracks():
        for item in track.items():
            if isinstance(item, hiero.core.EffectTrackItem):
                continue

            # Verificar si el clip tiene el color Rev_Lega
            bin_item = item.source().binItem()
            if bin_item.color() == REV_LEGA_COLOR:
                # Calcular la distancia al playhead
                clip_start = item.timelineIn()
                if clip_start > playhead_pos:  # Solo considerar clips después del playhead
                    distance = clip_start - playhead_pos
                    if distance < min_distance:
                        min_distance = distance
                        next_clip = item

    return next_clip

def find_editref_clip_at_position(position):
    """
    Encuentra el clip en el track EditRef en la posición dada.
    """
    seq = hiero.ui.activeSequence()
    if not seq:
        debug_print("No hay una secuencia activa.")
        return None

    # Buscar el track EditRef
    edit_ref_track = None
    for track in seq.videoTracks():
        if track.name() == "EditRef":
            edit_ref_track = track
            break

    if not edit_ref_track:
        debug_print("No se encontró un track llamado 'EditRef'.")
        return None

    # Buscar el clip que contiene la posición
    for item in edit_ref_track.items():
        if item.timelineIn() <= position < item.timelineOut():
            return item

    # Si no se encuentra un clip que contenga la posición,
    # buscar el más cercano después de la posición
    closest_clip = None
    min_distance = float('inf')
    for item in edit_ref_track.items():
        if item.timelineIn() > position:
            distance = item.timelineIn() - position
            if distance < min_distance:
                min_distance = distance
                closest_clip = item

    return closest_clip

def set_in_out_from_clip(clip):
    """
    Establece los puntos In y Out de la secuencia basados en el clip.
    """
    if not clip:
        return None, None

    seq = hiero.ui.activeSequence()
    if not seq:
        return None, None

    ref_in = clip.timelineIn()
    ref_out = clip.timelineOut()

    seq.setInTime(ref_in)
    seq.setOutTime(ref_out)
    debug_print(f"Se ha establecido el in/out de la secuencia a [{ref_in}, {ref_out}]")

    return ref_in, ref_out

def move_playhead_to_position(position):
    """
    Mueve el playhead a una posición específica.
    """
    viewer = hiero.ui.currentViewer()
    if viewer:
        debug_print(f"Moviendo playhead a la posición: {position}")
        viewer.setTime(position)

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
    Función principal que ejecuta la secuencia completa de operaciones.
    """
    # 1. Encontrar el siguiente clip Rev_Lega
    next_clip = find_next_revlega_clip()
    if not next_clip:
        debug_print("No se encontraron más clips con estado Rev_Lega.")
        return

    # 2. Obtener la posición del clip
    clip_position = next_clip.timelineIn()
    debug_print(f"Clip Rev_Lega encontrado en posición: {clip_position}")

    # 3. Encontrar el clip EditRef correspondiente
    edit_ref_clip = find_editref_clip_at_position(clip_position)
    if not edit_ref_clip:
        debug_print("No se encontró un clip EditRef correspondiente.")
        return

    # 4. Establecer In/Out basados en el clip EditRef
    in_point, out_point = set_in_out_from_clip(edit_ref_clip)
    if in_point is None:
        debug_print("No se pudieron establecer los puntos In/Out.")
        return

    # 5. Mover el playhead a la posición del In
    move_playhead_to_position(in_point)

    # 6. Ajustar el zoom para que se ajuste al clip
    ajustar_vista_al_clip()

if __name__ == "__main__":
    main()
