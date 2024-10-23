"""
__________________________________________________________

  LGA_NKS_ExploreTimelineWidgets v1.0 - 2024 - Lega
  
  Explora y muestra la estructura completa de widgets del timeline
  activo en Hiero. Útil para desarrollo y debugging de scripts
  que necesitan acceder a widgets específicos del timeline.
  
  Muestra:
  - Jerarquía completa de widgets
  - Tipo de cada widget
  - Nombre del objeto (si tiene)
  - Clase del widget (si es QWidget)
  
  Ejemplo de uso:
  Para encontrar la ruta correcta a un widget específico,
  como scrollbars, sliders o contenedores del timeline.
__________________________________________________________

"""

import hiero.core
import hiero.ui
from PySide2 import QtWidgets

def explore_timeline_widgets():
    """
    Explora la estructura completa de widgets del timeline.
    """
    t = hiero.ui.getTimelineEditor(hiero.ui.activeSequence())
    if not t:
        print("No se encontró un timeline activo.")
        return
    
    print("\nExplorando estructura completa de widgets:")
    def explore_widget(widget, depth=0):
        indent = "  " * depth
        print(f"{indent}Type: {type(widget).__name__}")
        if hasattr(widget, 'objectName') and widget.objectName():
            print(f"{indent}Name: {widget.objectName()}")
        if isinstance(widget, QtWidgets.QWidget):
            print(f"{indent}Class: {widget.metaObject().className()}")
        
        if hasattr(widget, 'children'):
            for child in widget.children():
                explore_widget(child, depth + 1)
    
    explore_widget(t.window())

def main():
    """
    Función principal que ejecuta la exploración de widgets.
    """
    try:
        explore_timeline_widgets()
    except Exception as e:
        print(f"Error durante la exploración: {e}")
        import traceback
        print(traceback.format_exc())

if __name__ == "__main__":
    main()
