import hiero.core

def print_clip_path(project, bin_name, clip_name):
    """
    Imprime el path del clip dado dentro del bin especificado en el proyecto.
    
    Args:
    - project (hiero.core.Project): El proyecto actual en Hiero.
    - bin_name (str): El nombre del bin que contiene el clip.
    - clip_name (str): El nombre del clip cuyo path queremos imprimir.
    """
    # Buscar el bin por su nombre
    test_bin = None
    for bin_item in project.clipsBin().items():
        if bin_item.name() == bin_name:
            test_bin = bin_item
            break

    if test_bin:
        # Buscar el clip por su nombre dentro del bin
        for clip_item in test_bin.items():
            if clip_item.name() == clip_name:
                # Obtener la fuente de medios del clip
                media_source = clip_item.activeItem().mediaSource()
                if media_source:
                    # Obtener la lista de archivos del clip y imprimir el path del primero
                    files = media_source.fileinfos()
                    if files:
                        file_path = files[0].filename()
                        print("Path del clip '{}': {}".format(clip_name, file_path))
                        return

    # Si no se encuentra el bin o el clip, imprimir un mensaje de error
    print("No se encontro el bin '{}' o el clip '{}' dentro del proyecto.".format(bin_name, clip_name))

# Obtener el proyecto actual en Hiero
project = hiero.core.projects()[0] if hiero.core.projects() else None

if project:
    bin_name = "Test"
    clip_name = "EHQALPV_025_010_TV_Isla-A_comp"
    print_clip_path(project, bin_name, clip_name)
else:
    print("No se encontro un proyecto abierto en Hiero.")
