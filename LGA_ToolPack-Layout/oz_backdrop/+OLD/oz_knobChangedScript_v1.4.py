try:
    node=nuke.thisNode()
    knob=nuke.thisKnob()
    name=knob.name()

    def updateKnobs():
        nodeWidth=node['bdwidth'].getValue()
        nodeHeight=node['bdheight'].getValue()
        node['sizeNode'].setValue([int(nodeWidth),int(nodeHeight)])
        node['node_position_x'].setValue(int(node['xpos'].value()))
        node['node_position_y'].setValue(int(node['ypos'].value()))
        node['zorder'].setValue(int(node['z_order'].getValue()))
        node['font_size'].setValue(int(node['note_font_size'].getValue()))
        node['oz_appearance'].setValue( node['appearance'].value() )
        node['oz_border_width'].setValue( node['border_width'].value() )
        #node['fontColor'].setValue(int(node['note_font_color'].getValue()))

    def updateLabelKnob():
        curLabel = node['label'].getValue()
        if '<p align=center>' in curLabel:
            node['text'].setValue(curLabel.replace('<p align=center>', ''))
            node['alignment'].setValue(1)
        elif '<p align=right>' in curLabel:
            node['text'].setValue(curLabel.replace('<p align=right>', ''))
            node['alignment'].setValue(2)
        elif '<center>' in curLabel:
            node['text'].setValue(curLabel.replace('<center>', ''))
            node['alignment'].setValue(1)
        else:
            node['text'].setValue(curLabel)
            node['alignment'].setValue(0)

    ### OPENING SETUP
    if name=='showPanel':
        updateKnobs()
        updateLabelKnob()

    ### UPDATE STYLE
    if name in ['oz_appearance', 'oz_border_width']:
        node['appearance'].setValue( node['oz_appearance'].value() )
        node['border_width'].setValue( node['oz_border_width'].value() )

    ### CHANGE THE SIZE OF THE NODE
    if name=='sizeNode':
        node['bdwidth'].setValue(int(node['sizeNode'].getValue()[0]))
        node['bdheight'].setValue(int(node['sizeNode'].getValue()[1]))

    ### POSITION
    if name=='node_position_x' or name=='node_position_y':
        node.setXYpos(int(node['node_position_x'].getValue()),int(node['node_position_y'].getValue()))

    ### ZORDER
    if name=='zorder':
        node['z_order'].setValue(node['zorder'].getValue())

    ### UPDATE THE 'CURRENT SIZE' AND ORDER
    #if name=='bdwidth' or name=='bdheight' or name=='z_order':
    if name in ['bdwidth', 'bdheight', 'z_order']:
        updateKnobs()

    ### UPDATE LABEL
    title = node['name'].value()
    text = node['text'].value()

    if name in ['text', 'alignment', 'title', 'Oz_Backdrop_bold']:
        if text == '':
            if node['alignment'].getValue() == 1:
                newLabel = '<p align=center>'  # +title
            elif node['alignment'].getValue() == 2:
                newLabel = '<p align=right>'  # +title
            else:
                newLabel=title
        else:
            if node['alignment'].getValue()==1:
                newLabel='<p align=center>'+text
            elif node['alignment'].getValue()==2:
                newLabel='<p align=right>'+text
            else:
                newLabel=text

        if node['Oz_Backdrop_bold'].value():
            if '<b>' not in newLabel and '</b>' not in newLabel:
                newLabel = f"<b>{newLabel}</b>"
        else:
            newLabel = newLabel.replace('<b>', '').replace('</b>', '')

        if 'Oz_Font_Color' in node.knobs():
            font_color = node['Oz_Font_Color'].value()
            newLabel = f'<font color="{font_color}">{newLabel}</font>'

        node['label'].setValue(newLabel)

    if name=="font_size":
        new_font_size = node["font_size"].value()
        node['note_font_size'].setValue(new_font_size)


    """
    if name == "font_color_toggle":
        current_font_color = node['Oz_Font_Color'].value()
        current_label = node['label'].value()
        print(f"font_color_toggle: Aplicando color {current_font_color} al label")

        # Actualiza el color en la etiqueta del nodo
        if 'color="' in current_label:
            new_label = current_label.replace(current_label[current_label.find('color="') + 7:current_label.find('">')], current_font_color)
        else:
            new_label = f'<font color="{current_font_color}">{current_label}</font>'
        
        node['label'].setValue(new_label)
        print(f"font_color_toggle: Updated label: {new_label}")
    """




    if name == "font_color":
        font_color_value = node["font_color"].value()
        font_color_hex = "#{:06x}".format(font_color_value & 0xFFFFFF)
        curLabel = node['label'].value()
        if 'color' in curLabel:
            # Actualiza el color en la etiqueta existente
            newLabel = curLabel.replace('color="{}"'.format(prev_font_color_hex), 'color="{}"'.format(font_color_hex))
        else:
            # Anadir color si no esta presente
            newLabel = '<font color="{}">{}</font>'.format(font_color_hex, curLabel)
        node['label'].setValue(newLabel)
        prev_font_color_hex = font_color_hex

    del newLabel

except:
    pass
