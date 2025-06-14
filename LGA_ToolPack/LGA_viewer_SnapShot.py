"""
______________________________________

  LGA_viewer_SnapShot v0.1 | Lega
______________________________________

"""

import nuke
import os

# Path de destino (asegurate que la carpeta exista)
output_path = r"T:\Borrame\snapshot.jpg"

# Obtener el viewer activo
viewer = nuke.activeViewer()
if viewer is None:
    nuke.message("No hay viewer activo.")
    raise Exception("No viewer active")

# Obtener el nodo asociado al viewer
view_node = viewer.node()
input_index = viewer.activeInput()
input_node = view_node.input(input_index)

if input_node is None:
    nuke.message("No hay nodo conectado al viewer.")
    raise Exception("No node connected to viewer")

# Obtener el frame actual
frame = int(nuke.frame())

# Crear un Write temporal
write_node = nuke.createNode("Write", inpanel=False)
write_node.setInput(0, input_node)
write_node["file"].setValue(output_path)
write_node["file_type"].setValue("jpeg")

# Renderizar el frame actual
nuke.execute(write_node, frame, frame)

# Borrar el write después de usarlo
nuke.delete(write_node)

nuke.message("Snapshot guardado:\n{}".format(output_path))
