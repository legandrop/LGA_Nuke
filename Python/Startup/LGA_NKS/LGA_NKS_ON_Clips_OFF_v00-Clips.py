"""
______________________________________________________

  LGA_NKS_ON_Clips_OFF_v00-Clips v1.0 - 2024 - Lega
  Activa todos los clips y desactiva clips v00
______________________________________________________

"""

import hiero.core
import hiero.ui
import os
import re

DEBUG = False

def debug_print(*message):
    if DEBUG:
        print(*message)

def main():
    try:
        seq = hiero.ui.activeSequence()
        if seq:
            te = hiero.ui.getTimelineEditor(seq)
            selected_items = te.selection()
            if selected_items:
                for item in selected_items:
                    if not isinstance(item, hiero.core.EffectTrackItem):
                        file_path = item.source().mediaSource().fileinfos()[0].filename() if item.source().mediaSource().fileinfos() else None
                        if file_path and '_comp_' in os.path.basename(file_path).lower():
                            if re.search(r'_comp_v00', os.path.basename(file_path).lower()):
                                item.setEnabled(False)
                                debug_print(f"Clip '{item.name()}' desactivado.")
                            else:
                                item.setEnabled(True)
                                debug_print(f"Clip '{item.name()}' activado.")
                        else:
                            item.setEnabled(True)
                            debug_print(f"Clip '{item.name()}' activado.")
            else:
                debug_print("No hay clips seleccionados en la linea de tiempo.")
        else:
            debug_print("No se encontro una secuencia activa en Hiero.")
    except Exception as e:
        debug_print(f"Error durante la operacion: {e}")
