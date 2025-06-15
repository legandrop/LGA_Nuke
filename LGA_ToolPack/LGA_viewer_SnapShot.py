"""
______________________________________________________________________________

  LGA_viewer_SnapShot v0.57 - Lega
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
    from PySide.QtCore import QTimer, QEventLoop
except:
    # nuke>=11
    import PySide2.QtGui as QtGui
    import PySide2.QtCore as QtCore
    import PySide2.QtWidgets as QtWidgets
    from PySide2.QtGui import QImage, QClipboard
    from PySide2.QtWidgets import QApplication
    from PySide2.QtCore import QTimer, QEventLoop

DEBUG = True
SaveToFile = True


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


def get_viewer_info():
    """
    Obtiene informacion del viewer activo y el nodo conectado.
    Retorna una tupla (viewer, view_node, input_index, input_node) o None si hay error.
    """
    viewer = nuke.activeViewer()
    if viewer is None:
        debug_print("ERROR: No hay viewer activo.")
        return None

    view_node = viewer.node()
    if view_node is None:
        debug_print("ERROR: El viewer no está mostrando ningún nodo.")
        return None

    input_index = viewer.activeInput()
    if not isinstance(input_index, int):
        debug_print(
            f"ERROR: viewer.activeInput() devolvió un tipo inesperado: {type(input_index)}"
        )
        return None

    input_node = view_node.input(input_index)
    if input_node is None:
        debug_print("ERROR: No hay nodo conectado al viewer en la entrada activa.")
        return None

    return viewer, view_node, input_index, input_node


def show_snapshot():
    """
    Muestra el snapshot temporal en el viewer durante 1 segundo.
    """
    import time

    # 1. Verificar si existe el archivo snapshot
    temp_dir = tempfile.gettempdir()
    snapshot_path = os.path.join(temp_dir, "LGA_snapshot.jpg")

    if not os.path.exists(snapshot_path):
        debug_print(
            f"ERROR: No existe archivo de snapshot en la carpeta temporal: {snapshot_path}"
        )
        return

    debug_print(f"Snapshot encontrado: {snapshot_path}")

    # 2. Verificar viewer y nodo conectado
    viewer_info = get_viewer_info()
    if viewer_info is None:
        debug_print("ERROR: No se pudo obtener informacion del viewer")
        return

    viewer, view_node, input_index, input_node = viewer_info
    debug_print(
        f"Viewer activo: {view_node.name()}, nodo conectado: {input_node.name()}"
    )

    # 3. Guardar estado original
    originally_selected_nodes = nuke.selectedNodes()
    debug_print(
        f"Nodos originalmente seleccionados: {[n.name() for n in originally_selected_nodes]}"
    )

    # Obtener posicion del nodo de entrada
    input_node_xpos = input_node.xpos()
    input_node_ypos = input_node.ypos()

    # Calcular offset Y dinamico
    dynamic_y_offset = input_node.screenHeight() + 10
    debug_print(
        f"Posicion del nodo: ({input_node_xpos}, {input_node_ypos}), offset Y: {dynamic_y_offset}"
    )

    read_node = None
    try:
        # 4. Deseleccionar todos los nodos y seleccionar el nodo conectado
        for node in nuke.allNodes():
            node.setSelected(False)
        input_node.setSelected(True)

        # 5. Crear nodo Read temporal
        safe_path = snapshot_path.replace("\\", "/")
        read_node = nuke.createNode(
            "Read",
            f"file {{{safe_path}}} label 'LGA_SNAPSHOT_TEMP'",
            inpanel=False,
        )

        # Posicionar el nodo Read debajo del nodo de entrada
        read_node.setXpos(input_node_xpos)
        read_node.setYpos(input_node_ypos + dynamic_y_offset)

        debug_print(
            f"Nodo Read creado: {read_node.name()} en posicion ({read_node.xpos()}, {read_node.ypos()})"
        )

        # 6. Conectar el Read al viewer
        view_node.setInput(input_index, read_node)
        debug_print(f"Read conectado al viewer en input {input_index}")

        # 7. Esperar 1 segundo
        debug_print("Mostrando snapshot por 1 segundo...")
        loop = QEventLoop()
        QTimer.singleShot(1000, loop.quit)
        loop.exec_()

    except Exception as e:
        debug_print(f"Error al mostrar snapshot: {e}")

    finally:
        # 8. Restaurar estado original
        try:
            if read_node and nuke.exists(read_node.name()):
                # Reconectar el nodo original al viewer
                view_node.setInput(input_index, input_node)
                debug_print(f"Nodo original {input_node.name()} reconectado al viewer")

                # Eliminar el nodo Read temporal
                nuke.delete(read_node)
                debug_print("Nodo Read temporal eliminado")

            # Restaurar seleccion original
            for node in nuke.allNodes():
                node.setSelected(False)
            for node in originally_selected_nodes:
                node.setSelected(True)
            debug_print(
                f"Seleccion restaurada: {[n.name() for n in originally_selected_nodes]}"
            )

        except Exception as e:
            debug_print(f"Error al restaurar estado original: {e}")

    debug_print("✅ Snapshot mostrado y estado restaurado")


def take_snapshot():
    # --- Comprobaciones iniciales del viewer de Nuke ---
    viewer_info = get_viewer_info()
    if viewer_info is None:
        nuke.message(
            "No hay viewer activo o nodo conectado. Por favor, conecta un nodo al viewer antes de tomar un snapshot."
        )
        return

    viewer, view_node, input_index, input_node = viewer_info

    # --- Una vez que las comprobaciones iniciales son satisfactorias, proceder con la lógica RenderComplete ---
    render_complete_active = check_render_complete_module()
    original_wav_path = None

    # Si RenderComplete esta activo, cambiar temporalmente el wav
    if render_complete_active:
        original_wav_path = set_silence_wav_temporarily()

    try:
        temp_dir = tempfile.gettempdir()
        output_path = os.path.join(temp_dir, "LGA_snapshot.jpg")

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
            # Hacer una copia adicional en la ubicacion especificada
            save_path = r"T:\Borrame\snapshot.jpg"
            output_dir = os.path.dirname(save_path)
            try:
                os.makedirs(output_dir, exist_ok=True)
                # Copiar el archivo temporal a la ubicacion final
                import shutil

                shutil.copy2(output_path, save_path)
                debug_print(f"Copia adicional guardada en: {save_path}")
            except Exception as e:
                debug_print(f"ERROR: No se pudo crear copia adicional: {e}")
                # No hacer return aqui, continuar con el proceso normal

        # Copiar al portapapeles
        app = QApplication.instance()
        if not app:
            app = QApplication([])

        clipboard = app.clipboard()
        clipboard.setImage(qimage)

        debug_print("✅ Imagen copiada al portapapeles.")

        # NO eliminar el archivo temporal - lo necesitamos para show_snapshot()
        debug_print(f"Archivo temporal mantenido para show_snapshot: {output_path}")

    finally:
        # Restaurar el wav original si se cambio temporalmente
        if render_complete_active and original_wav_path:
            restore_original_wav(original_wav_path)


def test_hold(start):
    """
    Crea un nodo NoOp mientras el botón está presionado y lo borra al soltar.

    Args:
        start (bool): True para crear el nodo, False para eliminarlo
    """
    node_name = "LGA_HOLD_TEST"

    if start:
        # Crear nodo solo si no existe
        if not nuke.exists(node_name):
            try:
                # Crear el nodo NoOp
                noop_node = nuke.createNode(
                    "NoOp", f"name {node_name} label 'HOLD TEST'", inpanel=False
                )

                # Posicionarlo en una ubicacion visible
                noop_node.setXpos(0)
                noop_node.setYpos(0)

                # Darle un color distintivo
                noop_node["tile_color"].setValue(0xFF0000FF)  # Azul

                debug_print("✅ Nodo NoOp creado para test hold")
                print("🔽 HOLD TEST: Nodo NoOp creado")

            except Exception as e:
                debug_print(f"Error al crear nodo NoOp: {e}")
                print(f"❌ Error al crear nodo: {e}")
        else:
            debug_print("Nodo NoOp ya existe")
            print("⚠️ Nodo NoOp ya existe")
    else:
        # Eliminar nodo si existe
        if nuke.exists(node_name):
            try:
                node_to_delete = nuke.toNode(node_name)
                nuke.delete(node_to_delete)
                debug_print("🗑️ Nodo NoOp eliminado")
                print("🔼 HOLD TEST: Nodo NoOp eliminado")

            except Exception as e:
                debug_print(f"Error al eliminar nodo NoOp: {e}")
                print(f"❌ Error al eliminar nodo: {e}")
        else:
            debug_print("No hay nodo NoOp para eliminar")
            print("⚠️ No hay nodo NoOp para eliminar")
