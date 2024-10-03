'''
I reused the script from Franklin VFX Co.
with mods I had from a previus tools I made.

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
    except:
        appearance_value = "Fill"
        default_color = "Random"
        alignment_value = "left"
        note_font_size = 50
        margin_value = 50


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
    alignment = nuke.Enumeration_Knob('alignment', '', ['left', 'center', 'right'])
    alignment.clearFlag(nuke.STARTLINE)
    alignment.setValue(alignment_value)
    appearance = nuke.Enumeration_Knob('oz_appearance', 'appearance', ['Fill', 'Border'])
    appearance.clearFlag(nuke.STARTLINE)
    appearance.setValue(appearance_value)
    border = nuke.Double_Knob('oz_border_width', 'width')
    border.clearFlag(nuke.STARTLINE)
    border.setRange(0,10)
    border.setValue(2)
    # space1 = nuke.Text_Knob('S01', ' ', ' ')
    space2 = nuke.Text_Knob('S02', ' ', ' ')
    space3 = nuke.Text_Knob('S03', ' ', '     ')
    space3.clearFlag(nuke.STARTLINE)
    space4 = nuke.Text_Knob('S04', ' ', ' ')
    space4.clearFlag(nuke.STARTLINE)
    space5 = nuke.Text_Knob('S05', ' ', ' ')
    space5.clearFlag(nuke.STARTLINE)
    space6 = nuke.Text_Knob('S06', ' ', ' ')
    space7 = nuke.Text_Knob('S07', ' ', '     ')
    space7.clearFlag(nuke.STARTLINE)
    space8 = nuke.Text_Knob('S08', ' ', ' ')
    divider1 = nuke.Text_Knob('divider1','')
    divider2 = nuke.Text_Knob('divider2','')
    divider3 = nuke.Text_Knob('divider3','')
    
    grow = nuke.PyScript_Knob('grow', ' <img src="MergeMin.png">', "n=nuke.thisNode()\n\ndef grow(node=None,step=50):\n    try:\n        if not node:\n            n=nuke.selectedNode()\n        else:\n            n=node\n            n['xpos'].setValue(n['xpos'].getValue()-step)\n            n['ypos'].setValue(n['ypos'].getValue()-step)\n            n['bdwidth'].setValue(n['bdwidth'].getValue()+step*2)\n            n['bdheight'].setValue(n['bdheight'].getValue()+step*2)\n    except e:\n        print('Error:: %s' % e)\n\ngrow(n,50)")
    shrink = nuke.PyScript_Knob('shrink', ' <img src="MergeMax.png">', "n=nuke.thisNode()\n\ndef shrink(node=None,step=50):\n    try:\n        if not node:\n            n=nuke.selectedNode()\n        else:\n            n=node\n            n['xpos'].setValue(n['xpos'].getValue()+step)\n            n['ypos'].setValue(n['ypos'].getValue()+step)\n            n['bdwidth'].setValue(n['bdwidth'].getValue()-step*2)\n            n['bdheight'].setValue(n['bdheight'].getValue()-step*2)\n    except e:\n        print('Error:: %s' % e)\n\nshrink(n,50)")
    zorder = nuke.Int_Knob("zorder", "Z Order")
    zorder.clearFlag(nuke.STARTLINE)
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
    sizeWH = nuke.WH_Knob("sizeNode", "Size")
    sizeWH.setSingleValue(False)
    sizeWH.clearFlag(nuke.STARTLINE)
    
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
            globals()[key].setFlag(nuke.STARTLINE)
        
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
    n.addKnob(divider1)
    # n.addKnob(space1)
    n.addKnob(buttonRandomColor)
   
   
    for button in color_buttons:
        n.addKnob(button)
    
    n.addKnob(space8)
    n.addKnob(appearance)
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
    n.addKnob(space7)
    n.addKnob(zorder)

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
