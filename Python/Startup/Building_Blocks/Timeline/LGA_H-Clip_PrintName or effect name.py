import hiero.core
import hiero.ui
import os

# Obtener la secuencia activa y el editor de línea de tiempo
seq = hiero.ui.activeSequence()
if seq:  # Asegurarse de que hay una secuencia activa
    te = hiero.ui.getTimelineEditor(seq)
    selected_clips = te.selection()

    # Iterar sobre los elementos seleccionados
    if selected_clips:
        for clip in selected_clips:
            # Verificar si el elemento es un clip de video o un efecto
            if isinstance(clip, hiero.core.EffectTrackItem):
                # Es un efecto, imprimir su nombre
                print("Effect name:", clip.name())
            else:
                # Es un clip de video, imprimir el nombre del archivo
                file_path = clip.source().mediaSource().fileinfos()[0].filename()
                print("Clip name:", os.path.basename(file_path))
    else:
        print("No clips selected on the timeline.")
else:
    print("No active sequence found.")
