"""
______________________________________________________________________

  LGA_NKS_SelfReplaceClip v1.0 - 2024 - Lega
  Reemplaza clips seleccionados y los mueve a bins especificos
______________________________________________________________________

"""

import hiero.core
import hiero.ui
import os
import re

DEBUG = True

def debug_print(*message):
    if DEBUG:
        print(*message)

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
    project = hiero.core.projects()[0] if hiero.core.projects() else None
    try:
        seq = hiero.ui.activeSequence()
        if not seq:
            debug_print("No se encontro una secuencia activa.")
            return

        te = hiero.ui.getTimelineEditor(seq)
        selected_clips = te.selection()
        project = hiero.core.projects()[0]
        project.beginUndo("Self Replace Clip")

        if len(selected_clips) == 0:
            debug_print("*** No hay clips seleccionados en la pista ***")
        else:
            for shot in selected_clips:
                if isinstance(shot, hiero.core.EffectTrackItem):
                    debug_print(f"Ignorando item de efecto: {shot.name()}")
                else:            
                    file_path = shot.source().mediaSource().fileinfos()[0].filename() if shot.source().mediaSource().fileinfos() else None
                    if not file_path:
                        debug_print("No se encontro el path del archivo del clip.")
                        continue
                    debug_print("File path:", file_path)

                    bin_item = shot.source().binItem()
                    full_bin_path = get_full_bin_path(bin_item)
                    full_bin_path = full_bin_path.replace("Sequences/", "")
                    debug_print("Ruta completa del bin para el clip:", full_bin_path)

                    try:
                        shot.replaceClips(file_path)
                        debug_print("Clip reemplazado exitosamente.")
                    except Exception as e:
                        debug_print(f"Error reemplazando el clip: {e}")

                    new_clip_name = shot.source().name()
                    debug_print(f"Nombre del clip: {new_clip_name}")

                    conform_bin_name = "Conform"
                    original_bin_name = full_bin_path.split(' > ')[-1]
                    move_clip_to_bin(project, new_clip_name, conform_bin_name, full_bin_path, shot)

        project.endUndo()
    except Exception as e:
        debug_print(f"Error durante la operacion: {e}")
