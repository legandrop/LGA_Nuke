"""
_____________________________________________________________________________________________

  LGA_fr_TimeClip_to_Write v1.0 | Lega
  Sets the frame range of the write noded to match the frame range of the selected TimeClip
_____________________________________________________________________________________________

"""

import nuke


def set_write_from_timeclip():
    # Obtener nodos seleccionados
    selected_nodes = nuke.selectedNodes()

    # Verificar si solo hay dos nodos seleccionados
    if len(selected_nodes) != 2:
        nuke.message("You must select exactly two nodes: a Write and a TimeClip.")
        return

    # Inicializar variables para los nodos
    write_node = None
    timeclip_node = None

    # Identificar los nodos
    for node in selected_nodes:
        if node.Class() == "Write":
            write_node = node
        elif node.Class() == "TimeClip":
            timeclip_node = node

    # Verificar si ambos nodos necesarios estan presentes
    if not write_node or not timeclip_node:
        nuke.message("You must select exactly one Write node and one TimeClip node.")
        return

    # Copiar el rango de frames del TimeClip al Write
    write_node["use_limit"].setValue(True)
    write_node["first"].setValue(timeclip_node["first"].value())
    write_node["last"].setValue(timeclip_node["last"].value())


# set_write_from_timeclip()
