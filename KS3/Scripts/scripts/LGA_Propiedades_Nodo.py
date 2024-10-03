import nuke

# Obtener el nodo seleccionado
selected_node = nuke.selectedNode()

# Imprimir el nombre del nodo
print(f"Nombre del nodo seleccionado: {selected_node.name()}")

# Imprimir las propiedades del nodo
print("Propiedades del nodo:")
for knob in selected_node.knobs():
    print(f"- {knob}")
