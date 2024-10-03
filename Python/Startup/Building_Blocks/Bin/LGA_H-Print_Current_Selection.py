import hiero.ui
from PySide2.QtWidgets import QApplication

def print_current_project_selection():
    """
    Prints the current selection in the Project window.
    """
    # Process events to ensure the UI is up to date
    QApplication.processEvents()

    # Get the project window
    project_window = None
    for window in hiero.ui.windowManager().windows():
        if window.windowTitle() == "Project":
            project_window = window
            break
    
    if not project_window:
        print("No se pudo encontrar la ventana 'Project'.")
        return

    # Activate the project window
    project_window.raise_()
    project_window.activateWindow()
    project_window.setFocus()

    # Give time for the interface to update
    QApplication.processEvents()

    # Get the current active view (which should be the Project Bin view)
    active_view = hiero.ui.activeView()

    if active_view and hasattr(active_view, 'selection'):
        current_selection = active_view.selection()

        if current_selection:
            print("Current selection in the Project window:")
            for item in current_selection:
                print(f"- {item.name()} ({type(item).__name__})")
        else:
            print("No items are currently selected in the Project window.")
    else:
        print("Could not retrieve the current selection or there is no active view.")

# Call the function to print the current selection in the Project window
print_current_project_selection()
