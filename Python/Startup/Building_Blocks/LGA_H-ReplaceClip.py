import hiero.core
import hiero.ui


# Obtener la secuencia activa y el editor de linea de tiempo
seq = hiero.ui.activeSequence()
if seq:  # Asegurarse de que hay una secuencia activa
    te = hiero.ui.getTimelineEditor(seq)
    selected_clips = te.selection()

    # Iterar sobre los clips seleccionados para reemplazarlos
    for shot in selected_clips:
        file_path = shot.source().mediaSource().fileinfos()[0].filename()
        print("File path:", file_path)

        # Reemplazar el clip por el del path
        try:
            shot.replaceClips(file_path)
            print("Clip replaced successfully.")
        except:
            print("Error replacing clip.")
else:
    print("No active sequence found.")
