import hiero.core
import hiero.ui

def close_and_reopen_active_sequence():
    """
    Cierra el viewer activo y reabre la misma secuencia en un nuevo timeline viewer.
    Luego, cambia la visualizacion del viewer a Rec.709.
    """
    # Obtener el viewer activo
    active_viewer = hiero.ui.currentViewer()
    if not active_viewer:
        return

    # Guardar la informacion de la secuencia activa
    active_sequence = active_viewer.player(0).sequence()
    if not active_sequence:
        return

    current_time = active_viewer.player(0).time()

    # Cerrar el viewer activo
    viewer_window = active_viewer.window()
    if viewer_window:
        viewer_window.close()

    # Abrir la secuencia en un nuevo timeline
    new_timeline = hiero.ui.openInTimeline(active_sequence)
    if new_timeline:
        # Intentar establecer el tiempo en el nuevo viewer (si se abrio automaticamente)
        new_viewer = hiero.ui.currentViewer()
        if new_viewer:
            new_viewer.setTime(current_time)
            # Cambiar el viewer a Rec.709
            new_viewer.player().setLUT('ACES/Rec.709')

# Llamar a la funcion para cerrar el viewer activo y reabrir la misma secuencia
close_and_reopen_active_sequence()
