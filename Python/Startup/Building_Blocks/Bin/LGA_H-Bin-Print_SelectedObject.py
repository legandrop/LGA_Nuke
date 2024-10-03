from PySide2.QtWidgets import QAction
import hiero.ui

class SelectedBinItemAction(QAction):
    def __init__(self):
        QAction.__init__(self, "Obtener seleccion del bin", None)
        self.triggered.connect(self.getBinSelection)
        hiero.core.events.registerInterest("kShowContextMenu/kBin", self.eventHandler)
        self.setShortcut("Ctrl+Alt+B")

    def getBinSelection(self):
        """Obtener la seleccion actual en la vista del bin y mostrarla"""
        view = hiero.ui.activeView()
        if isinstance(view, hiero.ui.BinView):
            selection = view.selection()
            if selection:
                print("Elementos seleccionados en la vista del bin:")
                for item in selection:
                    print(item.name())
            else:
                print("No hay elementos seleccionados en la vista del bin.")
        else:
            print("Este comando solo esta disponible en la vista del bin.")

    def eventHandler(self, event):
        # Agregar la opcion al menu contextual
        event.menu.addAction(self)

# Inicializar la accion para obtener la seleccion del bin
SelectedBinItemAction = SelectedBinItemAction()

# Agregar la accion al menu Edit en la barra de menu
editMenu = hiero.ui.findMenuAction("Edit")
editMenu.menu().addAction(SelectedBinItemAction)
