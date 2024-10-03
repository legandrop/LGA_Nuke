# Imprime todos los tags del clip seleccionado
# pero ninguno de estos tags es visible en el timeline

import hiero.core
import hiero.ui

# Obtiene la secuencia activa y el editor de timeline
seq = hiero.ui.activeSequence()
if seq:  # Asegurarse de que hay una secuencia activa
    te = hiero.ui.getTimelineEditor(seq)
    selected_items = te.selection()

    # Iterar sobre los clips seleccionados y verificar sus tags
    for item in selected_items:
        if isinstance(item, hiero.core.TrackItem):  # Verificar si es un clip
            clip = item.source()  # Obtiene el clip asociado al TrackItem
            tags = clip.tags()  # Obtiene los tags del clip
            if tags:
                print(f"Clip: {clip.name()} has the following tags:")
                for tag in tags:
                    print(f"- {tag.name()} with icon: {tag.icon()}")
            else:
                print(f"Clip: {clip.name()} has no tags.")
        else:
            print(f"Ignore non-clip item: {item.name()}")
else:
    print("No active sequence found.")
