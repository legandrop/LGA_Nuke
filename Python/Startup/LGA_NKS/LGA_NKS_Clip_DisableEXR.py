"""
______________________________________________________________________________________________

  LGA_NKS_Clip_DisableEXR v1.0 - 2024 - Lega

  Habilita o deshabilita el clip en el track EXR que se encuentra bajo el playhead.
  
  Funcionamiento:
  1. Obtiene la posición actual del playhead
  2. Busca el track llamado "EXR"
  3. Encuentra el clip que coincide con la posición del playhead
  4. Invierte el estado de habilitación del clip (enabled/disabled)
______________________________________________________________________________________________
"""

import hiero.core
import hiero.ui

DEBUG = False

def debug_print(*message):
    if DEBUG:
        print(*message)

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

def find_exr_clip_at_position(position):
    """
    Encuentra el clip en el track EXR en la posición dada.
    """
    seq = hiero.ui.activeSequence()
    if not seq:
        debug_print("No hay una secuencia activa.")
        return None

    # Buscar el track EXR
    exr_track = None
    for track in seq.videoTracks():
        if track.name() == "EXR":
            exr_track = track
            break

    if not exr_track:
        debug_print("No se encontró un track llamado 'EXR'.")
        return None

    # Buscar el clip que contiene la posición
    for item in exr_track.items():
        if item.timelineIn() <= position < item.timelineOut():
            return item

    return None

def toggle_clip_enabled(clip):
    """
    Invierte el estado de habilitación del clip.
    """
    if not clip:
        return False

    try:
        # Obtener el estado actual y cambiarlo
        nuevo_estado = not clip.isEnabled()
        clip.setEnabled(nuevo_estado)
        
        estado_texto = "habilitado" if nuevo_estado else "deshabilitado"
        debug_print(f"Clip {clip.name()} {estado_texto}")
        return True
    except Exception as e:
        debug_print(f"Error al cambiar el estado del clip: {e}")
        return False

def main():
    """
    Función principal que ejecuta la secuencia de operaciones.
    """
    # 1. Obtener la posición del playhead
    playhead_pos = get_current_playhead_position()
    if playhead_pos is None:
        debug_print("No se pudo obtener la posición del playhead.")
        return

    # 2. Encontrar el clip en el track EXR
    clip = find_exr_clip_at_position(playhead_pos)
    if not clip:
        debug_print("No se encontró un clip en el track EXR en la posición actual.")
        return

    # 3. Cambiar el estado del clip
    if toggle_clip_enabled(clip):
        debug_print("Operación completada con éxito.")
    else:
        debug_print("No se pudo cambiar el estado del clip.")

if __name__ == "__main__":
    main() 