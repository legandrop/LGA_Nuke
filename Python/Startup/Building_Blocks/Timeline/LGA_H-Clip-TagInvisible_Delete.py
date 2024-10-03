# Borra todos los tags
# pero ninguno de estos tags es visible en el timeline

import hiero.core
import hiero.ui

# Obtiene la secuencia activa y el editor de timeline
seq = hiero.ui.activeSequence()
if seq:  # Asegurarse de que hay una secuencia activa
    te = hiero.ui.getTimelineEditor(seq)
    selected_items = te.selection()
    project = hiero.core.projects()[0]
    project.beginUndo("Remove All Tags from Clips")

    # Iterar sobre los clips seleccionados y eliminar sus tags
    for item in selected_items:
        if isinstance(item, hiero.core.TrackItem):  # Verificar si es un clip
            clip = item.source()  # Obtiene el clip asociado al TrackItem
            tags = clip.tags()  # Obtiene todos los tags del clip
            for tag in tags:
                clip.removeTag(tag)  # Elimina cada tag
                print(f"Tag removed from clip: {clip.name()}")
        else:
            print(f"Ignore non-clip item: {item.name()}")

    project.endUndo()
else:
    print("No active sequence found.")
