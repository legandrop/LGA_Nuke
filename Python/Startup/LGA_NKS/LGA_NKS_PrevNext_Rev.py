"""
______________________________________________________________________________________________

  LGA_NKS_PrevNext_Rev v1.2 - 2024 - Lega

  Busca el clip anterior o siguiente con estado Rev_Lega o Rev_Sup
  y ajusta la vista:
  1. Obtiene la posición actual del playhead.
  2. Encuentra el clip más cercano con el color especificado en la dirección indicada.
  3. Establece los puntos In/Out basados en el clip EditRef correspondiente a esa posición.
  4. Selecciona el clip EditRef.
  5. Mueve el playhead a la posición del In.
  6. Ajusta el zoom para que se ajuste al clip seleccionado.
  7. Deselecciona todos los clips.
______________________________________________________________________________________________
"""

import hiero.core
import hiero.ui
from PySide2.QtGui import QColor
from PySide2.QtCore import QTimer

DEBUG = False

def debug_print(*message):
    if DEBUG:
        print(*message)

# Definir los colores que buscamos
COLORS = {
    "lega": QColor(105, 19, 94),   # #69135e
    "sup": QColor(163, 85, 126)    # #a3557e
}

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

def find_clip_with_color(direction, rev_type):
    """
    Encuentra el clip con el color especificado en la dirección indicada.
    Ignora el clip actual si el playhead está sobre él.
    """
    seq = hiero.ui.activeSequence()
    if not seq:
        debug_print("No hay una secuencia activa.")
        return None

    playhead_pos = get_current_playhead_position()
    if playhead_pos is None:
        debug_print("No se pudo obtener la posición del playhead.")
        return None

    target_clip = None
    min_distance = float('inf')
    target_color = COLORS.get(rev_type)

    # Buscar en todas las pistas de video
    for track in seq.videoTracks():
        for item in track.items():
            if isinstance(item, hiero.core.EffectTrackItem):
                continue

            # Verificar si el clip tiene el color buscado
            bin_item = item.source().binItem()
            if bin_item.color() == target_color:
                clip_start = item.timelineIn()
                clip_end = item.timelineOut()

                # Ignorar el clip si el playhead está sobre él
                if clip_start <= playhead_pos < clip_end:
                    debug_print(f"Ignorando clip actual: {item.name()}")
                    continue

                # Para dirección "next", buscar clips después del playhead
                if direction == "next" and clip_start > playhead_pos:
                    distance = clip_start - playhead_pos
                    if distance < min_distance:
                        min_distance = distance
                        target_clip = item
                        debug_print(f"Encontrado clip siguiente: {item.name()} a distancia {distance}")

                # Para dirección "prev", buscar clips antes del playhead
                elif direction == "prev" and clip_end < playhead_pos:
                    distance = playhead_pos - clip_end
                    if distance < min_distance:
                        min_distance = distance
                        target_clip = item
                        debug_print(f"Encontrado clip anterior: {item.name()} a distancia {distance}")

    if target_clip:
        debug_print(f"Clip seleccionado: {target_clip.name()}")
    else:
        debug_print(f"No se encontraron más clips {rev_type} en dirección {direction}")

    return target_clip

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

    return closest_clip  # Retornar el clip más cercano si no se encuentra uno exacto

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
    Primero activa la ventana del timeline y luego ejecuta el comando con un timer.
    """
    try:
        # Obtener y activar la ventana del timeline
        window = hiero.ui.getTimelineEditor(hiero.ui.activeSequence()).window()
        window.activateWindow()
        window.setFocus()

        # Ejecutar el comando Zoom to Fit después de que la UI se actualice
        QTimer.singleShot(0, lambda: hiero.ui.findMenuAction('Zoom to Fit').trigger())
        debug_print("Ejecutando comando Zoom to Fit")
    except Exception as e:
        debug_print(f"Error al ajustar la vista: {e}")

def main(direction, rev_type):
    """
    Función principal que ejecuta la secuencia completa de operaciones.
    """
    # 1. Encontrar el clip con el color especificado en la dirección indicada
    target_clip = find_clip_with_color(direction, rev_type)
    if not target_clip:
        debug_print(f"No se encontraron más clips con estado Rev_{rev_type.capitalize()}.")
        return

    # 2. Obtener la posición del clip
    clip_position = target_clip.timelineIn()
    debug_print(f"Clip Rev_{rev_type.capitalize()} encontrado en posición: {clip_position}")

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

    # 5. Seleccionar el clip EditRef
    timeline_editor = hiero.ui.getTimelineEditor(hiero.ui.activeSequence())
    if timeline_editor:
        timeline_editor.setSelection([edit_ref_clip])
        debug_print(f"Clip seleccionado: {edit_ref_clip.name()}")

    # 6. Mover el playhead a la posición del In
    move_playhead_to_position(in_point)

    # 7. Ajustar el zoom para que se ajuste al clip
    ajustar_vista_al_clip()

    # 8. Deseleccionar todos los clips
    if timeline_editor:
        timeline_editor.selectNone()
        debug_print("Clips deseleccionados")

if __name__ == "__main__":
    # Si se ejecuta directamente, usar valores por defecto
    main("next", "lega")
