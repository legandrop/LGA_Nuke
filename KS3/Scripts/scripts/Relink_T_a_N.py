
for node in nuke.allNodes('Read'):
    readPath = node['file'].value()
    if "T:/" in readPath:
        newPath = readPath.replace("T:/", "N:/")
        node['file'].setValue(newPath)


for node in nuke.allNodes('Write'):
    readPath = node['file'].value()
    if "T:/" in readPath:
        newPath = readPath.replace("T:/", "N:/")
        node['file'].setValue(newPath)

