import hiero.ui

# Obtén la secuencia activa
sequence = hiero.ui.activeSequence()

if sequence:
    print("Secuencia activa encontrada:", sequence)
    viewer = hiero.ui.currentViewer()  # Obtén el visor actual
    if viewer:
        # Imprime la posición actual del playhead
        current_time = viewer.time()  # Obtén el tiempo actual del playhead
        print("Posición actual del playhead:", current_time)

        # Mueve el playhead al inicio del timeline
        viewer.setTime(0)

        # Verifica si el playhead se ha movido
        new_time = viewer.time()
        print("Nueva posición del playhead después de moverlo:", new_time)
    else:
        print("No se encontró ningún visor activo.")
else:
    print("No se encontró ninguna secuencia activa.")
