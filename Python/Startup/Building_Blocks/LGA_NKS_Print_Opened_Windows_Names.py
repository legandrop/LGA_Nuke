# Imprime los nombres de todas las ventanas abiertas

import hiero.ui

def listAllWindows():
    """
    Imprime los titulos de todas las ventanas disponibles en la UI de Hiero.
    """
    window_manager = hiero.ui.windowManager()
    windows = window_manager.windows()
    
    print("Ventanas disponibles:")
    for window in windows:
        print(window.windowTitle())

# Ejecutar la funcion para listar todas las ventanas
listAllWindows()
