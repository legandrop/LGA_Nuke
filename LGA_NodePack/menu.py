"""
___________________________________________________________________________________________

  LGA_NodePack v1.32 Lega Pugliese
  Automatically imports all tools located within folders and subfolders into the Node Bar
___________________________________________________________________________________________

"""

import os
import nuke

# Obtener la ruta del directorio del script actual
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))


def get_folder_icon(folder_name, folder_path):
    icon_ext = ".png"  # Ajusta la extension del icono
    icon_path = os.path.join(folder_path, f"{folder_name}{icon_ext}")
    if os.path.exists(icon_path):
        return icon_path


def get_file_icon(file_name):
    pass


def load_files_in_directory(directory, menu):
    list_files = sorted(
        os.listdir(directory), key=lambda x: os.path.splitext(x)[0].lower()
    )
    directories = []
    files = []
    # Separar a las carpetas de los archivos
    for f in list_files:
        f_name, f_ext = os.path.splitext(f)
        f_path = os.path.join(directory, f)
        if os.path.isdir(f_path):
            directories.append((f_name, f_path))
        elif f_ext in [".nk", ".py", ".gizmo"]:
            files.append((f_name, f_path))
    # Agregar carpetas al menu
    for folder_name, folder_path in directories:
        f_icon_path = get_folder_icon(folder_name, folder_path)
        sub_menu = menu.addMenu(folder_name, icon=f_icon_path)
        load_files_in_directory(folder_path, sub_menu)
        nuke.pluginAddPath(folder_path)
    # Agregar archivos al menu
    for file_name, file_path in files:
        f_icon_path = get_file_icon(file_name)
        if file_name != "menu":
            if file_path.endswith(".gizmo"):
                menu.addCommand(
                    file_name,
                    'nuke.createNode("{}")'.format(file_name),
                    icon=f_icon_path,
                )
            elif file_path.endswith(".nk") or (
                file_path.endswith(".py") and "init" in file_name
            ):
                menu.addCommand(
                    file_name,
                    'nuke.loadToolset("{}")'.format(file_path.replace("\\", "/")),
                    icon=f_icon_path,
                )


nodes_menu = nuke.menu("Nodes")

# Obtener todas las subcarpetas dentro del directorio del script actual y ordenarlas alfabeticamente
subfolders = [
    os.path.join(SCRIPT_DIR, d)
    for d in sorted(os.listdir(SCRIPT_DIR), key=lambda x: x.lower())
    if os.path.isdir(os.path.join(SCRIPT_DIR, d))
]

# Crear menus para cada subcarpeta que no contenga *init*.py o menu.py
for folder in subfolders:
    menu_name = os.path.basename(folder)
    if not os.path.exists(os.path.join(folder, "menu.py")) and not any(
        file.endswith(".py") and "init" in file for file in os.listdir(folder)
    ):
        sub_menu = nodes_menu.addMenu(
            menu_name, icon=get_folder_icon(menu_name, folder)
        )
        load_files_in_directory(folder, sub_menu)
        nuke.pluginAddPath(folder)
    else:
        nuke.pluginAddPath(folder)
