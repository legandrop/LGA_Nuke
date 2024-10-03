"""
____________________________________________________________

  LGA_NKS_EXRTrack_Difference v1.0 - 2024 - Lega
  Alterna el modo de mezcla del track "EXR" a "Difference"
____________________________________________________________

"""

import hiero.core
import hiero.ui

DEBUG = False

def debug_print(*message):
    if DEBUG:
        print(*message)

def main():
    try:
        # Obtiene la secuencia activa
        seq = hiero.ui.activeSequence()

        if not seq:
            debug_print("No hay una secuencia activa.")
            return

        # Itera sobre los tracks de video para encontrar el que se llama "EXR"
        for index, track in enumerate(seq.videoTracks()):
            if track.name() == "EXR":
                # Verifica si el blend mode ya está activado
                if track.isBlendEnabled():
                    # Si está activado, lo desactiva
                    track.setBlendEnabled(False)
                    debug_print(f"Blend mode desactivado para el track 'EXR' en el índice: {index}")
                else:
                    # Si no está activado, lo activa y cambia el modo a "Difference"
                    track.setBlendEnabled(True)
                    track.setBlendMode("difference")
                    debug_print(f"Blend mode 'Difference' activado para el track 'EXR' en el índice: {index}")
                break
        else:
            debug_print("No se encontró un track llamado 'EXR'.")
    except Exception as e:
        debug_print(f"Error durante la operación: {e}")
