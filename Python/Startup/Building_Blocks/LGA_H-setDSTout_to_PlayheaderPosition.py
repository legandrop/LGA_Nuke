import hiero.core
import hiero.ui

def setDstOutToPlayhead(trackItem, playhead_frame):
    # Intentar cambiar el DST Out del clip al frame del playhead
    try:
        trackItem.setTimelineOut(playhead_frame + 1)  # Cambiar el DST Out al frame actual del playhead
        print(f"DST Out changed to {playhead_frame + 1} for clip: {trackItem.name()}")
    except AttributeError:
        print("Unable to set DST Out directly. This method may not exist or be accessible.")

# Obtener la secuencia activa y el editor de linea de tiempo
seq = hiero.ui.activeSequence()
if seq:  # Asegurarse de que hay una secuencia activa
    te = hiero.ui.getTimelineEditor(seq)
    selected_clips = te.selection()
    
    # Obtener la instancia del reproductor y la posicion del playhead
    current_viewer = hiero.ui.currentViewer()
    player = current_viewer.player() if current_viewer else None
    playhead_frame = player.time() if player else None

    # Cambiar el DST Out de cada clip seleccionado al frame del playhead
    if selected_clips and playhead_frame is not None:
        for shot in selected_clips:
            setDstOutToPlayhead(shot, playhead_frame)
    else:
        print("No clips selected or playhead position unavailable.")
else:
    print("No active sequence found.")
