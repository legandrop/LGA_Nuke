#recursively adds all folders in Cattery folder to nuke's plugin path

file = __file__
file = file.replace('\\','/')

def addPluginPathRecursive(path):
    nuke.pluginAddPath(path)
    lst = os.listdir(path)
    for i in lst:
        itemPath = '/'.join([path,i])
        if os.path.isdir(itemPath):
            addPluginPathRecursive(itemPath)

fullDir = os.path.dirname(file)
dirname = fullDir.split('/')[-1]
if dirname.lower() == 'cattery':
    dirLst = os.listdir(fullDir)
    for name in dirLst:
        itemPath = '/'.join([fullDir,name])
        if os.path.isdir(itemPath):
            addPluginPathRecursive(itemPath)