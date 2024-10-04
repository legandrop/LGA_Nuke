"""
_________________________________________

  LGA_EditToolsPanel v2.5 - 2024 - Lega
  Tools panel for Hiero / Nuke Studio
_________________________________________

"""


import hiero.ui
import hiero.core
import os
import re
import subprocess
import socket
import PySide2, hiero
from PySide2.QtWidgets import *
from PySide2.QtGui import QIcon
from PySide2.QtCore import *
from PySide2 import QtWidgets, QtCore

# Variable global para activar o desactivar los prints
DEBUG = False

def debug_print(*message):
    if DEBUG:
        print(*message)

class ReconnectMediaWidget(QWidget):
    def __init__(self):
        super(ReconnectMediaWidget, self).__init__()

        self.setObjectName("com.lega.toolPanel")
        self.setWindowTitle("Edit")
        self.setStyleSheet("QToolTip { color: #ffffff; background-color: #2a2a2a; border: 1px solid white; }")

        self.layout = QGridLayout(self)  # Usamos QGridLayout en lugar de QVBoxLayout
        self.setLayout(self.layout)

        # Crear el organizador
        self.organizer = OrganizeProject()

        # Crear botones y agregarlos al layout
        self.buttons = [
            ("Organize Project", self.organizer.organize_project, "#283548"),
            ("Clean Project", self.clean_project, "#283548"),
            ("Rec709 | Clip", self.rec709_clip, "#434c41"),
            ("Default | Clip", self.default_clip, "#434c41"),
            ("Set Shot Name", self.set_shot_name, "#453434"),
            ("Extend &Edit", self.extend_edit_to_playhead, "#453434", "Alt+E", "Alt+E"),
            ("Reconnect T > N", self.reconnect_t_to_n, "#4a4329"),
            ("Reconnect N > T", self.reconnect_n_to_t, "#4a4329"),
            ("Reconnect Media", self.reconnectMediaFromTimeline, "#4a4329", "Alt+M", "Alt+M"),
            ]

        self.num_columns = 1  # Inicialmente una columna
        self.create_buttons()

        # Conectar la senal de cambio de tamano del widget al metodo correspondiente
        self.adjust_columns_on_resize()
        self.resizeEvent = self.adjust_columns_on_resize

    def create_buttons(self):
        for index, button_info in enumerate(self.buttons):
            name = button_info[0]
            handler = button_info[1]
            style = button_info[2]
            shortcut = button_info[3] if len(button_info) > 3 else None
            tooltip = button_info[4] if len(button_info) > 4 else None

            button = QPushButton(name)
            button.setStyleSheet(f"background-color: {style}")
            button.clicked.connect(handler)
            if shortcut:
                button.setShortcut(shortcut)
            if tooltip:
                button.setToolTip(tooltip)

            row = index // self.num_columns
            column = index % self.num_columns
            self.layout.addWidget(button, row, column)

    def adjust_columns_on_resize(self, event=None):
        # Obtener el ancho actual del widget
        panel_width = self.width()
        button_width = 120  # Ancho aproximado de cada boton
        min_button_spacing = 10  # Espacio minimo entre botones

        # Calcular el numero de columnas en funcion del ancho del widget
        self.num_columns = max(1, (panel_width + min_button_spacing) // (button_width + min_button_spacing))

        # Limpiar el layout actual y eliminar widgets solo si existen
        while self.layout.count():
            item = self.layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

        # Volver a crear los botones con el nuevo numero de columnas
        self.create_buttons()

        # Calcular el numero de filas usadas
        num_rows = (len(self.buttons) + self.num_columns - 1) // self.num_columns

        # Anadir el espaciador vertical
        spacer = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)
        self.layout.addItem(spacer, num_rows, 0, 1, self.num_columns)


###### Rec 709 en clips seleccionados
    def rec709_clip(self):
        # Obtener la secuencia activa y el editor de linea de tiempo
        seq = hiero.ui.activeSequence()
        if seq:  # Asegurarse de que hay una secuencia activa
            te = hiero.ui.getTimelineEditor(seq)
            selected_clips = te.selection()

            # Iterar sobre los clips seleccionados para cambiar el color transform
            for clip in selected_clips:
                try:
                    clip.setSourceMediaColourTransform("Output - Rec.709")
                    debug_print("Color transform changed successfully.")
                except Exception as e:
                    debug_print("Error changing color transform:", e)
        else:
            debug_print("No active sequence found.")

###### Default space color en clips seleccionados
    def default_clip(self):
        # Obtener la secuencia activa y el editor de linea de tiempo
        seq = hiero.ui.activeSequence()
        if seq:  # Asegurarse de que hay una secuencia activa
            te = hiero.ui.getTimelineEditor(seq)
            selected_clips = te.selection()

            # Iterar sobre los clips seleccionados para cambiar el color transform
            for clip in selected_clips:
                try:
                    clip.setSourceMediaColourTransform("default")
                    debug_print("Color transform changed successfully.")
                except Exception as e:
                    debug_print("Error changing color transform:", e)
        else:
            debug_print("No active sequence found.")




###### Shot name
    def set_shot_name(self):
        try:
            project = hiero.core.projects()[-1]
            with project.beginUndo("Set Shot Name"):
                seq = hiero.ui.activeSequence()
                if not seq:
                    debug_print("No active sequence found.")
                    return

                te = hiero.ui.getTimelineEditor(seq)
                selected_clips = te.selection()

                if len(selected_clips) == 0:
                    debug_print("*** No clips selected on the track ***")
                else:
                    for shot in selected_clips:
                        # Obtener el file path del clip seleccionado
                        file_path = shot.source().mediaSource().fileinfos()[0].filename()
                        debug_print("Original file path:", file_path)

                        # Obtener el nombre del plano del path del clip
                        shot_name = self.get_shot_name(file_path)
                        debug_print("Shot name:", shot_name)

                        # Cambiar el nombre del plano al clip seleccionado
                        shot.setName(shot_name)
                        debug_print("Shot name changed successfully.")
        except Exception as e:
            debug_print(f"Error: {e}")

    def get_shot_name(self, file_path):
        # Dividir el path en partes usando '/' como separador
        path_parts = file_path.split('/')
        # El shot name seria la tercera parte del path
        shot_name = path_parts[3]
        return shot_name


###### Extend edit
    def extend_edit_to_playhead(self):
        seq = hiero.ui.activeSequence()
        if not seq:
            debug_print("\nNo active sequence found.")
            return
            
        te = hiero.ui.getTimelineEditor(seq)
        selected_clips = te.selection()
        
        current_viewer = hiero.ui.currentViewer()
        player = current_viewer.player() if current_viewer else None
        playhead_frame = player.time() if player else None

        if selected_clips and playhead_frame is not None:
            for shot in selected_clips:
                try:
                    shot.setTimelineOut(playhead_frame + 1)
                    debug_print(f"DST Out extended to {playhead_frame + 1} for clip: {shot.name()}")
                except Exception as e:
                    debug_print(f"Error setting DST Out: {e}")
        else:
            debug_print("No clips selected or playhead position unavailable.")


###### Reconnect
    def reconnect_t_to_n(self):
        try:
            project = hiero.core.projects()[-1]
            project.beginUndo("Reconnect T > N")
            try:
                self.reconnect_media("t:", "n:")
            except Exception as e:
                debug_print(f"Error: {e}")
            project.endUndo()
        except Exception as e:
            debug_print(f"Error: {e}")

    def reconnect_n_to_t(self):
        try:
            project = hiero.core.projects()[-1]
            with project.beginUndo("Reconnect N > T"):
                self.reconnect_media("n:", "t:")
        except Exception as e:
            debug_print(f"Error: {e}")
        finally:
            if project.undoStack().canEnd():
                project.endUndo()
            else:
                debug_print("No current undo item to end.")

    def reconnect_media(self, old_prefix, new_prefix):
        try:
            seq = hiero.ui.activeSequence()
            if not seq:
                debug_print("No active sequence found.")
                return

            te = hiero.ui.getTimelineEditor(seq)
            selected_clips = te.selection()

            if len(selected_clips) == 0:
                debug_print("*** No clips selected on the track ***")
            else:
                for shot in selected_clips:
                    # Obtener el file path del clip seleccionado
                    file_path = shot.source().mediaSource().fileinfos()[0].filename()
                    debug_print("Original file path:", file_path)

                    # Normalizar el path convirtiendo todo a minusculas
                    normalized_file_path = file_path.lower()

                    # Reemplazar el prefijo antiguo por el nuevo
                    new_file_path = normalized_file_path.replace(old_prefix, new_prefix)
                    debug_print("Modified file path:", new_file_path)

                    # Obtener solo la ruta del directorio sin el nombre del archivo
                    directory_path = os.path.dirname(new_file_path)

                    # Reemplazar el clip por el del nuevo path
                    try:
                        shot.reconnectMedia(directory_path)
                        debug_print("Clip reconnected successfully.")
                    except Exception as e:
                        debug_print(f"Error reconnecting clip: {e}")
        except Exception as e:
            debug_print(f"Error: {e}")

    def reconnectMediaFromTimeline(self): 
        seq = hiero.ui.activeSequence()
        if not seq:
            debug_print("\nNo active sequence found.")
            return
            
        te = hiero.ui.getTimelineEditor(seq)
        selected_track_items = te.selection()

        if len(selected_track_items) == 0:
            debug_print("*** No track items selected ***")
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






###### Clean Project
    def clean_project(self):
        try:
            clean_action = CleanUnusedAction()
            clean_action.CleanUnused()
        except Exception as e:
            debug_print(f"Error during project cleaning: {e}")

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
                debug_print('Not purging anything.')
            elif ret == QMessageBox.Ok:
                with project.beginUndo('Clean Unused Clips'):
                    BINS = []
                    for clip in CLIPSTOREMOVE:
                        BI = clip.binItem()
                        B = BI.parentBin()
                        BINS+=[B]
                        debug_print('Removing:', BI)
                        try:
                            B.removeItem(BI)
                        except:
                            debug_print('Unable to remove:', BI)
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
             debug_print('Cancel')
             return
        elif ret == QMessageBox.Ok:
            BINS = []
            with project.beginUndo('Clean Unused Clips'):
                # Delete the rest of the Clips
                for clip in CLIPSTOREMOVE:
                    BI = clip.binItem()
                    B = BI.parentBin()
                    BINS+=[B]
                    debug_print('Removing:', BI)
                    try:
                        B.removeItem(BI)
                    except:
                        debug_print('Unable to remove:', BI)

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


##### Organize Project
class OrganizeProject:
    def find_or_create_bin(self, root_bin, bin_name):
        for item in root_bin.items():
            if isinstance(item, hiero.core.Bin) and item.name() == bin_name:
                return item
        new_bin = hiero.core.Bin(bin_name)
        root_bin.addItem(new_bin)
        return new_bin

    def move_clips_from_bin(self, bin_item):
        if bin_item.name() == "Published":  # Ignorar el bin 'Published' y sus subcarpetas
            return
        for item in bin_item.items():
            if isinstance(item, hiero.core.BinItem) and isinstance(item.activeItem(), hiero.core.Clip):
                clip = item.activeItem()
                media_source = clip.mediaSource()
                if media_source and media_source.fileinfos():
                    file_path = media_source.fileinfos()[0].filename()
                    parts = file_path.split('/')
                    if len(parts) > 3:
                        folder_name = f"F {parts[2]}"
                        shot_name = parts[3]
                        folder_bin = self.find_or_create_bin(self.project.clipsBin(), folder_name)
                        shot_bin = self.find_or_create_bin(folder_bin, shot_name)
                        clip_item = clip.binItem()
                        if clip_item.parentBin() != shot_bin:
                            clip_item.parentBin().removeItem(clip_item)
                            shot_bin.addItem(clip_item)
            elif isinstance(item, hiero.core.Bin):
                self.move_clips_from_bin(item)

    def clean_empty_bins(self, bin_item):
        if bin_item.name() == "Published":
            return
        items_to_check = list(bin_item.items())
        for item in items_to_check:
            if isinstance(item, hiero.core.Bin):
                self.clean_empty_bins(item)
        if not bin_item.items() and bin_item.parentBin():
            bin_item.parentBin().removeItem(bin_item)

    def move_clips_based_on_path(self, project):
        self.project = project
        with project.beginUndo('Reorganize Clips Based on Path'):
            for bin_item in project.clipsBin().items():
                if isinstance(bin_item, hiero.core.Bin):
                    self.move_clips_from_bin(bin_item)

            for bin_item in list(project.clipsBin().items()):
                if isinstance(bin_item, hiero.core.Bin):
                    self.clean_empty_bins(bin_item)

    def organize_project(self):
        project = hiero.core.projects()[0] if hiero.core.projects() else None
        if project:
            self.move_clips_based_on_path(project)
        else:
            debug_print("No se encontro un proyecto abierto en Hiero.")


# Crear la instancia del widget y anadirlo al gestor de ventanas de Hiero
reconnectWidget = ReconnectMediaWidget()
wm = hiero.ui.windowManager()
wm.addWindow(reconnectWidget)
