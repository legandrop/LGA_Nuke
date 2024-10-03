import PySide2, hiero
from PySide2.QtWidgets import QAction, QMessageBox
from PySide2.QtGui import QIcon
from PySide2.QtCore import *

class PurgeUnusedAction:

    def __init__(self):
         pass
         
    # Method to return whether a Bin is empty...
    def binIsEmpty(self,b):
        numBinItems = 0
        bItems = b.items()
        empty = False

        if len(bItems) == 0:
            empty = True
            return empty
        else:
            for b in bItems:
                if isinstance(b,hiero.core.BinItem) or isinstance(b,hiero.core.Bin):
                    numBinItems+=1
            if numBinItems == 0:
                empty = True

        return empty

    def PurgeUnused(self) :

        # Get the active project
        project = get_active_project()

        # Build a list of Projects
        SEQS = hiero.core.findItems(project, "Sequences")

        # Build a list of Clips
        CLIPSTOREMOVE = hiero.core.findItems(project, "Clips")


        if len(SEQS)==0:
            # Present Dialog Asking if User wants to remove Clips
            msgBox = QMessageBox()
            msgBox.setText("Purge Unused Clips");
            msgBox.setInformativeText("You have no Sequences in this Project. Do you want to remove all Clips (%i) from Project: %s?" % (len(CLIPSTOREMOVE), project.name()));
            msgBox.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel);
            msgBox.setDefaultButton(QMessageBox.Ok);
            ret = msgBox.exec_()
            if ret == QMessageBox.Cancel:
                print('Not purging anything.')
            elif ret == QMessageBox.Ok:
                with project.beginUndo('Purge Unused Clips'):
                    BINS = []
                    for clip in CLIPSTOREMOVE:
                        BI = clip.binItem()
                        B = BI.parentBin()
                        BINS+=[B]
                        print('Removing:', BI)
                        try:
                            B.removeItem(BI)
                        except:
                            print('Unable to remove:', BI)
            return

        # For each sequence, iterate through each track Item, see if the Clip is in the CLIPS list.
        # Remaining items in CLIPS will be removed

        for seq in SEQS:

            #Loop through selected and make folders
            for track in seq:
                for trackitem in track:

                    if trackitem.source() in CLIPSTOREMOVE:
                        CLIPSTOREMOVE.remove(trackitem.source())

        # Present Dialog Asking if User wants to remove Clips
        msgBox = QMessageBox()
        msgBox.setText("Purge Unused Clips");
        msgBox.setInformativeText("Remove %i unused Clips from Project %s?" % (len(CLIPSTOREMOVE), project.name()));
        msgBox.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel);
        msgBox.setDefaultButton(QMessageBox.Ok);
        ret = msgBox.exec_()

        if ret == QMessageBox.Cancel:
             print('Cancel')
             return
        elif ret == QMessageBox.Ok:
            BINS = []
            with project.beginUndo('Purge Unused Clips'):
                # Delete the rest of the Clips
                for clip in CLIPSTOREMOVE:
                    BI = clip.binItem()
                    B = BI.parentBin()
                    BINS+=[B]
                    print('Removing:', BI)
                    try:
                        B.removeItem(BI)
                    except:
                        print('Unable to remove:', BI)

    def eventHandler(self, event):
        if not hasattr(event.sender, 'selection'):
                # Something has gone wrong, we shouldn't only be here if raised
                # by the Bin view which will give a selection.
                return

        self.selectedItem = None
        s = event.sender.selection()

        if len(s)>=1:
            self.selectedItem = s[0]
            title = "Purge Unused Clips"
            self.setText(title)
            event.menu.addAction(self)

        return

def get_active_project():
    """
    Obtiene el proyecto activo en Hiero.

    Returns:
    - hiero.core.Project o None: El proyecto activo, o None si no se encuentra ningun proyecto activo.
    """
    projects = hiero.core.projects()
    if projects:
        return projects[0]  # Devuelve el primer proyecto en la lista
    else:
        return None

# Create an instance of PurgeUnusedAction
purge_action = PurgeUnusedAction()

# Call the PurgeUnused function directly
purge_action.PurgeUnused()
