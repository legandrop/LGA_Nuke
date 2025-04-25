"""
___________________________________________________________________________

  LGA_renameWritesFromReads v1.0 | Lega
  Renames Write nodes based on the filename of their connected Read nodes
___________________________________________________________________________

"""

import re
import nuke
import os


def renameWrite():
    # Funcion para obtener el nombre del archivo sin extension a partir de la ruta de archivo proporcionada
    def get_file_name_without_extension(file_path):
        # Usar os.path.basename para obtener el nombre del archivo de la ruta
        file_name_with_extension = os.path.basename(file_path)
        # Usar os.path.splitext para dividir el nombre del archivo y la extension
        file_name, file_extension = os.path.splitext(file_name_with_extension)
        return file_name

    # Funcion para eliminar el relleno despues del ultimo guion bajo
    def remove_padding(file_name):
        if "_" in file_name:
            return "_".join(
                file_name.split("_")[:-1]
            )  # Unir todas las partes excepto la ultima despues del ultimo guion bajo
        else:
            return file_name

    # Funcion para encontrar el nodo Read mas alto en las dependencias ascendentes del nodo
    def find_top_read_node(node):
        if node.Class() == "Read":
            return node

        for input_node in node.dependencies():
            return find_top_read_node(input_node)

        return None

    # Obtener los nodos Write seleccionados
    write_nodes = nuke.selectedNodes("Write")

    if not write_nodes:
        nuke.message("`Selecciona al menos un nodo Write")
    else:
        for write_node in write_nodes:
            # Encontrar el nodo Read mas alto conectado a cada nodo Write
            read_node = find_top_read_node(write_node)

            if not read_node:
                nuke.message(
                    "No hay un nodo Read conectado a ninguno de los nodos Write seleccionados"
                )
            else:
                # Obtener la ruta de archivo del nodo Read y extraer el nombre del archivo sin extension
                file_path = read_node["file"].value()
                file_name = get_file_name_without_extension(file_path)
                file_name_no_padding = remove_padding(file_name)

                # Renombrar el nodo Write con el nombre de archivo extraido
                write_node.setName(file_name_no_padding)
