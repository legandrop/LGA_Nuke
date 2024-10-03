import hiero.core 
from PySide2 import QtWidgets, QtCore
from hiero.core import events

"""
A workaround for Bug ID 576670 in the Nuke Studio Timeline Viewer
"""

import nuke
nuke.tprint("adding %s"%__name__)

class ExampleAction(QtWidgets.QAction):

    def __init__(self): 
        QtWidgets.QAction.__init__(self, "Clear Out Point Only", None) 
        self.triggered.connect(self.doit) 

    def doit(self):
        seq = hiero.ui.activeSequence()
        try:
            inTime = seq.inTime()
        except:
            inTime = None
        active = seq.activePlayhead()
        seq.clearPlayheadOutTime(active)
        if inTime:
            seq.setPlayheadInTime(active, inTime) 
        
my_action = ExampleAction() 
hiero.ui.registerAction(my_action) 
my_action.setShortcut("Alt+P")
#### The action needs to be added to a section of the UI
hiero.ui.mainWindow().addAction(my_action)

def AddActionToMenu(event):
    menu = event.menu
    menu.addAction(my_action)

events.registerInterest((events.EventType.kShowContextMenu, events.EventType.kViewer), AddActionToMenu)