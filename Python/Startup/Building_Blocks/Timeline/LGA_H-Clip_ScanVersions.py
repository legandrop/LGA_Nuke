import hiero.core
import re

# Listas para almacenar los nombres de las versiones existentes y nuevas
existing_versions_list = []
new_versions_info = []

# Obtiene la secuencia activa y el editor de timeline
seq = hiero.ui.activeSequence()
if seq:  # Asegurarse de que hay una secuencia activa
    te = hiero.ui.getTimelineEditor(seq)
    selected_items = te.selection()
    project = hiero.core.projects()[0]


    for item in selected_items:
        bin_item = item.source().binItem()
        if item.source().mediaSource().isMediaPresent():
            current_version = bin_item.activeVersion()
            existing_versions = list(bin_item.items())  # Obtiene todas las versiones existentes antes de anadir nuevas

            # Imprimir nombres de las versiones actuales con su indice
            print("Existing versions:")
            for index, version in enumerate(existing_versions):
                existing_version_name = version.name()
                existing_versions_list.append((existing_version_name, index))  # Agregar el nombre de la version existente y su indice a la lista
                print(f"- {existing_version_name} ({index})")

            # Imprimir el nombre de la version activa con su indice
            active_index = existing_versions.index(current_version)
            print(f"Active version: {current_version.name()} ({active_index})")

            # Detectar nuevas versiones
            scanner = hiero.core.VersionScanner()
            new_versions_paths = scanner.findNewVersions(current_version)
            print("Found versions names and paths:")
            for new_version_path in new_versions_paths:
                new_version = hiero.core.Version(new_version_path)
                new_version_name = new_version.name()
                new_versions_info.append((new_version_name, new_version_path))  # Agregar el nombre y path de la nueva version a la lista
                print(f"- {new_version_name} ({new_version_path})")

else:
    print("No active sequence found.")

# Imprimir la lista de nombres de las versiones existentes al final
print("Existing versions list:")
for version_info in existing_versions_list:
    version_name, index = version_info
    print(f"{version_name} ({index})")

# Imprimir la lista de nombres y paths de nuevas versiones al final
print("New versions list with names and paths:")
for version_info in new_versions_info:
    version_name, version_path = version_info
    print(f"{version_name} ({version_path})")

# Comparar la version activa con las nuevas versiones
matching_versions = [version_info for version_info in new_versions_info if version_info[0] == current_version.name()]

# Imprimir los nombres que coinciden en ambas listas con su indice
print("Matching versions with index:")
for version_info in matching_versions:
    version_name, version_path = version_info
    # Cambio aqui para usar el indice de la version activa
    print(f"{version_name} ({version_path}) ({active_index})")

# Obtener las versiones existentes y nuevas como conjuntos
existing_versions_set = set([version_info[0] for version_info in existing_versions_list])
new_versions_set = set([version_info[0] for version_info in new_versions_info])

# Versiones nuevas que no estan en las existentes
unmatched_new_versions = new_versions_set - existing_versions_set

def extract_version_number(name):
    match = re.search(r'_v(\d+)', name)
    return int(match.group(1)) if match else None

# Preparar lista de todas las versiones con numero de version
all_versions_with_numbers = [(name, extract_version_number(name), path) for name, path in new_versions_info]
all_versions_with_numbers += [(name, extract_version_number(name), None) for name, index in existing_versions_list]

# Ordenar por numero de version
all_versions_sorted = sorted(all_versions_with_numbers, key=lambda x: x[1])

# Encontrar indice de la version activa en la lista ordenada
active_version_index = next((i for i, v in enumerate(all_versions_sorted) if v[0] == current_version.name()), None)

# Asignar indices a las versiones no coincidentes
indexed_unmatched_new_versions = []
for i, (name, version_number, path) in enumerate(all_versions_sorted):
    if name in unmatched_new_versions:
        relative_index = i - active_version_index  # Calcula indice relativo
        indexed_unmatched_new_versions.append((name, path, relative_index))

# Imprimir las unmatched new versions con numeros de indice asignados
print("Unmatched new versions with assigned indices:")
for name, path, index in indexed_unmatched_new_versions:
    print(f"{name} ({path}) ({index})")

# Dividir las versiones en ascendentes y descendentes respecto a la version activa
ascendentes = []
descendentes = []

for name, version_number, path in all_versions_sorted:
    if name in unmatched_new_versions:
        relative_index = version_number - extract_version_number(current_version.name())
        if relative_index > 0:  # Ascendente
            ascendentes.append((name, path, relative_index))
        elif relative_index < 0:  # Descendente
            descendentes.append((name, path, relative_index))

# Ordenar ascendentes y descendentes para asegurar el orden correcto
ascendentes.sort(key=lambda x: x[2])  # Ordena por indice relativo
descendentes.sort(key=lambda x: x[2], reverse=True)  # Ordena por indice relativo, pero en orden descendente

# Imprimir las versiones ascendentes y descendentes
print("Ascendentes:")
for name, path, index in ascendentes:
    print(f"{name} ({path}) ({index})")

print("Descendentes:")
for name, path, index in descendentes:
    print(f"{name} ({path}) ({index})")

project.beginUndo("Update Versions")

# Imprimir la lista de nombres de las versiones existentes que no son la version activa
print("Existing versions that are not the active version:")
for version_info in existing_versions_list:
    version_name, index = version_info
    if version_name != current_version.name():
        print(f"{version_name} (Index: {index})")

# Eliminar las versiones que no son la version activa
print("Removing non-active versions:")
for version in existing_versions:
    if version.name() != current_version.name():
        bin_item.removeVersion(version)
        print(f"Removed version: {version.name()}")

# Funcion para extraer el numero de version del nombre de la version
def extract_version_number(name):
    match = re.search(r'_v(\d+)', name)
    return int(match.group(1)) if match else None

# Ordenar las found versions por numero de version
sorted_new_versions_info = sorted(new_versions_info, key=lambda x: extract_version_number(x[0]))


if len(sorted_new_versions_info) > 1:  # Verificar si hay mas de una version encontrada
    first_version_info = sorted_new_versions_info[0]  # Obtener la primera version de la lista ordenada
    first_version_name, first_version_path = first_version_info
    
    if first_version_name != current_version.name():  # Chequear que no matchee con la version activa actual
        # Crear el objeto Version con el path especifico y anadirlo
        first_new_version = hiero.core.Version(first_version_path)
        bin_item.addVersion(first_new_version)
        print(f"Added new version: {first_version_name}")

        # Seleccionar la version recien agregada como la version activa
        # Como acabamos de anadirla, estara en el indice 1
        bin_item.setActiveVersion(bin_item.items()[1])
        print(f"Set version {first_version_name} as active version at index 1.")
else:
    print("No action needed, only one or no version found.")


# Acceder a la version en el indice 0
version_to_remove = bin_item.items()[0]

# Eliminar la version en el indice 0 
#bin_item.removeVersion(version_to_remove) SE CUELGAAAAAA!!!!!SE CUELGAAAAAA!!!!!SE CUELGAAAAAA!!!!!SE CUELGAAAAAA!!!!!
print(f"Removed version at index 0: {version_to_remove.name()}")
project.endUndo()


"""
# Anadir las found versions ordenadas
print("Adding found versions in order:")
for version_info in sorted_new_versions_info:
    version_name, version_path = version_info
    new_version = hiero.core.Version(version_path)  # Crear el objeto Version con el path especifico
    bin_item.addVersion(new_version)  # Anadir la version al bin_item
    print(f"Added new version: {version_name}")


# Identificar el indice de la version del mismo nombre que la version activa, pero que no sea la activa (indice 0)
active_version_name = current_version.name()  # Nombre de la version activa
duplicate_version_index = None  # Inicializar la variable para almacenar el indice de la version duplicada

for index, version in enumerate(existing_versions):
    if version.name() == active_version_name and index != 0:
        duplicate_version_index = index  # Encontrar el indice de la version duplicada
        break  # Salir del bucle una vez encontrada la version

if duplicate_version_index is not None:
    # Acceder a la version duplicada usando el indice encontrado y establecerla como la version activa
    duplicate_version = bin_item.items()[duplicate_version_index]
    bin_item.setActiveVersion(duplicate_version)
    print(f"Set version {duplicate_version.name()} as active version.")
else:
    print("No duplicate version found to set as active.")

# Acceder a la version en el indice 0
version_to_remove = bin_item.items()[0]

# Eliminar la version en el indice 0
bin_item.removeVersion(version_to_remove)
print(f"Removed version at index 0: {version_to_remove.name()}")

"""