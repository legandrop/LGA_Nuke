"""
__________________________________________________________

  LGA_NKS_ClearCachePlayback v1.0 - 2024 - Lega
  Limpia el cache de reproduccion del viewer activo en Hiero
__________________________________________________________

"""

import hiero.core
import hiero.ui


def main():
    """
    Funcion principal que limpia el cache de reproduccion del viewer activo.
    """
    # Obtener el viewer activo
    viewer = hiero.ui.currentViewer()
    
    if viewer is None:
        print("No se encontro un viewer activo.")
        return
        
    try:
        # Limpiar el cache de reproduccion del viewer activo
        viewer.flushCache()
        
        # Limpiar el cache de todos los viewers y pausar el caching
        hiero.ui.flushAllViewersCache()
        
        print("Cache de reproduccion limpiado exitosamente.")
    except Exception as e:
        print(f"Error al limpiar el cache de reproduccion: {e}")


if __name__ == "__main__":
    main()
