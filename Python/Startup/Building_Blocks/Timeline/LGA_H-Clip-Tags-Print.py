import hiero.core
import hiero.ui

def print_tag_details():
    # Obtiene la seleccion actual en el editor de timeline
    selection = hiero.ui.getTimelineEditor(hiero.ui.activeSequence()).getSelection()
    if not selection:
        print("No clips selected.")
        return

    # Recorre cada clip seleccionado
    for clip in selection:
        tags = clip.tags()
        if tags:
            for tag in tags:
                print(f"Tag Name: {tag.name()}, Note: {tag.note()}, Icon: {tag.icon()}")
        else:
            print("No tags on this clip.")

print_tag_details()
