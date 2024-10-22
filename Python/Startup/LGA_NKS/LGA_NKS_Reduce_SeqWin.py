"""
______________________________________________________________________

  LGA_NKS_Reduce_SeqWin v1.1 - 2024 - Lega
  Ajusta el tamaño del panel izquierdo del timeline editor de Hiero
______________________________________________________________________

"""

import hiero.ui
from PySide2 import QtWidgets

# Variable global para activar o desactivar los prints de depuración
DEBUG = False

def debug_print(*message):
    if DEBUG:
        print(*message)

# Tamaño deseado para el panel izquierdo (en píxeles)
PANEL_IZQUIERDO_TAMANO = 340

def imprimir_tamanos(splitter, mensaje):
    sizes = splitter.sizes()
    ancho_total = sum(sizes)
    debug_print(f"\n{mensaje}")
    debug_print(f"Ancho total del timeline: {ancho_total} píxeles")
    debug_print(f"Panel izquierdo: {sizes[0]} píxeles")
    debug_print(f"Panel derecho: {sizes[1]} píxeles")

def main():
    timeline_editor = hiero.ui.getTimelineEditor(hiero.ui.activeSequence())
    if not timeline_editor:
        debug_print("No se pudo obtener el editor de línea de tiempo activo.")
        return

    window = timeline_editor.window()
    main_splitter = window.findChild(QtWidgets.QSplitter)

    if main_splitter:
        # Imprimir tamaños antes del cambio
        imprimir_tamanos(main_splitter, "Tamaños antes del cambio:")

        sizes = main_splitter.sizes()
        if len(sizes) == 2:
            ancho_total = sum(sizes)
            nuevo_tamano = [PANEL_IZQUIERDO_TAMANO, ancho_total - PANEL_IZQUIERDO_TAMANO]
            main_splitter.setSizes(nuevo_tamano)
            debug_print(f"\nPanel izquierdo ajustado a {PANEL_IZQUIERDO_TAMANO} píxeles.")

            # Imprimir tamaños después del cambio
            imprimir_tamanos(main_splitter, "Tamaños después del cambio:")
        else:
            debug_print("La estructura del splitter no es la esperada.")
    else:
        debug_print("No se pudo encontrar el splitter principal.")

if __name__ == "__main__":
    main()
