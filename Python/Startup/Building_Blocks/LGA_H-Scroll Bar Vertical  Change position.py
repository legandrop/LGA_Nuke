def scroll_to_position(position):
    try:
        # Obtener el editor de la secuencia activa
        t = hiero.ui.getTimelineEditor(hiero.ui.activeSequence())
        
        # Navegar directamente en la jerarquia de widgets como indico soporte
        t.window().children()[3].children()[0].children()[0].children()[7].children()[0].setValue(position)
        
        print(f"Scrolled to position {position}.")
        
    except Exception as e:
        print(f"An error occurred: {e}")

# Variable para la posicion del scroll
scroll_position = -160

# Llamar a la funcion con la posicion deseada
scroll_to_position(scroll_position)
