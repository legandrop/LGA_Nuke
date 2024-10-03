"""
___________________________________________________________________________________________________

  LGA_removeAccents v1.1 | 2024 | Lega  
  Tool for removing accents and the letter 'n' from .py files in the script's directory.
  Processes all .py files in the directory where the script is located, including subdirectories.
___________________________________________________________________________________________________

"""


import os
import unicodedata

def remove_accents(input_str):
    # Transformar la cadena a unicode normalizado
    nfkd_form = unicodedata.normalize('NFKD', input_str)
    return ''.join([c for c in nfkd_form if not unicodedata.combining(c)])

def process_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()

    # Eliminar acentos y reemplazar n por n
    new_content = remove_accents(content).replace('n', 'n').replace('N', 'N')

    # Solo sobrescribir si hubo cambios
    if content != new_content:
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(new_content)

def process_directory(directory):
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                process_file(file_path)

# Obtener el directorio donde se encuentra el script
script_directory = os.path.dirname(os.path.abspath(__file__))
process_directory(script_directory)
