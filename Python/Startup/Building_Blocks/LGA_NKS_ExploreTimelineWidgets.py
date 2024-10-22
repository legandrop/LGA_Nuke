"""
LGA_NKS_ExploreTimelineWidgets.py
imprime información sobre los widgets del timeline de Nuke Studio
para poder identificar los widgets y trabajar con ellos (ej: reducir el panel lateral)
"""

import hiero.ui
from PySide2 import QtWidgets, QtCore

def explore_widget(widget, indent=0):
    """Explora recursivamente un widget y sus hijos, imprimiendo información sobre cada uno."""
    if widget is None:
        return

    # Imprimir información sobre el widget actual
    print("  " * indent + f"Tipo: {type(widget).__name__}")
    
    # Si es un QSplitter, imprimir información adicional
    if isinstance(widget, QtWidgets.QSplitter):
        print("  " * indent + f"Orientación: {'Horizontal' if widget.orientation() == QtCore.Qt.Horizontal else 'Vertical'}")
        print("  " * indent + f"Tamaños: {widget.sizes()}")
    
    # Si es un QTabWidget, imprimir información sobre las pestañas
    if isinstance(widget, QtWidgets.QTabWidget):
        print("  " * indent + f"Número de pestañas: {widget.count()}")
        for i in range(widget.count()):
            print("  " * (indent + 1) + f"Pestaña {i}: {widget.tabText(i)}")
    
    # Explorar los hijos del widget actual
    for child in widget.children():
        if isinstance(child, QtWidgets.QWidget):
            explore_widget(child, indent + 1)

def main():
    # Obtener el editor de línea de tiempo activo
    timeline_editor = hiero.ui.getTimelineEditor(hiero.ui.activeSequence())
    
    if timeline_editor:
        print("Explorando widgets del editor de línea de tiempo:")
        window = timeline_editor.window()
        explore_widget(window)
    else:
        print("No se pudo obtener el editor de línea de tiempo activo.")

if __name__ == "__main__":
    main()
