@echo off
rem Cambiar directorio a la carpeta deseada
cd /d "C:\Users\leg4-pc\.nuke"

rem Copiar temporalmente el archivo LGA_ToolPack.pdf a la carpeta actual
copy "LGA_ToolPack\LGA_ToolPack.pdf" .

rem Crear el archivo zip con las exclusiones especificadas y el archivo PDF en la raíz
"C:\Program Files\7-Zip\7z.exe" a -tzip LGA_ToolPack.zip LGA_ToolPack\* LGA_ToolPack.pdf -xr@LGA_ToolPack\+exclude.lst

rem Eliminar el archivo PDF temporal de la carpeta actual
del LGA_ToolPack.pdf



rem Pause the script to see any error messages
rem pause
