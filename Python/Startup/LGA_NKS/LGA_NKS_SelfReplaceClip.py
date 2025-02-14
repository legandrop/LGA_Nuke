"""
______________________________________________________________________

  LGA_NKS_SelfReplaceClip v1.1 - 2025 - Lega
  Reconnect automático con el mismo clip, corrige desplazamiento de frames
  y mueve versión original al bin 'Conform' 
______________________________________________________________________

"""

import hiero.core
import hiero.ui
import os
import re

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

def get_full_bin_path(bin_item):
    path = []
    while bin_item:
        if isinstance(bin_item, hiero.core.Bin):
            path.append(bin_item.name())
        bin_item = bin_item.parentBin() if hasattr(bin_item, 'parentBin') else None
    return '/'.join(reversed(path))

def find_or_create_bin(project, bin_path):
    """
    Encuentra un bin existente o crea uno nuevo si no existe.

    Args:
    - project (hiero.core.Project): El proyecto actual en Hiero.
    - bin_path (str): La ruta del bin.

    Returns:
    - hiero.core.Bin: El bin encontrado o creado.
    """
    bin_names = bin_path.split('/')
    current_bin = project.clipsBin()
    for bin_name in bin_names:
        found_bin = None
        for item in current_bin.items():
            if isinstance(item, hiero.core.Bin) and item.name() == bin_name:
                found_bin = item
                break
        if not found_bin:
            found_bin = hiero.core.Bin(bin_name)
            current_bin.addItem(found_bin)
        current_bin = found_bin
    return current_bin

def move_clip_to_bin(project, clip_name, source_bin_name, target_bin_path, shot):
    """
    Mueve un clip de un bin de origen a un bin de destino en el proyecto.

    Args:
    - project (hiero.core.Project): El proyecto actual en Hiero.
    - clip_name (str): El nombre del clip que se movera.
    - source_bin_name (str): El nombre del bin de origen que contiene el clip.
    - target_bin_path (str): La ruta del bin de destino donde se movera el clip.
    """
    source_bin = None
    for bin_item in project.clipsBin().items():
        if bin_item.name() == source_bin_name:
            source_bin = bin_item
            break

    if source_bin:
        clip_to_move = None
        for clip_item in source_bin.items():
            if clip_item.name() == clip_name:
                clip_to_move = clip_item
                break

        if clip_to_move:
            target_bin = find_or_create_bin(project, target_bin_path)
            source_bin.removeItem(clip_to_move)
            # Remover el clip del bin original (no me esta funcionando)
            original_bin_item = shot.source().binItem()
            original_bin = original_bin_item.parentBin()
            # original_bin.removeItem(original_bin_item)    

            target_bin.addItem(clip_to_move)
            debug_print(f"Se movio el clip '{clip_name}' del bin '{source_bin_name}' al bin '{target_bin_path}'.")
        else:
            debug_print(f"No se encontro el clip '{clip_name}' en el bin de origen '{source_bin_name}'.")
    else:
        debug_print(f"No se encontro el bin de origen '{source_bin_name}'.")

def main():
    debug_print("\n==== INICIANDO SCRIPT DE SELFREPLACE ====")
    try:
        project = hiero.core.projects()[-1]
        with project.beginUndo("Self Replace Clips"):
            seq = hiero.ui.activeSequence()
            if not seq:
                debug_print("No active sequence found.")
                return

            te = hiero.ui.getTimelineEditor(seq)
            selected_clips = te.selection()

            if len(selected_clips) == 0:
                debug_print("*** No hay clips seleccionados en la pista ***")
            else:
                valid_clips = [clip for clip in selected_clips if not isinstance(clip, hiero.core.EffectTrackItem)]
                skipped_clips = [clip.name() for clip in selected_clips if isinstance(clip, hiero.core.EffectTrackItem)]
                
                debug_print(f"Procesando {len(valid_clips)} clips válidos...")
                if skipped_clips:
                    debug_print(f"Salteando {len(skipped_clips)} efectos: {', '.join(skipped_clips)}")
                
                for shot in valid_clips:
                    # Imprimir información del clip antes del reemplazo
                    print_clip_info(shot, "BEFORE")
                    
                    # Guardar los valores originales
                    original_source_in = shot.sourceIn()
                    original_source_out = shot.sourceOut()
                    original_source_in_source = shot.source().sourceIn()
                    frame_offset = 997  # Offset para llevar a 1001
                    
                    file_path = shot.source().mediaSource().fileinfos()[0].filename() if shot.source().mediaSource().fileinfos() else None
                    if not file_path:
                        debug_print("No se encontro el path del archivo del clip.")
                        continue
                    debug_print("\nFile path:", file_path)

                    bin_item = shot.source().binItem()
                    full_bin_path = get_full_bin_path(bin_item)
                    full_bin_path = full_bin_path.replace("Sequences/", "")
                    debug_print("Ruta completa del bin para el clip:", full_bin_path)

                    try:
                        shot.replaceClips(file_path)
                        debug_print("Clip reemplazado exitosamente.")
                        
                        # Verificar si los frames necesitan corrección
                        if shot.sourceIn() < original_source_in:
                            debug_print("\n¡ADVERTENCIA! Los frames se han corrido, aplicando corrección...")
                            
                            # Calcular el nuevo source in/out basado en el original + offset
                            new_source_in = original_source_in
                            new_source_out = original_source_out
                            
                            # Aplicar los nuevos valores
                            shot.setSourceIn(new_source_in)
                            shot.setSourceOut(new_source_out)
                            
                            debug_print("\nFrame correction applied:")
                            debug_print(f"Source In adjusted: {shot.sourceIn()} -> {new_source_in}")
                            debug_print(f"Source Out adjusted: {shot.sourceOut()} -> {new_source_out}")
                        else:
                            debug_print("\nLos frames están correctos, no se requiere corrección.")
                        
                        # Imprimir información del clip después del reemplazo
                        print_clip_info(shot, "AFTER")
                        
                    except Exception as e:
                        debug_print(f"Error reemplazando el clip: {e}")

                    new_clip_name = shot.source().name()
                    debug_print(f"Nombre del clip: {new_clip_name}")

                    conform_bin_name = "Conform"
                    original_bin_name = full_bin_path.split(' > ')[-1]
                    move_clip_to_bin(project, new_clip_name, conform_bin_name, full_bin_path, shot)

        debug_print("\n==== SCRIPT DE SELFREPLACE COMPLETADO ====")
    except Exception as e:
        debug_print(f"Error en script SelfReplace: {e}")
