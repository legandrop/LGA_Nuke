@echo off
rem Cambiar directorio a la carpeta deseada
cd /d "C:\Users\leg4-pc\.nuke"

rem Copiar temporalmente el archivo LGA_LayoutToolPack.pdf a la carpeta actual
copy "LGA_ToolPack-Layout\LGA_LayoutToolPack.pdf" .

rem Crear el archivo zip con las exclusiones especificadas y el archivo PDF en la raíz
"C:\Program Files\7-Zip\7z.exe" a -tzip LGA_ToolPack-Layout.zip LGA_ToolPack-Layout\* LGA_LayoutToolPack.pdf -xr@LGA_ToolPack-Layout\+exclude.lst

rem Eliminar el archivo PDF temporal de la carpeta actual
del LGA_LayoutToolPack.pdf

rem Pause the script to see any error messages
rem pause
