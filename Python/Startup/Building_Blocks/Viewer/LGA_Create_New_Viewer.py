import hiero.ui

def open_new_viewer():
    # Intentar obtener la secuencia activa actual
    active_sequence = hiero.ui.activeSequence()
    
    if active_sequence:
        # Si hay una secuencia activa, abrirla en un nuevo viewer
        new_viewer = hiero.ui.openInNewViewer(active_sequence)
        if new_viewer:
            print(f"Se ha abierto un nuevo viewer con la secuencia activa: {active_sequence.name()}")
        else:
            print("No se pudo abrir un nuevo viewer.")
    else:
        # Si no hay una secuencia activa, abrir un viewer vacio
        new_viewer = hiero.ui.openInNewViewer(None)
        if new_viewer:
            print("Se ha abierto un nuevo viewer vacio.")
        else:
            print("No se pudo abrir un nuevo viewer.")

# Llamar a la funcion
open_new_viewer()