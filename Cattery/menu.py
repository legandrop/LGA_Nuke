if nuke.NUKE_VERSION_MAJOR==13:
	nuke.pluginAddPath('./icons')
	import cattery
	cattery.create_menu()