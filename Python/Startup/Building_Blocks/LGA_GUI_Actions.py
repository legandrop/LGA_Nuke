# Busca en una de las ventanas del GUI, la abre y hace algo. En este caso con los settings del proyecto

from contextlib import contextmanager
from PySide2 import QtWidgets
import hiero.ui

def getWindow(windowTitle: str) -> QtWidgets.QWidget:
    """
    Obtiene una ventana de la UI de Hiero con el titulo proporcionado.
    Args:
        windowTitle: str - el nombre de la ventana

    Returns:
        La ventana encontrada (si existe)
    """
    foundWindow = None
    for window in hiero.ui.windowManager().windows():
        if window.windowTitle().lower() == windowTitle.lower():
            foundWindow = window
    return foundWindow

def triggerRegisteredAction(action: str) -> None:
    """
    Activa una accion registrada en Hiero. Una lista de acciones registradas
    se puede encontrar aqui: https://gist.github.com/melMass/634800017869948fb4dec60ad9cf77d6

    Args:
        action: str - el nombre de la accion a activar

    Returns:
        None
    """
    for act in hiero.ui.registeredActions():
        if act.text() == action:
            act.trigger()

@contextmanager
def getProjectSettingsWindow() -> QtWidgets.QWidget:
    """
    Obtiene la ventana de configuracion del proyecto como si el usuario hiciera clic en Proyecto > Editar Configuracion.

    Returns:
        QtWidgets.QWidget: La ventana de configuracion del proyecto
    """
    projectSettingsWindow = getWindow("Project Settings")

    if not projectSettingsWindow:
        triggerRegisteredAction("Edit Settings")
        projectSettingsWindow = getWindow("Project Settings")
    if not projectSettingsWindow:
        raise ValueError("No se encontro la ventana de configuracion del proyecto.")

    yield projectSettingsWindow

    try:
        projectSettingsWindow.parentWidget().parentWidget().close()
    except AttributeError:
        try:
            projectSettingsWindow.parentWidget().close()
        except AttributeError:
            projectSettingsWindow.close()

def setColorManagement():
    with getProjectSettingsWindow() as psw:
        # Abrir la pestana de Gestion de Color
        stackWidget = psw.findChildren(QtWidgets.QStackedWidget)[0]
        stackWidget.setCurrentIndex(3)  # Indice de la pestana de Gestion de Color (ajustar si es necesario)
        colorManagementTab = stackWidget.currentWidget()

        # Obtener una lista de todos los menus desplegables y filtrar para encontrar el que queremos
        dropdownMenus = colorManagementTab.findChildren(QtWidgets.QComboBox)
        ocioConfigKnob = None
        for knob in dropdownMenus:
            allItems = [knob.itemText(i) for i in range(knob.count())]
            if "Rec.709 (ACES)" in allItems:
                ocioConfigKnob = knob
                break
        
        if ocioConfigKnob:
            ocioConfigKnob.setCurrentText("ACES/Log")
            print("Viewer color space set to 'Rec.709 (ACES)'")
        else:
            print("No se encontro la opcion 'Rec.709 (ACES)' en los menus desplegables.")

# Ejecutar la funcion para cambiar la configuracion de gestion de color
setColorManagement()
