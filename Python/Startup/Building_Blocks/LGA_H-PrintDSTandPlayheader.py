import hiero.core
import hiero.ui

def getDstIn(trackItem):
    return trackItem.timelineIn()  # Posicion de entrada del clip en el timeline

def getDstOut(trackItem):
    return trackItem.timelineOut()  # Posicion de salida del clip en el timeline

# Obtener la secuencia activa y el editor de linea de tiempo
seq = hiero.ui.activeSequence()
if seq:  # Asegurarse de que hay una secuencia activa
    te = hiero.ui.getTimelineEditor(seq)
    selected_clips = te.selection()
    
    # Obtener la instancia del reproductor y la posicion del playhead
    current_viewer = hiero.ui.currentViewer()
    player = current_viewer.player() if current_viewer else None
    playhead_frame = player.time() if player else "No player available"

    # Iterar sobre los clips seleccionados para imprimir la informacion deseada
    for shot in selected_clips:
        if isinstance(shot, hiero.core.TrackItem):
            dstIn = getDstIn(shot)
            dstOut = getDstOut(shot)
            print(f"Clip: {shot.name()} - Frame number at DST In: {dstIn} - Frame number at DST Out: {dstOut} - Playhead at Frame: {playhead_frame}")
        else:
            print("Selected item is not a track item.")
else:
    print("No active sequence found.")
