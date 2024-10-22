"""
______________________________________________________________________

  LGA_NKS_Reduce_SeqWin v1.0 - 2024 - Lega
  Reduce el tamaño del panel lateral del timeline editor de Hiero
______________________________________________________________________

"""

import hiero.ui
from PySide2 import QtWidgets

# Tamaño deseado para el panel lateral (en píxeles)
PANEL_LATERAL_TAMANO = 2700

def main():
    timeline_editor = hiero.ui.getTimelineEditor(hiero.ui.activeSequence())
    if not timeline_editor:
        print("No se pudo obtener el editor de línea de tiempo activo.")
        return

    window = timeline_editor.window()
    main_splitter = window.findChild(QtWidgets.QSplitter)

    if main_splitter:
        sizes = main_splitter.sizes()
        if len(sizes) == 2:
            nuevo_tamano = [sizes[0] + sizes[1] - PANEL_LATERAL_TAMANO, PANEL_LATERAL_TAMANO]
            main_splitter.setSizes(nuevo_tamano)
            print(f"Panel lateral reducido a {PANEL_LATERAL_TAMANO} píxeles.")
        else:
            print("La estructura del splitter no es la esperada.")
    else:
        print("No se pudo encontrar el splitter principal.")

if __name__ == "__main__":
    main()
