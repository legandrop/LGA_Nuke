import hiero.ui
import hiero.core

def check_clip_status():
    try:
        seq = hiero.ui.activeSequence()
        if seq:
            te = hiero.ui.getTimelineEditor(seq)
            selected_items = te.selection()
            if selected_items:
                for item in selected_items:
                    if not isinstance(item, hiero.core.EffectTrackItem):
                        is_enabled = item.isEnabled()
                        status = "enabled" if is_enabled else "disabled"
                        print(f"Clip '{item.name()}' is {status}")
            else:
                print("No clips selected on the timeline.")
        else:
            print("No active sequence found in Hiero.")
    except Exception as e:
        print(f"Error during operation: {e}")

# Ejecutar la funcion para verificar el estado del clip seleccionado
check_clip_status()
