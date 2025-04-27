"""
_____________________________________

  LGA_ToolPack v2.3 | Lega
  Colección de herramientas de Nuke
_____________________________________

"""

import nuke
import nukescripts

# Importar iconos de la carpeta icons
import os


def _get_icon(name):
    icons_root = os.path.join(os.path.dirname(__file__), "icons")
    path = os.path.join(icons_root, name) + ".png"
    return path.replace("\\", "/")


# Crea el menu "TP2" (ToolPack)
n2 = nuke.menu("Nuke").addMenu("TP2", icon=_get_icon("LGA2"))


# -----------------------------------------------------------------------------
#                              READ n WRITE TOOLS
# -----------------------------------------------------------------------------
# Agrega el comando "READ n WRITE" al menu "TP" y "TP2"
n2.addCommand("READ n WRITE", lambda: None)
# Define el icono para los items de Read n Write
icon_RnW = _get_icon("TP_RnW")


# Importar el LGA_mediaMissingFrames
import LGA_mediaMissingFrames

n2.addCommand(
    "  Media Missing Frames",
    "LGA_mediaMissingFrames.main()",
    "ctrl+alt+shift+m",
    shortcutContext=2,
    icon=icon_RnW,
)


# Importar el LGA_reloadAllReads
import LGA_reloadAllReads

n2.addCommand(
    "  Reload all Reads",
    "LGA_reloadAllReads.main()",
    "ctrl+alt+shift+r",
    shortcutContext=2,
    icon=icon_RnW,
)


# Importar el LGA_renameWritesFromReads
import LGA_renameWritesFromReads

n2.addCommand(
    "  Rename Writes from Reads",
    "LGA_renameWritesFromReads.renameWrite()",
    "F2",
    shortcutContext=2,
    icon=icon_RnW,
)


# -----------------------------------------------------------------------------
#                              FRAME RANGE TOOLS
# -----------------------------------------------------------------------------
# Crear separador
n2.addSeparator()
n2.addCommand("FRAME RANGE", lambda: None)
# Define el icono para los items de Frame Range
icon_FR = _get_icon("TP_FR")


# Importar el LGA_fr_Read_to_FrameRange
import LGA_fr_Read_to_FrameRange

n2.addCommand(
    "  Read -> FrameRange",
    "LGA_fr_Read_to_FrameRange.set_frame_range_from_read()",
    "ctrl+alt+f",
    shortcutContext=2,
    icon=icon_FR,
)


# Importar el LGA_fr_Read_to_Write
import LGA_fr_Read_to_Write

n2.addCommand(
    "  Read -> Write",
    "LGA_fr_Read_to_Write.Writes_FrameRange()",
    shortcutContext=2,
    icon=icon_FR,
)


# Importar el LGA_fr_TimeClip_to_Write
import LGA_fr_TimeClip_to_Write

n2.addCommand(
    "  TimeClip -> Write",
    "LGA_fr_TimeClip_to_Write.set_write_from_timeclip()",
    "ctrl+t",
    shortcutContext=2,
    icon=icon_FR,
)


# -----------------------------------------------------------------------------
#                                 NODE BUILDS
# -----------------------------------------------------------------------------
n2.addCommand("NODE BUILDS", lambda: None)
icon_Knobs = _get_icon("TP_Knobs")

# Importar el LGA_DasGrain_Kronos_Comp
import LGA_DasGrain_Kronos_Comp

n2.addCommand(
    "  DasGrain Kronos Comp", "LGA_DasGrain_Kronos_Comp.main()", icon=icon_Knobs
)

# Importar el animation maker
import AnimationMaker

n2.addCommand(
    "  Animation Maker",
    lambda: nuke.message("Right click on any knob and select Animation Maker"),
    icon=icon_Knobs,
)


# Importar el MultiKnobTool con shortcut F12
import wbMultiKnobEdit

n2.addCommand(
    "  Multi Knob Edit", "wbMultiKnobEdit.multiEditExec()", "F12", icon=icon_Knobs
)


# Importar Default (para definir los valores por defecto de los Nodos)
from default.default import default_main
from default.default import helper
from default.default import about

n2.addCommand(
    "  Edit Default Knobs Values", default_main.show_defaults_window, icon=icon_Knobs
)
# Add commands to animation menu.
nuke.menu("Animation").addCommand(
    "default/set as new knobDefault", "default_main.create_default()"
)
nuke.menu("Animation").addCommand(
    "default/show knob list", "default_main.show_knob_list()"
)
nuke.menu("Animation").addCommand("default/reset", "default_main.reset_to_default()")
# Auto load knob defaults when launching.
helper.load_knob_defaults(init=True)


# -----------------------------------------------------------------------------
#                                 VA TOOLS
# -----------------------------------------------------------------------------
# Crea separador y titulo
n2.addSeparator()
n2.addCommand("VA", lambda: None)
# Define el icono para los items de Frame Range
icon_VA = _get_icon("TP_VA")


# Importar el LGA_CDL_CC_IP
import LGA_CDL_CC_IP

n2.addCommand(
    "  CDL -> CC Input Process",
    "LGA_CDL_CC_IP.main()",
    "ctrl+alt+shift+i",
    shortcutContext=2,
    icon=icon_VA,
)


# Importar Performance timers en el menu TP y como un Panel
import perf_time

n2.addCommand("  Performance Timers", "perf_time.show_panel()", icon=icon_VA)
pane_m = nuke.menu("Pane")
pane_m.addCommand("Performance Timers", perf_time.add_perf_time_panel)
nukescripts.registerPanel("com.lega.perfTime", perf_time.add_perf_time_panel)


# Importar el shortcut editor
try:
    import shortcuteditor

    shortcuteditor.nuke_setup()
except Exception:
    import traceback

    traceback.print_exc()
from shortcuteditor import gui

n2.addCommand("  Edit Keyboard Shortcuts", gui, icon=icon_VA)


# -----------------------------------------------------------------------------
#                                 Version
# -----------------------------------------------------------------------------
# Crea separador y titulo
n2.addSeparator()
import webbrowser
import nuke

TP_script_dir = os.path.dirname(os.path.realpath(__file__))
TP_pdf_path = os.path.join(TP_script_dir, "LGA_ToolPack.pdf")

n2.addCommand("v2.3", lambda: webbrowser.open("file://" + TP_pdf_path))
