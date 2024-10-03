import hiero.ui
from PySide2.QtWidgets import *
import os

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


# Crear la instancia del widget y anadirlo al gestor de ventanas de Hiero
reconnectWidget = ReconnectMediaWidget()
wm = hiero.ui.windowManager()
wm.addWindow(reconnectWidget)
