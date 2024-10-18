# Pone en negro el viewer mask

import hiero.ui

# Obten el viewer actual
viewer = hiero.ui.currentViewer()

# Verifica si el viewer fue encontrado
if viewer is not None:
    # Aplica un estilo de mascara de superposicion
    try:
        # Establece el estilo de superposicion a 'eMaskOverlayFull'
        viewer.setMaskOverlayStyle(hiero.ui.Player.MaskOverlayStyle.eMaskOverlayFull)
        print("El estilo de mascara de superposicion se ha aplicado correctamente.")
    except AttributeError as e:
        print(f"Error: {e}")
else:
    print("No se pudo obtener el viewer actual.")
