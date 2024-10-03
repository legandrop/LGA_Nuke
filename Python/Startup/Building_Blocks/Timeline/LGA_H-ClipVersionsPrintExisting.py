# Imprime solo las versiones existentes (que ya fueron escaneadas)

import hiero.core
import re

# Obtiene la secuencia activa y el editor de timeline
seq = hiero.ui.activeSequence()
if seq:  # Asegurarse de que hay una secuencia activa
    te = hiero.ui.getTimelineEditor(seq)
    selected_items = te.selection()
    project = hiero.core.projects()[0]

    for item in selected_items:
        bin_item = item.source().binItem()
        if item.source().mediaSource().isMediaPresent():
            current_version = bin_item.activeVersion()
            existing_versions = list(bin_item.items())  # Obtiene todas las versiones existentes antes de anadir nuevas

            # Imprimir nombres de las versiones actuales con su indice
            print("Existing versions:")
            for index, version in enumerate(existing_versions):
                existing_version_name = version.name()
                print(f"- {existing_version_name} ({index})")
else:
    print("No active sequence found.")

