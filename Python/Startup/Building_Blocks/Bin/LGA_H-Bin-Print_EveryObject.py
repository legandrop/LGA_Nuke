# Imprime todas las seqs y carpetas del bin

import hiero.core

def print_bin_structure(project):
    """
    Imprime la estructura de Bins del proyecto.
    
    Args:
    - project (hiero.core.Project): El proyecto actual en Hiero.
    """
    print("Estructura de Bins del proyecto:")
    for root_bin in project.clipsBin().items():
        print_bin_hierarchy(root_bin)

def print_bin_hierarchy(bin_item, indent=0):
    """
    Imprime la jerarquia de un Bin y sus sub-bins.
    
    Args:
    - bin_item (hiero.core.BinItem): El Bin o carpeta de Bin actual.
    - indent (int): La cantidad de espacios de indentacion.
    """
    bin_name = bin_item.name()
    if not bin_name.endswith('.nk'):  # Filtrar archivos .nk
        print("{}{}".format("    " * indent, bin_name))
        indent += 1
        if isinstance(bin_item, hiero.core.Bin):
            for item in bin_item.items():
                if not isinstance(item, hiero.core.Sequence):  # Filtrar secuencias
                    print_bin_hierarchy(item, indent)

# Obtener el proyecto actual en Hiero
project = hiero.core.projects()[0] if hiero.core.projects() else None

if project:
    print_bin_structure(project)
else:
    print("No se encontro un proyecto abierto en Hiero.")
