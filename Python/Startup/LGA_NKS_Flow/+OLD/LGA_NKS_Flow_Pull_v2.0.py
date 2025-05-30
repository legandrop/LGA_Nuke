"""
____________________________________________________________________________

  LGA_NKS_Flow_Pull v2.0 - 2024 - Lega Pugliese
  Compara los estados de las task Comp de los shots del timeline de Hiero 
  con los estados registrados en un archivo JSON basado en Flow PT
  
  Tambien aplica tags con los colores de los estados en xyplorer 
____________________________________________________________________________

"""

import json
import hiero.core
import hiero.ui
import os
import re
import nuke
import shotgun_api3
from PySide2.QtWidgets import QApplication, QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem, QHeaderView, QColorDialog, QMessageBox
from PySide2.QtWidgets import QStyledItemDelegate, QStyle
from PySide2.QtGui import QColor, QBrush, QScreen, QFont, QPalette
from PySide2.QtCore import Qt
import sys
import ctypes
import ctypes.wintypes
import platform




# Variable global para activar o desactivar los prints
DEBUG = False

def debug_print(message):
    if DEBUG:
        print(message)


def extract_version_number(version_str):
    """Extrae el numero de version numerico de un string de version."""
    match = re.search(r'_v(\d+)', version_str)
    if match:
        return int(match.group(1))
    return 0

class ShotGridManager:
    """Clase para manejar operaciones con datos de un archivo JSON en lugar de ShotGrid."""
    def __init__(self, json_path):
        with open(json_path, 'r', encoding='utf-8') as file:
            self.data = json.load(file)
        self.task_status_dict = {
            'apr': ('Approved', '#5cb849', 'Approved'),
            'enviad': ('Enviado', '#000000', 'Approved'),
            'wts': ('Waiting to start', '#000000', None),
            'corr': ('Corrections', '#2e77d4', 'Corrections'),
            'progre': ('In Progress', '#7d4cff', None),
            'noread': ('Not Ready To Start', '#000000', None),
            'rev': ('Pending Review', '#000000', None),
            'pubsh': ('Publish', '#244c19', 'Approved'),
            'pbshed': ('Published', '#244c19', 'Approved'),
            'ready': ('Ready To Start', '#8a8a8a', None),
            'rev_di': ('Review Dir', '#98c054', 'ReviewDir'),
            'revleg': ('Review Lega', '#69135e', 'Rev_Lega'),
            'rev_su': ('Review Sup', '#a3557e', 'Rev_Sup'),
            'vwd': ('Viewed', '#000000', None),
            'check': ('Delivery Checked', '#244c19', None)
        }

    def find_project(self, project_name):
        """Busca un proyecto por nombre en el JSON."""
        return next((p for p in self.data['projects'] if p['project_name'] == project_name), None)

    def find_shot(self, project_name, shot_code):
        """Busca un shot por nombre y codigo en el JSON."""
        project = self.find_project(project_name)
        if project:
            return next((s for s in project['shots'] if s['shot_name'] == shot_code), None)
        return None

    def find_task(self, shot, task_name):
        """Busca una tarea especifica por nombre en un shot."""
        return next((t for t in shot['tasks'] if t['task_type'].lower() == task_name.lower()), None)

    def find_highest_version_for_shot(self, shot):
        """Encuentra la version mas alta de un shot basandose en el JSON."""
        all_versions = []
        for task in shot['tasks']:
            all_versions.extend(task['versions'])
        if all_versions:
            highest_version = max(all_versions, key=lambda v: int(re.search(r'_v(\d+)', v['version_number']).group(1)))
            return highest_version
        return None



class GUI_Table(QWidget):
    def __init__(self, sg_manager, parent=None):
        super(GUI_Table, self).__init__(parent)
        self.sg_manager = sg_manager
        self.row_background_colors = []  # Lista para almacenar listas de colores de fondo por fila
        self.hiero_ops = None 
        self.initUI()
        self.last_selected_index = None  # Guardar el indice de la ultima fila seleccionada

    def set_hiero_ops(self, hiero_ops):
        self.hiero_ops = hiero_ops  # Assign instance of HieroOperations
        self.update_table()  # Now you can check for changes and display the table

    def update_table(self):
        if self.hiero_ops:
            changes_exist = self.hiero_ops.process_selected_clips(self.table, self.sg_manager)
            if changes_exist:
                self.adjust_window_size()
                self.show()
            else:
                QMessageBox.information(self, "No Changes", "No changes were detected in the selected shots.")

    def add_color_to_background_list(self, row_colors):
        """Agrega una lista de colores de fondo para una nueva fila."""
        self.row_background_colors.append(row_colors)

    def initUI(self):
        self.setWindowTitle("Read Nodes EXR Info")
        layout = QVBoxLayout(self)
        self.table = QTableWidget(0, 6, self)
        self.table.setHorizontalHeaderLabels(['Shot', ' v_NKS ', ' v_SG ', ' v_Status ', ' Previous Status ', ' New Status '])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setSelectionMode(QTableWidget.SingleSelection)
        self.table.verticalHeader().setVisible(False)
        self.table.setFocusPolicy(Qt.NoFocus)
        self.table.setStyleSheet("""
            QTableView::item:selected {
                color: black;
                background-color: transparent;  // Hacer transparente el fondo de los items seleccionados
            }
        """)

        # Asigna el delegado personalizado
        delegate = ColorMixDelegate(self.table, self.row_background_colors)
        self.table.setItemDelegate(delegate)

        layout.addWidget(self.table)
        self.setLayout(layout)
        font = QFont()
        font.setBold(True)
        self.table.horizontalHeader().setFont(font)

    def mix_colors(self, original_color, mix_color=(88, 88, 88)):
        """Mezcla dos colores RGB."""
        r1, g1, b1 = original_color
        r2, g2, b2 = mix_color
        mixed_color = ((r1 + r2) // 2, (g1 + g2) // 2, (b1 + b2) // 2)
        return mixed_color

    def adjust_window_size(self):
        # Ajustes para cambiar el tamano y posicion de la ventana de acuerdo a la pantalla
        self.table.horizontalHeader().setStretchLastSection(False)
        self.table.resizeColumnsToContents()
        width = self.table.verticalHeader().width() - 30
        for i in range(self.table.columnCount()):
            width += self.table.columnWidth(i) + 20
        screen = QApplication.primaryScreen()
        screen_rect = screen.availableGeometry()
        max_width = screen_rect.width() * 0.8
        final_width = min(width, max_width)
        height = self.table.horizontalHeader().height() + 20
        for i in range(self.table.rowCount()):
            height += self.table.rowHeight(i) + 4
        max_height = screen_rect.height() * 0.8
        final_height = min(height, max_height)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.resize(final_width, final_height)
        self.move((screen_rect.width() - final_width) // 2, (screen_rect.height() - final_height) // 2)

    def keyPressEvent(self, event):
        """Cierra la ventana cuando se presiona la tecla ESC."""
        if event.key() == Qt.Key_Escape:
            self.close()
        else:
            super(GUI_Table, self).keyPressEvent(event)



class ColorMixDelegate(QStyledItemDelegate):
    def __init__(self, table_widget, background_colors, mix_color=(88, 88, 88), parent=None):
        super(ColorMixDelegate, self).__init__(parent)
        self.table_widget = table_widget
        self.background_colors = background_colors
        self.mix_color = mix_color

    def paint(self, painter, option, index):
        row = index.row()
        column = index.column()
        if option.state & QStyle.State_Selected:
            original_color = QColor(self.background_colors[row][column])
            mixed_color = self.mix_colors((original_color.red(), original_color.green(), original_color.blue()), self.mix_color)
            option.palette.setColor(QPalette.Highlight, QColor(*mixed_color))
        else:
            original_color = QColor(self.background_colors[row][column])
            option.palette.setColor(QPalette.Base, original_color)
        
        super(ColorMixDelegate, self).paint(painter, option, index)

    def mix_colors(self, original_color, mix_color):
        r1, g1, b1 = original_color
        r2, g2, b2 = mix_color
        return ((r1 + r2) // 2, (g1 + g2) // 2, (b1 + b2) // 2)



class HieroOperations:
    """Clase para manejar operaciones en Hiero."""
    def __init__(self, shotgrid_manager, gui_table):
        self.sg_manager = shotgrid_manager
        self.gui_table = gui_table  # Almacenar la referencia a GUI_Table
        self.hiero_status_dict = {
            'v_00': '#8a8a8a',
            'Rev_Sup_D': '#523d80',
            'Rev_Dir_D': '#4d21a8'
        }

    def parse_exr_name(self, file_name):
        """Extrae el nombre base del archivo EXR y el numero de version con prefijo."""
        base_name = re.sub(r'_%04d\.exr$', '', file_name)
        version_match = re.search(r'(_v\d+)', base_name)
        version_str = version_match.group(1) if version_match else '_vUnknown'
        return base_name, version_str

    def get_current_clip_color(self, item):
        """Obtiene el color actual del clip."""
        bin_item = item.source().binItem()
        if item.source().mediaSource().isMediaPresent():
            active_version = bin_item.activeVersion()
            if active_version:
                current_color = bin_item.color()
                return current_color.name()  # Retorna el color en formato hexadecimal
        return None

    def add_row_to_table(self, table, gui_table, shot_code, version_number, prev_status, prev_color, new_status, new_color, sg_version_number, sg_status):
        row_count = table.rowCount()
        table.insertRow(row_count)
        
        # Extraer numeros de version de forma segura
        version_num = extract_version_number(version_number)
        sg_version_num = extract_version_number(sg_version_number)
        
        # Anadir un espacio al final de cada texto para mejorar la visualizacion
        shot_item = QTableWidgetItem(shot_code + "   ")
        version_item = QTableWidgetItem(str(version_num))
        sg_version_item = QTableWidgetItem(str(sg_version_num))
        sg_status_item = QTableWidgetItem(sg_status)
        prev_status_item = QTableWidgetItem(" " + prev_status + " ")
        new_status_item = QTableWidgetItem(new_status)

        # Centrado de algunas columnas
        version_item.setTextAlignment(Qt.AlignCenter)
        sg_version_item.setTextAlignment(Qt.AlignCenter)
        sg_status_item.setTextAlignment(Qt.AlignCenter)
        
        # Configuracion de color de fondo y texto para el nombre del shot
        """
        shot_color_bg = QColor('#323232')  # Color oscuro para el fondo
        shot_color_text = QColor('#c8c8c8')  # Texto blanco para mejor contraste
        shot_item.setBackground(QBrush(shot_color_bg))
        shot_item.setForeground(QBrush(shot_color_text))
        """
        
        # Configuracion del color de fondo para la columna v_SG basada en la condicion especifica
        if sg_version_num > version_num:  # Condicion para pintar la columna v_SG
            sg_version_item.setBackground(QBrush(QColor('#81395a')))
            sg_version_item.setForeground(QBrush(QColor('#c8c8c8')))  # Texto blanco para mejor contraste

        # Configuracion del color de fondo para la columna v_Status basada en la condicion especifica
        if sg_status == 'rev':  # Condicion para pintar la columna v_Status
            sg_status_item.setBackground(QBrush(QColor('#81395a')))
            sg_status_item.setForeground(QBrush(QColor('#c8c8c8')))  # Texto blanco para mejor contraste

        # Configuracion de colores para columna de estado previo y nuevo
        prev_status_bg_color = QColor(prev_color)
        prev_status_text_color = self.color_for_background(prev_color)
        prev_status_item.setBackground(QBrush(prev_status_bg_color))
        prev_status_item.setForeground(QBrush(prev_status_text_color))
        prev_status_item.setTextAlignment(Qt.AlignCenter)
        
        new_status_bg_color = QColor(new_color)
        new_status_text_color = self.color_for_background(new_color)
        new_status_item.setBackground(QBrush(new_status_bg_color))
        new_status_item.setForeground(QBrush(new_status_text_color))
        new_status_item.setTextAlignment(Qt.AlignCenter)

        # Anadir los items a la fila
        table.setItem(row_count, 0, shot_item)
        table.setItem(row_count, 1, version_item)
        table.setItem(row_count, 2, sg_version_item)
        table.setItem(row_count, 3, sg_status_item)
        table.setItem(row_count, 4, prev_status_item)
        table.setItem(row_count, 5, new_status_item)

        # Configuracion de colores que se agregan a la lista para la linea de seleccion
        row_colors = ['#8a8a8a'] * 6  # Color por defecto para todas las columnas
        if sg_version_num > version_num:  # Si la version SG es mayor que la version NKS
            row_colors[2] = '#81395a'  # Color para la columna v_SG
        if sg_status == 'rev':  # Si el estado es "rev"
            row_colors[3] = '#81395a'  # Color para la columna v_Status

        row_colors[4] = prev_color  # Color para la columna de estado previo
        row_colors[5] = new_color  # Color para la columna de nuevo estado
        gui_table.add_color_to_background_list(row_colors)  # Anadir la lista de colores al final del metodo
        
        table.resizeColumnsToContents()

    def add_color_to_background_list(self, color):
        self.row_background_colors.append(color)

    def luminance(self, color):
        """Calcula la luminancia de un color para determinar si es claro u oscuro."""
        red = color.red()
        green = color.green()
        blue = color.blue()
        return 0.299 * red + 0.587 * green + 0.114 * blue

    def color_for_background(self, hex_color):
        """Determina el color del texto basado en el color de fondo."""
        color = QColor(hex_color)
        return '#ffffff' if self.luminance(color) < 128 else '#000000'

    def change_clip_color(self, item, new_color_hex, task_status, task_name, shot_code):
        current_color_hex = self.get_current_clip_color(item)
        current_status = self.get_status_name_by_color(current_color_hex)

        # No cambiar el color si las condiciones especificas se cumplen
        if current_color_hex == new_color_hex:
            return ""
        if (current_status == 'v_00' and (task_status == 'Not Ready To Start' or task_status == 'Ready To Start')):
            return ""
        if task_status == 'In Progress' and current_status != 'v_00':
            return ""

        # Cambia el color del clip si no se cumplen las condiciones anteriores
        new_color = QColor(new_color_hex)
        bin_item = item.source().binItem()
        previous_color_hex = current_color_hex if current_color_hex else "None"
        bin_item.setColor(new_color)

        # Formatea los nombres y colores de los estados para el mensaje
        text_color = self.color_for_background(new_color_hex)
        status_format = f"<span style='background-color: {new_color_hex}; color: {text_color};'>{task_status}</span>"
        previous_status_format = f"<span style='background-color: {previous_color_hex}; color: {self.color_for_background(previous_color_hex)};'>{current_status}</span>"
        return f"{shot_code} | {task_name} | {previous_status_format} -> {status_format}<br>"

    def get_status_name_by_color(self, color_hex):
        """Devuelve el nombre del estado basado en el color."""
        # Verificar primero en el diccionario de Hiero
        for status, color in self.hiero_status_dict.items():
            if color == color_hex:
                return status
        # Si no se encuentra en Hiero, buscar en el diccionario de ShotGrid
        for status, (name, color, tag) in self.sg_manager.task_status_dict.items():
            if color == color_hex:
                return name
        return "Unknown"

    def add_custom_tag_to_clip(self, clip, tag_name, tag_description, tag_icon, assignee):
        """Anade un tag personalizado a un clip con una descripcion dinamica y un assignee separado."""
        new_tag = hiero.core.Tag(tag_name)
        new_tag.setIcon(tag_icon)
        
        # Anadir la nota
        safe_description = str(tag_description) if tag_description is not None else "-"
        new_tag.setNote(safe_description)
        
        # Anadir el assignee en los metadatos con la clave "Assignee" y espacio adicional
        formatted_assignee = assignee + " "
        new_tag.metadata().setValue("tag.Assignee", formatted_assignee)
        
        clip.addTag(new_tag)
        debug_print(f"Added tag '{tag_name}' with note '{safe_description}' and assignee '{formatted_assignee}' to clip: {clip.name()}")


    def process_selected_clips(self, table, sg_manager):
        seq = hiero.ui.activeSequence()
        changes_made = False
        if seq:
            te = hiero.ui.getTimelineEditor(seq)
            selected_clips = te.selection()
            if selected_clips:
                project = hiero.core.projects()[0]
                #project.beginUndo("Change Clip Colors")
                for clip in selected_clips:
                    if isinstance(clip, hiero.core.EffectTrackItem):  # Verificar si es un efecto
                        debug_print(f"Ignore effect item: {clip.name()}")
                        pass
                    else:                
                        file_path = clip.source().mediaSource().fileinfos()[0].filename() if clip.source().mediaSource().fileinfos() else None
                        if not file_path or '_comp_' not in os.path.basename(file_path).lower():
                            continue
                        exr_name = os.path.basename(file_path)
                        base_name, version_str = self.parse_exr_name(exr_name)
                        version_number = extract_version_number(version_str)  # Use extracted version number

                        project_name = base_name.split('_')[0]
                        parts = base_name.split('_')
                        shot_code = '_'.join(parts[:5])
                        task_name = parts[5].lower()

                        # Obtener la ruta base del shot (subimos un nivel adicional)
                        shot_base_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(file_path))))
                        debug_print(f"Ruta base del shot: {shot_base_path}")

                        # Obtener el estado y el tag correspondiente
                        shot = sg_manager.find_shot(project_name, shot_code)
                        if shot:
                            task = sg_manager.find_task(shot, task_name)
                            if task:
                                task_status_code = task['task_status']
                                task_status_name, new_color_hex, xyplorer_tag = sg_manager.task_status_dict.get(task_status_code, ("Estado desconocido", "#000000", None))

                                # Aplicar el tag correspondiente en XYplorer
                                tag_shot_folder(shot_base_path, xyplorer_tag)

                                current_color_hex = self.get_current_clip_color(clip)
                                current_status = self.get_status_name_by_color(current_color_hex)

                                highest_version = sg_manager.find_highest_version_for_shot(shot)
                                sg_version_str = highest_version['version_number'] if highest_version else "No info"
                                sg_version_number = extract_version_number(sg_version_str)  # Use extracted SG version number
                                sg_status = highest_version['version_status'] if highest_version else "No info"
                                sg_description = highest_version['version_description'] if highest_version and 'version_description' in highest_version else "No description available"

                                # Obtener el nombre del asignado si existe
                                assignee = task.get('task_assigned_to', 'No assignee')
                                debug_print(f"Assignee: {assignee}")

                                # Mantener sg_description sin el assignee

                                change = self.change_clip_color(clip, new_color_hex, task_status_name, task_name, shot_code)
                                if change or sg_version_number > version_number:
                                    prev_color_hex = current_color_hex if current_color_hex else "#000000"
                                    self.add_row_to_table(table, self.gui_table, shot_code, version_str, current_status, prev_color_hex, task_status_name, new_color_hex, sg_version_str, sg_status)
                                    changes_made = True

                                    if sg_version_number > version_number:
                                        self.add_custom_tag_to_clip(clip, "Updated Version", sg_description, "icons:TagYellow.png", assignee)
                                        highest_version = self.change_to_highest_version(clip)
                                        
                                        # Extraer el nuevo numero de version del clip actualizado
                                        new_version_str = highest_version.name().split('_v')[-1]
                                        new_version_number = int(new_version_str)
                                        
                                        # Volver a comparar con la version de SG
                                        if sg_version_number > new_version_number:
                                            self.add_custom_tag_to_clip(clip, "Version Mismatch", f"SG Version: {sg_version_str}", "icons:TagRed.png", assignee)

                            else:
                                debug_print("No matching tasks found for this clip.")
                                pass
                        else:
                            debug_print(f"No valid data found for {shot_code}.")
                            pass
                #project.endUndo()
            else:
                debug_print("No clips selected on the timeline.")
                pass
        else:
            debug_print("No active sequence found in Hiero.")
            pass
        return changes_made



    def get_highest_version(self, binItem):
        """Obtiene la version mas alta de un binItem."""
        versions = binItem.items()
        highest_version = max(versions, key=lambda v: int(v.name().split('_v')[-1]))
        return highest_version

    def change_to_highest_version(self, clip):
        """Cambia el clip a la version mas alta disponible."""
        binItem = clip.source().binItem()
        activeVersion = binItem.activeVersion()
        vc = hiero.core.VersionScanner()
        vc.doScan(activeVersion)
        highest_version = self.get_highest_version(binItem)
        binItem.setActiveVersion(highest_version)
        return highest_version



##### Aca empieza la joda del XYplorer
def get_xy_hwnd(xy_class='ThunderRT6FormDC'):
    user32 = ctypes.windll.user32
    EnumWindows = user32.EnumWindows
    EnumWindowsProc = ctypes.WINFUNCTYPE(ctypes.wintypes.BOOL, ctypes.wintypes.HWND, ctypes.wintypes.LPARAM)
    GetClassName = user32.GetClassNameW
    EnumChildWindows = user32.EnumChildWindows
    GetWindowTextLength = user32.GetWindowTextLengthW
    GetWindowText = user32.GetWindowTextW

    found_hwnd = None

    def enum_windows_callback(hwnd, lParam):
        nonlocal found_hwnd
        class_name = ctypes.create_unicode_buffer(256)
        GetClassName(hwnd, class_name, 256)
        if class_name.value == xy_class:
            child_count = [0]

            def enum_child_windows_callback(hwnd_child, lParam_child):
                child_count[0] += 1
                return True

            EnumChildWindows(hwnd, EnumWindowsProc(enum_child_windows_callback), 0)

            if child_count[0] >= 10:
                found_hwnd = hwnd
                return False
        return True

    EnumWindows(EnumWindowsProc(enum_windows_callback), 0)
    return found_hwnd

# Determina la arquitectura del sistema
if platform.architecture()[0] == '32bit':
    ULONG_PTR = ctypes.wintypes.ULONG
else:
    ULONG_PTR = ctypes.c_uint64

# Define la estructura COPYDATASTRUCT
class COPYDATASTRUCT(ctypes.Structure):
    _fields_ = [("dwData", ULONG_PTR),
                ("cbData", ctypes.wintypes.DWORD),
                ("lpData", ctypes.c_void_p)]

def Send_WM_COPYDATA(xyHwnd, message):
    if not xyHwnd:
        return None

    cds = COPYDATASTRUCT()
    cds.dwData = 4194305
    cds.cbData = len(message.encode('utf-16-le'))
    cds_data = ctypes.create_unicode_buffer(message)
    cds.lpData = ctypes.cast(ctypes.addressof(cds_data), ctypes.c_void_p)

    user32 = ctypes.WinDLL('user32', use_last_error=True)
    result = user32.SendMessageW(xyHwnd, 74, 0, ctypes.byref(cds))

    return result

def tag_shot_folder(shot_base_path, tag):
    if tag is None:
        return  # No hacer nada si no hay tag definido para el estado

    try:
        hwnd = get_xy_hwnd()
        if hwnd:
            tag_command = f"::tag '{tag}', '{shot_base_path}';"
            result = Send_WM_COPYDATA(hwnd, tag_command)
            if result:
                debug_print(f"Tag '{tag}' applied to {shot_base_path}")
            else:
                debug_print(f"Failed to apply tag '{tag}' to {shot_base_path}")
        else:
            debug_print("XYplorer window not found.")
    except Exception as e:
        debug_print(f"Error applying tag in XYplorer: {e}")



##### Aca termina


app = None
window = None

def FPT_Hiero():
    global app, window, hiero_ops

    # Obten el path del script actual
    script_path = os.path.dirname(__file__)
    
    # Genera la ruta relativa para el archivo JSON
    json_path = os.path.join(script_path, 'Data', 'LGA_NKS_Flow_Downloader_Local.json')
    
    # Verifica si el archivo JSON existe
    if not os.path.exists(json_path):
        debug_print(f"JSON file not found at path: {json_path}")
        return

    # Instancia ShotGridManager con la ruta relativa
    sg_manager = ShotGridManager(json_path)
    
    app = QApplication.instance() if QApplication.instance() else QApplication(sys.argv)
    window = GUI_Table(sg_manager)
    hiero_ops = HieroOperations(sg_manager, window)
    window.set_hiero_ops(hiero_ops)

"""
if __name__ == "__FPT_Hiero__":
    FPT_Hiero()
"""