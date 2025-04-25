"""
____________________________________________________________________________________

  LGA_Write_Focus v1.4 | Lega
  Script para buscar, enfocar, centrar y hacer zoom a un nodo con nombre definido
  en el archivo de configuracion. Por defecto es Write_Pub.
____________________________________________________________________________________
"""

import nuke
import time
import os
import configparser

# Variable global para activar o desactivar los prints de depuracion
DEBUG = False  # Cambiar a True para ver los mensajes detallados


# Funcion para imprimir mensajes de depuracion
def debug_print(*message):
    if DEBUG:
        print(*message)


# Constante para el nombre del archivo de configuracion
CONFIG_FILE_NAME = "Write_Focus.ini"
# Constante para el nombre de la seccion en el archivo .ini
CONFIG_SECTION = "Settings"
# Constante para la clave del nombre del nodo en el archivo .ini
CONFIG_NODE_NAME_KEY = "node_name"
# Valor por defecto para el nombre del nodo
DEFAULT_NODE_NAME = "Write_Pub"


def get_config_path():
    """Devuelve la ruta completa al archivo de configuracion."""
    try:
        appdata_path = os.getenv("APPDATA")
        if not appdata_path:

            debug_print("Error: No se pudo encontrar la variable de entorno APPDATA.")
            return None
        config_dir = os.path.join(appdata_path, "LGA", "ToolPack")
        return os.path.join(config_dir, CONFIG_FILE_NAME)
    except Exception as e:

        debug_print(f"Error al obtener la ruta de configuracion: {e}")
        return None


def ensure_config_exists():
    """
    Asegura que el directorio de configuracion y el archivo .ini existan.
    Si no existen, los crea con el valor predeterminado.
    """
    config_file_path = get_config_path()
    if not config_file_path:
        return  # Salir si no se pudo obtener la ruta

    config_dir = os.path.dirname(config_file_path)

    try:
        # Crear el directorio si no existe
        if not os.path.exists(config_dir):
            os.makedirs(config_dir)

            debug_print(f"Directorio creado: {config_dir}")

        # Crear el archivo .ini si no existe
        if not os.path.exists(config_file_path):
            config = configparser.ConfigParser()
            config[CONFIG_SECTION] = {CONFIG_NODE_NAME_KEY: DEFAULT_NODE_NAME}
            with open(config_file_path, "w") as configfile:
                config.write(configfile)

            debug_print(
                f"Archivo de configuración creado: {config_file_path} con valor predeterminado '{DEFAULT_NODE_NAME}'"
            )
        # Opcional: Imprimir si ya existia para depuracion
        # else:
        #     debug_print(f"Archivo de configuración ya existe: {config_file_path}")

    except Exception as e:

        debug_print(f"Error al asegurar la configuración: {e}")


def get_node_name_from_config():
    """
    Lee el nombre del nodo desde el archivo de configuracion .ini.
    Devuelve el valor leido o el valor por defecto si hay errores.
    """
    config_file_path = get_config_path()
    if not config_file_path or not os.path.exists(config_file_path):

        debug_print("Archivo de configuración no encontrado, usando valor por defecto.")
        return DEFAULT_NODE_NAME

    try:
        config = configparser.ConfigParser()
        config.read(config_file_path)

        # Verificar si la seccion y la clave existen
        if config.has_section(CONFIG_SECTION) and config.has_option(
            CONFIG_SECTION, CONFIG_NODE_NAME_KEY
        ):
            node_name = config.get(CONFIG_SECTION, CONFIG_NODE_NAME_KEY)
            # Devolver el valor leido, quitando posibles espacios extra
            return node_name.strip() if node_name else DEFAULT_NODE_NAME
        else:

            debug_print(
                f"Sección [{CONFIG_SECTION}] o clave '{CONFIG_NODE_NAME_KEY}' no encontrada en {config_file_path}. Usando valor por defecto."
            )
            # Si falta la seccion o clave, podemos intentar recrear el archivo con el valor por defecto
            # O simplemente usar el valor por defecto. Optamos por lo segundo por simplicidad.
            return DEFAULT_NODE_NAME

    except configparser.Error as e:

        debug_print(
            f"Error al leer el archivo de configuración {config_file_path}: {e}. Usando valor por defecto."
        )
        return DEFAULT_NODE_NAME
    except Exception as e:

        debug_print(
            f"Error inesperado al leer la configuración: {e}. Usando valor por defecto."
        )
        return DEFAULT_NODE_NAME


# Asegurarse de que el archivo de configuracion existe al iniciar
ensure_config_exists()


def main():
    """
    Busca un nodo Write con el nombre especificado en la configuracion,
    lo centra en el DAG, aplica un zoom fijo y abre su panel de propiedades.
    Si no encuentra el nodo, muestra un mensaje de error.
    Incluye medicion de tiempo para cada proceso.
    """
    # Log inicial y medicion de tiempo total
    tiempo_inicio_total = time.time()

    debug_print("Inicio script - Tiempo: 0.00 ms")

    # Valor de zoom fijo que queremos aplicar
    ZOOM_LEVEL = 1.5

    # --- Leer nombre del nodo desde config ---
    tiempo_inicio_config = time.time()
    node_to_find = get_node_name_from_config()
    tiempo_fin_config = time.time()

    debug_print(
        f"Configuración leída ('{node_to_find}') - Tiempo: {(tiempo_fin_config - tiempo_inicio_total) * 1000:.2f} ms"
    )

    # --- Buscar nodo directamente por nombre ---
    tiempo_inicio_busqueda = time.time()
    write_pub = nuke.toNode(node_to_find)
    tiempo_fin_busqueda = time.time()
    # Log despues de intentar encontrar el nodo

    debug_print(
        f"Búsqueda de nodo finalizada - Tiempo: {(tiempo_fin_busqueda - tiempo_inicio_total) * 1000:.2f} ms"
    )
    # Imprimir tiempo especifico de la busqueda

    debug_print(
        f"  Tiempo específico de búsqueda (nuke.toNode): {(tiempo_fin_busqueda - tiempo_inicio_busqueda) * 1000:.2f} ms"
    )

    # Si encontramos el nodo, lo seleccionamos, centramos y mostramos sus propiedades
    if write_pub:
        # Verificamos que sea del tipo correcto
        if write_pub.Class() != "Write":
            nuke.message(
                f"Se encontró un nodo llamado '{node_to_find}' pero no es del tipo Write."
            )
            tiempo_fin_total = (
                time.time()
            )  # Registrar tiempo final incluso si hay error de tipo

            debug_print(
                f"Error: Tipo de nodo incorrecto. Tiempo total: {(tiempo_fin_total - tiempo_inicio_total) * 1000:.2f} ms"
            )
            return

        # Deseleccionamos todos los nodos
        tiempo_inicio_deseleccion = time.time()
        for n in nuke.selectedNodes():
            n["selected"].setValue(False)
        tiempo_fin_deseleccion = time.time()

        debug_print(
            f"  Tiempo de deselección: {(tiempo_fin_deseleccion - tiempo_inicio_deseleccion) * 1000:.2f} ms"
        )

        # Seleccionamos el nodo Write_Pub
        tiempo_inicio_seleccion = time.time()
        write_pub["selected"].setValue(True)
        tiempo_fin_seleccion = time.time()

        debug_print(
            f"  Tiempo de selección: {(tiempo_fin_seleccion - tiempo_inicio_seleccion) * 1000:.2f} ms"
        )

        # Calculamos el centro del nodo Write_Pub
        tiempo_inicio_calculo = time.time()
        xCenter = write_pub.xpos() + write_pub.screenWidth() / 2
        yCenter = write_pub.ypos() + write_pub.screenHeight() / 2
        tiempo_fin_calculo = time.time()

        debug_print(
            f"  Tiempo de cálculo de centro: {(tiempo_fin_calculo - tiempo_inicio_calculo) * 1000:.2f} ms"
        )

        # Centramos y aplicamos zoom fijo
        tiempo_inicio_zoom = time.time()
        nuke.zoom(ZOOM_LEVEL, [xCenter, yCenter])
        tiempo_fin_zoom = time.time()

        debug_print(
            f"  Tiempo de zoom: {(tiempo_fin_zoom - tiempo_inicio_zoom) * 1000:.2f} ms"
        )

        # Mostramos el panel de propiedades
        tiempo_inicio_panel = time.time()
        write_pub.showControlPanel()
        tiempo_fin_panel = time.time()

        debug_print(
            f"  Tiempo de mostrar panel: {(tiempo_fin_panel - tiempo_inicio_panel) * 1000:.2f} ms"
        )

        tiempo_fin_total = time.time()

        debug_print(
            f"Nodo '{node_to_find}' encontrado y enfocado. Tiempo total: {(tiempo_fin_total - tiempo_inicio_total) * 1000:.2f} ms"
        )
    else:
        # --- Inicio ELIMINACION: Se elimina el bloque de busqueda alternativa ---
        # Ya no hay busqueda alternativa, solo mensaje de error directo
        tiempo_fin_total = (
            time.time()
        )  # Registrar tiempo final en caso de no encontrarlo

        debug_print(
            f"Error: Nodo no encontrado. Tiempo total: {(tiempo_fin_total - tiempo_inicio_total) * 1000:.2f} ms"
        )
        nuke.message(
            f"No se encontró ningún nodo llamado '{node_to_find}' en el script actual."
        )
        # --- Fin ELIMINACION ---


# Ejecutar la funcion cuando se importe este script
# main()
