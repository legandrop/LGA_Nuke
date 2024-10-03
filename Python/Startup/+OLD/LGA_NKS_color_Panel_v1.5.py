"""
______________________

  LGA_colorPanel v1.5
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



    def change_clip_color(self, color):
        try:
            seq = hiero.ui.activeSequence()
            if seq:  # Asegurarse de que hay una secuencia activa
                te = hiero.ui.getTimelineEditor(seq)
                selected_items = te.selection()
                project = hiero.core.projects()[0]
                project.beginUndo("Change Clip Color")

                # Iterar sobre los clips seleccionados y cambiar su color
                for item in selected_items:
                    if isinstance(item, hiero.core.EffectTrackItem):  # Verificar si es un efecto
                        #print(f"Ignore effect item: {item.name()}")
                        pass
                    else:
                        bin_item = item.source().binItem()
                        if item.source().mediaSource().isMediaPresent():
                            active_version = bin_item.activeVersion()
                            if active_version:
                                bin_item.setColor(color) # Aplica el color al BinItem
                                #print(f"Color changed for active version of clip: {item.name()}")
                            else:
                                #print(f"No active version found for clip: {item.name()}")
                                pass
                        else:
                            #print(f"No media present for clip: {item.name()}")
                            pass
                project.endUndo()
            else:
                print("No active sequence found.")
        except Exception as e:
            print(f"\nError during operation: {e}")                

# Crear la instancia del widget y anadirlo al gestor de ventanas de Hiero
colorChanger = ColorChangeWidget()
wm = hiero.ui.windowManager()
wm.addWindow(colorChanger)
