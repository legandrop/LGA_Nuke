import hiero.core
import hiero.ui
from PySide2.QtGui import QColor

# Define el color que deseas aplicar
color = QColor(255, 220, 0)  # Rojo, por ejemplo

# Funcion para obtener todas las versiones del binItem
def get_all_versions(binItem):
    versions = binItem.items()
    return sorted(versions, key=lambda v: int(v.name().split('_v')[-1]))

# Obtiene la secuencia activa y el editor de timeline
seq = hiero.ui.activeSequence()
if seq:  # Asegurarse de que hay una secuencia activa
    te = hiero.ui.getTimelineEditor(seq)
    selected_items = te.selection()
    project = hiero.core.projects()[0]
    project.beginUndo("Scan for New Versions")

    for item in selected_items:
        if isinstance(item, hiero.core.EffectTrackItem):  # Verificar si es un efecto
            print(f"Ignore effect item: {item.name()}")
        else:
            bin_item = item.source().binItem()
            if item.source().mediaSource().isMediaPresent():
                versions = get_all_versions(bin_item)
                if versions:
                    current_version = bin_item.activeVersion()
                    current_version_index = versions.index(current_version)
                    
                    if current_version_index > 0:
                        previous_version = versions[current_version_index - 1]
                        bin_item.setActiveVersion(previous_version)
                        print(f"Changed {item.name()} to version {previous_version.name()}")
                    else:
                        print(f"{item.name()} is already at the oldest version available.")
                else:
                    print(f"No versions found for clip: {item.name()}")
            else:
                print(f"No media present for clip: {item.name()}")
    project.endUndo()
else:
    print("No active sequence found.")
