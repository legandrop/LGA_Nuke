"""
______________________________________________________

  LGA_NKS_SnapShot v0.5 - Lega
  Crea un snapshot de la imagen actual del viewer y lo copia al portapapeles
______________________________________________________

"""

import nuke
import nukescripts
import os
import tempfile
from PySide2 import QtWidgets, QtGui

DEBUG = True
SaveToFile = False


def debug_print(*message):
    if DEBUG:
        print(*message)


def main():
    temp_dir = tempfile.gettempdir()
    output_path = os.path.join(temp_dir, "snapshot.jpg")

    viewer = nuke.activeViewer()
    if viewer is None:
        nuke.message("No hay viewer activo.")
        return

    view_node = viewer.node()
    input_index = viewer.activeInput()
    input_node = view_node.input(input_index)

    if input_node is None:
        nuke.message("No hay nodo conectado al viewer.")
        return

    frame = int(nuke.frame())

    # Crear el Write temporal limpio
    write_node = nuke.createNode(
        "Write",
        "file_type jpeg postage_stamp false hide_input true label 'LGA_TEMP'",
        inpanel=False,
    )
    write_node.setInput(0, input_node)

    # Blindaje: convertir path a forward slashes para evitar problemas de escapes
    safe_path = output_path.replace("\\", "/")
    write_node["file"].setValue(safe_path)

    debug_print("Generando snapshot temporal en:", safe_path)

    try:
        nuke.execute(write_node, frame, frame)
    except Exception as e:
        nuke.delete(write_node)
        nuke.message(f"Error al ejecutar el Write: {str(e)}")
        return

    nuke.delete(write_node)

    if not os.path.exists(output_path):
        nuke.message("Error: el archivo no se generó.")
        return

    # Cargar el JPEG como QImage
    qimage = QtGui.QImage(output_path)
    if qimage.isNull():
        nuke.message("Error al leer el snapshot generado.")
        return

    debug_print("Snapshot size:", qimage.width(), "×", qimage.height())

    if SaveToFile:
        save_path = r"T:\Borrame\snapshot.jpg"
        output_dir = os.path.dirname(save_path)
        os.makedirs(output_dir, exist_ok=True)
        ok = qimage.save(save_path, "JPEG")
        debug_print("Archivo final guardado:", ok, save_path)

    # Copiar al portapapeles
    app = QtWidgets.QApplication.instance()
    if not app:
        app = QtWidgets.QApplication([])

    clipboard = app.clipboard()
    clipboard.setImage(qimage)

    debug_print("✅ Imagen copiada al portapapeles.")

    # Limpiar el temporal
    try:
        os.remove(output_path)
    except:
        pass


# --- Main Execution ---
if __name__ == "__main__":
    main()
