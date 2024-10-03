Aca esta todo:

file:///C:/Program%20Files/Nuke15.0v4/Documentation/PythonDevGuide/Nuke/Hiero/index.html



for act in hiero.ui.registeredActions():
  print (act.text(), act.objectName())
# Result: 
Edit Playhead Time foundry.viewer.editPlayheadTime
New Project... foundry.application.newProject
Open Project... foundry.application.openProject
Open Recent Project foundry.project.recentprojects
Close Project foundry.project.close
 
Save Project (Untitled 1) foundry.project.save
Save Project As (Untitled 1)... foundry.project.saveas
 
Import File(s)... foundry.project.importFiles
Import Folder(s)... foundry.project.importFolder
Import EDL/XML/AAF... foundry.project.importSequence
Import OTIO [BETA] foundry.project.importOtio
 
Export... foundry.project.export
 
Quit foundry.application.quit
Undo foundry.application.undo
Redo foundry.application.redo
 
Cut foundry.application.cut
Copy foundry.application.copy
Paste foundry.application.paste
Replace Paste foundry.application.replacePaste
Sequential Paste foundry.application.sequentialPaste
Sequential Replace Paste foundry.application.sequentialReplacePaste
Duplicate foundry.application.duplicate
Delete foundry.application.delete
 
Clone foundry.application.clone
Replace Clone foundry.application.replaceClone
Sequential Clone foundry.application.sequentialClone
Sequential Replace Clone foundry.application.sequentialReplaceClone
Copy As Clones foundry.application.copyAsClones
Declone foundry.application.declone
 
Select All foundry.application.selectAll
Select None foundry.application.selectNone
 
Preferences... foundry.application.preferences
Save Workspace... foundry.application.saveWorkspace
Delete Workspace... foundry.application.deleteWorkspace
Reset Workspace foundry.application.resetWorkspace
Edit Workspace Details foundry.application.editWorkspace
 
 foundry.end.workspace.actions
Toggle Fullscreen foundry.application.toggleFullScreenWindow
Toggle Floating Viewers foundry.application.toggleFloatingViewers
 
Previous Pane foundry.application.focusPreviousPane
Next Pane foundry.application.focusNextPane
Previous Tab foundry.application.focusPreviousTab
Next Tab foundry.application.focusNextTab
 
Zoom to Actual Size foundry.viewer.zoomToActualSize
Zoom to Half Size foundry.viewer.zoomToHalfSize
Zoom to Fill foundry.viewer.zoomToFill
Zoom to Fit foundry.viewer.zoomToFit
Zoom In foundry.viewer.zoomIn
Zoom Out foundry.viewer.zoomOut
Full Screen foundry.viewer.fullScreen
Full Quality 1:1 foundry.viewer.fullScreen1_1
Clipping Warning foundry.viewer.clippingwarning
 
Mark In foundry.viewer.markIn
Mark Out foundry.viewer.markOut
Clear In Point foundry.viewer.clearIn
Clear Out Point foundry.viewer.clearOut
Clear In/Out Points foundry.viewer.clearInOut
 
Go to Start foundry.viewer.goToStart
Go to End foundry.viewer.goToEnd
Go to In Point foundry.viewer.goToInPoint
Go to Out Point foundry.viewer.goToOutPoint
Go to Poster Frame foundry.viewer.goToPosterFrame
Frame Backwards foundry.viewer.frameBackwards
Frame Forwards foundry.viewer.frameForwards
Skip Backwards foundry.viewer.skipBackwards
Skip Forwards foundry.viewer.skipForwards
Previous Edit foundry.viewer.prevEdit
Next Edit foundry.viewer.nextEdit
Previous Tag foundry.viewer.prevTag
Next Tag foundry.viewer.nextTag
 
Play/Pause foundry.viewer.play
Play Forward foundry.viewer.playForward
Play Backward foundry.viewer.playBackward
Pause foundry.viewer.pause
Edit Playhead Time foundry.viewer.editPlayheadTime
Playhead 
Playhead 1 foundry.timeline.activatePlayhead1
Playhead 2 foundry.timeline.activatePlayhead2
Playhead 3 foundry.timeline.activatePlayhead3
Playhead 4 foundry.timeline.activatePlayhead4
Playhead 5 foundry.timeline.activatePlayhead5
Playhead 6 foundry.timeline.activatePlayhead6
Playhead 7 foundry.timeline.activatePlayhead7
Playhead 8 foundry.timeline.activatePlayhead8
Playhead 9 foundry.timeline.activatePlayhead9
Playhead 10 foundry.timeline.activatePlayhead10
 
Ignore Pixel Aspect foundry.viewer.ignorePixelAspect
 
Show Timeline Editor foundry.viewer.showLinked
 
Swap Inputs foundry.project.swapAB
 
Channels foundry.menu.channels
RGB foundry.viewer.channelRGB
Red foundry.viewer.channelR
Green foundry.viewer.channelG
Blue foundry.viewer.channelB
Alpha foundry.viewer.channelA
Luma foundry.viewer.channelY
View foundry.menu.views
Previous View foundry.viewer.previousview
Next View foundry.viewer.nextview
Previous Layer foundry.viewer.prevLayer
Next Layer foundry.viewer.nextLayer
Show Overlays foundry.viewer.showOverlays
Toggle Split Wipe foundry.viewer.toggleSplitWipe
Render All Comp Containers... foundry.render.renderall
Render Selected Comp Containers... foundry.render.renderselected
Cancel foundry.render.cancel
New Bin foundry.project.newBin
New Tag foundry.project.newTag
New Sequence foundry.project.newSequence
 
Explorer foundry.project.openInOSShell
 
Edit Settings foundry.project.settings
Open In foundry.menu.openItem
Viewer foundry.project.openInViewer
New Viewer foundry.project.openInNewViewer
Viewer Input A foundry.project.sendToViewerA
Viewer Input B foundry.project.sendToViewerB
Viewer All Tracks Input A foundry.project.sendAllTracksToViewerA
Viewer All Tracks Input B foundry.project.sendAllTracksToViewerB
Timeline View foundry.project.openInSequence
Spreadsheet View foundry.project.openInSpreadsheet
Metadata View foundry.project.openInMetadata
Versions Bin foundry.project.openInVersionsBin
Properties View foundry.project.openInPropertiesView
 
Set Active Version foundry.project.setactiveversion
Hide Version foundry.project.hideversion
Add Snapshot... foundry.project.addsnapshot
Use Bin Version foundry.project.versionlinkusebinversion
Use Track Item Version foundry.project.versionlinkusetrackitemversion
Unlink Selected foundry.project.versionunlinkselected
Version Up foundry.project.versionup
Version Down foundry.project.versiondown
Max Version foundry.project.maxversion
Min Version foundry.project.minversion
Select Version... foundry.project.selectVersion
Link All foundry.project.versionlinkall
Unlink All foundry.project.versionunlinkall
 
Clear Tags foundry.project.clearTags
Clear In/Out Points foundry.project.clearInOut
Set Soft Trims... foundry.timeline.softTrims
 
Reconnect Media... foundry.project.reconnectMedia
Replace Clip... foundry.project.replaceClips
Refresh Clips foundry.project.refreshClips
Rescan Clip Range foundry.project.rescanClips
Set Frame Rate 
8 foundry.project.setFrameRate_8
10 foundry.project.setFrameRate_10
12 foundry.project.setFrameRate_12
12.50 foundry.project.setFrameRate_12.50
15 foundry.project.setFrameRate_15
23.98 foundry.project.setFrameRate_23.98
24 foundry.project.setFrameRate_24
25 foundry.project.setFrameRate_25
29.97 foundry.project.setFrameRate_29.97
30 foundry.project.setFrameRate_30
48 foundry.project.setFrameRate_48
50 foundry.project.setFrameRate_50
59.94 foundry.project.setFrameRate_59.94
60 foundry.project.setFrameRate_60
 
Remove Audio foundry.project.removeAudio
Remove Video foundry.project.removeVideo
 
Insert foundry.viewer.insert
Overwrite foundry.viewer.overwrite
Set Localisation Policy 
On foundry.project.localcachealwayslocalise
From auto-localize path foundry.project.localcacheautolocalise
On demand foundry.project.localcacheondemandlocalise
Off foundry.project.localcacheneverlocalise
RAM Cache 
Clear Playback Cache foundry.viewer.flushAllViewersCache
Clear Audio Waveform Cache foundry.viewer.clearAudioWaveformCache
Clear Audio Cache foundry.viewer.clearAudioCache
Disk Cache 
Pause foundry.cache.pause_disk_cache
 
Cache Sequence Range foundry.cache.cache_sequence
Cache Selected Shot Ranges foundry.cache.cache_selected_clip_ranges
Cache In/Out Range foundry.cache.cache_in_out_range
 
Clear Unused foundry.cache.clear_cache_unused
Clear Sequence Range foundry.cache.clear_cache_sequence
Clear Selected Shot Ranges foundry.cache.clear_cache_selected_clip_ranges
Clear In/Out Range foundry.cache.clear_cache_in_out_range
 
Cache Settings foundry.cache.show_disk_cache_settings
Localization foundry.menu.localization
Pause foundry.project.localcachetoggle
 
Mode 
On foundry.project.localcachesetmodeon
Manual foundry.project.localcachesetmodemanual
Off foundry.project.localcachesetmodeoff
Force Update 
All foundry.project.localcacheforceupdate
Selected foundry.project.localcacheforceupdateselected
On demand only foundry.project.localcacheforceupdateondemand
Clear Unused Local Files foundry.project.clearlocalcache
Localization foundry.menu.localizationNuke
Pause foundry.project.localcachetoggleNuke
 
Mode 
On foundry.project.localcachesetmodeonNuke
Manual foundry.project.localcachesetmodemanualNuke
Off foundry.project.localcachesetmodeoffNuke
Force Update 
All foundry.project.localcacheforceupdateNuke
Selected foundry.project.localcacheforceupdateselectedNuke
On demand only foundry.project.localcacheforceupdateondemandNuke
Clear Unused Local Files foundry.project.clearlocalcacheNuke
New Video Track foundry.timeline.newVideoTrack
New Video Track Blend foundry.menu.sequence.newTrackMenu.blendingModes
Over foundry.timeline.newVideoBlendTrack_Over
Plus foundry.timeline.newVideoBlendTrack_Plus
Multiply foundry.timeline.newVideoBlendTrack_Multiply
Screen foundry.timeline.newVideoBlendTrack_Screen
Color Dodge foundry.timeline.newVideoBlendTrack_Color_Dodge
Color Burn foundry.timeline.newVideoBlendTrack_Color_Burn
Hard Light foundry.timeline.newVideoBlendTrack_Hard_Light
Difference foundry.timeline.newVideoBlendTrack_Difference
Minus foundry.timeline.newVideoBlendTrack_Minus
Min foundry.timeline.newVideoBlendTrack_Min
Max foundry.timeline.newVideoBlendTrack_Max
New Audio Track foundry.timeline.newAudioTrack
 
Mark Selection foundry.timeline.markSelection
Mark Clip foundry.timeline.markClip
 
Razor Selected foundry.timeline.razorSelected
Razor All foundry.timeline.razorAll
 
Ripple Delete foundry.timeline.rippleDelete
 
Retime... foundry.timeline.retime
Make Freeze Frame foundry.timeline.makeFreezeFrame
 
Add Transition foundry.menu.transition
Dissolve foundry.timeline.addDissolveTransition
Fade In foundry.timeline.addFadeInTransition
Fade Out foundry.timeline.addFadeOutTransition
 
Audio Crossfade foundry.timeline.addAudioCrossfadeTransition
Audio Fade In foundry.timeline.addAudioFadeInTransition
Audio Fade Out foundry.timeline.addAudioFadeOutTransition
 
Enable Track Blend foundry.timeline.toggleTrackBlend
Enable Masking foundry.timeline.toggleMaskBlend
Enable Item foundry.timeline.enableItem
Project View foundry.project.openInBin
Project View (Comp Render) foundry.project.openRenderInBinAction
 
Select All in Track foundry.timeline.selectTrackItems
Nudge 
Nudge Left foundry.timeline.nudgeLeft
Nudge Right foundry.timeline.nudgeRight
Nudge Left More foundry.timeline.nudgeLeftMore
Nudge Right More foundry.timeline.nudgeRightMore
Nudge Up foundry.timeline.nudgeUp
Nudge Down foundry.timeline.nudgeDown
 
Audio Scrubbing foundry.timeline.toggleAudioScrubbing
Properties 
Curve Editor 
Dope Sheet 
Progress 
Toolbar 
Error Console 
Pixel Analyzer 
Profile 
Scene Graph 
 
(Viewer1) 
Node Graph 
 
 
New Timeline Viewer foundry.application.newViewer
New Sequence View foundry.application.newTimelineEditor
New Spreadsheet View foundry.application.newSpreadsheet
New Scope 
Histogram foundry.application.newHistogramScope
Waveform foundry.application.newWaveformScope
Vector foundry.application.newVectorScope
 
Timeline Keyboard Shortcuts foundry.help.shortcuts
 
Documentation foundry.help.documentation
Release Notes foundry.help.releasenotes
Training and Tutorials foundry.help.trainingtutorials
Python Dev Guide foundry.help.devguide
Nukepedia foundry.help.nukepedia
Forums foundry.help.mailinglist
 
License... foundry.help.licensing
 
Manage Crash Reports foundry.help.manageCrashReports
About Nuke Studio foundry.application.about
Timeline Tool Group 1 foundry.timeline.timelineToolGroup1
Timeline Tool Group 2 foundry.timeline.timelineToolGroup2
Timeline Tool Group 3 foundry.timeline.timelineToolGroup3
Timeline Tool Group 4 foundry.timeline.timelineToolGroup4
Timeline Tool Group 5 foundry.timeline.timelineToolGroup5
Timeline Tool Group 1 foundry.timeline.timelineToolGroup1
Timeline Tool Group 2 foundry.timeline.timelineToolGroup2
Timeline Tool Group 3 foundry.timeline.timelineToolGroup3
Timeline Tool Group 4 foundry.timeline.timelineToolGroup4
Timeline Tool Group 5 foundry.timeline.timelineToolGroup5
Rename Shots... foundry.timeline.renameshots
Create Comp foundry.timeline.comp.createComp
Create Comp Special... foundry.timeline.comp.createCompSpecial
ColorCorrect foundry.timeline.effect.addColorCorrect
Grade foundry.timeline.effect.addGrade
Transform foundry.timeline.effect.addTransform
 foundry.timeline.effect.separator
Text foundry.timeline.effect.addText
Timewarp foundry.timeline.effect.addTimewarp
Color foundry.timeline.effect.colorMenuAction
ColorLookup foundry.timeline.effect.addColorLookup
OCIO CDLTransform foundry.timeline.effect.addOCIOCDLTransform
OCIO ColorSpace foundry.timeline.effect.addOCIOColorSpace
OCIO Display foundry.timeline.effect.addOCIODisplay
OCIO FileTransform LUT foundry.timeline.effect.addOCIOFileTransform
OCIO LogConvert foundry.timeline.effect.addOCIOLogConvert
OCIO LookTransform foundry.timeline.effect.addOCIOLookTransform
OCIO NamedTransform foundry.timeline.effect.addOCIONamedTransform
Denoise foundry.timeline.effect.Denoise
ChromaKeyer foundry.timeline.effect.ChromaKeyer
Merge foundry.timeline.effect.mergeMenuAction
Premult foundry.timeline.effect.Premult
Unpremult foundry.timeline.effect.Unpremult
Transformations foundry.timeline.effect.transformsMenuAction
Crop foundry.timeline.effect.addCrop
LensDistortion foundry.timeline.effect.LensDistortion
Mirror foundry.timeline.effect.addMirror
CornerPin foundry.timeline.effect.CornerPin
ModifyMetaData foundry.timeline.effect.ModifyMetaData
Burn-In foundry.timeline.effect.addBurnIn
Inference foundry.timeline.effect.Inference
BlinkScript foundry.timeline.effect.BlinkScript