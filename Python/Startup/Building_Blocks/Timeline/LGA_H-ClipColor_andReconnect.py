import hiero.core
import hiero.ui
from PySide2.QtGui import QColor

def change_clip_color(color):
    try:
        seq = hiero.ui.activeSequence()
        if not seq:
            print("No active sequence found.")
            return

        te = hiero.ui.getTimelineEditor(seq)
        selected_clips = te.selection()

        if len(selected_clips) == 0:
            print("*** No clips selected on the track ***")
        else:
            for shot in selected_clips:
                # Obtener el file path del clip seleccionado
                file_path = shot.source().mediaSource().fileinfos()[0].filename()
                print("File path:", file_path)

                # Reemplazar el clip por el del file path
                try:
                    shot.replaceClips(file_path)
                    print("Clip replaced successfully.")
                except:
                    print("Error replacing clip.")

                # Cambiar el color del clip
                shot.source().binItem().setColor(color)
                print(f"Color changed for clip: {shot.name()}")
    except Exception as e:
        print(f"Error changing color: {e}")

# Cambiar el color al mismo que el boton 'Corrections'
color = QColor(46, 119, 212)
change_clip_color(color)
