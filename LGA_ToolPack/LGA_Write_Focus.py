"""
____________________________________________________________________________________

  LGA_Write_Focus v1.2 | 2025 | Lega  
  Script para buscar, enfocar, centrar y hacer zoom a un nodo Write_Pub
____________________________________________________________________________________
"""

import nuke
import time

def main():
    """
    Busca un nodo Write llamado Write_Pub, lo centra en el DAG, 
    aplica un zoom fijo y abre su panel de propiedades.
    Si no encuentra el nodo, muestra un mensaje de error.
    Incluye medición de tiempo para cada proceso.
    """
    tiempo_inicio_total = time.time()
    
    # Valor de zoom fijo que queremos aplicar
    ZOOM_LEVEL = 1.5
    
    # Método optimizado: buscar directamente por nombre
    tiempo_inicio_busqueda = time.time()
    write_pub = nuke.toNode('Write_Pub')
    tiempo_fin_busqueda = time.time()
    print(f"Tiempo de búsqueda: {(tiempo_fin_busqueda - tiempo_inicio_busqueda) * 1000:.2f} ms")
    
    # Si encontramos el nodo, lo seleccionamos, centramos y mostramos sus propiedades
    if write_pub:
        # Verificamos que sea del tipo correcto
        if write_pub.Class() != 'Write':
            nuke.message("Se encontró un nodo llamado 'Write_Pub' pero no es del tipo Write.")
            return
            
        # Deseleccionamos todos los nodos
        tiempo_inicio_deseleccion = time.time()
        for n in nuke.selectedNodes():
            n['selected'].setValue(False)
        tiempo_fin_deseleccion = time.time()
        print(f"Tiempo de deselección: {(tiempo_fin_deseleccion - tiempo_inicio_deseleccion) * 1000:.2f} ms")
        
        # Seleccionamos el nodo Write_Pub
        tiempo_inicio_seleccion = time.time()
        write_pub['selected'].setValue(True)
        tiempo_fin_seleccion = time.time()
        print(f"Tiempo de selección: {(tiempo_fin_seleccion - tiempo_inicio_seleccion) * 1000:.2f} ms")
        
        # Calculamos el centro del nodo Write_Pub
        tiempo_inicio_calculo = time.time()
        xCenter = write_pub.xpos() + write_pub.screenWidth()/2
        yCenter = write_pub.ypos() + write_pub.screenHeight()/2
        tiempo_fin_calculo = time.time()
        print(f"Tiempo de cálculo de centro: {(tiempo_fin_calculo - tiempo_inicio_calculo) * 1000:.2f} ms")
        
        # Centramos y aplicamos zoom fijo
        tiempo_inicio_zoom = time.time()
        nuke.zoom(ZOOM_LEVEL, [xCenter, yCenter])
        tiempo_fin_zoom = time.time()
        print(f"Tiempo de zoom: {(tiempo_fin_zoom - tiempo_inicio_zoom) * 1000:.2f} ms")
        
        # Mostramos el panel de propiedades
        tiempo_inicio_panel = time.time()
        write_pub.showControlPanel()
        tiempo_fin_panel = time.time()
        print(f"Tiempo de mostrar panel: {(tiempo_fin_panel - tiempo_inicio_panel) * 1000:.2f} ms")
        
        tiempo_fin_total = time.time()
        print(f"Tiempo total de ejecución: {(tiempo_fin_total - tiempo_inicio_total) * 1000:.2f} ms")
        print("Nodo Write_Pub encontrado, centrado y enfocado en el panel de propiedades.")
    else:
        # Como alternativa, podemos buscar en nodos Write si no se encuentra directamente
        # pero solo si hay pocos nodos Write para no penalizar el rendimiento
        nodos_write = nuke.allNodes('Write')
        if len(nodos_write) < 10:  # Solo buscar si hay pocos nodos Write
            for node in nodos_write:
                if node.name() == 'Write_Pub':
                    main()  # Volver a ejecutar la función ahora que se ha creado el nodo
                    return
                    
        tiempo_fin_total = time.time()
        print(f"Tiempo total de ejecución (error): {(tiempo_fin_total - tiempo_inicio_total) * 1000:.2f} ms")
        nuke.message("No se encontró ningún nodo Write llamado 'Write_Pub' en el script actual.")

# Ejecutar la función cuando se importe este script
#main()