default
=======

**author:** simon jokuschies
**version:** 5.0.0
**contact:** info@leafpictures.de
**website:** www.leafpictures.de

Description
-----------
Set knob defaults on the fly so you don't have to write them manually into your
nuke home directory. Just set a knob like you want to have it as knob default
and then right click, choose 'defaults -> set as knob default'. If you want to
get rid of the knob default just right click on the knob and choose
'defaults -> reset'.

Installation
------------
Put defaults folder inside your nuke home directory. In
your int.py write:

nuke.pluginAddPath("default")

You can also put the default folder some where else; just make sure to
reference to the correct path when adding it to nuke's plugin path.