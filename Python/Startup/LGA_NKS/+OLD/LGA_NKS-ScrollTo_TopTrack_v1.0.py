import hiero
import time

DEBUG = False

def debug_print(*message):
    if DEBUG:
        print(*message)


def obtener_limites_scrollbar():
    try:
        t = hiero.ui.getTimelineEditor(hiero.ui.activeSequence())
        scrollbar = t.window().children()[3].children()[0].children()[0].children()[7].children()[0]
        
        limite_inferior = scrollbar.minimum()
        limite_superior = scrollbar.maximum()
        
        posicion_actual = scrollbar.value()
        
        debug_print(f"Posición actual del scrollbar: {posicion_actual}")
        debug_print(f"Rango del scrollbar: {scrollbar.minimum()} a {scrollbar.maximum()}")
        debug_print(f"Tamaño de página del scrollbar: {scrollbar.pageStep()}")
        
        return limite_inferior, limite_superior, scrollbar
    
    except Exception as e:
        debug_print(f"Ocurrió un error al obtener los límites: {e}")
        return None, None, None

def scroll_to_position(scrollbar, position):
    try:
        scrollbar.setValue(position)
        debug_print(f"Scrolled to position {position}.")
    except Exception as e:
        debug_print(f"Ocurrió un error al mover el scrollbar: {e}")

# Obtener los límites y el scrollbar
tiempo_inicio = time.time()
limite_inferior, limite_superior, scrollbar = obtener_limites_scrollbar()
tiempo_total = time.time() - tiempo_inicio

if limite_inferior is not None and limite_superior is not None:
    debug_print(f"Límite inferior del scrollbar: {limite_inferior}")
    debug_print(f"Límite superior del scrollbar: {limite_superior}")
    debug_print(f"Tiempo de ejecución: {tiempo_total:.2f} segundos")
    
    # Calcular la nueva posición y mover el scrollbar
    nueva_posicion = limite_inferior + 70
    scroll_to_position(scrollbar, nueva_posicion)
    
    # Verificar la posición final
    posicion_final = scrollbar.value()
    debug_print(f"Posición final del scrollbar: {posicion_final}")