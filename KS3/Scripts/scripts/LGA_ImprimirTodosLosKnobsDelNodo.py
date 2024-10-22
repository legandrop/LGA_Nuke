import nuke

def print_all_knobs(node):
    """Imprime todos los knobs del nodo, organizados por tabs"""
    print(f"Knobs en el nodo {node.name()}:")
    
    current_tab = "Main"
    for i, knob in enumerate(node.allKnobs()):
        if isinstance(knob, nuke.Tab_Knob):
            current_tab = knob.name()
            print(f"\nTab: {current_tab}")
        else:
            print(f"{i}: {knob.name()} ({knob.Class()}) - Tab: {current_tab}")

# Obtener el nodo DasGrain seleccionado
selected_nodes = nuke.selectedNodes('Group')
dasgrain_node = next((node for node in selected_nodes if node.name().startswith('DasGrain')), None)

if dasgrain_node:
    print_all_knobs(dasgrain_node)
else:
    print("No se encontró un nodo DasGrain seleccionado.")