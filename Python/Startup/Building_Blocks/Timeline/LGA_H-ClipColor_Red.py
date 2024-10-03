# Aplica color rojo al clip seleccionados
# Antes se fija que el clip seleccionado no sea un efecto

import hiero.core
import hiero.ui
from PySide2.QtGui import QColor

# Define el color que deseas aplicar
color = QColor(255, 220, 0)  # Rojo, por ejemplo

# Obtiene la secuencia activa y el editor de timeline
seq = hiero.ui.activeSequence()
if seq:  # Asegurarse de que hay una secuencia activa
    te = hiero.ui.getTimelineEditor(seq)
    selected_items = te.selection()
    project = hiero.core.projects()[0]
    project.beginUndo("Change Clip Color")

    # Iterar sobre los clips seleccionados y cambiar su color
    for item in selected_items:
        if isinstance(item, hiero.core.EffectTrackItem):  # Verificar si es un efecto
            print(f"Ignore effect item: {item.name()}")
        else:
            bin_item = item.source().binItem()
            if item.source().mediaSource().isMediaPresent():
                active_version = bin_item.activeVersion()
                if active_version:
                    bin_item.setColor(color) # Aplica el color al BinItem
                    print(f"Color changed for active version of clip: {item.name()}")
                else:
                    print(f"No active version found for clip: {item.name()}")
            else:
                print(f"No media present for clip: {item.name()}")
    project.endUndo()
else:
    print("No active sequence found.")
