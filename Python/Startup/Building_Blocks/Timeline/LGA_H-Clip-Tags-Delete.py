import hiero.core
import hiero.ui

def delete_tags_from_selected_clips():
    # Obtiene la seleccion actual en el editor de timeline
    selection = hiero.ui.getTimelineEditor(hiero.ui.activeSequence()).getSelection()
    if not selection:
        print("No clips selected.")
        return

    # Recorre cada clip seleccionado
    for clip in selection:
        tags = clip.tags()
        if tags:
            for tag in list(tags):  # Usa list(tags) para evitar modificar la lista mientras se itera
                clip.removeTag(tag)
            print(f"All tags removed from clip: {clip.name()}")
        else:
            print("No tags on this clip to remove.")

delete_tags_from_selected_clips()
