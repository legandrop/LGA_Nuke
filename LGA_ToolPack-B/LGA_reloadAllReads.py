"""
________________________________________

  LGA_reloadAllReads v1.0 | 2024 | Lega  
________________________________________

"""

import nuke

def main():
    # Obtener todos los nodos del proyecto
    all_nodes = nuke.allNodes()

    # Filtrar solo los nodos de clase Read y ejecutar el comando reload
    for node in all_nodes:
        if node.Class() == 'Read':
            node['reload'].execute()

# Ejecutar la funcion
#main()
