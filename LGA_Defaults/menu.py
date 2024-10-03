
# Agregar resoluciones
CustomReso_A = '3840 1632 DEP 4K 2.35'
nuke.addFormat( CustomReso_A )

CustomReso_B = '4448 2502 DMNA 4K 1.78'
nuke.addFormat( CustomReso_B )


# Cambiar defaults del render a Global y que no continue en error
import nukescripts 
nukescripts.setRenderDialogDefaultOption("frame_range", "global") 
nukescripts.setRenderDialogDefaultOption("continue", False) 



# Poner por defecto Rec709 en el viewer
def setViewerProcessAsRecACES():
    nuke.knobDefault('Viewer.viewerProcess', 'Rec.709 (ACES)')
    [nuke.delete(v) for v in nuke.allNodes('Viewer')]
    nuke.removeOnCreate(setViewerProcessAsRecACES, nodeClass="Viewer")
    nuke.createNode('Viewer')
nuke.addOnCreate(setViewerProcessAsRecACES, nodeClass="Viewer")


nuke.knobDefault('Write.frame_range_mode', 'global')
nuke.knobDefault('Write.continueOnError', 'False')



## Intentando que el continue del write este en false:
## nukescripts.setRenderDialogDefaultOption('Write.continue','false')


# Shortcuts para nodos:
#ms = nuke.menu("Nodes").menu("ToolSets").addMenu("shortcuts")
#ms.addCommand("Mask with BBox A", "nuke.createNode('Merge2', 'operation mask bbox A')", "Shift+M")


