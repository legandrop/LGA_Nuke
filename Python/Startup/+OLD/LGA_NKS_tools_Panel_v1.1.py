import hiero.ui
import os
import PySide2, hiero
from PySide2.QtWidgets import *
from PySide2.QtGui import QIcon
from PySide2.QtCore import *

class ReconnectMediaWidget(QWidget):
    def __init__(self):
        super(ReconnectMediaWidget, self).__init__()

        self.setObjectName("com.lega.toolPanel")
        self.setWindowTitle("Tools")

        layout = QVBoxLayout(self)

        # Boton para reconectar de "t:" a "n:"
        self.reconnect_t_to_n_button = QPushButton('Reconnect T > N')
        self.reconnect_t_to_n_button.clicked.connect(self.reconnect_t_to_n)
        self.reconnect_t_to_n_button.setStyleSheet("background-color: #1f1f1f")
        layout.addWidget(self.reconnect_t_to_n_button)

        # Boton para reconectar de "n:" a "t:"
        self.reconnect_n_to_t_button = QPushButton('Reconnect N > T')
        self.reconnect_n_to_t_button.clicked.connect(self.reconnect_n_to_t)
        self.reconnect_n_to_t_button.setStyleSheet("background-color: #1f1f1f")
        layout.addWidget(self.reconnect_n_to_t_button)

        # Boton para establecer el nombre del plano
        self.set_shot_name_button = QPushButton('Set Shot Name')
        self.set_shot_name_button.clicked.connect(self.set_shot_name)
        self.set_shot_name_button.setStyleSheet("background-color: #1f1f1f")
        layout.addWidget(self.set_shot_name_button)

        # Boton para limpiar el proyecto
        self.clean_project_button = QPushButton('Clean Project')
        self.clean_project_button.clicked.connect(self.clean_project)
        self.clean_project_button.setStyleSheet("background-color: #1f1f1f")
        layout.addWidget(self.clean_project_button)        

        # Boton para revelar en el explorador
        self.reveal_in_explorer_button = QPushButton('Reveal in Explorer')
        self.reveal_in_explorer_button.clicked.connect(self.reveal_in_explorer)
        self.reveal_in_explorer_button.setStyleSheet("background-color: #1f1f1f")
        layout.addWidget(self.reveal_in_explorer_button)

        # Boton para revelar el script
        self.reveal_script_button = QPushButton('Reveal Script')
        self.reveal_script_button.clicked.connect(self.reveal_script)
        self.reveal_script_button.setStyleSheet("background-color: #1f1f1f")
        layout.addWidget(self.reveal_script_button)

        # Agregar un espaciador vertical al final para un mejor espaciado
        layout.addStretch()

    def reconnect_t_to_n(self):
        try:
            project = hiero.core.projects()[-1]
            project.beginUndo("Reconnect T > N")
            try:
                self.reconnect_media("t:", "n:")
            except Exception as e:
                print(f"Error: {e}")
            project.endUndo()
        except Exception as e:
            print(f"Error: {e}")

    def reconnect_n_to_t(self):
        try:
            project = hiero.core.projects()[-1]
            with project.beginUndo("Reconnect N > T"):
                self.reconnect_media("n:", "t:")
        except Exception as e:
            print(f"Error: {e}")
        finally:
            if project.undoStack().canEnd():
                project.endUndo()
            else:
                print("No current undo item to end.")

    def reconnect_media(self, old_prefix, new_prefix):
        try:
            seq = hiero.ui.activeSequence()
            if not seq:
                print("No active sequence found.")
                return

            te = hiero.ui.getTimelineEditor(seq)
            selected_clips = te.selection()

            if len(selected_clips) == 0:
                print("*** No clips selected on the track ***")
            else:
                for shot in selected_clips:
                    # Obtener el file path del clip seleccionado
                    file_path = shot.source().mediaSource().fileinfos()[0].filename()
                    print("Original file path:", file_path)

                    # Normalizar el path convirtiendo todo a minusculas
                    normalized_file_path = file_path.lower()

                    # Reemplazar el prefijo antiguo por el nuevo
                    new_file_path = normalized_file_path.replace(old_prefix, new_prefix)
                    print("Modified file path:", new_file_path)

                    # Obtener solo la ruta del directorio sin el nombre del archivo
                    directory_path = os.path.dirname(new_file_path)

                    # Reemplazar el clip por el del nuevo path
                    try:
                        shot.reconnectMedia(directory_path)
                        print("Clip reconnected successfully.")
                    except Exception as e:
                        print(f"Error reconnecting clip: {e}")
        except Exception as e:
            print(f"Error: {e}")

    def set_shot_name(self):
        try:
            project = hiero.core.projects()[-1]
            with project.beginUndo("Set Shot Name"):
                seq = hiero.ui.activeSequence()
                if not seq:
                    print("No active sequence found.")
                    return

                te = hiero.ui.getTimelineEditor(seq)
                selected_clips = te.selection()

                if len(selected_clips) == 0:
                    print("*** No clips selected on the track ***")
                else:
                    for shot in selected_clips:
                        # Obtener el file path del clip seleccionado
                        file_path = shot.source().mediaSource().fileinfos()[0].filename()
                        print("Original file path:", file_path)

                        # Obtener el nombre del plano del path del clip
                        shot_name = self.get_shot_name(file_path)
                        print("Shot name:", shot_name)

                        # Cambiar el nombre del plano al clip seleccionado
                        shot.setName(shot_name)
                        print("Shot name changed successfully.")
        except Exception as e:
            print(f"Error: {e}")

    def get_shot_name(self, file_path):
        # Dividir el path en partes usando '/' como separador
        path_parts = file_path.split('/')
        # El shot name seria la tercera parte del path
        shot_name = path_parts[3]
        return shot_name


    def clean_project(self):
        try:
            clean_action = CleanUnusedAction()
            clean_action.CleanUnused()
        except Exception as e:
            print(f"Error during project cleaning: {e}")


    def reveal_in_explorer(self):
        try:
            seq = hiero.ui.activeSequence()
            if not seq:
                print("No active sequence found.")
                return

            te = hiero.ui.getTimelineEditor(seq)
            selected_clips = te.selection()

            if len(selected_clips) == 0:
                print("*** No clips selected on the track ***")
            else:
                for shot in selected_clips:
                    # Obtener el file path del clip seleccionado
                    file_path = shot.source().mediaSource().fileinfos()[0].filename()
                    print("Original file path:", file_path)

                    # Abrir el explorador de archivos en el directorio del clip
                    try:
                        os.startfile(os.path.dirname(file_path))
                        print("Revealed in explorer successfully.")
                    except Exception as e:
                        print(f"Error revealing in explorer: {e}")
        except Exception as e:
            print(f"Error: {e}")


    def reveal_script(self):
        try:
            seq = hiero.ui.activeSequence()
            if not seq:
                print("No active sequence found.")
                return

            te = hiero.ui.getTimelineEditor(seq)
            selected_clips = te.selection()

            if len(selected_clips) == 0:
                print("*** No clips selected on the track ***")
            else:
                for shot in selected_clips:
                    # Obtener el file path del clip seleccionado
                    file_path = shot.source().mediaSource().fileinfos()[0].filename()
                    print("Original file path:", file_path)

                    # Obtener la nueva ruta del proyecto
                    project_path = self.get_project_path(file_path)
                    print("Project path:", project_path)

                    # Abre el explorador de archivos en la nueva ruta del proyecto
                    try:
                        os.startfile(project_path)
                        print("Revealed in explorer successfully.")
                    except Exception as e:
                        print(f"Error revealing in explorer: {e}")
        except Exception as e:
            print(f"Error: {e}")

    # Metodo para obtener la ruta del proyecto
    def get_project_path(self, file_path):
        # Dividir el path en partes usando '/' como separador
        path_parts = file_path.split('/')
        # Construir la nueva ruta agregando '/Comp/1_projects'
        project_path = '/'.join(path_parts[:4]) + '/Comp/1_projects'
        return project_path



class CleanUnusedAction:

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

    def CleanUnused(self) :

        # Get the active project
        project = get_active_project()

        # Build a list of Projects
        SEQS = hiero.core.findItems(project, "Sequences")

        # Build a list of Clips
        CLIPSTOREMOVE = hiero.core.findItems(project, "Clips")


        if len(SEQS)==0:
            # Present Dialog Asking if User wants to remove Clips
            msgBox = QMessageBox()
            msgBox.setText("Clean Unused Clips");
            msgBox.setInformativeText("You have no Sequences in this Project. Do you want to remove all Clips (%i) from Project: %s?" % (len(CLIPSTOREMOVE), project.name()));
            msgBox.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel);
            msgBox.setDefaultButton(QMessageBox.Ok);
            ret = msgBox.exec_()
            if ret == QMessageBox.Cancel:
                print('Not purging anything.')
            elif ret == QMessageBox.Ok:
                with project.beginUndo('Clean Unused Clips'):
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
        msgBox.setText("Clean Unused Clips");
        msgBox.setInformativeText("Remove %i unused Clips from Project %s?" % (len(CLIPSTOREMOVE), project.name()));
        msgBox.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel);
        msgBox.setDefaultButton(QMessageBox.Ok);
        ret = msgBox.exec_()

        if ret == QMessageBox.Cancel:
             print('Cancel')
             return
        elif ret == QMessageBox.Ok:
            BINS = []
            with project.beginUndo('Clean Unused Clips'):
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
            title = "Clean Unused Clips"
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




# Crear la instancia del widget y anadirlo al gestor de ventanas de Hiero
reconnectWidget = ReconnectMediaWidget()
wm = hiero.ui.windowManager()
wm.addWindow(reconnectWidget)
