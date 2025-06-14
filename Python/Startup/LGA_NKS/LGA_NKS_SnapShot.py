"""
______________________________________________________

  LGA_NKS_SnapShot v0.5 - Lega
  Crea un snapshot de la imagen actual del viewer y lo copia al portapapeles
______________________________________________________

"""

import hiero.core
import hiero.ui
from PySide2 import QtWidgets, QtCore

DEBUG = True


def debug_print(*message):
    if DEBUG:
        print(*message)


import os
import hiero
from PySide2 import QtWidgets
from PySide2.QtCore import QRect


def crop_to_16_9(qimage):
    width = qimage.width()
    height = qimage.height()

    target_aspect = 16 / 9
    current_aspect = width / height

    if current_aspect > target_aspect:
        new_width = int(height * target_aspect)
        offset_x = int((width - new_width) / 2)
        rect = QRect(offset_x, 0, new_width, height)
        cropped = qimage.copy(rect)
        return cropped
    else:
        return qimage


output_path = r"T:\Borrame\snapshot.jpg"

viewer = hiero.ui.currentViewer()
if not viewer:
    raise Exception("No active viewer")

qimage = viewer.image()
if qimage is None or qimage.isNull():
    raise Exception("viewer.image() devolvió None o imagen nula")

# Aplicar crop
qimage_cropped = crop_to_16_9(qimage)

debug_print(
    "Snapshot size (cropped):", qimage_cropped.width(), "×", qimage_cropped.height()
)
debug_print("Ruta de salida:", output_path)

output_dir = os.path.dirname(output_path)
if not os.path.isdir(output_dir):
    os.makedirs(output_dir, exist_ok=True)

ok = qimage_cropped.save(output_path, "JPEG")
debug_print("qimage.save result:", ok)

if ok and os.path.exists(output_path):
    debug_print("✅ Archivo creado:", output_path)
else:
    debug_print("❌ No se pudo crear el archivo.")

# Copiar al portapapeles
app = QtWidgets.QApplication.instance()
if not app:
    app = QtWidgets.QApplication([])

clipboard = app.clipboard()
clipboard.setImage(qimage_cropped)

debug_print("✅ Imagen (cropeada) copiada al portapapeles.")
