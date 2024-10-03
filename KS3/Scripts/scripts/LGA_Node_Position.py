import nuke

def obtener_posicion_y_nodo_seleccionado():
    node = nuke.selectedNode()  # Obtener el nodo seleccionado actualmente
    if node:
        pos_y = node['ypos'].value() + node.screenHeight() / 2  # Obtener la posicion en Y del nodo
        print(f"Posicion Y del nodo {node.name()}: {pos_y}")
    else:
        print("No hay ningun nodo seleccionado.")

# Llamar a la funcion para imprimir la posicion Y del nodo seleccionado
obtener_posicion_y_nodo_seleccionado()
