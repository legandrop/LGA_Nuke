import nuke
import nukescripts
import oz_backdrop
nuke.pluginAddPath("./icons")
nukescripts.autoBackdrop = oz_backdrop.autoBackdrop
nuke.menu('Nodes').addCommand( 'Other/Backdrop', 'oz_backdrop.autoBackdrop()', 'alt+b', 'Backdrop.png')


item_list = [item.name() for item in nuke.menu('Nuke').menu('Edit').items()]
index_number = item_list.index('Node')
nuke.menu('Nuke').addCommand( 'Edit/Replace all old backdrops', 'oz_backdrop.replaceOldBackdrops()', icon='Backdrop.png', index=index_number+1)