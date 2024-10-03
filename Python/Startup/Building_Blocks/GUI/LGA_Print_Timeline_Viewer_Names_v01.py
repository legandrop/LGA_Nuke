import hiero.core
import hiero.ui

def print_active_timeline_and_viewer():
    # Obtener el timeline activo
    active_sequence = hiero.ui.activeSequence()
    if active_sequence:
        print(f"Timeline activo: {active_sequence.name()}")
    else:
        print("No hay un timeline activo")
    
    # Obtener el viewer activo
    active_viewer = hiero.ui.currentViewer()
    if active_viewer:
        current_sequence = active_viewer.player(0).sequence()
        if current_sequence:
            print(f"Secuencia en el Viewer activo: {current_sequence.name()}")
        else:
            print("No hay una secuencia en el Viewer activo")
    else:
        print("No hay un Viewer activo")

# Llamar a la funcion
print_active_timeline_and_viewer()