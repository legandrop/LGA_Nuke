"""
______________________________________________

  LGA_toolsPanel v1.7 - 2024 - Lega Pugliese
  Tools panel for Hiero / Nuke Studio
______________________________________________

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



class ReconnectMediaWidget(QWidget):
    def __init__(self):
        super(ReconnectMediaWidget, self).__init__()

        self.setObjectName("com.lega.toolPanel")
        self.setWindowTitle("Tools")
        self.setStyleSheet("QToolTip { color: #ffffff; background-color: #2a2a2a; border: 1px solid white; }")

        self.layout = QGridLayout(self)  # Usamos QGridLayout en lugar de QVBoxLayout
        self.setLayout(self.layout)

        # Crear el organizador
        self.organizer = OrganizeProject()

        # Crear botones y agregarlos al layout
        self.buttons = [
            ("Reconnect T > N", self.reconnect_t_to_n, "#1f1f1f"),
            ("Reconnect N > T", self.reconnect_n_to_t, "#1f1f1f"),
            ("Reconnect Media", self.reconnectMediaFromTimeline, "#1f1f1f", "Alt+M", "Alt+M"),
            ("Self ReplaceClip", self.SelfReaplaceClip, "#1f1f1f"),
            ("Organize Project", self.organizer.organize_project, "#191f28"),
            ("Clean Project", self.clean_project, "#191f28"),
            ("Set Shot Name", self.set_shot_name, "#191f28"),
            ("Extend &Edit", self.extend_edit_to_playhead, "#191f28", "Alt+E", "Alt+E"),
            ("Rec709 | Clip", self.rec709_clip, "#191f28"),
            ("Rec709 | Viewer", self.rec709_viewer, "#191f28"),
            ("Reveal in &Explorer", self.reveal_in_explorer, "#261e1a", "Shift+E", "Shift+E"),
            ("Reveal Project", self.reveal_project, "#261e1a"),
            ("Reveal Sc&ript", self.reveal_script, "#261e1a", "Shift+R", "Shift+R"),
            ("OpenIn&NukeX", self.open_in_nukex_main, "#261e1a", "Shift+N", "Shift+N")
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




####### Reconnect
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

    def reconnectMediaFromTimeline(self): 
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


#### SelfReaplaceClip
    def get_full_bin_path(self, bin_item):
        path = []
        while bin_item:
            if isinstance(bin_item, hiero.core.Bin):
                path.append(bin_item.name())
            bin_item = bin_item.parentBin() if hasattr(bin_item, 'parentBin') else None
        return '/'.join(reversed(path))

    def find_or_create_bin(self, project, bin_path):
        """
        Encuentra un bin existente o crea uno nuevo si no existe.

        Args:
        - project (hiero.core.Project): El proyecto actual en Hiero.
        - bin_path (str): La ruta del bin.

        Returns:
        - hiero.core.Bin: El bin encontrado o creado.
        """
        # Dividir la ruta en partes
        bin_names = bin_path.split('/')

        # Empezar desde el bin de clips
        current_bin = project.clipsBin()

        # Iterar sobre las partes de la ruta
        for bin_name in bin_names:
            found_bin = None
            # Buscar el bin actual por su nombre
            for item in current_bin.items():
                if isinstance(item, hiero.core.Bin) and item.name() == bin_name:
                    found_bin = item
                    break
            # Si no se encontro el bin, crear uno nuevo
            if not found_bin:
                found_bin = hiero.core.Bin(bin_name)
                current_bin.addItem(found_bin)
            current_bin = found_bin

        return current_bin

    def move_clip_to_bin(self, project, clip_name, source_bin_name, target_bin_path, shot):
        """
        Mueve un clip de un bin de origen a un bin de destino en el proyecto.

        Args:
        - project (hiero.core.Project): El proyecto actual en Hiero.
        - clip_name (str): El nombre del clip que se movera.
        - source_bin_name (str): El nombre del bin de origen que contiene el clip.
        - target_bin_path (str): La ruta del bin de destino donde se movera el clip.
        """
        # Buscar el bin de origen por su nombre
        source_bin = None
        for bin_item in project.clipsBin().items():
            if bin_item.name() == source_bin_name:
                source_bin = bin_item
                break

        if source_bin:
            # Buscar el clip por su nombre dentro del bin de origen
            clip_to_move = None
            for clip_item in source_bin.items():
                if clip_item.name() == clip_name:
                    clip_to_move = clip_item
                    break

            if clip_to_move:
                # Encontrar o crear el bin de destino
                target_bin = self.find_or_create_bin(project, target_bin_path)

                # Remover el clip del bin de origen
                source_bin.removeItem(clip_to_move)

                # Remover el clip del bin original (no me esta funcionando)
                original_bin_item = shot.source().binItem()
                original_bin = original_bin_item.parentBin()
                #original_bin.removeItem(original_bin_item)    
                
                # Agregar el clip al bin de destino
                target_bin.addItem(clip_to_move)
                print("Se movio el clip '{}' del bin '{}' al bin '{}'.".format(clip_name, source_bin_name, target_bin_path))
            else:
                print("No se encontro el clip '{}' en el bin de origen '{}'.".format(clip_name, source_bin_name))
        else:
            print("No se encontro el bin de origen '{}'.".format(source_bin_name))
    

    def SelfReaplaceClip(self):
        # Obtener el proyecto actual en Hiero
        project = hiero.core.projects()[0] if hiero.core.projects() else None
        try:
            seq = hiero.ui.activeSequence()
            if not seq:
                print("No active sequence found.")
                return

            te = hiero.ui.getTimelineEditor(seq)
            selected_clips = te.selection()
            project = hiero.core.projects()[0]
            project.beginUndo("Change Clip Color")

            if len(selected_clips) == 0:
                print("*** No clips selected on the track ***")
            else:


                for shot in selected_clips:
                    if isinstance(shot, hiero.core.EffectTrackItem):  # Verificar si es un efecto
                        print(f"Ignore effect item: {shot.name()}")
                    else:            
                    
                        file_path = shot.source().mediaSource().fileinfos()[0].filename()
                        print("File path:", file_path)

                        bin_item = shot.source().binItem()
                        full_bin_path = self.get_full_bin_path(bin_item)
                        full_bin_path = full_bin_path.replace("Sequences/", "")
                        print("Full bin path for the clip:", full_bin_path)

                        try:
                            shot.replaceClips(file_path)
                            print("Clip replaced successfully.")
                        except:
                            print("Error replacing clip.")


                        
                        new_clip_name = shot.source().name()
                        print(f"Clip name: {new_clip_name}")

                        conform_bin_name = "Conform"
                        original_bin_name = full_bin_path.split(' > ')[-1]
                        self.move_clip_to_bin(project, new_clip_name, conform_bin_name, full_bin_path, shot)


            project.endUndo()
        except Exception as e:
            print(f"Error during operation: {e}")


####### Shot name
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

##### Extend edit
    def extend_edit_to_playhead(self):
        seq = hiero.ui.activeSequence()
        if not seq:
            print("\nNo active sequence found.")
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
                    print(f"DST Out extended to {playhead_frame + 1} for clip: {shot.name()}")
                except Exception as e:
                    print(f"Error setting DST Out: {e}")
        else:
            print("No clips selected or playhead position unavailable.")

##### Rec 709 en clips seleccionados
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
                    print("Color transform changed successfully.")
                except Exception as e:
                    print("Error changing color transform:", e)
        else:
            print("No active sequence found.")

##### Rec 709 en viewer
    def rec709_viewer(self):
        hiero.ui.currentViewer().player().setLUT('ACES/Rec.709')
        

##### Clean Project
    def clean_project(self):
        try:
            clean_action = CleanUnusedAction()
            clean_action.CleanUnused()
        except Exception as e:
            print(f"Error during project cleaning: {e}")

##### Reveal in explorer
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
                    if isinstance(shot, hiero.core.EffectTrackItem):  # Verificar si es un efecto
                        #print(f"Ignore effect item: {item.name()}")
                        pass  
                    else:
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

##### Reveal 
    def reveal_project(self):
        # Obtener el proyecto activo
        project = get_active_project()
        if project:
            # Obtener el directorio del proyecto activo
            project_path = project.path()

            # Imprimir el directorio del proyecto activo
            print("El directorio del proyecto activo es:", project_path)

            # Abre el explorador de archivos en el directorio del proyecto
            try:
                os.startfile(os.path.dirname(project_path))
                print("Revealed in explorer successfully.")
            except:
                print("Error revealing in explorer.")
        else:
            print("No se encontro un proyecto activo en Hiero.")

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
                    if isinstance(shot, hiero.core.EffectTrackItem):  # Verificar si es un efecto
                        #print(f"Ignore effect item: {item.name()}")
                        pass  
                    else:
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
            

##### OpenInNukeX
    def open_in_nukex_main(self):
        seq = hiero.ui.activeSequence()
        if seq:  # Asegurarse de que hay una secuencia activa
            te = hiero.ui.getTimelineEditor(seq)
            selected_clips = te.selection()

            if selected_clips:  # Verificar si hay clips seleccionados
                # Tomar solo el primer clip seleccionado
                shot = selected_clips[0]
                file_path = shot.source().mediaSource().fileinfos()[0].filename()
                project_path = self.get_project_path(file_path)
                script_name = self.get_script_name(file_path)
                script_full_path = os.path.join(project_path, script_name)

                # Verificar si el archivo existe y abrir en Nuke si es asi
                if os.path.exists(script_full_path):
                    self.open_nuke_script(script_full_path)
                else:
                    #show_message("Error", f"File not found: \n\n{script_full_path}") 
                    formatted_message = "<div style='text-align: left;'><b>File not found</b><br><br>" + script_full_path + "</div>"
                    self.show_message("Error", formatted_message)            
        else:
            show_message("Error", "No active sequence found.")

    def show_message(self, title, message, duration=None):
        msgBox = QtWidgets.QMessageBox()
        msgBox.setWindowTitle(title)
        # Interpretar el mensaje como HTML si incluye etiquetas, de lo contrario como texto normal
        if '<' in message and '>' in message:
            msgBox.setTextFormat(QtCore.Qt.TextFormat.RichText)  # Interpretar como HTML
        else:
            msgBox.setTextFormat(QtCore.Qt.TextFormat.PlainText)  # Interpretar como texto normal
        msgBox.setText(message)
        msgBox.setStandardButtons(QtWidgets.QMessageBox.Ok)
        if duration:
            QtCore.QTimer.singleShot(duration, msgBox.close)
        msgBox.exec_()

    def show_timed_message(sef, title, message, duration):
        msgBox = TimedMessageBox(title, message, duration)
        msgBox.exec_()

    # Funcion para obtener la ruta del proyecto
    def get_project_path(self, file_path):
        # Dividir el path en partes usando '/' como separador
        path_parts = file_path.split('/')
        # Construir la nueva ruta agregando '/Comp/1_projects'
        project_path = '/'.join(path_parts[:4]) + '/Comp/1_projects'
        return project_path

    # Funcion para obtener el nombre del archivo del script relacionado con el clip
    def get_script_name(self, file_path):
        # Extraer el nombre del archivo del path completo
        script_name = os.path.basename(file_path)
        # Eliminar la extension y cualquier secuencia de frame como %04d
        script_name = re.sub(r'_%\d+?d\.exr$', '', script_name)  # Ajusta la expresion regular segun necesidad
        return script_name + '.nk'  # Anadir la extension correcta de Nuke

    # Funcion para abrir Nuke Studio o NukeX si la conexion falla
    def open_nuke_script(self, nk_filepath):
        host = 'localhost'
        port = 54325
        nuke_path = "C:/Program Files/Nuke15.0v4/Nuke15.0.exe"

        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(10)
                s.connect((host, port))
                # Enviar un comando 'ping'
                s.sendall("ping".encode())
                # Esperar una respuesta para confirmar que NukeX esta operativo
                response = s.recv(1024).decode()
                if "pong" in response:
                    print("NukeX is active and responding.")
                    # Cerrar el socket anterior y abrir uno nuevo para enviar el comando de ejecucion
                    s.close()
                    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as new_socket:
                        new_socket.connect((host, port))
                        normalized_path = os.path.normpath(nk_filepath).replace('\\', '/')
                        full_command = f"run_script||{normalized_path}"
                        new_socket.sendall(full_command.encode())
                        self.show_timed_message(
                            "OpenInNukeX", 
                            (
                                f"<div style='text-align: center;'>"
                                f"<span>Opening</span><br>"
                                f"<span style='font-style: italic; color: #9f9f9f; font-size: 0.9em;'>{os.path.basename(nk_filepath)}</span><br><br>"
                                f"<span style='color:white;'>Please switch to the NukeX window...</span>"
                                f"</div>"
                            ),
                            5000
                        )
                        return

                else:
                    raise Exception("NukeX is not responding as expected.")
        except (socket.timeout, ConnectionRefusedError, Exception) as e:
            # Si no se puede establecer la conexion o no se recibe la respuesta esperada, intentar abrir NukeX directamente
            command = f'"{nuke_path}" --nukex "{nk_filepath}"'
            subprocess.Popen(command, shell=True)
            self.show_timed_message(
                "Error", 
                (
                    f"<span style='color:white;'><b>Failed to connect to NukeX</b></span><br><br>"
                    f"Opening a new NukeX instance<br>"
                    f"<span style='font-style: italic; color: #9f9f9f; font-size: 0.9em;'>{nuke_path}</span>"
                ), 
                5000
            )
        except ConnectionResetError:
            self.show_message("Error", "The connection was closed by the server.")

            

class TimedMessageBox(QtWidgets.QMessageBox):
    def __init__(self, title, message, duration):
        super().__init__()
        self.setWindowTitle(title)
        self.setText(message)
        self.setStandardButtons(QtWidgets.QMessageBox.Ok)

        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.updateButton)
        self.timeLeft = duration // 1000  # Convert milliseconds to seconds
        self.timer.start(1000)  # Update every second

        self.updateButton()  # Initialize the button text

    def updateButton(self):
        if self.timeLeft > 0:
            self.button(QtWidgets.QMessageBox.Ok).setText(f"OK ({self.timeLeft})")
            self.timeLeft -= 1
        else:
            self.timer.stop()
            self.accept()  # Close the message box automatically



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
            print("No se encontro un proyecto abierto en Hiero.")


# Crear la instancia del widget y anadirlo al gestor de ventanas de Hiero
reconnectWidget = ReconnectMediaWidget()
wm = hiero.ui.windowManager()
wm.addWindow(reconnectWidget)