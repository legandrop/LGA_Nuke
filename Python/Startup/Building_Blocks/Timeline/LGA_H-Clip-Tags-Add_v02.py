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
    tag_note = "Esto es una Note"
    tag_assignee = "Persona"
    tag_icon = "icons:TagRed.png"

    # Recorre cada clip seleccionado y anade el tag
    for clip in selection:
        # Crea el tag
        new_tag = hiero.core.Tag(tag_name)
        new_tag.setIcon(tag_icon)
        new_tag.setNote(tag_note)
        
        # Anadir el assignee en los metadatos con la clave "Assignee" y espacio adicional
        formatted_assignee = tag_assignee + " "
        new_tag.metadata().setValue("tag.Assignee", formatted_assignee)
        
        # Anade el tag al clip
        clip.addTag(new_tag)
        print(f"Added tag '{tag_name}' with note '{tag_note}' and assignee '{formatted_assignee}' to clip: {clip.name()}")

add_custom_tag_to_selected_clips()
