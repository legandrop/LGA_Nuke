@echo off
rem Cambiar directorio a la carpeta deseada
cd /d "C:\Users\leg4-pc\.nuke"

rem Definir la ruta de destino para el archivo zip
set "DESTINO=C:\Users\leg4-pc\.nuke\LGA_ToolsVA"

rem Verificar si el archivo zip ya existe y borrarlo si es necesario
if exist "%DESTINO%\LGA_NodePack.zip" del "%DESTINO%\LGA_NodePack.zip"

rem Copiar temporalmente el archivo de instalación a la carpeta actual
copy "LGA_ToolsVA\+Instalacion_NodePack.txt" .

rem Crear el archivo zip con las exclusiones especificadas y el archivo de instalación en la raíz
"C:\Program Files\7-Zip\7z.exe" a -tzip "%DESTINO%\LGA_NodePack.zip" LGA_NodePack\* +Instalacion_NodePack.txt -xr@LGA_NodePack\+exclude.lst

rem Eliminar el archivo de instalación temporal de la carpeta actual
del +Instalacion_NodePack.txt

rem Pausar el script para ver cualquier mensaje de error
pause
