import hiero.core
import hiero.ui
from PySide2.QtGui import QColor

# Obtiene la secuencia activa y el editor de timeline
seq = hiero.ui.activeSequence()
if seq:  # Asegurarse de que hay una secuencia activa
    te = hiero.ui.getTimelineEditor(seq)
    selected_items = te.selection()
    project = hiero.core.projects()[0]
    project.beginUndo("Print Clip Color")

    # Iterar sobre los clips seleccionados y imprimir su color
    for item in selected_items:
        if isinstance(item, hiero.core.EffectTrackItem):  # Verificar si es un efecto
            print(f"Ignore effect item: {item.name()}")
        else:
            bin_item = item.source().binItem()
            if item.source().mediaSource().isMediaPresent():
                active_version = bin_item.activeVersion()
                if active_version:
                    current_color = bin_item.color()  # Obtiene el color actual del BinItem
                    # Imprimir color en formato QColor
                    print(f"Current color for active version of clip {item.name()}: {current_color}")
                    # Imprimir color en formato RGB
                    rgb_color = f"RGB: ({current_color.red()}, {current_color.green()}, {current_color.blue()})"
                    print(f"RGB color: {rgb_color}")
                    # Imprimir color en formato hexadecimal
                    hex_color = f"Hex: #{current_color.name()}"
                    print(f"Hexadecimal color: {hex_color}")
                else:
                    print(f"No active version found for clip: {item.name()}")
            else:
                print(f"No media present for clip: {item.name()}")
    project.endUndo()
else:
    print("No active sequence found.")
