import hiero.core

def list_sequences_in_project(project):
    """
    Lista todas las secuencias en el proyecto usando BinItem.
    
    Args:
    - project (hiero.core.Project): El proyecto actual en Hiero.
    """
    print(f"Secuencias en el proyecto: {project.name()}")
    sequences = find_sequences(project.clipsBin())
    
    if sequences:
        for seq in sequences:
            print(f"- {seq.name()}")
            # Imprimir informacion adicional
            print(f"  Tipo: {type(seq).__name__}")
            if hasattr(seq, 'activeItem'):
                active_item = seq.activeItem()
                print(f"  Tipo de item activo: {type(active_item).__name__}")
            print("---")
    else:
        print("No se encontraron secuencias en el proyecto.")

def find_sequences(bin_item):
    """
    Busca recursivamente todas las secuencias en un Bin y sus sub-Bins.
    
    Args:
    - bin_item (hiero.core.Bin): El Bin en el que buscar.
    
    Returns:
    - list: Una lista de todas las secuencias encontradas.
    """
    sequences = []
    for item in bin_item.items():
        if isinstance(item, hiero.core.BinItem) and isinstance(item.activeItem(), hiero.core.Sequence):
            sequences.append(item)
        elif isinstance(item, hiero.core.Bin):
            sequences.extend(find_sequences(item))
    return sequences

# Obtener el proyecto actual en Hiero
project = hiero.core.projects()[0] if hiero.core.projects() else None

if project:
    list_sequences_in_project(project)
else:
    print("No se encontro un proyecto abierto en Hiero.")