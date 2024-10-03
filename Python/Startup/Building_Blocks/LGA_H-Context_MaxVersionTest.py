import hiero.core, hiero.ui, nuke
from PySide2 import QtWidgets
from PySide2.QtWidgets import QMessageBox
from hiero.core import events

class max_version(QtWidgets.QAction):
    def __init__(self, event):
        QtWidgets.QAction.__init__(self, "", None)
        self.event = event
        self.triggered.connect(self.doit)

    def doit(self):
        for item in hiero.ui.getTimelineEditor(hiero.ui.activeSequence()).selection():
            item.maxVersion()

def AddActionToMenu(event):
    menu = event.menu
    menu.addAction("Max Version Test", lambda: max_version(event).trigger())
    


events.registerInterest((events.EventType.kShowContextMenu), AddActionToMenu)
