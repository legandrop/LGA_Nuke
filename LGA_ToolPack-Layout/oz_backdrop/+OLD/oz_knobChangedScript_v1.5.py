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

    if name in ['text', 'alignment', 'title', 'Oz_Backdrop_bold', 'note_font_color']:
        text = node['text'].value()
        alignment = node['alignment'].getValue()
        is_bold = node['Oz_Backdrop_bold'].value()

        if alignment == 1:
            newLabel = f'<p align=center>{text}</p>'
        elif alignment == 2:
            newLabel = f'<p align=right>{text}</p>'
        else:
            newLabel = text

        # Captura la fuente actual y muestra en consola
        current_font = node['note_font'].value()
        #print(f"Fuente antes de cambiar: {current_font}")

        # Solo proceder si current_font tiene un valor valido
        if current_font:
            font_family = current_font.replace(" Bold", "").strip()

            # Modifica la fuente segun el estado del checkbox de bold
            if is_bold:
                new_font = f"{font_family} Bold"
            else:
                new_font = font_family

            # Aplicar el nuevo valor de la fuente
            node['note_font'].setValue(new_font)
            #print(f"Fuente despues de cambiar: {new_font}")

        # Actualiza el label sin etiquetas HTML
        node['label'].setValue(newLabel)




    if name=="font_size":
        new_font_size = node["font_size"].value()
        node['note_font_size'].setValue(new_font_size)



    del newLabel

except:
    pass
