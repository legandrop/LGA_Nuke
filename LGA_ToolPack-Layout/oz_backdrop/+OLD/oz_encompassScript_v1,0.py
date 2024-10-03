this = nuke.thisNode()
padding = this['sides'].getValue()
if this.isSelected:
    this.setSelected(False)
selNodes = nuke.selectedNodes()
        
def nodeIsInside (node, backdropNode):
    # Returns true if node geometry is inside backdropNode otherwise returns false
    topLeftNode = [node.xpos(), node.ypos()]
    topLeftBackDrop = [backdropNode.xpos(), backdropNode.ypos()]
    bottomRightNode = [node.xpos() + node.screenWidth(), node.ypos() + node.screenHeight()]
    bottomRightBackdrop = [backdropNode.xpos() + backdropNode.screenWidth(), backdropNode.ypos() + backdropNode.screenHeight()]
                    
    topLeft = ( topLeftNode[0] >= topLeftBackDrop[0] ) and ( topLeftNode[1] >= topLeftBackDrop[1] )
    bottomRight = ( bottomRightNode[0] <= bottomRightBackdrop[0] ) and ( bottomRightNode[1] <= bottomRightBackdrop[1] )
                    
    return topLeft and bottomRight

if not selNodes:
    nuke.message('Some nodes should be selected')
else:
    # Calculate bounds for the backdrop node.
    bdX = min([node.xpos() for node in selNodes])
    bdY = min([node.ypos() for node in selNodes])
    bdW = max([node.xpos() + node.screenWidth() for node in selNodes]) - bdX
    bdH = max([node.ypos() + node.screenHeight() for node in selNodes]) - bdY
                        
    zOrder = 0
    selectedBackdropNodes = nuke.selectedNodes( "BackdropNode" )

    #if there are backdropNodes selected put the new one immediately behind the farthest one
                
    if len( selectedBackdropNodes ):
        zOrder = min( [node.knob( "z_order" ).value() for node in selectedBackdropNodes] ) - 1
    else :
        #otherwise (no backdrop in selection) find the nearest backdrop if exists and set the new one in front of it
        nonSelectedBackdropNodes = nuke.allNodes("BackdropNode")
        for nonBackdrop in selNodes:
            for backdrop in nonSelectedBackdropNodes:
                if nodeIsInside( nonBackdrop, backdrop ):
                    zOrder = max( zOrder, backdrop.knob( "z_order" ).value() + 1 )
    
    # Expand the bounds to leave a little border. Elements are offsets for left, top, right and bottom edges respectively
    left, top, right, bottom = (-padding, -(padding+70), padding, padding)
    bdX += left
    bdY += top
    bdW += (right - left)
    bdH += (bottom - top)

    this['xpos'].setValue(bdX)
    this['bdwidth'].setValue(bdW)
    this['ypos'].setValue(bdY)
    this['bdheight'].setValue(bdH)
    this['z_order'].setValue(zOrder)
