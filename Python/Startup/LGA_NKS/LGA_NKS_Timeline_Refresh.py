"""
__________________________________________________________

  LGA_NKS_Timeline_Refresh v1.2 - 2024 - Lega

  Refresca el timeline cerrándolo y volviéndolo a abrir,
  manteniendo los ajustes del viewer:
  1. Captura el estado actual del viewer (masking, etc).
  2. Cierra el viewer activo.
  3. Reabre la misma secuencia en un nuevo timeline viewer.
  4. Restaura los ajustes del viewer.
__________________________________________________________
"""

import hiero.core
import hiero.ui

DEBUG = True

def debug_print(*message):
    if DEBUG:
        print(*message)

def get_viewer_state(viewer):
    """
    Captura el estado actual del viewer.
    """
    if not viewer:
        return None

    try:
        state = {
            'time': viewer.time(),
            'mask_style': viewer.maskOverlayStyle(),
            'lut': viewer.player().LUT(),
            'gain': viewer.gain(),
            'gamma': viewer.gamma()
        }
        debug_print("Estado del viewer capturado:")
        debug_print(f"- Tiempo: {state['time']}")
        debug_print(f"- Estilo de máscara: {state['mask_style']}")
        debug_print(f"- LUT: {state['lut']}")
        debug_print(f"- Gain: {state['gain']}")
        debug_print(f"- Gamma: {state['gamma']}")
        return state
    except Exception as e:
        debug_print(f"Error al capturar el estado del viewer: {e}")
        return None

def restore_viewer_state(viewer, state):
    """
    Restaura el estado del viewer.
    """
    if not viewer or not state:
        debug_print("No se puede restaurar el estado: viewer o state es None")
        return

    try:
        debug_print("\nRestaurando estado del viewer...")
        debug_print(f"- Estableciendo tiempo a: {state['time']}")
        viewer.setTime(state['time'])

        debug_print(f"- Estableciendo estilo de máscara a: {state['mask_style']}")
        viewer.setMaskOverlayStyle(state['mask_style'])

        # Si había un aspecto 2.35:1, lo restauramos
        if state['mask_style'] != hiero.ui.Player.MaskOverlayStyle.eMaskOverlayNone:
            debug_print("- Estableciendo aspecto 2.35:1")
            viewer.setMaskOverlayFromRemote("2.35:1")

        debug_print(f"- Estableciendo LUT a: {state['lut']}")
        viewer.player().setLUT(state['lut'])

        debug_print(f"- Estableciendo Gain a: {state['gain']}")
        viewer.setGain(state['gain'])  # Cambiado de setDisplayGain a setGain

        debug_print(f"- Estableciendo Gamma a: {state['gamma']}")
        viewer.setGamma(state['gamma'])  # Cambiado de setDisplayGamma a setGamma

        debug_print("Estado del viewer restaurado completamente")
    except Exception as e:
        debug_print(f"Error al restaurar el estado del viewer: {e}")

def main():
    """
    Cierra el viewer activo y reabre la misma secuencia en un nuevo timeline viewer.
    """
    # Obtener el viewer activo
    active_viewer = hiero.ui.currentViewer()
    if not active_viewer:
        debug_print("No se encontró un viewer activo")
        return

    debug_print("\n1. Capturando estado del viewer activo...")
    # Guardar el estado del viewer
    viewer_state = get_viewer_state(active_viewer)
    if not viewer_state:
        debug_print("No se pudo capturar el estado del viewer")
        return

    debug_print("\n2. Guardando información de la secuencia activa...")
    # Guardar la información de la secuencia activa
    active_sequence = active_viewer.player().sequence()
    if not active_sequence:
        debug_print("No se encontró una secuencia activa")
        return

    debug_print("\n3. Cerrando viewer activo...")
    # Cerrar el viewer activo
    viewer_window = active_viewer.window()
    if viewer_window:
        viewer_window.close()

    debug_print("\n4. Abriendo nueva secuencia...")
    # Abrir la secuencia en un nuevo timeline
    new_timeline = hiero.ui.openInTimeline(active_sequence)
    if new_timeline:
        debug_print("\n5. Obteniendo nuevo viewer...")
        # Obtener el nuevo viewer y restaurar su estado
        new_viewer = hiero.ui.currentViewer()
        if new_viewer:
            restore_viewer_state(new_viewer, viewer_state)
        else:
            debug_print("No se pudo obtener el nuevo viewer")
    else:
        debug_print("No se pudo abrir el nuevo timeline")

if __name__ == "__main__":
    main()
