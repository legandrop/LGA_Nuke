# This example shows how you can add custom keyboard shortcuts to Hiero.
# If you wish for this code to be run on startup, copy it to your <HIERO_PATH>/Startup directory.

from hiero.ui import findMenuAction
from PySide2 import QtGui

#myMenuItem = findMenuAction('Reconnect Media...')
#myMenuItem.setShortcut(QtGui.QKeySequence('Alt+M'))

# Hace lo mismo
#myMenuItem = findMenuAction('foundry.project.reconnectMedia')
#myMenuItem.setShortcut(QtGui.QKeySequence('shift+alt+u'))