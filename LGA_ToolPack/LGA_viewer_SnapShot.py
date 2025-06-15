"""
______________________________________________________________________________

  LGA_NKS_SnapShot v0.55 - Lega
  Crea un snapshot de la imagen actual del viewer y lo copia al portapapeles
______________________________________________________________________________

"""

import nuke
import nukescripts
import os
import tempfile

try:
    # nuke <11
    import PySide.QtGui as QtGui
    import PySide.QtCore as QtCore
    import PySide.QtWidgets as QtWidgets
    from PySide.QtGui import QImage, QClipboard
    from PySide.QtWidgets import QApplication
except:
    # nuke>=11
    import PySide2.QtGui as QtGui
    import PySide2.QtCore as QtCore
    import PySide2.QtWidgets as QtWidgets
    from PySide2.QtGui import QImage, QClipboard
    from PySide2.QtWidgets import QApplication

DEBUG = True
SaveToFile = False


def debug_print(*message):
    if DEBUG:
        print(*message)


def check_render_complete_module():
    """
    Verifica si el modulo LGA_Write_RenderComplete esta disponible y si el sonido esta activado.
    Retorna True si ambas condiciones se cumplen, False en caso contrario.
    """
    try:
        # Intentar importar las funciones necesarias del modulo RenderComplete
        from LGA_Write_RenderComplete import (
            get_sound_enabled_from_config,
            get_wav_path_from_config,
            save_wav_path_to_config,
        )

        # Verificar si el sonido esta activado en la configuracion
        sound_enabled = get_sound_enabled_from_config()
        debug_print(f"RenderComplete encontrado. Sonido activado: {sound_enabled}")
        return sound_enabled

    except ImportError as e:
        debug_print(f"Modulo LGA_Write_RenderComplete no encontrado: {e}")
        return False
    except Exception as e:
        debug_print(f"Error al verificar RenderComplete: {e}")
        return False


def set_silence_wav_temporarily():
    """
    Guarda el wav actual y lo reemplaza temporalmente por el archivo de silencio.
    Retorna el path del wav original para poder restaurarlo despues.
    """
    try:
        from LGA_Write_RenderComplete import (
            get_wav_path_from_config,
            save_wav_path_to_config,
        )

        # Obtener el wav actual
        original_wav_path = get_wav_path_from_config()
        debug_print(f"WAV original: {original_wav_path}")

        # Crear el path del archivo de silencio (en la misma carpeta que este script)
        silence_wav_path = os.path.join(
            os.path.dirname(__file__), "LGA_Write_RenderComplete_silence.wav"
        )

        # Verificar que el archivo de silencio existe
        if not os.path.exists(silence_wav_path):
            debug_print(f"Archivo de silencio no encontrado: {silence_wav_path}")
            return original_wav_path

        # Guardar temporalmente el wav de silencio
        save_wav_path_to_config(silence_wav_path)
        debug_print(f"WAV cambiado temporalmente a: {silence_wav_path}")

        return original_wav_path

    except Exception as e:
        debug_print(f"Error al configurar wav de silencio: {e}")
        return None


def restore_original_wav(original_wav_path):
    """
    Restaura el wav original en la configuracion.
    """
    if not original_wav_path:
        debug_print("No hay wav original para restaurar")
        return

    try:
        from LGA_Write_RenderComplete import save_wav_path_to_config

        save_wav_path_to_config(original_wav_path)
        debug_print(f"WAV restaurado a: {original_wav_path}")

    except Exception as e:
        debug_print(f"Error al restaurar wav original: {e}")


def main():
    # --- Comprobaciones iniciales del viewer de Nuke ---
    viewer = nuke.activeViewer()
    if viewer is None:
        nuke.message(
            "No hay viewer activo. Por favor, abre un viewer antes de tomar un snapshot."
        )
        debug_print("ERROR: No hay viewer activo. Saliendo.")
        return

    view_node = viewer.node()
    if view_node is None:
        nuke.message(
            "El viewer no está mostrando ningún nodo. Conecta un nodo al viewer para tomar un snapshot."
        )
        debug_print("ERROR: El viewer no está mostrando ningún nodo. Saliendo.")
        return

    input_index = viewer.activeInput()
    # Nuke generalmente devuelve un entero para activeInput(), pero se añade una verificación defensiva.
    if not isinstance(input_index, int):
        debug_print(
            f"ERROR: viewer.activeInput() devolvió un tipo inesperado: {type(input_index)}. Saliendo."
        )
        return

    # Esta línea ahora está segura, ya que input_index es un entero
    input_node = view_node.input(input_index)

    if input_node is None:
        nuke.message(
            "No hay nodo conectado al viewer en la entrada activa. Asegúrate de que un nodo esté conectado para tomar un snapshot."
        )
        debug_print(
            "ERROR: No hay nodo conectado al viewer en la entrada activa. Saliendo."
        )
        return

    # --- Una vez que las comprobaciones iniciales son satisfactorias, proceder con la lógica RenderComplete ---
    render_complete_active = check_render_complete_module()
    original_wav_path = None

    # Si RenderComplete esta activo, cambiar temporalmente el wav
    if render_complete_active:
        original_wav_path = set_silence_wav_temporarily()

    try:
        temp_dir = tempfile.gettempdir()
        output_path = os.path.join(temp_dir, "snapshot.jpg")

        frame = int(nuke.frame())

        # Obtener la posicion del nodo de entrada
        input_node_xpos = input_node.xpos()
        input_node_ypos = input_node.ypos()

        # 1. Recordar el nodo seleccionado actualmente
        originally_selected_nodes = nuke.selectedNodes()
        debug_print(
            f"Nodos originalmente seleccionados: {[n.name() for n in originally_selected_nodes]}"
        )

        try:
            # 2. Deseleccionar todos los nodos y seleccionar solo el nodo conectado al viewer
            for node in nuke.allNodes():
                node.setSelected(False)
            input_node.setSelected(True)
            debug_print(f"Nodo seleccionado temporalmente: {input_node.name()}")

            # Calcular el offset Y basado en la altura del nodo de entrada
            dynamic_y_offset = input_node.screenHeight() + 10
            debug_print(f"Offset Y dinamico: {dynamic_y_offset}")

            # 3. Crear el Write temporal (ahora se creara conectado al nodo correcto)
            write_node = nuke.createNode(
                "Write",
                "file_type jpeg postage_stamp false hide_input true label 'LGA_TEMP'",
                inpanel=False,
            )

            # Mover el nodo Write a la posicion del nodo de entrada
            write_node.setXpos(input_node_xpos)
            write_node.setYpos(input_node_ypos + dynamic_y_offset)

            # Blindaje: convertir path a forward slashes para evitar problemas de escapes
            safe_path = output_path.replace("\\", "/")
            write_node["file"].setValue(safe_path)

            debug_print("Generando snapshot temporal en:", safe_path)

            try:
                nuke.execute(write_node, frame, frame)
            except Exception as e:
                nuke.delete(write_node)
                nuke.message(f"Error al ejecutar el Write: {str(e)}")
                return
            finally:
                # Asegurar que el nodo Write se elimine incluso si hay error
                if nuke.exists(write_node.name()):
                    nuke.delete(write_node)

        finally:
            # 4. Restaurar la seleccion original
            for node in nuke.allNodes():
                node.setSelected(False)
            for node in originally_selected_nodes:
                node.setSelected(True)
            debug_print(
                f"Seleccion restaurada: {[n.name() for n in originally_selected_nodes]}"
            )

        if not os.path.exists(output_path):
            nuke.message(
                "Error: el archivo del snapshot no se generó. Por favor, verifica los permisos o la ruta temporal."
            )
            return

        # Cargar el JPEG como QImage
        qimage = QtGui.QImage(output_path)
        if qimage.isNull():
            nuke.message(
                "Error al leer el snapshot generado. El archivo de imagen temporal está vacío o corrupto."
            )
            return

        debug_print("Snapshot size:", qimage.width(), "×", qimage.height())

        if SaveToFile:
            save_path = r"T:\Borrame\snapshot.jpg"
            output_dir = os.path.dirname(save_path)
            try:
                os.makedirs(output_dir, exist_ok=True)
            except Exception as e:
                nuke.message(f"Error al crear el directorio de guardado: {str(e)}")
                debug_print(f"ERROR: No se pudo crear el directorio de guardado: {e}")
                return
            ok = qimage.save(save_path, "JPEG")
            debug_print("Archivo final guardado:", ok, save_path)

        # Copiar al portapapeles
        app = QApplication.instance()
        if not app:
            app = QApplication([])

        clipboard = app.clipboard()
        clipboard.setImage(qimage)

        debug_print("✅ Imagen copiada al portapapeles.")

        # Limpiar el temporal
        try:
            os.remove(output_path)
        except:
            pass

    finally:
        # Restaurar el wav original si se cambio temporalmente
        if render_complete_active and original_wav_path:
            restore_original_wav(original_wav_path)


# --- Main Execution ---
if __name__ == "__main__":
    main()
