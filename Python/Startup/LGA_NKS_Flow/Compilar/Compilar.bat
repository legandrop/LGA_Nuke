@echo off
setlocal enabledelayedexpansion

REM Initialize variables
set "max_version=0"
set "max_version_file="

REM Search for files matching the pattern
for %%f in (LGA_NKS_Flow_Downloader_v*.py) do (
    REM Extract the version number from the filename
    set "filename=%%~nf"
    set "version=!filename:*_v=!"

    REM Ensure the version number is treated as an integer
    set /a version_num=!version!

    REM Compare with the highest version found so far
    if !version_num! gtr !max_version! (
        set "max_version=!version_num!"
        set "max_version_file=%%f"
    )
)

REM Print the file with the highest version number
if defined max_version_file (
    echo The highest version is v!max_version! in the file "!max_version_file!"
    
    REM Check if LGA_NKS_Flow_Downloader.py already exists
    if exist LGA_NKS_Flow_Downloader.py (
        echo LGA_NKS_Flow_Downloader.py already exists and will be overwritten.
    ) else (
        echo LGA_NKS_Flow_Downloader.py does not exist and will be created.
    )
    
    REM Copy the file with the highest version to LGA_NKS_Flow_Downloader.py
    copy /y "!max_version_file!" "LGA_NKS_Flow_Downloader.py"
    
    REM Confirm the file was copied
    if exist LGA_NKS_Flow_Downloader.py (
        echo The file has been successfully copied and renamed to LGA_NKS_Flow_Downloader.py.
        
        REM Compile the file using pyinstaller
        echo Compiling the file with pyinstaller...
        pyinstaller --onefile --add-data "Data/no_icon.ico;Data" --add-data "Data/LGA.ico;Data" --add-data "Data/settings_off.png;Data" --add-data "Data/settings_on.png;Data" --add-data "Data/CTkScrollableDropdown/ctk_scrollable_dropdown.py;Data/CTkScrollableDropdown" --add-data "Data/LGA_NKS_Flow_Downloader_CCTK_Theme.json;Data" -i "Data/LGA.ico" LGA_NKS_Flow_Downloader.py
        
        echo Compilation completed.
    ) else (
        echo There was an error copying the file.
    )
) else (
    echo No files matching the pattern were found.
)

pause
