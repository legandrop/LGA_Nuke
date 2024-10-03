"""
_________________________

LGA_reconnectMedia v1.1
_________________________
"""


import hiero.core
import hiero.ui 
from PySide2 import QtWidgets 
import os

class AltReconnectMedia(QtWidgets.QAction): 

    def __init__(self): 
        QtWidgets.QAction.__init__(self, "Alt Reconnect Media...", None) 
        self.setObjectName("timeline.reconnectMedia") 
        self.triggered.connect(self.doit) 

    def doit(self): 
        seq = hiero.ui.activeSequence()
        if not seq:
            print("\nNo active sequence found.")
            return
        
        te = hiero.ui.getTimelineEditor(seq)
        selected_track_items = te.selection()

        if len(selected_track_items) == 0:
            print("*** No track items selected ***")
            return

        # Obtener la ruta del clip seleccionado
        selected_clip = selected_track_items[0]  # Solo usaremos el primer clip seleccionado
        file_path = selected_clip.source().mediaSource().fileinfos()[0].filename()
        initial_path = os.path.dirname(file_path)

        # Agregar una barra al final del path si no esta presente
        if not initial_path.endswith("/"):
            initial_path += "/"

        # Abrir el file browser con la ruta inicial del clip seleccionado
        search_path = hiero.ui.openFileBrowser("Choose directory to search for media", mode=3, initialPath=initial_path)[0] 

        for track_item in selected_track_items:         
            track_item.reconnectMedia(search_path)

altMediaReconnect = AltReconnectMedia() 
hiero.ui.registerAction(altMediaReconnect) 
altMediaReconnect.setShortcut("Alt+M") 

hiero.ui.mainWindow().addAction(altMediaReconnect)
