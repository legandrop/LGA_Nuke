import hiero.core
import hiero.ui
from PySide2.QtGui import QColor
import os

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
    # Dividir la ruta en partes
    bin_names = bin_path.split('/')

    # Empezar desde el bin de clips
    current_bin = project.clipsBin()

    # Iterar sobre las partes de la ruta
    for bin_name in bin_names:
        found_bin = None
        # Buscar el bin actual por su nombre
        for item in current_bin.items():
            if isinstance(item, hiero.core.Bin) and item.name() == bin_name:
                found_bin = item
                break
        # Si no se encontro el bin, crear uno nuevo
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
    # Buscar el bin de origen por su nombre
    source_bin = None
    for bin_item in project.clipsBin().items():
        if bin_item.name() == source_bin_name:
            source_bin = bin_item
            break

    if source_bin:
        # Buscar el clip por su nombre dentro del bin de origen
        clip_to_move = None
        for clip_item in source_bin.items():
            if clip_item.name() == clip_name:
                clip_to_move = clip_item
                break

        if clip_to_move:
            # Encontrar o crear el bin de destino
            target_bin = find_or_create_bin(project, target_bin_path)

            # Remover el clip del bin de origen
            source_bin.removeItem(clip_to_move)

            # Remover el clip del bin original (no me esta funcionando)
            original_bin_item = shot.source().binItem()
            original_bin = original_bin_item.parentBin()
            #original_bin.removeItem(original_bin_item)    
            
            # Agregar el clip al bin de destino
            target_bin.addItem(clip_to_move)
            print("Se movio el clip '{}' del bin '{}' al bin '{}'.".format(clip_name, source_bin_name, target_bin_path))
        else:
            print("No se encontro el clip '{}' en el bin de origen '{}'.".format(clip_name, source_bin_name))
    else:
        print("No se encontro el bin de origen '{}'.".format(source_bin_name))

# Obtener el proyecto actual en Hiero
project = hiero.core.projects()[0] if hiero.core.projects() else None

def replaceClip_in_place():
    try:
        seq = hiero.ui.activeSequence()
        if not seq:
            print("No active sequence found.")
            return

        te = hiero.ui.getTimelineEditor(seq)
        selected_clips = te.selection()
        project = hiero.core.projects()[0]
        project.beginUndo("Change Clip Color")

        if len(selected_clips) == 0:
            print("*** No clips selected on the track ***")
        else:


            for shot in selected_clips:
                if isinstance(shot, hiero.core.EffectTrackItem):  # Verificar si es un efecto
                    print(f"Ignore effect item: {shot.name()}")
                else:            
                
                    file_path = shot.source().mediaSource().fileinfos()[0].filename()
                    print("File path:", file_path)

                    bin_item = shot.source().binItem()
                    full_bin_path = get_full_bin_path(bin_item)
                    full_bin_path = full_bin_path.replace("Sequences/", "")
                    print("Full bin path for the clip:", full_bin_path)

                    try:
                        shot.replaceClips(file_path)
                        print("Clip replaced successfully.")
                    except:
                        print("Error replacing clip.")


                    
                    new_clip_name = shot.source().name()
                    print(f"Clip name: {new_clip_name}")

                    conform_bin_name = "Conform"
                    original_bin_name = full_bin_path.split(' > ')[-1]
                    move_clip_to_bin(project, new_clip_name, conform_bin_name, full_bin_path, shot)


        project.endUndo()
    except Exception as e:
        print(f"Error during operation: {e}")

replaceClip_in_place()
