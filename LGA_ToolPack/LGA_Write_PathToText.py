"""
____________________________________________________________________________________

  LGA_Write_PathToText v0.1 | Lega
  Script para crear un nodo Text conectado al Write seleccionado y copiar el path del Write al campo message del Text.
____________________________________________________________________________________
"""

import nuke

# Variable global para activar o desactivar los prints de depuracion
debug = True  # Cambiar a False para ocultar los mensajes de debug


# Funcion para imprimir mensajes de depuracion
def debug_print(*message):
    if debug:
        print("[LGA_Write_PathToText]", *message)


def main():
    """
    Si hay un nodo Write seleccionado, crea un nodo Text conectado a él,
    copia el path del Write al campo message del Text y hace un debug log con la resolución actual del script.
    """
    # Buscar nodos seleccionados
    selected_nodes = nuke.selectedNodes()
    if not selected_nodes:
        debug_print("No hay nodos seleccionados. No se hace nada.")
        return
    # Buscar el primer nodo Write seleccionado
    write_node = None
    for node in selected_nodes:
        if node.Class() == "Write":
            write_node = node
            break
    if not write_node:
        debug_print("No hay ningun nodo Write seleccionado. No se hace nada.")
        return
    # Crear el nodo Text y conectarlo al Write
    text_node = nuke.createNode("Text", inpanel=False)
    text_node.setInput(0, write_node)
    # Copiar el path del Write al campo message del Text
    write_file = write_node["file"].value()
    message_text = write_file
    # Si el path contiene brackets, intentar evaluarlo y agregar el resultado
    if "[" in write_file and "]" in write_file:
        try:
            # Usar nuke.filename para obtener el path evaluado
            evaluated_path = nuke.filename(write_node)
            if evaluated_path is None:
                evaluated_path = ""
            message_text += "\n\n" + evaluated_path
            debug_print(f"Path evaluado: {evaluated_path}")
        except Exception as e:
            debug_print(f"Error al evaluar el path: {e}")
    text_node["message"].setValue(message_text)
    # Imprimir la resolucion actual del script
    script_format = nuke.root().format()
    width = script_format.width()
    height = script_format.height()
    debug_print(f"Resolucion del script: {width}x{height}")
    debug_print(f"Path copiado al Text: {write_file}")


# --- Main Execution ---
if __name__ == "__main__":
    # Necesario para ejecucion standalone fuera de Nuke
    main()
