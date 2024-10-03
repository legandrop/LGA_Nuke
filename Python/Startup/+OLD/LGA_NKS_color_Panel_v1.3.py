"""
______________________

LGA_colorPanel v1.3
______________________
"""


import hiero.ui
import hiero.core
from PySide2.QtWidgets import *
from PySide2.QtGui import QColor
import os

class ColorChangeWidget(QWidget):
    def __init__(self):
        super(ColorChangeWidget, self).__init__()

        self.setObjectName("com.lega.colorChangePanel")
        self.setWindowTitle("ClipColor")

        self.setLayout(QVBoxLayout())


        self.v_00_button = QPushButton('v_00')
        self.v_00_button.setStyleSheet("background-color: #8a8a8a")
        self.v_00_button.clicked.connect(lambda: self.change_clip_color(QColor(138, 138, 138)))
        self.layout().addWidget(self.v_00_button)
        
        self.Corrections_button = QPushButton('Corrections')
        self.Corrections_button.setStyleSheet("background-color: #2e77d4")
        self.Corrections_button.clicked.connect(lambda: self.change_clip_color(QColor(46, 119, 212)))
        self.layout().addWidget(self.Corrections_button)
       
        self.LegaCorrs_button = QPushButton('Corrs Lega')
        self.LegaCorrs_button.setStyleSheet("background-color: #69135e")
        self.LegaCorrs_button.clicked.connect(lambda: self.change_clip_color(QColor(105, 19, 94)))   
        self.layout().addWidget(self.LegaCorrs_button)        

        self.Rev_Sup_button = QPushButton('Rev_Sup')
        self.Rev_Sup_button.setStyleSheet("background-color: #a3557e")
        self.Rev_Sup_button.clicked.connect(lambda: self.change_clip_color(QColor(163, 85, 126)))
        self.layout().addWidget(self.Rev_Sup_button)

        self.Rev_Dir_button = QPushButton('Rev_Dir')
        self.Rev_Dir_button.setStyleSheet("background-color: #c79bb7")
        self.Rev_Dir_button.clicked.connect(lambda: self.change_clip_color(QColor(199, 155, 183)))
        self.layout().addWidget(self.Rev_Dir_button)

        self.Approved_button = QPushButton('Approved')
        self.Approved_button.setStyleSheet("background-color: #5cb849")
        self.Approved_button.clicked.connect(lambda: self.change_clip_color(QColor(92, 184, 73)))
        self.layout().addWidget(self.Approved_button)

        self.Rev_Sup_D_button = QPushButton('Rev_Sup_D')
        self.Rev_Sup_D_button.setStyleSheet("background-color: #523d80")
        self.Rev_Sup_D_button.clicked.connect(lambda: self.change_clip_color(QColor(82, 61, 128)))
        self.layout().addWidget(self.Rev_Sup_D_button)

        self.Rev_Dir_D_button = QPushButton('Rev_Dir_D')
        self.Rev_Dir_D_button.setStyleSheet("background-color: #4d21a8")
        self.Rev_Dir_D_button.clicked.connect(lambda: self.change_clip_color(QColor(77, 33, 168)))
        self.layout().addWidget(self.Rev_Dir_D_button)

        self.Plate_button = QPushButton('Plate')
        self.Plate_button.setStyleSheet("background-color: #42616d")
        self.Plate_button.clicked.connect(lambda: self.change_clip_color(QColor(66, 97, 109)))
        self.layout().addWidget(self.Plate_button)

        self.EditRef_button = QPushButton('EditRef')
        self.EditRef_button.setStyleSheet("background-color: #aa9e54")
        self.EditRef_button.clicked.connect(lambda: self.change_clip_color(QColor(170, 158, 84)))
        self.layout().addWidget(self.EditRef_button)

        self.Pic_Mark_button = QPushButton('Pic_Mark')
        self.Pic_Mark_button.setStyleSheet("background-color: #80533d")
        self.Pic_Mark_button.clicked.connect(lambda: self.change_clip_color(QColor(128, 83, 61)))
        self.layout().addWidget(self.Pic_Mark_button)

        self.Error_button = QPushButton('Error')
        self.Error_button.setStyleSheet("background-color: #611313")
        self.Error_button.clicked.connect(lambda: self.change_clip_color(QColor(97, 19, 19)))
        self.layout().addWidget(self.Error_button)
        

        # Agregar un espaciador vertical al final
        self.layout().addStretch()       

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
                print("\nSe movio el clip '{}' del bin '{}' al bin '{}'.".format(clip_name, source_bin_name, target_bin_path))
            else:
                print("\nNo se encontro el clip '{}' en el bin de origen '{}'.".format(clip_name, source_bin_name))
        else:
            print("\nNo se encontro el bin de origen '{}'.".format(source_bin_name))

    # Obtener el proyecto actual en Hiero
    project = hiero.core.projects()[0] if hiero.core.projects() else None

    def change_clip_color(self, color):
        try:
            seq = hiero.ui.activeSequence()
            if not seq:
                print("\nNo active sequence found.")
                return

            te = hiero.ui.getTimelineEditor(seq)
            selected_clips = te.selection()

            if len(selected_clips) == 0:
                print("*** No clips selected on the track ***")
            else:
                project = hiero.core.projects()[0]
                project.beginUndo("Change Clip Color")

                for shot in selected_clips:
                    
                    file_path = shot.source().mediaSource().fileinfos()[0].filename()
                    print("\nFile path:", file_path)

                    bin_item = shot.source().binItem()
                    full_bin_path = self.get_full_bin_path(bin_item)
                    full_bin_path = full_bin_path.replace("Sequences/", "")
                    print("\nFull bin path for the clip:", full_bin_path)

                    try:
                        shot.replaceClips(file_path)
                        print("\nClip replaced successfully.")
                    except:
                        print("\nError replacing clip.")


                    
                    new_clip_name = shot.source().name()
                    print(f"\nClip name: {new_clip_name}")

                    conform_bin_name = "Conform"
                    original_bin_name = full_bin_path.split(' > ')[-1]
                    self.move_clip_to_bin(project, new_clip_name, conform_bin_name, full_bin_path, shot)

                   

                    shot.source().binItem().setColor(color)
                    print(f"\nColor changed for clip: {new_clip_name}")

                project.endUndo()
        except Exception as e:
            print(f"\nError during operation: {e}")


# Crear la instancia del widget y anadirlo al gestor de ventanas de Hiero
colorChanger = ColorChangeWidget()
wm = hiero.ui.windowManager()
wm.addWindow(colorChanger)
