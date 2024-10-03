import hiero.core
import hiero.ui
import os


# Obtener la secuencia activa y el editor de linea de tiempo
seq = hiero.ui.activeSequence()
if seq:  # Asegurarse de que hay una secuencia activa
    te = hiero.ui.getTimelineEditor(seq)
    selected_clips = te.selection()

    # Iterar sobre los clips seleccionados para hacer el "reveal in explorer"
    for shot in selected_clips:
        file_path = shot.source().mediaSource().fileinfos()[0].filename()
        print("Original file path:", file_path)

        # Abre el explorador de archivos en el directorio del clip
        try:
            os.startfile(os.path.dirname(file_path))
            print("Revealed in explorer successfully.")
        except:
            print("Error revealing in explorer.")
else:
    print("No active sequence found.")
