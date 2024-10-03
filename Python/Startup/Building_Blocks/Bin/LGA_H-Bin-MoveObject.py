import hiero.core

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

def move_clip_to_bin(project, clip_name, source_bin_name, target_bin_path):
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
            # Agregar el clip al bin de destino
            target_bin.addItem(clip_to_move)
            print("Se movio el clip '{}' del bin '{}' al bin '{}'.".format(clip_name, source_bin_name, target_bin_path))
        else:
            print("No se encontro el clip '{}' en el bin de origen '{}'.".format(clip_name, source_bin_name))
    else:
        print("No se encontro el bin de origen '{}'.".format(source_bin_name))

# Obtener el proyecto actual en Hiero
project = hiero.core.projects()[0] if hiero.core.projects() else None

if project:
    clip_name = "EHQALPV_055_160_Chroma_Auto-D4_comp"
    source_bin_name = "Conform"
    target_bin_path = "Test/Testito"  # Ruta del bin de destino
    move_clip_to_bin(project, clip_name, source_bin_name, target_bin_path)
else:
    print("No se encontro un proyecto abierto en Hiero.")


# Funciona perfecto con subcarpetas