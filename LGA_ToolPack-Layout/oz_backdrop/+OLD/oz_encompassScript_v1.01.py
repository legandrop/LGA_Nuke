# Mod Lega v1.0 para tener en cuenta el tamano y cantidad de lineas del texto

# Variable global para activar o desactivar los prints
DEBUG = False

def debug_print(*message):
    if DEBUG:
        print(*message)
        

# Definir la funcion para calcular el tamano adicional necesario para el texto
def calculate_extra_top(text, font_size):
    """
    Calcula el tamano adicional necesario para el texto en funcion del tamano de la fuente y el numero de lineas.
    """
    line_count = text.count('\n') + 2  # Contar las lineas en el texto
    text_height = font_size * line_count  # Calcular la altura total del texto
    return text_height

# Obtener el nodo actual y el valor de padding
this = nuke.thisNode()
padding = this['sides'].getValue()
if this.isSelected:
    this.setSelected(False)
selNodes = nuke.selectedNodes()

# Definir la funcion para comprobar si un nodo esta dentro del backdrop
def nodeIsInside(node, backdropNode):
    # Returns true if node geometry is inside backdropNode otherwise returns false
    topLeftNode = [node.xpos(), node.ypos()]
    topLeftBackDrop = [backdropNode.xpos(), backdropNode.ypos()]
    bottomRightNode = [node.xpos() + node.screenWidth(), node.ypos() + node.screenHeight()]
    bottomRightBackdrop = [backdropNode.xpos() + backdropNode.screenWidth(), backdropNode.ypos() + backdropNode.screenHeight()]
                    
    topLeft = ( topLeftNode[0] >= topLeftBackDrop[0] ) and ( topLeftNode[1] >= topLeftBackDrop[1] )
    bottomRight = ( bottomRightNode[0] <= bottomRightBackdrop[0] ) and ( bottomRightNode[1] <= bottomRightBackdrop[1] )
                    
    return topLeft and bottomRight

if not selNodes:
    nuke.message('Some nodes should be selected')
else:
    # Obtener el texto y tamano de fuente del backdrop actual
    user_text = this['label'].getValue()
    note_font_size = this['note_font_size'].getValue()
    
    # Calcular los limites para el nodo de fondo
    bdX = min([node.xpos() for node in selNodes])
    bdY = min([node.ypos() for node in selNodes])
    bdW = max([node.xpos() + node.screenWidth() for node in selNodes]) - bdX
    bdH = max([node.ypos() + node.screenHeight() for node in selNodes]) - bdY

    # Calcular el tamano adicional necesario para el texto
    extra_top = calculate_extra_top(user_text, note_font_size)
    debug_print(f"extra_top encompass: {extra_top}")
    
    # Expandir los limites para dejar un pequeno borde. Los elementos son desplazamientos para los bordes izquierdo, superior, derecho e inferior respectivamente
    left = -padding
    debug_print(f"left nuevo encompass: {left}")
    top = -(padding + extra_top)
    debug_print(f"top nuevo encompass: {top}")
    right = padding
    debug_print(f"right nuevo encompass: {right}")
    bottom = padding
    debug_print(f"bottom nuevo encompass: {bottom}")

    bdX += left
    bdY += top
    bdW += (right - left)
    bdH += (bottom - top)


    zOrder = 0
    selectedBackdropNodes = nuke.selectedNodes("BackdropNode")

    # Si hay nodos de fondo seleccionados, colocar el nuevo inmediatamente detras del mas lejano
    if len(selectedBackdropNodes):
        zOrder = min([node.knob("z_order").value() for node in selectedBackdropNodes]) - 1
    else:
        # De lo contrario (sin fondo en la seleccion) encontrar el fondo mas cercano si existe y colocar el nuevo frente a el
        nonSelectedBackdropNodes = nuke.allNodes("BackdropNode")
        for nonBackdrop in selNodes:
            for backdrop in nonSelectedBackdropNodes:
                if nodeIsInside(nonBackdrop, backdrop):
                    zOrder = max(zOrder, backdrop.knob("z_order").value() + 1)


    this['xpos'].setValue(bdX)
    this['bdwidth'].setValue(bdW)
    this['ypos'].setValue(bdY)
    this['bdheight'].setValue(bdH)
    this['z_order'].setValue(zOrder)
