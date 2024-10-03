# Lista todas las versiones del clip y borra todas menos la ultima (deberia ser menos la active)

import hiero.core
import hiero.ui

def remove_version_by_name(bin_item, version_name):
    """
    Remove a version from a BinItem based on its name.
    
    Args:
        bin_item (hiero.core.BinItem): The BinItem containing the versions.
        version_name (str): The name of the version to be removed.
    """
    # Obtener todas las versiones
    all_versions = [bin_item.version(i) for i in range(bin_item.numVersions())]
    
    # Encuentra la version que quieres eliminar por nombre
    version_to_remove = None
    for version in all_versions:
        if version.name() == version_name:
            version_to_remove = version
            break
    
    if version_to_remove:
        # Intenta eliminar la version
        try:
            bin_item.removeVersion(version_to_remove)
            print(f"Removed version '{version_name}'")
        except Exception as e:
            print(f"Error removing version '{version_name}': {e}")
    else:
        print(f"Version '{version_name}' not found")

# Obtiene la secuencia activa y el editor de timeline
seq = hiero.ui.activeSequence()
if seq:  # Asegurate de que hay una secuencia activa
    te = hiero.ui.getTimelineEditor(seq)
    selected_clips = te.selection()

    # Lista para almacenar los nombres de las versiones que existen
    existing_versions = []

    # Iterar sobre los clips seleccionados para listar sus versiones
    for shot in selected_clips:
        bin_item = shot.source().binItem()
        
        # Imprimir todas las versiones hasta llegar a la version maxima
        print(f"Versions for clip {shot.name()}:")
        active_version_name = bin_item.activeVersion().name() if bin_item.activeVersion() else None
        print(f"\n+++++++++++active version name: {active_version_name}") 
        i = 0
        max_version_name = bin_item.maxVersion().name() if bin_item.maxVersion() else None
        print(f"Maximum version name: {max_version_name}")
        
        while True:
            current_version = bin_item.version(i)
            if current_version is None or current_version.name() == max_version_name:
                # Imprime la ultima version antes de salir del bucle
                if current_version is not None:
                    print(f"Version index: {i}, Version name: {current_version.name()}")
                    existing_versions.append(current_version.name())  # Agregar version existente a la lista
                break
            if current_version.name():  # Verificar si el nombre de la version no esta vacio
                print(f"Version index: {i}, Version name: {current_version.name()}")
                existing_versions.append(current_version.name())  # Agregar version existente a la lista
            i += 1

        min_version_name = bin_item.minVersion().name() if bin_item.minVersion() else "None"
        print(f"Minimum version name: {min_version_name}")

        #next_version_name = bin_item.nextVersion().name() if bin_item.nextVersion() else None
        #print(f"next version name: {next_version_name}")      


        #prev_version_name = bin_item.prevVersion().name() if bin_item.prevVersion() else None
        #print(f"prev version name: {prev_version_name}")            



    # Imprimir los nombres de las versiones que existen en la lista
    print("Existing version names:")
    for version_name in existing_versions:
        print(version_name)
        remove_version_by_name(bin_item, version_name)
else:
    print("No active sequence found.")



