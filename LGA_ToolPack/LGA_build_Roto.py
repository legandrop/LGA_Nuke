"""
_____________________________________________________________________________

  LGA_build_Roto v1.0 | 2024 | Lega  
  
  Crea nodos Roto, Blur y Dot conectados al input 1 del nodo seleccionado.
  Requiere que haya un nodo seleccionado para funcionar.
  Diseñado para añadir rápidamente máscaras a nodos existentes.
_____________________________________________________________________________

"""

import nuke
from PySide2.QtGui import QCursor, QMouseEvent
from PySide2.QtWidgets import QApplication
from PySide2.QtCore import Qt, QEvent, QPoint

def get_common_variables():
    distanciaY = 30  # Espacio libre entre nodos en la columna derecha
    distanciaX = 130
    dot_width = int(nuke.toNode("preferences")['dot_node_scale'].value() * 12)
    return distanciaX, distanciaY, dot_width

def get_selected_node():
    try:
        selected_node = nuke.selectedNode()
        return selected_node
    except ValueError:
        return None

def create_roto_chain():
    """Crea una cadena de nodos Roto, Blur y Dot conectada al nodo seleccionado"""
    # Obtener las variables comunes
    distanciaX, distanciaY, dot_width = get_common_variables()

    # Obtener el nodo seleccionado
    selected_node = get_selected_node()
    
    # Si no hay nodo seleccionado, no hacemos nada
    if not selected_node:
        nuke.message("Selecciona un nodo primero")
        return
    
    # Deseleccionar todos los nodos existentes
    for n in nuke.allNodes():
        n.setSelected(False)

    # Crear un Dot al lado del nodo seleccionado (a la misma altura)
    dot_right = nuke.nodes.Dot()
    dot_right.setXpos(selected_node.xpos() + distanciaX + (selected_node.screenWidth() // 2) - (dot_width // 2))
    # Posicionamos el dot aproximadamente a la altura del centro del nodo seleccionado
    dot_right.setYpos(selected_node.ypos() + (selected_node.screenHeight() // 2) - (dot_right.screenHeight() // 2))

    # Crear un nodo Blur arriba del Dot
    blur = nuke.nodes.Blur()
    blur.setXpos(dot_right.xpos() - (blur.screenWidth() // 2) + (dot_width // 2))
    blur.setYpos(dot_right.ypos() - blur.screenHeight() - distanciaY)
    blur['channels'].setValue("alpha")
    blur['size'].setValue(7)
    blur['label'].setValue("[value size]")
    
    # Conectar el blur al dot
    dot_right.setInput(0, blur)

    # Crear un nodo Roto arriba del Blur
    roto = nuke.nodes.Roto()
    roto.setXpos(blur.xpos())
    roto.setYpos(blur.ypos() - roto.screenHeight() - distanciaY)
    
    # Conectar el roto al blur
    blur.setInput(0, roto)

    # Abrir las propiedades del nodo Roto
    nuke.show(roto)

    # Conectar el dot al input 1 del nodo seleccionado
    selected_node.setInput(1, dot_right)

    # Al final de la función, seleccionar solo los nuevos nodos
    roto['selected'].setValue(True)
    blur['selected'].setValue(True)
    dot_right['selected'].setValue(True)

def main():
    create_roto_chain()

# Ejecuta la funcion
#main()
