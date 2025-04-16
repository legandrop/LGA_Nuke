"""
___________________________________________________________________________________________________

  LGA_CDL_CC_IP v1.0 | 2024 | Lega  

  Herramienta para exportar los valores CDL desde un nodo Read o OCIOCDLTransform y convertirlos 
  en un archivo .cc que se guarda en el mismo directorio que el archivo CDL original.

  Crea dos nodos OCIOFileTransform:
  uno para el renderizado de MOV y otro configurado como el Input Process activo.
___________________________________________________________________________________________________

"""


import nuke
import os

# Variable global para activar o desactivar los prints
DEBUG = False

def debug_print(*message):
    if DEBUG:
        print(*message)

def main():
    # Obtener el nodo seleccionado
    selected_node = nuke.selectedNode()
    
    # Verificar si hay un nodo seleccionado y si es un OCIOCDLTransform o un Read
    if selected_node and selected_node.Class() in ["OCIOCDLTransform", "Read"]:
        # Obtener el valor del knob 'file'
        if selected_node.Class() == "OCIOCDLTransform":
            file_path = selected_node['file'].value()
        else:  # Read node
            file_path = selected_node['file'].value()
            cdl_path = os.path.splitext(file_path)[0] + '.cdl'
            if not os.path.exists(cdl_path):
                print(f"Error: No se encontro un archivo .cdl correspondiente para {file_path}")
                return
            file_path = cdl_path
        
        # Crear el nuevo nombre de archivo con extension .cc
        new_file_path = os.path.splitext(file_path)[0] + '.cc'
        
        # Crear el contenido del archivo .cc
        if selected_node.Class() == "OCIOCDLTransform":
            slope = selected_node['slope'].value()
            offset = selected_node['offset'].value()
            power = selected_node['power'].value()
            saturation = selected_node['saturation'].value()
        else:  # Read node
            # Leer los valores del archivo .cdl
            slope, offset, power, saturation = read_cdl_values(cdl_path)
        
        cc_content = f"""<ColorCorrection id="{os.path.basename(new_file_path)}">
    <SOPNode>
        <Slope>{slope[0]} {slope[1]} {slope[2]}</Slope>
        <Offset>{offset[0]} {offset[1]} {offset[2]}</Offset>
        <Power>{power[0]} {power[1]} {power[2]}</Power>
    </SOPNode>
    <SatNode>
        <Saturation>{saturation}</Saturation>
    </SatNode>
</ColorCorrection>
"""
        
        # Escribir el archivo .cc
        try:
            with open(new_file_path, 'w') as f:
                f.write(cc_content)
            debug_print(f"Archivo CC exportado exitosamente: {new_file_path}")
            
            # Deseleccionar todos los nodos
            for n in nuke.allNodes():
                n['selected'].setValue(False)
            
            # Crear y configurar el nodo OCIOFileTransform desconectado
            ocio_file_transform = nuke.nodes.OCIOFileTransform()
            ocio_file_transform['file'].setValue(new_file_path)
            ocio_file_transform['working_space'].setValue("ACES - ACEScct")
            ocio_file_transform['label'].setValue("Input Process")
            
            # Posicionar y seleccionar el nuevo OCIOFileTransform (desconectado)
            ocio_file_transform.setXYpos(selected_node.xpos(), selected_node.ypos() + 140)
            ocio_file_transform['selected'].setValue(True)
            debug_print("Nodo OCIOFileTransform creado y configurado.")

            # Asignar el nodo como input process al viewer activo
            for viewer in nuke.allNodes("Viewer"):
                viewer['input_process_node'].setValue(ocio_file_transform.name())
                debug_print(f"Nodo {ocio_file_transform.name()} configurado como Input Process en el Viewer {viewer.name()}.")

            # Obtener el nodo seleccionado (que es el OCIOFileTransform)
            selected_node = nuke.selectedNode()
            for n in nuke.allNodes():
                n['selected'].setValue(False)
            
            # Duplicar el nodo seleccionado y copiar las configs del original
            ocio_file_transform_duplicate = nuke.createNode("OCIOFileTransform")
            ocio_file_transform_duplicate['file'].setValue(selected_node['file'].value())
            ocio_file_transform_duplicate['working_space'].setValue(selected_node['working_space'].value())
            ocio_file_transform_duplicate['label'].setValue("Write MOV")
            ocio_file_transform_duplicate.setXYpos(selected_node.xpos(), selected_node.ypos() + 80)
            
            debug_print("Nodo duplicado con etiqueta 'Write MOV' creado.")
            
        except Exception as e:
            print(f"Error: {str(e)}")

    else:
        print("No se ha seleccionado un nodo OCIOCDLTransform o Read valido.")

import nuke

def read_cdl_values(cdl_path):
    # Inicializacion de variables como None para verificar si se encontraron en el archivo
    slope = None
    offset = None
    power = None
    saturation = None
    
    # Abre el archivo CDL en modo lectura
    with open(cdl_path, 'r') as f:
        # Itera sobre cada linea del archivo
        for line in f:
            # Busca y extrae los valores de Slope, Offset, Power y Saturation
            if '<Slope>' in line:
                slope = [float(x) for x in line.split('>')[1].split('<')[0].split()]
            elif '<Offset>' in line:
                offset = [float(x) for x in line.split('>')[1].split('<')[0].split()]
            elif '<Power>' in line:
                power = [float(x) for x in line.split('>')[1].split('<')[0].split()]
            elif '<Saturation>' in line:
                saturation = float(line.split('>')[1].split('<')[0])
    
    # Chequea si se encontraron todos los valores necesarios o tira mensaje de error
    if slope is None:
        nuke.message("Error: No se encontro el valor de Slope en el archivo CDL.")
        raise ValueError("Falta el valor de Slope")
    
    if offset is None:
        nuke.message("Error: No se encontro el valor de Offset en el archivo CDL.")
        raise ValueError("Falta el valor de Offset")
    
    if power is None:
        nuke.message("Error: No se encontro el valor de Power en el archivo CDL.")
        raise ValueError("Falta el valor de Power")
    
    if saturation is None:
        nuke.message("Error: No se encontro el valor de Saturation en el archivo CDL.")
        raise ValueError("Falta el valor de Saturation")
    
    # Si todos los valores se encontraron, los devuelve como una tupla
    return slope, offset, power, saturation

# Ejecutar la funcion
#main()