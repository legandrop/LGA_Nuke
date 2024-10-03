import hiero.core
from PySide2.QtGui import QColor

# Define el color que deseas aplicar
color = QColor(255, 220, 0)  # Amarillo, por ejemplo

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
                        for new_version_file in new_versions:
                            new_version = hiero.core.Version(new_version_file)
                            # Anadir la nueva version, si no esta ya en la lista de versiones
                            if new_version not in bin_item.items():
                                bin_item.addVersion(new_version, -1)
                                print(f"Added new version: {new_version_file}")
                            # Activar la nueva version
                            bin_item.setActiveVersion(new_version)
                            print(f"Activated new version: {new_version_file}")
                    else:
                        print(f"No new versions found for clip: {item.name()}")
                else:
                    print(f"No active version found for clip: {item.name()}")
            else:
                print(f"No media present for clip: {item.name()}")
    project.endUndo()
else:
    print("No active sequence found.")
