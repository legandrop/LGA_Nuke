"""
__________________________________________________________

  LGA_NKS_Viewer_235 v1.0 - 2024 - Lega
  Ajusta el overlay del viewer a 2.35:1 y 
  alterna los estilos de máscara entre None, Half y Full
__________________________________________________________


"""

import hiero.ui

def rotate_overlay_style(viewer):
    current_style = viewer.maskOverlayStyle()
    style_order = [
        hiero.ui.Player.MaskOverlayStyle.eMaskOverlayNone,
        hiero.ui.Player.MaskOverlayStyle.eMaskOverlayHalf,
        hiero.ui.Player.MaskOverlayStyle.eMaskOverlayFull
    ]
    
    # Encontrar el índice del estilo actual y rotar al siguiente
    try:
        current_index = style_order.index(current_style)
        next_index = (current_index + 1) % len(style_order)
        new_style = style_order[next_index]
    except ValueError:
        # Si el estilo actual no está en la lista, comenzar desde el principio
        new_style = style_order[0]
    
    return new_style

# Obtener el visor actual
viewer = hiero.ui.currentViewer()

# Verificar si se encontró el visor
if viewer is not None:
    try:
        # Obtener y mostrar el estilo actual
        current_style = viewer.maskOverlayStyle()
        print(f"Estilo actual: {current_style}")

        # Rotar al siguiente estilo
        new_style = rotate_overlay_style(viewer)
        viewer.setMaskOverlayStyle(new_style)
        print(f"Nuevo estilo aplicado: {new_style}")

        # Aplicar siempre el aspecto 2.35:1
        viewer.setMaskOverlayFromRemote("2.35:1")
        print("Aspecto 2.35:1 aplicado")

    except AttributeError as e:
        print(f"Error: {e}")
else:
    print("No se pudo obtener el visor actual.")