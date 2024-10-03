@echo off
rem Change directory to the desired folder
cd /d "C:\Users\leg4-pc\.nuke"

rem Create the zip file with exclusions from the specified folder
"C:\Program Files\7-Zip\7z.exe" a -tzip LGA_HeiroTools.zip Python\Startup\* +Instalacion_HieroTools.txt -xr@Python\Startup\+exclude.lst

rem Pause the script to see any error messages
pause
