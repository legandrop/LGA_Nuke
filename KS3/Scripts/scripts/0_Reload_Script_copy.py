import nuke
undo = nuke.Undo()
undo.end()

import importlib
import LGA_arrangeNodes
importlib.reload(LGA_arrangeNodes)