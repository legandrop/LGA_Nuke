"""
______________________________________________________________________________________________

  LGA_fr_Read_to_FrameRange v1.0 | 2024 | Lega    
  Sets the frame range of the Frame Range node to match the frame range of the selected Read  
______________________________________________________________________________________________

"""

import nuke

def set_frame_range_from_read():
    # Obtener nodos seleccionados
    selected_nodes = nuke.selectedNodes()

    # Filtrar los nodos Read y FrameRange de los nodos seleccionados
    read_nodes = [node for node in selected_nodes if node.Class() == "Read"]
    framerange_nodes = [node for node in selected_nodes if node.Class() == "FrameRange"]

    # Verificar si hay exactamente un nodo Read seleccionado
    if len(read_nodes) != 1:
        nuke.message("You must select exactly one Read node.")
        return

    # Verificar si hay al menos un nodo FrameRange seleccionado
    if not framerange_nodes:
        nuke.message("You must select at least one FrameRange node.")
        return

    # Nodo Read seleccionado
    read_node = read_nodes[0]

    # Obtener el rango de frames del nodo Read
    read_first = read_node['first'].value()
    read_last = read_node['last'].value()

    # Establecer el rango de frames en cada nodo FrameRange seleccionado
    for fr_node in framerange_nodes:
        fr_node['first_frame'].setValue(read_first)
        fr_node['last_frame'].setValue(read_last)

# Ejecutar la funcion
#set_frame_range_from_read()
