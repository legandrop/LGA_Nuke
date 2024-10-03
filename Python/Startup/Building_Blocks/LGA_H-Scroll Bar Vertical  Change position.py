def scroll_to_position(position):
    try:
        # Obtener el editor de la secuencia activa
        t = hiero.ui.getTimelineEditor(hiero.ui.activeSequence())
        
        # Navegar directamente en la jerarquía de widgets como indicó soporte
        t.window().children()[3].children()[0].children()[0].children()[7].children()[0].setValue(position)
        
        print(f"Scrolled to position {position}.")
        
    except Exception as e:
        print(f"An error occurred: {e}")

# Variable para la posición del scroll
scroll_position = -160

# Llamar a la función con la posición deseada
scroll_to_position(scroll_position)
