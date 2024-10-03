import hiero.core
import hiero.ui

def find_sequence_by_name(project, sequence_name):
    """
    Busca una secuencia especifica por nombre en el proyecto.
    
    Args:
    - project (hiero.core.Project): El proyecto actual en Hiero.
    - sequence_name (str): El nombre de la secuencia a buscar.
    
    Returns:
    - hiero.core.Sequence or None: La secuencia encontrada o None si no se encuentra.
    """
    def search_in_bin(bin_item):
        for item in bin_item.items():
            if isinstance(item, hiero.core.BinItem) and isinstance(item.activeItem(), hiero.core.Sequence):
                if item.name() == sequence_name:
                    return item.activeItem()
            elif isinstance(item, hiero.core.Bin):
                result = search_in_bin(item)
                if result:
                    return result
        return None

    return search_in_bin(project.clipsBin())

def open_sequence_in_new_viewer_and_timeline(sequence_name):
    """
    Abre la secuencia especificada en un nuevo viewer y un nuevo timeline.
    
    Args:
    - sequence_name (str): El nombre de la secuencia a abrir.
    """
    # Obtener el proyecto actual en Hiero
    project = hiero.core.projects()[0] if hiero.core.projects() else None

    if not project:
        print("No se encontro un proyecto abierto en Hiero.")
        return

    # Buscar la secuencia
    sequence = find_sequence_by_name(project, sequence_name)

    if sequence:
        # Abrir la secuencia en un nuevo viewer
        new_viewer = hiero.ui.openInNewViewer(sequence)
        if new_viewer:
            print(f"Se ha abierto la secuencia '{sequence_name}' en un nuevo viewer.")
        else:
            print(f"No se pudo abrir un nuevo viewer para la secuencia '{sequence_name}'.")
        
        # Abrir la secuencia en un nuevo timeline
        new_timeline = hiero.ui.openInTimeline(sequence)
        if new_timeline:
            print(f"Se ha abierto la secuencia '{sequence_name}' en un nuevo timeline.")
        else:
            print(f"No se pudo abrir un nuevo timeline para la secuencia '{sequence_name}'.")
    else:
        print(f"No se encontro la secuencia '{sequence_name}' en el proyecto.")

# Llamar a la funcion para abrir la secuencia "011-020" en un nuevo viewer y timeline
open_sequence_in_new_viewer_and_timeline("011-020")