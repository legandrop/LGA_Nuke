'''
I reused the script from Franklin VFX Co.
with mods I had from a previus tools I made.

Lega mod v1.0

update 1.3 - April 2023 - Added back the original colors with the 3 click shades.
                        - Now colors can be added easily with a dictionary in it's own file.

update 1.2 - April 2023 : Edited by Hossein Karamian (hkaramian.com | kmworks.call@gmail.com)
                       - Made script compatible with Nuke 12,13,14
                       - replace icons by nuke default icons. (so in a script including oz_backdrops, backdrops will perfectly shown even when oz_backdrops isn't installed)
                       - replace color icons by html/css code
                       - Add setting panel to nuke preferences, so users can set default values for new backdrops. (color,text alignment, text size, appearance, inner margin)

update 1.1 - June 2020 - Added Position knobs
                       - Split secondary code into other files
                       - Added replace old backdrops
                       - Appearance and border width from Nuke12.1
update 1.0 - 2019 -Initial Relase

oz@Garius.io
'''

import nuke, random, nukescripts, colorsys, os

from oz_colors import colors
try:
    import oz_settings
except:
    print("Failed to find oz_settings.py, was oz_backdrop installed correctly?")

# IMPORT OTHER SCRIPTS AS VARIABLES
# These are to avoid the background node from not working when loaded on a Nuke
# that doesn't have the scripts saved. Basically each created node is trying to
# be it's own little world.
file_KCS = open(os.path.join(os.path.dirname(__file__),"oz_knobChangedScript.py"), 'r')
knobChangedScript = file_KCS.read()
file_KCS.close()

file_RCS = open(os.path.join(os.path.dirname(__file__),"oz_randomColorScript.py"), 'r')
randomColorScript = file_RCS.read()
file_RCS.close()

file_ES = open(os.path.join(os.path.dirname(__file__),"oz_encompassScript.py"), 'r')
encompassScript = file_ES.read()
file_ES.close()


# FUNCTIONS
# These are only used on node creation.
# They don't need to travel with the nodes.
def nodeIsInside(node, backdropNode):
    '''
    Returns true if node geometry is inside backdropNode
    otherwise returns false
    '''
    topLeftNode = [node.xpos(), node.ypos()]
    topLeftBackDrop = [backdropNode.xpos(), backdropNode.ypos()]
    bottomRightNode = [node.xpos() + node.screenWidth(),
                       node.ypos() + node.screenHeight()]
    bottomRightBackdrop = [backdropNode.xpos() + backdropNode.screenWidth(),
                           backdropNode.ypos() + backdropNode.screenHeight()]

    topLeft = ((topLeftNode[0] >= topLeftBackDrop[0]) and
               (topLeftNode[1] >= topLeftBackDrop[1]))
    bottomRight = ((bottomRightNode[0] <= bottomRightBackdrop[0]) and
                   (bottomRightNode[1] <= bottomRightBackdrop[1]))

    return topLeft and bottomRight

def hsv_to_hex(hsv):
    """ converts hsv values given as a list to a hex string """
    rgb = colorsys.hsv_to_rgb(hsv[0], hsv[1], hsv[2])
    hex_color = '#{:02x}{:02x}{:02x}'.format(int(rgb[0]*255), int(rgb[1]*255), int(rgb[2]*255))
    return hex_color

def autoBackdrop():
    '''
    Automatically puts a backdrop behind the selected nodes.

    The backdrop will be just big enough to fit all the select nodes in,
    with room at the top for some text in a large font.
    '''
    sel = nuke.selectedNodes()
    forced = False

    # if nothing is selected
    if not sel:
        forced = True
        b = nuke.createNode('NoOp')
        sel.append(b)

    # Calculate bounds for the backdrop node.
    bdX = min([node.xpos() for node in sel])
    bdY = min([node.ypos() for node in sel])
    bdW = max([node.xpos() + node.screenWidth() for node in sel]) - bdX
    bdH = max([node.ypos() + node.screenHeight() for node in sel]) - bdY

    zOrder = 0
    selectedBackdropNodes = nuke.selectedNodes("BackdropNode")

    # if there are backdropNodes selected
    # put the new one immediately behind the farthest one
    if len(selectedBackdropNodes):
        zOrder = min([node.knob("z_order").value()
                      for node in selectedBackdropNodes]) - 1
    else:
        # otherwise (no backdrop in selection) find the nearest backdrop
        # if exists and set the new one in front of it
        nonSelectedBackdropNodes = nuke.allNodes("BackdropNode")
        for nonBackdrop in sel:
            for backdrop in nonSelectedBackdropNodes:
                if nodeIsInside(nonBackdrop, backdrop):
                    zOrder = max(zOrder, backdrop.knob("z_order").value() + 1)

    # Grab values from Settings, or go for default if something doesn't work
    try:
        appearance_value = nuke.toNode('preferences')['Oz_Backdrop_Appearance'].value()
        default_color = nuke.toNode('preferences')['Oz_Backdrop_color'].value()
        alignment_value = nuke.toNode('preferences')['Oz_Backdrop_text_alignment'].value()
        note_font_size = int((nuke.toNode('preferences')['Oz_Backdrop_font_size'].value()))
        margin_value = int(nuke.toNode('preferences')['Oz_Backdrop_margin'].value())
        bold_value = nuke.toNode('preferences')['Oz_Backdrop_bold'].value()
    except:
        appearance_value = "Fill"
        default_color = "Random"
        alignment_value = "left"
        note_font_size = 50
        margin_value = 50
        bold_value = False


    # Expand the bounds to leave a little border.
    # Elements are offsets for left, top, right and bottom edges respectively
    left, top, right, bottom = (-1 * margin_value, -100, margin_value, margin_value)
    bdX += left
    bdY += top
    bdW += (right - left)
    bdH += (bottom - top)

    rgbRandom = random.random(),.1+random.random()*.15,.15 + random.random()*.15

    def switch_color(case):
        return colors.get(case, rgbRandom)
        
    R, G, B = colorsys.hsv_to_rgb(switch_color(default_color)[0],switch_color(default_color)[1],switch_color(default_color)[2])
    
    tile_color = int('%02x%02x%02x%02x' % (int(R*255),int(G*255),int(B*255),255), 16)

    n = nuke.nodes.BackdropNode(xpos=bdX, bdwidth=bdW, ypos=bdY,
                                bdheight=bdH,
                                tile_color=tile_color,
                                note_font_size=note_font_size,
                                z_order=zOrder,
                                appearance=appearance_value)

    n.showControlPanel()

    # Buid all knobs for Backdrop
    tab = nuke.Tab_Knob('Settings')
    text = nuke.Multiline_Eval_String_Knob('text', 'Text')
    text.setFlag(nuke.STARTLINE)
    
    size = nuke.Double_Knob('font_size', 'Font Size') 
    size.setRange(10,100)
    size.setValue(note_font_size) # default value : 50
    size.setFlag(nuke.NO_ANIMATION)

    alignment = nuke.Enumeration_Knob('alignment', '', ['left', 'center', 'right'])
    alignment.clearFlag(nuke.STARTLINE)
    alignment.setValue(alignment_value)

    
    # Nuevo knob para el color de la fuente
    font_color = nuke.PyScript_Knob('Black / White', 'B/W', '''
node = nuke.thisNode()
current_label = node['label'].value()
if 'color="#ffffff"' in current_label:
    new_label = current_label.replace('color="#ffffff"', 'color="#000000"')
elif 'color="#000000"' in current_label:
    new_label = current_label.replace('color="#000000"', 'color="#ffffff"')
else:
    new_label = '<font color="#ffffff">' + current_label + '</font>'
node['label'].setValue(new_label)
#print("Etiqueta despues de cambiar:", new_label)
''')
    font_color.setTooltip("Toggle font color for the label text")

    # Nuevo knob para cambiar la fuente a negrita
    font_bold = nuke.PyScript_Knob('Bold Font', 'Bold', '''
node = nuke.thisNode()
current_label = node['label'].value()
if '<b>' in current_label and '</b>' in current_label:
    new_label = current_label.replace('<b>', '').replace('</b>', '')
else:
    new_label = '<b>' + current_label + '</b>'
node['label'].setValue(new_label)
''')
    font_bold.setTooltip("Toggle bold font for the label text")


    appearance = nuke.Enumeration_Knob('oz_appearance', ' Appearance      ', ['Fill', 'Border'])
    appearance.clearFlag(nuke.STARTLINE)
    appearance.setValue(appearance_value)
    border = nuke.Double_Knob('', 'Border')
    border.clearFlag(nuke.STARTLINE)
    border.setRange(0,10)
    border.setValue(2)
    border.setFlag(nuke.NO_ANIMATION)
    border.setTooltip("Border width for Border appearence")  # Adjust the number of spaces to fit your nee
    space1 = nuke.Text_Knob('S01', ' ', ' ')
    space2 = nuke.Text_Knob('S02', ' ', ' ')
    space3 = nuke.Text_Knob('S03', ' ', '     ')
    space3.clearFlag(nuke.STARTLINE)
    space4 = nuke.Text_Knob('S04', ' ', ' ')
    space4.clearFlag(nuke.STARTLINE)
    space5 = nuke.Text_Knob('S05', ' ', ' ')
    space5.clearFlag(nuke.STARTLINE)
    space6 = nuke.Text_Knob('S06', ' ', ' ')
    space7 = nuke.Text_Knob('S07', ' ', ' ')
    #space7.clearFlag(nuke.STARTLINE)
    space8 = nuke.Text_Knob('S08', ' ', ' ')
    space82 = nuke.Text_Knob('S08', ' ', '       ')
    space82.clearFlag(nuke.STARTLINE)
    space9 = nuke.Text_Knob('S09', ' ', ' ')
    divider1 = nuke.Text_Knob('divider1','')
    divider2 = nuke.Text_Knob('divider2','')
    divider3 = nuke.Text_Knob('divider3','')
    divider4 = nuke.Text_Knob('divider4', '')
    divider5 = nuke.Text_Knob('divider5', '')
    
    grow = nuke.PyScript_Knob('grow', ' <img src="MergeMin.png">', "n=nuke.thisNode()\n\ndef grow(node=None,step=50):\n    try:\n        if not node:\n            n=nuke.selectedNode()\n        else:\n            n=node\n            n['xpos'].setValue(n['xpos'].getValue()-step)\n            n['ypos'].setValue(n['ypos'].getValue()-step)\n            n['bdwidth'].setValue(n['bdwidth'].getValue()+step*2)\n            n['bdheight'].setValue(n['bdheight'].getValue()+step*2)\n    except e:\n        print('Error:: %s' % e)\n\ngrow(n,50)")
    shrink = nuke.PyScript_Knob('shrink', ' <img src="MergeMax.png">', "n=nuke.thisNode()\n\ndef shrink(node=None,step=50):\n    try:\n        if not node:\n            n=nuke.selectedNode()\n        else:\n            n=node\n            n['xpos'].setValue(n['xpos'].getValue()+step)\n            n['ypos'].setValue(n['ypos'].getValue()+step)\n            n['bdwidth'].setValue(n['bdwidth'].getValue()-step*2)\n            n['bdheight'].setValue(n['bdheight'].getValue()-step*2)\n    except e:\n        print('Error:: %s' % e)\n\nshrink(n,50)")

    
    # Add Z Order label and number input
    zorder_label = nuke.Text_Knob('Z Order', '', 'Z Order     ')
    zorder_back_label = nuke.Text_Knob('', '', 'Back ')
    zorder = nuke.Double_Knob("zorder", "")
    zorder.setRange(-5, +5)
    zorder_front_label = nuke.Text_Knob('', '', ' Front')
    
    # Set flags to align on the same line
    zorder_label.clearFlag(nuke.STARTLINE)
    zorder_back_label.clearFlag(nuke.STARTLINE)
    zorder.clearFlag(nuke.STARTLINE)
    zorder_front_label.clearFlag(nuke.STARTLINE) 
    zorder.setFlag(nuke.NO_ANIMATION)
    
    
    encompassButton = nuke.PyScript_Knob('encompassSelectedNodes', ' <img src="ContactSheet.png">', encompassScript) 
    encompassPadding = nuke.Int_Knob('sides',"")
    encompassPadding.setValue(margin_value) # default value : 50
    encompassPadding.clearFlag(nuke.STARTLINE)
    position_text = nuke.Text_Knob('pos_text', 'Position', ' ')
    position_text.clearFlag(nuke.STARTLINE)
    position_x = nuke.Int_Knob("node_position_x", "x")
    position_x.clearFlag(nuke.STARTLINE)
    position_y = nuke.Int_Knob("node_position_y", "y")
    position_y.clearFlag(nuke.STARTLINE)
    sizeWH = nuke.WH_Knob("sizeNode", "Size       ")
    sizeWH.setSingleValue(False)
    sizeWH.clearFlag(nuke.STARTLINE)
    sizeWH.setFlag(nuke.NO_ANIMATION)
    
     


    # Boton Copy W
    copy_w_button = nuke.PyScript_Knob('Copy Width', 'Copy W', '''
import subprocess
import platform

node = nuke.thisNode()

# Llamar a la funcion updateKnobs para actualizar todos los valores
def updateKnobs(node):
    nodeWidth = node['bdwidth'].getValue()
    nodeHeight = node['bdheight'].getValue()
    node['sizeNode'].setValue([int(nodeWidth), int(nodeHeight)])
    node['zorder'].setValue(int(node['z_order'].getValue()))
    node['font_size'].setValue(int(node['note_font_size'].getValue()))
    node['oz_appearance'].setValue(node['appearance'].value())
    node['oz_border_width'].setValue(node['border_width'].value())

updateKnobs(node)

size_w = node['sizeNode'].getValue()[0]

# Copiar al portapapeles segun el sistema operativo
if platform.system() == 'Windows':
    cmd = 'echo ' + str(size_w).strip() + '| clip'
    subprocess.run(cmd, shell=True)
elif platform.system() == 'Darwin':
    cmd = 'echo ' + str(size_w).strip() + ' | pbcopy'
    subprocess.run(cmd, shell=True)
else:
    print("Sistema operativo no soportado para copiar al portapapeles")

#print("Size W copiado al portapapeles:", size_w)
''')
    copy_w_button.setTooltip("Copy the width of this backdrop to use in another backdrop")
    
    # Boton Paste W con funcionalidad para pegar el valor desde el portapapeles
    paste_w_button = nuke.PyScript_Knob('Paste Width', 'Paste W', '''
import subprocess
import platform

node = nuke.thisNode()

# Obtener el valor del portapapeles segun el sistema operativo
if platform.system() == 'Windows':
    cmd = 'powershell Get-Clipboard'
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    size_w = result.stdout.strip()
elif platform.system() == 'Darwin':
    cmd = 'pbpaste'
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    size_w = result.stdout.strip()
else:
    print("Sistema operativo no soportado para pegar desde el portapapeles")
    size_w = None

if size_w:
    try:
        size_w = float(size_w)
        node['bdwidth'].setValue(size_w)
        node['sizeNode'].setValue([size_w, node['sizeNode'].getValue()[1]])
        #print("Size W pegado desde el portapapeles:", size_w)
    except ValueError:
        print("El valor en el portapapeles no es un numero valido")
''')
    paste_w_button.setTooltip("Set this backdrop's width using the value copied from another backdrop")
   
    # Boton Copy H con actualizacion de valores
    copy_h_button = nuke.PyScript_Knob('Copy Height', 'Copy H', '''
import subprocess
import platform

node = nuke.thisNode()

# Llamar a la funcion updateKnobs para actualizar todos los valores
def updateKnobs(node):
    nodeWidth = node['bdwidth'].getValue()
    nodeHeight = node['bdheight'].getValue()
    node['sizeNode'].setValue([int(nodeWidth), int(nodeHeight)])
    node['zorder'].setValue(int(node['z_order'].getValue()))
    node['font_size'].setValue(int(node['note_font_size'].getValue()))
    node['oz_appearance'].setValue(node['appearance'].value())
    node['oz_border_width'].setValue(node['border_width'].value())

updateKnobs(node)

size_h = node['sizeNode'].getValue()[1]

# Copiar al portapapeles segun el sistema operativo
if platform.system() == 'Windows':
    cmd = 'echo ' + str(size_h).strip() + '| clip'
    subprocess.run(cmd, shell=True)
elif platform.system() == 'Darwin':
    cmd = 'echo ' + str(size_h).strip() + ' | pbcopy'
    subprocess.run(cmd, shell=True)
else:
    print("Sistema operativo no soportado para copiar al portapapeles")

#print("Size H copiado al portapapeles:", size_h)
''')
    copy_h_button.setTooltip("Copy the height of this backdrop to use in another backdrop")

    # Boton Paste H con funcionalidad para pegar el valor desde el portapapeles
    paste_h_button = nuke.PyScript_Knob('Paste Height', 'Paste H', '''
import subprocess
import platform

node = nuke.thisNode()

# Obtener el valor del portapapeles segun el sistema operativo
if platform.system() == 'Windows':
    cmd = 'powershell Get-Clipboard'
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    size_h = result.stdout.strip()
elif platform.system() == 'Darwin':
    cmd = 'pbpaste'
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    size_h = result.stdout.strip()
else:
    print("Sistema operativo no soportado para pegar desde el portapapeles")
    size_h = None

if size_h:
    try:
        size_h = float(size_h)
        node['bdheight'].setValue(size_h)
        node['sizeNode'].setValue([node['sizeNode'].getValue()[0], size_h])
        #print("Size H pegado desde el portapapeles:", size_h)
    except ValueError:
        print("El valor en el portapapeles no es un numero valido")
''')
    paste_h_button.setTooltip("Set this backdrop's height using the value copied from another backdrop")

    
    # Boton Copy Color con funcionalidad para copiar el valor de tile_color
    copy_color_button = nuke.PyScript_Knob('copy_color', '   Copy Color   ', '''
import subprocess
import platform

node = nuke.thisNode()

tile_color = node['tile_color'].value()
tile_color_hex = '{:08x}'.format(tile_color)  # Convertir a cadena hexadecimal de 8 digitos

# Copiar al portapapeles segun el sistema operativo
if platform.system() == 'Windows':
    cmd = 'echo ' + tile_color_hex + '| clip'
    subprocess.run(cmd, shell=True)
elif platform.system() == 'Darwin':
    cmd = 'echo ' + tile_color_hex + ' | pbcopy'
    subprocess.run(cmd, shell=True)
else:
    print("Sistema operativo no soportado para copiar al portapapeles")

#print("Color copiado al portapapeles:", tile_color_hex)
''')


    # Boton Paste Color con funcionalidad para pegar el valor de tile_color desde el portapapeles
    paste_color_button = nuke.PyScript_Knob('paste_color', '   Paste Color   ', '''
import subprocess
import platform

node = nuke.thisNode()

# Obtener el valor del portapapeles segun el sistema operativo
if platform.system() == 'Windows':
    cmd = 'powershell Get-Clipboard'
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    tile_color_hex = result.stdout.strip()
elif platform.system() == 'Darwin':
    cmd = 'pbpaste'
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    tile_color_hex = result.stdout.strip()
else:
    print("Sistema operativo no soportado para pegar desde el portapapeles")
    tile_color_hex = None

if tile_color_hex:
    try:
        tile_color = int(tile_color_hex, 16)
        node['tile_color'].setValue(tile_color)
        #print("Color pegado desde el portapapeles:", tile_color_hex)
    except ValueError:
        print("El valor en el portapapeles no es un color valido")
''')


    
    buttonRandomColor = nuke.PyScript_Knob('Random Color', ' <img src="ColorBars.png">', randomColorScript)
    
    # Generating buttons for colors.
    color_buttons = []
    
    for key, value in colors.items():
        # If the button needs a title generate it now
        name="<div>{}</div>".format(key.capitalize()) if value["title"] else ""
        # Create the button
        globals()[key] = nuke.PyScript_Knob(key.capitalize(),
                                            '<div style="background-color: {0}; color: {0}; font-size: 7px;">______</div><div style="background-color: {1}; color: {1}; font-size: 7px;">______</div><div style="background-color: {2}; color: {2}; font-size: 7px;">______</div>{title}'.format(hsv_to_hex(value["hsv"][0]), hsv_to_hex(value["hsv"][1]), hsv_to_hex(value["hsv"][2]), title=name),
                                            "import colorsys\nn=nuke.thisNode()\ndef clamp(x):\n    return int(max(0, min(x, 255)))\ntile_color=n['tile_color'].value()\ncolors={}\n#converting colors\ncolors_hex=[colorsys.hsv_to_rgb(color[0],color[1],color[2]) for color in colors]\ncolors_int=[int('%02x%02x%02x%02x' % (clamp(color[0]*255),clamp(color[1]*255),clamp(color[2]*255),255), 16) for color in colors_hex]\n#selecting color logic\nif tile_color in colors_int:\n    current_index=colors_int.index(tile_color)\n    if current_index >= (len(colors_int)-1):\n        new_color = colors_int[0]\n    else:\n        new_color = colors_int[current_index+1]\nelse:\n    new_color = colors_int[0]\n#apply color\nn['tile_color'].setValue(new_color)".format(value["hsv"])
                                            )
        # Add tooltip to button
        globals()[key].setTooltip(value["tooltip"])
        # Add a new line if needed
        if value["newline"]:
      
            #globals()[key].setFlag(nuke.STARTLINE)
            space = nuke.Text_Knob('space', ' ', ' ')
            color_buttons.append(space)              
        
        color_buttons.append(globals()[key])
        
        

    # Tooltips

    grow.setTooltip("Grows the size of the Backdrop by 50pt in every direction")
    shrink.setTooltip("Shrinks the size of the Backdrop by 50pt in every direction")
    encompassButton.setTooltip("Will resize the backdrop to encompass every selected nodes plus a padding number (the number next to the button)")
    encompassPadding.setTooltip("When encompassing nodes this number of pt will be added to the Backdrop size in every direction")

    buttonRandomColor.setTooltip("Generates a random color for the Backdrop (dark shades)")

    # Add the knobs
    n.addKnob(tab)
    n.addKnob(text)
    n.addKnob(size)
    
    #n['font_size'].setValue(50)
    n.addKnob(alignment)
    n.addKnob(font_color)
    n.addKnob(font_bold)
    n.addKnob(divider1)
    n.addKnob(space1)
    n.addKnob(buttonRandomColor)
    for button in color_buttons:
        n.addKnob(button)
    
    n.addKnob(space8)
    n.addKnob(copy_color_button)
    n.addKnob(paste_color_button)
    n.addKnob(space7)
    n.addKnob(appearance)
    n.addKnob(space82)
    n.addKnob(border)
    
   
    
    n.addKnob(divider2)
    n.addKnob(space2)
    n.addKnob(grow)
    n.addKnob(shrink)
    n.addKnob(space3)
    n.addKnob(encompassButton)
    n.addKnob(space4)
    n.addKnob(encompassPadding)
    n.addKnob(divider3)
    n.addKnob(space5)
    n.addKnob(position_text)
    n.addKnob(position_x)
    n.addKnob(position_y)
    n.addKnob(space6)
    n.addKnob(sizeWH)


    # Anadir los knobs al nodo
    n.addKnob(space9)
    n.addKnob(copy_w_button)
    n.addKnob(paste_w_button)
    n.addKnob(copy_h_button)
    n.addKnob(paste_h_button)  

    n.addKnob(divider4)
    #n.addKnob(zorder)    
 
    # Add the knobs in the correct order
    n.addKnob(zorder_label)
    n.addKnob(zorder_back_label)
    n.addKnob(zorder)
    n.addKnob(zorder_front_label) 
 

    # Add Logic & initial setup
    n['knobChanged'].setValue(knobChangedScript)

    # revert to previous selection
    n['selected'].setValue(True)
    if forced:
        nuke.delete(b)
    else:
        for node in sel:
            node['selected'].setValue(True)

    #return the new backdrop node        
    return n

def replaceOldBackdrops():
    nodes = nuke.allNodes()
    bd_nodes = [node for node in nodes if node.Class() == 'BackdropNode']
    
    for bd_node in bd_nodes:
        new_bd = autoBackdrop()
        new_bd['text'].setValue( bd_node['label'].value() )
        new_bd['font_size'].setValue( bd_node['note_font_size'].value() )
        new_bd['zorder'].setValue( int(bd_node['z_order'].value()) )
        new_bd['bdwidth'].setValue( bd_node['bdwidth'].value() )
        new_bd['bdheight'].setValue( bd_node['bdheight'].value() )
        new_bd['tile_color'].setValue( bd_node['tile_color'].value() )
        new_bd.setXYpos(bd_node.xpos(), bd_node.ypos())

        nuke.delete(bd_node)
