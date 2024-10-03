# Imprime todas las versiones que hay en el disco 

import hiero.core
from PySide2.QtGui import QColor

# Define el color que deseas aplicar
color = QColor(255, 220, 0)  # Rojo, por ejemplo

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
                version = bin_item.activeVersion()
                if version:
                    scanner = hiero.core.VersionScanner()
                    new_versions = scanner.findNewVersions(version)
                    if new_versions:
                        print(f"New versions found for clip: {item.name()}")
                        for new_version in new_versions:
                            version_index = scanner.getActiveIndexFromPath(new_version)
                            print(f"New version file: {new_version}, Index: {version_index}")
                            # Aqui puedes hacer lo que necesites con las nuevas versiones
                            # Por ejemplo, crear una nueva entrada en el timeline
                            # O realizar alguna accion especifica con las nuevas versiones
                    else:
                        print(f"No new versions found for clip: {item.name()}")
                else:
                    print(f"No active version found for clip: {item.name()}")
            else:
                print(f"No media present for clip: {item.name()}")
    project.endUndo()
else:
    print("No active sequence found.")
