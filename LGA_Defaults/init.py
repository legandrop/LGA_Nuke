import nuke


# Definir los valores por defecto de algunos Knobs que no pude definir con la tool "Default"
# Ejemplo: nuke.knobDefault('node_type.knob_name','default_knob_value')  
# Hay que hacer hover con el mouse en el knob para buscar el "knob_name"
nuke.knobDefault("Write.exr.compression","DWAA")
nuke.knobDefault("Write.exr.dw_compression_level","60")
nuke.knobDefault("Merge.bbox","B")
nuke.knobDefault("ColorLookup.channels","rgb")
nuke.knobDefault("Remove.operation","keep")
nuke.knobDefault("Remove.channels","rgb")


# Definir la reso por defecto
nuke.knobDefault("Root.format", "4K_DCP") 
#nuke.knobDefault("Root.format", "UHD_4k")

