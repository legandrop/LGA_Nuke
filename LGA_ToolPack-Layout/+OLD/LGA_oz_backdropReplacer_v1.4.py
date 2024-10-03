"""
___________________________________________________________________________________________

  LGA_oz_backdropReplacer v1.4 | 2024 | Lega 
  Replace the selected backdrop with an oz_backdrop or all backdrops if none are selected
___________________________________________________________________________________________

"""

import nuke
import nukescripts
import os
import sys

# Obtiene la ruta del directorio donde se encuentra el script actual.
script_dir = os.path.dirname(__file__)

# Construye la ruta hacia la carpeta 'oz_backdrop' asumiendo que esta en el mismo directorio que el script actual.
oz_backdrop_path = os.path.join(script_dir, "oz_backdrop")

# Agrega la ruta construida al sys.path
sys.path.append(oz_backdrop_path)

import oz_backdrop

def strip_html_tags(text):
    """Elimina etiquetas HTML del texto"""
    import re
    clean = re.compile('<.*?>')
    return re.sub(clean, '', text)


def replace_with_oz_backdrop():
    selected_backdrops = [n for n in nuke.selectedNodes() if n.Class() == 'BackdropNode']

    if selected_backdrops:
        # Si hay backdrops seleccionados, reemplaza solo esos
        nodes_to_replace = selected_backdrops
    else:
        # Si no hay backdrops seleccionados, reemplaza todos
        nodes_to_replace = [n for n in nuke.allNodes() if n.Class() == 'BackdropNode']

    for node in nodes_to_replace:
        # Guardar las propiedades del backdrop existente
        label = node['label'].getValue()
        note_font_size = int(node['note_font_size'].getValue())
        note_font_color = int(node['note_font_color'].getValue())
        tile_color = int(node['tile_color'].getValue())
        xpos = int(node.xpos())
        ypos = int(node.ypos())
        bdwidth = int(node['bdwidth'].getValue())
        bdheight = int(node['bdheight'].getValue())
        
        # Comprobar si 'zorder' o 'z_order' existen y guardar el valor
        if 'zorder' in node.knobs():
            zorder = int(node['zorder'].getValue())
        elif 'z_order' in node.knobs():
            zorder = int(node['z_order'].getValue())

        alignment_value = node['alignment'].value() if 'alignment' in node.knobs() else 'left'
        oz_appearance_value = node['oz_appearance'].value() if 'oz_appearance' in node.knobs() else 'Fill'
        border_width_value = int(node['border_width'].value()) if 'border_width' in node.knobs() else 2
        sides_value = int(node['sides'].value()) if 'sides' in node.knobs() else 50

        # Deseleccionar todos los nodos y seleccionar el actual
        for n in nuke.allNodes():
            n.setSelected(False)
        node.setSelected(True)

        # Crear un nuevo oz_backdrop
        new_bd = oz_backdrop.autoBackdrop(show_input=False, is_replacement=True, original_node=node)

        # Asignar valores solo si los knobs existen
        if 'label' in new_bd.knobs():
            new_bd['label'].setValue(label)
        if 'tile_color' in new_bd.knobs():
            new_bd['tile_color'].setValue(tile_color)
        if 'note_font_color' in new_bd.knobs():
            new_bd['note_font_color'].setValue(note_font_color)
        new_bd.setXYpos(xpos, ypos)
        if 'bdwidth' in new_bd.knobs():
            new_bd['bdwidth'].setValue(bdwidth)
        if 'bdheight' in new_bd.knobs():
            new_bd['bdheight'].setValue(bdheight)
        if 'zorder' in new_bd.knobs():
            new_bd['zorder'].setValue(zorder)

        # Configurar el valor del knob 'text' si existe, eliminando etiquetas HTML
        if 'text' in new_bd.knobs():
            stripped_label = strip_html_tags(label)
            new_bd['text'].setValue(stripped_label)

        # Aplicar los valores recuperados
        if 'note_font_size' in new_bd.knobs():
            new_bd['note_font_size'].setValue(note_font_size)
        if 'alignment' in new_bd.knobs():
            new_bd['alignment'].setValue(alignment_value)
        if 'oz_appearance' in new_bd.knobs():
            new_bd['oz_appearance'].setValue(oz_appearance_value)
        if 'oz_border_width' in new_bd.knobs():
            new_bd['oz_border_width'].setValue(border_width_value)
        if 'sides' in new_bd.knobs():
            new_bd['sides'].setValue(sides_value)

        # Eliminar el backdrop original
        nuke.delete(node)




# Llamar a la funcion para reemplazar los backdrops
# replace_with_oz_backdrop()
