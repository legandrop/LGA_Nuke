import hiero.core
import hiero.ui
from PySide2.QtWidgets import QMessageBox

def close_and_reopen_active_sequence():
    """
    Cierra el viewer activo y reabre la misma secuencia en un nuevo timeline viewer.
    """
    # Obtener el viewer activo
    active_viewer = hiero.ui.currentViewer()
    if not active_viewer:
        print("No hay un Viewer activo para cerrar")
        return

    # Guardar la informacion de la secuencia activa
    active_sequence = active_viewer.player(0).sequence()
    if not active_sequence:
        print("No hay una secuencia activa en el Viewer")
        return

    sequence_name = active_sequence.name()
    current_time = active_viewer.player(0).time()

    # Cerrar el viewer activo
    viewer_window = active_viewer.window()
    if viewer_window:
        viewer_window.close()
        print(f"Se ha cerrado el Viewer activo con la secuencia: {sequence_name}")
        
        # Mostrar mensaje
        msg_box = QMessageBox()
        msg_box.setText("El Viewer ha sido cerrado.")
        msg_box.setInformativeText("Presiona OK para reabrir la secuencia en un nuevo timeline viewer.")
        msg_box.setStandardButtons(QMessageBox.Ok)
        msg_box.exec_()
    else:
        print("No se pudo obtener la ventana del Viewer activo")
        return

    # Abrir la secuencia en un nuevo timeline
    new_timeline = hiero.ui.openInTimeline(active_sequence)
    if new_timeline:
        print(f"Se ha abierto la secuencia '{sequence_name}' en un nuevo timeline viewer.")
        
        # Intentar establecer el tiempo en el nuevo viewer (si se abrio automaticamente)
        new_viewer = hiero.ui.currentViewer()
        if new_viewer:
            new_viewer.setTime(current_time)
            print(f"Se ha establecido el tiempo en el nuevo viewer.")
    else:
        print(f"No se pudo abrir un nuevo timeline para la secuencia '{sequence_name}'.")

# Llamar a la funcion para cerrar el viewer activo y reabrir la misma secuencia
close_and_reopen_active_sequence()