"""
______________________________________________________________________

  LGA_NKS_Reconnect v1.1 - 2025 - Lega
  Reconecta clips seleccionados a diferentes rutas, manteniendo el color original.
______________________________________________________________________

"""

import hiero.core
import hiero.ui
import os
from PySide2.QtGui import QColor

# Eliminamos la importación del SelfReplace
# import LGA_NKS_SelfReplaceClip as self_replace

DEBUG = False

def debug_print(*message):
    if DEBUG:
        print(*message)

def print_clip_info(shot, prefix=""):
    """
    Imprime la información detallada del clip
    """
    debug_print(f"\n{prefix} Clip Info:")
    debug_print(f"Clip Name: {shot.name()}")
    
    # Información del clip en la timeline
    debug_print("\nTimeline Info:")
    debug_print(f"Source In: {shot.sourceIn()}")
    debug_print(f"Source Out: {shot.sourceOut()}")
    debug_print(f"Source Duration: {shot.sourceDuration()}")
    debug_print(f"Timeline In: {shot.timelineIn()}")
    debug_print(f"Timeline Out: {shot.timelineOut()}")
    debug_print(f"Timeline Duration: {shot.duration()}")
    
    # Información del Source
    source = shot.source()
    media_source = source.mediaSource()
    debug_print("\nSource Info:")
    debug_print(f"Source In: {source.sourceIn()}")
    debug_print(f"Source Out: {source.sourceOut()}")
    debug_print(f"Frame Rate: {source.framerate()}")
    
    # Información adicional del clip
    debug_print("\nAdditional Clip Info:")
    debug_print(f"Original Frame Rate: {shot.playbackSpeed()}")
    debug_print(f"Media Source Path: {media_source.fileinfos()[0].filename()}")
    
    # Información del formato
    format_obj = source.format()
    if format_obj:
        debug_print("\nFormat Info:")
        debug_print(f"Format: {format_obj.name()}")
        debug_print(f"Resolution: {format_obj.width()}x{format_obj.height()}")

def get_clip_color(clip):
    """
    Devuelve el color actual del BinItem asociado al clip.
    """
    try:
        bin_item = clip.source().binItem()
        return bin_item.color()
    except Exception as e:
        debug_print(f"No se pudo obtener el color del clip: {e}")
        return None

def set_clip_color(clip, color):
    """
    Asigna un color al BinItem asociado al clip.
    """
    try:
        bin_item = clip.source().binItem()
        if color:
            bin_item.setColor(color)
            debug_print(f"Color restaurado para el clip: {clip.name()}")
    except Exception as e:
        debug_print(f"No se pudo asignar el color al clip: {e}")

def main():
    debug_print("\n==== INICIANDO SCRIPT DE RECONNECT ====")
    try:
        project = hiero.core.projects()[-1]
        with project.beginUndo("Reconnect T Win > Mac"):
            seq = hiero.ui.activeSequence()
            if not seq:
                debug_print("No active sequence found.")
                return

            te = hiero.ui.getTimelineEditor(seq)
            selected_clips = te.selection()

            if len(selected_clips) == 0:
                debug_print("*** No clips selected on the track ***")
            else:
                valid_clips = [clip for clip in selected_clips if not isinstance(clip, hiero.core.EffectTrackItem)]
                skipped_clips = [clip.name() for clip in selected_clips if isinstance(clip, hiero.core.EffectTrackItem)]
                
                debug_print(f"Procesando {len(valid_clips)} clips válidos...")
                if skipped_clips:
                    debug_print(f"Salteando {len(skipped_clips)} efectos: {', '.join(skipped_clips)}")
                
                for shot in valid_clips:
                    # Leer color original antes de reconectar
                    original_color = get_clip_color(shot)
                    # Imprimir información del clip antes del reemplazo
                    print_clip_info(shot, "BEFORE")

                    # Guardar los valores originales antes de reconectar
                    original_source_in = shot.sourceIn()
                    original_source_out = shot.sourceOut()
                    original_duration = shot.sourceDuration()
                    # frame_offset = 997  # Offset para llevar a 1001 (comentado)

                    # Obtener el file path del clip seleccionado
                    file_path = shot.source().mediaSource().fileinfos()[0].filename()
                    debug_print("\nOriginal file path:", file_path)

                    # Inicializar new_file_path con el path original
                    new_file_path = file_path

                    # Primero intentar reemplazar "T:" si existe
                    if "T:" in file_path:
                        new_file_path = file_path.replace("T:", "/Volumes/T Viaja/T")
                    # Si no encontró T:, buscar si comienza con /VFX-
                    elif file_path.upper().startswith("/VFX-"):
                        new_file_path = "/Volumes/T Viaja/T" + file_path

                    # Reemplazar las barras invertidas por barras normales
                    new_file_path = new_file_path.replace("\\", "/")
                    debug_print("Modified file path:", new_file_path)

                    # Obtener solo la ruta del directorio sin el nombre del archivo
                    directory_path = os.path.dirname(new_file_path)

                    # Reconectar el clip con la nueva ruta
                    try:
                        # Reconectar el clip
                        shot.reconnectMedia(directory_path)
                        debug_print("\nClip reconnected successfully.")
                        # Restaurar el color original
                        set_clip_color(shot, original_color)
                        # Imprimir información del clip después del reemplazo
                        print_clip_info(shot, "AFTER RECONNECT")
                    except Exception as e:
                        debug_print(f"\nError reconnecting clip: {e}")
                        continue

                debug_print("\n==== SCRIPT DE RECONNECT COMPLETADO ====")

    except Exception as e:
        debug_print(f"Error en script Reconnect: {e}")