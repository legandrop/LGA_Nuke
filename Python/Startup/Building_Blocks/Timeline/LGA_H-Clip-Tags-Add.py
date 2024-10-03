import hiero.core
import hiero.ui

def add_custom_tag_to_selected_clips():
    # Obtiene la seleccion actual en el editor de timeline
    selection = hiero.ui.getTimelineEditor(hiero.ui.activeSequence()).getSelection()
    if not selection:
        print("No clips selected.")
        return

    # Define el tag con sus propiedades
    tag_name = "Magenta"
    tag_note = "Funciona"
    tag_icon = "icons:TagRed.png"

    # Recorre cada clip seleccionado y anade el tag
    for clip in selection:
        # Crea el tag
        new_tag = hiero.core.Tag(tag_name)
        new_tag.setIcon(tag_icon)
        new_tag.setNote(tag_note)
        
        # Anade el tag al clip
        clip.addTag(new_tag)
        print(f"Added tag '{tag_name}' with note '{tag_note}' to clip: {clip.name()}")

add_custom_tag_to_selected_clips()
