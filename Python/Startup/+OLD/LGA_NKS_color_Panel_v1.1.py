import hiero.ui
from PySide2.QtWidgets import *
from PySide2.QtGui import QColor

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
        import hiero.core
        import hiero.ui
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
                    print("File path:", file_path)

                    # Reemplazar el clip por el del file path
                    try:
                        shot.replaceClips(file_path)
                        print("Clip replaced successfully.")
                    except:
                        print("Error replacing clip.")

                    # Cambiar el color del clip
                    shot.source().binItem().setColor(color)
                    print(f"Color changed for clip: {shot.name()}")
        except Exception as e:
            print(f"Error changing color: {e}")


# Crear la instancia del widget y anadirlo al gestor de ventanas de Hiero
colorChanger = ColorChangeWidget()
wm = hiero.ui.windowManager()
wm.addWindow(colorChanger)
