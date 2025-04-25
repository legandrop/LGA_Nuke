"""
________________________________________________________________________________________________

  LGA_fr_Read_to_Write v1.0 | Lega
  Sets the frame range of the write noded to match the frame range of the connected Read nodes
________________________________________________________________________________________________

"""

import nuke


def Writes_FrameRange():
    print("\n")
    for i in nuke.allNodes("Write"):
        i["use_limit"].setValue(True)
        print(i.name())
        firstFrame = i.frameRange().first()
        lastFrame = i.frameRange().last()

        i["first"].setValue(firstFrame)
        i["last"].setValue(lastFrame)
