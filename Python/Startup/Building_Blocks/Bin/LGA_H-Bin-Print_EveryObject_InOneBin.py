import hiero.core

def print_conform_bin_structure(project):
    """
    Imprime la estructura de los items dentro del bin "Conform".
    
    Args:
    - project (hiero.core.Project): El proyecto actual en Hiero.
    """
    print("Items dentro del bin 'Conform':")
    conform_bin = None
    for bin_item in project.clipsBin().items():
        if bin_item.name() == "Conform":
            conform_bin = bin_item
            break

    if conform_bin:
        print_bin_hierarchy(conform_bin)
    else:
        print("El bin 'Conform' no fue encontrado en el proyecto.")

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
    print_conform_bin_structure(project)
else:
    print("No se encontro un proyecto abierto en Hiero.")
