
for node in nuke.allNodes('Read'):
    readPath = node['file'].value()
    if "N:/" in readPath:
        newPath = readPath.replace("N:/", "T:/")
        node['file'].setValue(newPath)


for node in nuke.allNodes('Write'):
    readPath = node['file'].value()
    if "N:/" in readPath:
        newPath = readPath.replace("N:/", "T:/")
        node['file'].setValue(newPath)

