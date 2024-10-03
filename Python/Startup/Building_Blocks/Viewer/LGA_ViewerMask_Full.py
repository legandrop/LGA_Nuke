# Pone en negro el viewer mask

import hiero.ui

# Obtén el viewer actual
viewer = hiero.ui.currentViewer()

# Verifica si el viewer fue encontrado
if viewer is not None:
    # Aplica un estilo de máscara de superposición
    try:
        # Establece el estilo de superposición a 'eMaskOverlayFull'
        viewer.setMaskOverlayStyle(hiero.ui.Player.MaskOverlayStyle.eMaskOverlayFull)
        print("El estilo de máscara de superposición se ha aplicado correctamente.")
    except AttributeError as e:
        print(f"Error: {e}")
else:
    print("No se pudo obtener el viewer actual.")
