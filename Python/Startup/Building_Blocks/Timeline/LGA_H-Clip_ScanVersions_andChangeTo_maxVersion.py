import hiero.core
import hiero.ui

def get_highest_version(binItem):
    versions = binItem.items()
    # Suponiendo que las versiones estan en orden ascendente y el ultimo es el mas alto
    highest_version = max(versions, key=lambda v: int(v.name().split('_v')[-1]))
    return highest_version

vc = hiero.core.VersionScanner()

for trackItem in hiero.ui.getTimelineEditor(hiero.ui.activeSequence()).selection():
    binItem = trackItem.source().binItem()
    activeVersion = binItem.activeVersion()
    vc.doScan(activeVersion)
    
    highest_version = get_highest_version(binItem)
    print(f"Clip: {binItem.name()}, Highest Version: {highest_version.name()}")
    
    # Cambiar a la version mas alta
    binItem.setActiveVersion(highest_version)

