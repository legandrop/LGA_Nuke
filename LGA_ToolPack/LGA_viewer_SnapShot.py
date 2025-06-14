"""
______________________________________________________

  LGA_NKS_SnapShot v0.51 - Lega
  Crea un snapshot de la imagen actual del viewer y lo copia al portapapeles
______________________________________________________

"""

import nuke
import nukescripts
import os
import tempfile
from PySide2 import QtWidgets, QtGui

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
    # Verificar si RenderComplete esta disponible y activado
    render_complete_active = check_render_complete_module()
    original_wav_path = None

    # Si RenderComplete esta activo, cambiar temporalmente el wav
    if render_complete_active:
        original_wav_path = set_silence_wav_temporarily()

    try:
        temp_dir = tempfile.gettempdir()
        output_path = os.path.join(temp_dir, "snapshot.jpg")

        viewer = nuke.activeViewer()
        if viewer is None:
            nuke.message("No hay viewer activo.")
            return

        view_node = viewer.node()
        input_index = viewer.activeInput()
        input_node = view_node.input(input_index)

        if input_node is None:
            nuke.message("No hay nodo conectado al viewer.")
            return

        frame = int(nuke.frame())

        # Crear el Write temporal limpio
        write_node = nuke.createNode(
            "Write",
            "file_type jpeg postage_stamp false hide_input true label 'LGA_TEMP'",
            inpanel=False,
        )
        write_node.setInput(0, input_node)

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

        if not os.path.exists(output_path):
            nuke.message("Error: el archivo no se generó.")
            return

        # Cargar el JPEG como QImage
        qimage = QtGui.QImage(output_path)
        if qimage.isNull():
            nuke.message("Error al leer el snapshot generado.")
            return

        debug_print("Snapshot size:", qimage.width(), "×", qimage.height())

        if SaveToFile:
            save_path = r"T:\Borrame\snapshot.jpg"
            output_dir = os.path.dirname(save_path)
            os.makedirs(output_dir, exist_ok=True)
            ok = qimage.save(save_path, "JPEG")
            debug_print("Archivo final guardado:", ok, save_path)

        # Copiar al portapapeles
        app = QtWidgets.QApplication.instance()
        if not app:
            app = QtWidgets.QApplication([])

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
