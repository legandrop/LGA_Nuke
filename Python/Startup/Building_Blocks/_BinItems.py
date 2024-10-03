import inspect
import hiero.core
from hiero.core import BinItem

# Crea un objeto ficticio de BinItem para inspeccion
# NOTA: Esto es solo para propositos de demostracion. No ejecutes esto en Hiero ya que BinItem espera parametros especificos.
# bin_item = BinItem()

# Si tienes un binItem real, puedes reemplazar el codigo de arriba con una referencia a un objeto real, por ejemplo:
# bin_item = alguna_funcion_que_devuelve_un_binItem()

# Imprime todos los metodos del objeto BinItem
methods = inspect.getmembers(BinItem, predicate=inspect.isfunction)
for method in methods:
    print(method[0])

# Para imprimir metodos y tambien atributos que puedes usar
attrs = inspect.getmembers(BinItem)
for attr in attrs:
    print(attr[0], '->', attr[1])

# Result: clone
createClipVersion
setActiveVersionIndex
versionDown
versionMaxAvailable
versionMinAvailable
versionNextAvailable
versionPrevAvailable
versionUp
__bool__ -> <slot wrapper '__bool__' of 'core.BinItem' objects>
__class__ -> <class 'Shiboken.ObjectType'>
__copy__ -> <method '__copy__' of 'core.BinItem' objects>
__delattr__ -> <slot wrapper '__delattr__' of 'Shiboken.Object' objects>
__dict__ -> {'__new__': <built-in method __new__ of Shiboken.ObjectType object at 0x000002A8BEB20A10>, '__repr__':
 <slot wrapper '__repr__' of 'core.BinItem' objects>, '__hash__': <slot wrapper '__hash__' of 'core.BinItem' objects>, 
 '__lt__': <slot wrapper '__lt__' of 'core.BinItem' objects>, '__le__': <slot wrapper '__le__' of 'core.BinItem' objects>,
 '__eq__': <slot wrapper '__eq__' of 'core.BinItem' objects>, '__ne__': <slot wrapper '__ne__' of 'core.BinItem' objects>, 
 '__gt__': <slot wrapper '__gt__' of 'core.BinItem' objects>, '__ge__': <slot wrapper '__ge__' of 'core.BinItem' objects>, 
 '__init__': <slot wrapper '__init__' of 'core.BinItem' objects>, '__bool__': <slot wrapper '__bool__' of 'core.BinItem' objects>, 
 '__getitem__': <slot wrapper '__getitem__' of 'core.BinItem' objects>, '__len__': <slot wrapper '__len__' of 'core.BinItem' objects>,
 'activeItem': <method 'activeItem' of 'core.BinItem' objects>, 'activeVersion': <method 'activeVersion' of 'core.BinItem' objects>, 
 'addSnapshot': <method 'addSnapshot' of 'core.BinItem' objects>, 'addVersion': <method 'addVersion' of 'core.BinItem' objects>, 
 'clone': <function deprecated.<locals>.new at 0x000002A8BB0A9C60>, 'color': <method 'color' of 'core.BinItem' objects>, 'copy': 
 <method 'copy' of 'core.BinItem' objects>, 'createClipVersion': 
 <function __createClip_wrapper.<locals>.wrapper at 0x000002A8BB0AA320>, 'deserializeChildItem': <method 'deserializeChildItem' 
 of 'core.BinItem' objects>, 'displayColor': <method 'displayColor' of 'core.BinItem' objects>, 'guid':
 <method 'guid' of 'core.BinItem' objects>, 'hasVersion': <method 'hasVersion' of 'core.BinItem' objects>, 'isClipVersion': 
 <method 'isClipVersion' of 'core.BinItem' objects>, 'isNull': <method 'isNull' of 'core.BinItem' objects>, 'items': 
 <method 'items' of 'core.BinItem' objects>, 'maxVersion': <method 'maxVersion' of 'core.BinItem' objects>, 'minVersion': 
 <method 'minVersion' of 'core.BinItem' objects>, 'name': <method 'name' of 'core.BinItem' objects>, 'nextVersion': 
 <method 'nextVersion' of 'core.BinItem' objects>, 'numSnapshots': <method 'numSnapshots' of 'core.BinItem' objects>,
 'numVersions': <method 'numVersions' of 'core.BinItem' objects>, 'parentBin': <method 'parentBin' of 'core.BinItem' objects>,
 'prevVersion': <method 'prevVersion' of 'core.BinItem' objects>, 'project': <method 'project' of 'core.BinItem' objects>,
 'removeVersion': <method 'removeVersion' of 'core.BinItem' objects>, 'restoreToSnapshot':
 <method 'restoreToSnapshot' of 'core.BinItem' objects>, 'serialize': <method 'serialize' of 'core.BinItem' objects>,
 'setActiveVersion': <method 'setActiveVersion' of 'core.BinItem' objects>, 'setActiveVersionIndex': 
 <function deprecated.<locals>.new at 0x000002A8BB0A96C0>, 'setColor': <method 'setColor' of 'core.BinItem' objects>,
 'setName': <method 'setName' of 'core.BinItem' objects>, 'snapshots': <method 'snapshots' of 'core.BinItem' objects>,
 'syncName': <method 'syncName' of 'core.BinItem' objects>, 'toString': <method 'toString' of 'core.BinItem' objects>,
 'version': <method 'version' of 'core.BinItem' objects>, 'versionDown': <function deprecated.<locals>.new at 0x000002A8BB0A93F0>,
 'versionMaxAvailable': <function deprecated.<locals>.new at 0x000002A8BB0A95A0>, 'versionMinAvailable': 
 <function deprecated.<locals>.new at 0x000002A8BB0A9630>, 'versionNextAvailable': 
 <function deprecated.<locals>.new at 0x000002A8BB0A9480>, 'versionPrevAvailable': 
 <function deprecated.<locals>.new at 0x000002A8BB0A9510>, 'versionUp': <function deprecated.<locals>.new at 0x000002A8BB0A9360>,
 '__copy__': <method '__copy__' of 'core.BinItem' objects>, '__doc__': 
 'Generic object wrapper with shared functionality for sequences and clips.', '__module__': 'core'}
__dir__ -> <method '__dir__' of 'object' objects>
__doc__ -> Generic object wrapper with shared functionality for sequences and clips.
__eq__ -> <slot wrapper '__eq__' of 'core.BinItem' objects>
__format__ -> <method '__format__' of 'object' objects>
__ge__ -> <slot wrapper '__ge__' of 'core.BinItem' objects>
__getattribute__ -> <slot wrapper '__getattribute__' of 'Shiboken.Object' objects>
__getitem__ -> <slot wrapper '__getitem__' of 'core.BinItem' objects>
__gt__ -> <slot wrapper '__gt__' of 'core.BinItem' objects>
__hash__ -> <slot wrapper '__hash__' of 'core.BinItem' objects>
__init__ -> <slot wrapper '__init__' of 'core.BinItem' objects>
__init_subclass__ -> <built-in method __init_subclass__ of Shiboken.ObjectType object at 0x000002A8BEB20A10>
__le__ -> <slot wrapper '__le__' of 'core.BinItem' objects>
__len__ -> <slot wrapper '__len__' of 'core.BinItem' objects>
__lt__ -> <slot wrapper '__lt__' of 'core.BinItem' objects>
__module__ -> core
__ne__ -> <slot wrapper '__ne__' of 'core.BinItem' objects>
__new__ -> <built-in method __new__ of Shiboken.ObjectType object at 0x000002A8BEB20A10>
__reduce__ -> <method '__reduce__' of 'object' objects>
__reduce_ex__ -> <method '__reduce_ex__' of 'object' objects>
__repr__ -> <slot wrapper '__repr__' of 'core.BinItem' objects>
__setattr__ -> <slot wrapper '__setattr__' of 'Shiboken.Object' objects>
__sizeof__ -> <method '__sizeof__' of 'object' objects>
__str__ -> <slot wrapper '__str__' of 'object' objects>
__subclasshook__ -> <built-in method __subclasshook__ of Shiboken.ObjectType object at 0x000002A8BEB20A10>
activeItem -> <method 'activeItem' of 'core.BinItem' objects>
activeVersion -> <method 'activeVersion' of 'core.BinItem' objects>
addSnapshot -> <method 'addSnapshot' of 'core.BinItem' objects>
addVersion -> <method 'addVersion' of 'core.BinItem' objects>
clone -> <function deprecated.<locals>.new at 0x000002A8BB0A9C60>
color -> <method 'color' of 'core.BinItem' objects>
copy -> <method 'copy' of 'core.BinItem' objects>
createClipVersion -> <function __createClip_wrapper.<locals>.wrapper at 0x000002A8BB0AA320>
deserializeChildItem -> <method 'deserializeChildItem' of 'core.BinItem' objects>
displayColor -> <method 'displayColor' of 'core.BinItem' objects>
guid -> <method 'guid' of 'core.BinItem' objects>
hasVersion -> <method 'hasVersion' of 'core.BinItem' objects>
isClipVersion -> <method 'isClipVersion' of 'core.BinItem' objects>
isNull -> <method 'isNull' of 'core.BinItem' objects>
items -> <method 'items' of 'core.BinItem' objects>
maxVersion -> <method 'maxVersion' of 'core.BinItem' objects>
minVersion -> <method 'minVersion' of 'core.BinItem' objects>
name -> <method 'name' of 'core.BinItem' objects>
nextVersion -> <method 'nextVersion' of 'core.BinItem' objects>
numSnapshots -> <method 'numSnapshots' of 'core.BinItem' objects>
numVersions -> <method 'numVersions' of 'core.BinItem' objects>
parentBin -> <method 'parentBin' of 'core.BinItem' objects>
prevVersion -> <method 'prevVersion' of 'core.BinItem' objects>
project -> <method 'project' of 'core.BinItem' objects>
removeVersion -> <method 'removeVersion' of 'core.BinItem' objects>
restoreToSnapshot -> <method 'restoreToSnapshot' of 'core.BinItem' objects>
serialize -> <method 'serialize' of 'core.BinItem' objects>
setActiveVersion -> <method 'setActiveVersion' of 'core.BinItem' objects>
setActiveVersionIndex -> <function deprecated.<locals>.new at 0x000002A8BB0A96C0>
setColor -> <method 'setColor' of 'core.BinItem' objects>
setName -> <method 'setName' of 'core.BinItem' objects>
snapshots -> <method 'snapshots' of 'core.BinItem' objects>
syncName -> <method 'syncName' of 'core.BinItem' objects>
toString -> <method 'toString' of 'core.BinItem' objects>
version -> <method 'version' of 'core.BinItem' objects>
versionDown -> <function deprecated.<locals>.new at 0x000002A8BB0A93F0>
versionMaxAvailable -> <function deprecated.<locals>.new at 0x000002A8BB0A95A0>
versionMinAvailable -> <function deprecated.<locals>.new at 0x000002A8BB0A9630>
versionNextAvailable -> <function deprecated.<locals>.new at 0x000002A8BB0A9480>
versionPrevAvailable -> <function deprecated.<locals>.new at 0x000002A8BB0A9510>
versionUp -> <function deprecated.<locals>.new at 0x000002A8BB0A9360>
