import nuke
from PySide2.QtWidgets import QDialog, QVBoxLayout, QCheckBox, QApplication
from PySide2.QtCore import Qt, QPoint
from PySide2.QtGui import QCursor, QFont

class DisableManagerDialog(QDialog):
    def __init__(self, parent=None):
        super(DisableManagerDialog, self).__init__(parent)
        self.setWindowTitle('Disable Manager')
        self.setLayout(QVBoxLayout())
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Popup | Qt.WindowStaysOnTopHint)
        
        # Initialize the dragging state and starting point
        self.dragging = False
        self.start_point = QPoint()

        # 'Disable All' checkbox initialization and set to bold
        self.disable_all = QCheckBox('Disable All')
        font = QFont()
        font.setBold(True)
        self.disable_all.setFont(font)
        self.layout().addWidget(self.disable_all)
        self.disable_all.stateChanged.connect(self.toggle_all_nodes)

        # Sort nodes by their ypos, and then by xpos
        nodes = sorted(nuke.allNodes(), key=lambda n: (n['ypos'].value(), n['xpos'].value()))

        # Checkboxes for each node with a 'disable' knob
        self.nodes_checkboxes = {}
        for node in nodes:
            if 'disable' in node.knobs():
                is_disabled = node['disable'].value()
                label_text = f" | {node['label'].value()}" if node['label'].value() else ""
                checkbox_text = f"{node.name()}{label_text}"
                checkbox = QCheckBox(checkbox_text)
                checkbox.setChecked(is_disabled)
                checkbox.stateChanged.connect(self.toggle_node)
                self.layout().addWidget(checkbox)
                self.nodes_checkboxes[node] = checkbox

        # Set 'Disable All' checkbox state based on all nodes' states
        all_disabled = all(node['disable'].value() for node in self.nodes_checkboxes.keys())
        self.disable_all.setChecked(all_disabled)

    def toggle_all_nodes(self, state):
        is_disabled = state == Qt.Checked
        for node, checkbox in self.nodes_checkboxes.items():
            checkbox.blockSignals(True)
            checkbox.setChecked(is_disabled)
            checkbox.blockSignals(False)
            node['disable'].setValue(is_disabled)

    def toggle_node(self, state):
        is_disabled = state == Qt.Checked
        node = [n for n, chkbx in self.nodes_checkboxes.items() if chkbx is self.sender()][0]
        node['disable'].setValue(is_disabled)

        # Update 'Disable All' checkbox based on the states of the individual checkboxes
        all_disabled = all(chkbx.isChecked() for chkbx in self.nodes_checkboxes.values())
        self.disable_all.blockSignals(True)
        self.disable_all.setChecked(all_disabled)
        self.disable_all.blockSignals(False)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.dragging = True
            self.start_point = event.pos()

    def mouseMoveEvent(self, event):
        if self.dragging:
            # Move the window
            self.move(self.pos() + (event.pos() - self.start_point))

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.dragging = False

    def focusOutEvent(self, event):
        # Close the dialog when it loses focus
        self.close()

def show_disable_manager():
    app = QApplication.instance() or QApplication([])
    dialog = DisableManagerDialog()
    dialog.adjustSize()
    dialog.move(QCursor.pos())
    dialog.exec_()

# Show the dialog at the cursor position
show_disable_manager()
