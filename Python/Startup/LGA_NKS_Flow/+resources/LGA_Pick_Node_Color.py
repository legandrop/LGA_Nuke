import nuke

# Funcion para convertir el valor de color en formato RGB
def convert_color(value):
    r = int((value & 0xff000000) >> 24)
    g = int((value & 0x00ff0000) >> 16)
    b = int((value & 0x0000ff00) >> 8)
    return r, g, b

# Obtener el nodo seleccionado
node = nuke.selectedNode()

# Verificar si el nodo tiene un valor de color
if 'tile_color' in node.knobs():
    # Obtener el valor del color
    color_value = node['tile_color'].value()
    
    # Si el color es 0, significa que usa el color por defecto
    if color_value == 0:
        # Obtener el tipo de nodo
        node_class = node.Class()
        
        # Obtener el color por defecto desde las preferencias de Nuke
        default_color_value = nuke.defaultNodeColor(node_class)
        r, g, b = convert_color(default_color_value)
    else:
        # Convertir el valor del color en RGB
        r, g, b = convert_color(color_value)
    
    # Imprimir el color en formato RGB
    print("Color del nodo seleccionado (RGB): ({}, {}, {})".format(r, g, b))
else:
    print("El nodo seleccionado no tiene un valor de color.")
