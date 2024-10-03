import hiero.core

def find_or_create_bin(root_bin, bin_name):
    """
    Busca o crea un bin dentro de otro bin.

    Args:
    - root_bin (hiero.core.Bin): El bin donde buscar o agregar el nuevo bin.
    - bin_name (str): El nombre del bin a buscar o crear.

    Returns:
    - hiero.core.Bin: El bin encontrado o creado.
    """
    for item in root_bin.items():
        if isinstance(item, hiero.core.Bin) and item.name() == bin_name:
            return item
    new_bin = hiero.core.Bin(bin_name)
    root_bin.addItem(new_bin)
    return new_bin

def move_clips_based_on_path(project):
    """
    Mueve los clips a bins basados en la estructura de carpetas derivada de sus paths de archivo.

    Args:
    - project (hiero.core.Project): El proyecto actual en Hiero.
    """
    # Funcion auxiliar para mover clips de manera recursiva
    def move_clips_from_bin(bin_item):
        if bin_item.name() == "Published":  # Ignorar el bin 'Published' y sus subcarpetas
            return
        for item in bin_item.items():
            if isinstance(item, hiero.core.BinItem) and isinstance(item.activeItem(), hiero.core.Clip):
                clip = item.activeItem()
                media_source = clip.mediaSource()
                if media_source and media_source.fileinfos():
                    file_path = media_source.fileinfos()[0].filename()
                    parts = file_path.split('/')
                    if len(parts) > 3:
                        folder_name = f"F {parts[2]}"
                        shot_name = parts[3]
                        folder_bin = find_or_create_bin(project.clipsBin(), folder_name)
                        shot_bin = find_or_create_bin(folder_bin, shot_name)
                        clip_item = clip.binItem()
                        if clip_item.parentBin() != shot_bin:
                            clip_item.parentBin().removeItem(clip_item)
                            shot_bin.addItem(clip_item)
            elif isinstance(item, hiero.core.Bin):
                move_clips_from_bin(item)

    def clean_empty_bins(bin_item):
        # Recursivamente limpiar bins vacios, excluyendo 'Published'
        if bin_item.name() == "Published":
            return
        items_to_check = list(bin_item.items())
        for item in items_to_check:
            if isinstance(item, hiero.core.Bin):
                clean_empty_bins(item)
        # Eliminar el bin si esta vacio despues de revisar sub-bins
        if not bin_item.items() and bin_item.parentBin():
            bin_item.parentBin().removeItem(bin_item)

    with project.beginUndo('Reorganize Clips Based on Path'):
        for bin_item in project.clipsBin().items():
            if isinstance(bin_item, hiero.core.Bin):
                move_clips_from_bin(bin_item)

        # Despues de mover todos los clips, limpiamos los bins vacios
        for bin_item in list(project.clipsBin().items()):
            if isinstance(bin_item, hiero.core.Bin):
                clean_empty_bins(bin_item)

project = hiero.core.projects()[0] if hiero.core.projects() else None
if project:
    move_clips_based_on_path(project)
else:
    print("No se encontro un proyecto abierto en Hiero.")
