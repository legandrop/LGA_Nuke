### created by satheesh-r July 2014
### to extract selected roto shapes from selected roto node. Tested with nuke 6,7,8.
### for bugs and reports: satheesrev@gmail.com

import nuke, nukescripts

def extractSelectedShapes():
    panel = nuke.Panel("extractSelectedShapes", 200)
    panel.addEnumerationPulldown('shapes goes to:\nroto node', 'single each')
    panel.addButton("cancel")
    panel.addButton("ok")
    showPanel = panel.show()
    userChoice = panel.value('shapes goes to:\nroto node')
    if showPanel == 0:
        return
    if showPanel == 1:
        selNode = None
        try:
            selNode = nuke.selectedNode()
            selXpos = selNode.xpos()
            selYpos = selNode.ypos()
        except ValueError: # no node selected
            pass

        if selNode:
            if userChoice == 'single':
                newRotoNode = nuke.nodes.Roto()
                newRotoNode['xpos'].setValue(selXpos+200)
                newRotoNode['ypos'].setValue(selYpos)
                newRotoNode['curves'].rootLayer.setTransform(selNode['curves'].rootLayer.getTransform())
                for selShape in selNode['curves'].getSelected():
                    shapeName = selShape.name
                    newRotoNode.setName(shapeName)
                    newRotoNode['curves'].rootLayer.append(selShape.clone())
            if userChoice == 'each':
                for selShape in selNode['curves'].getSelected():
                    selXpos = selXpos + 200
                    shapeName = selShape.name
                    newRotoNode = nuke.nodes.Roto()
                    newRotoNode['curves'].rootLayer.setTransform(selNode['curves'].rootLayer.getTransform())
                    newRotoNode['xpos'].setValue(selXpos)
                    newRotoNode['ypos'].setValue(selYpos)
                    newRotoNode.setName(shapeName)
                    newRotoNode['curves'].rootLayer.append(selShape.clone())

        else:
            nuke.message('<center>make sure you have selected your roto node\n<center>then try again :)')
