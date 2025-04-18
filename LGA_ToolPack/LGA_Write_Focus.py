"""
____________________________________________________________________________________

  LGA_Write_Focus v1.3 | 2025 | Lega
  Script para buscar, enfocar, centrar y hacer zoom a un nodo con nombre definido
  en el archivo de configuracion. Por defecto es Write_Pub.
____________________________________________________________________________________
"""

import nuke
import time
import os
import configparser

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
            print("Error: No se pudo encontrar la variable de entorno APPDATA.")
            return None
        config_dir = os.path.join(appdata_path, "LGA", "ToolPack")
        return os.path.join(config_dir, CONFIG_FILE_NAME)
    except Exception as e:
        print(f"Error al obtener la ruta de configuracion: {e}")
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
            print(f"Directorio creado: {config_dir}")

        # Crear el archivo .ini si no existe
        if not os.path.exists(config_file_path):
            config = configparser.ConfigParser()
            config[CONFIG_SECTION] = {CONFIG_NODE_NAME_KEY: DEFAULT_NODE_NAME}
            with open(config_file_path, "w") as configfile:
                config.write(configfile)
            print(
                f"Archivo de configuración creado: {config_file_path} con valor predeterminado '{DEFAULT_NODE_NAME}'"
            )
        # Opcional: Imprimir si ya existia para depuracion
        # else:
        #     print(f"Archivo de configuración ya existe: {config_file_path}")

    except Exception as e:
        print(f"Error al asegurar la configuración: {e}")


def get_node_name_from_config():
    """
    Lee el nombre del nodo desde el archivo de configuracion .ini.
    Devuelve el valor leido o el valor por defecto si hay errores.
    """
    config_file_path = get_config_path()
    if not config_file_path or not os.path.exists(config_file_path):
        print("Archivo de configuración no encontrado, usando valor por defecto.")
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
            print(
                f"Sección [{CONFIG_SECTION}] o clave '{CONFIG_NODE_NAME_KEY}' no encontrada en {config_file_path}. Usando valor por defecto."
            )
            # Si falta la seccion o clave, podemos intentar recrear el archivo con el valor por defecto
            # O simplemente usar el valor por defecto. Optamos por lo segundo por simplicidad.
            return DEFAULT_NODE_NAME

    except configparser.Error as e:
        print(
            f"Error al leer el archivo de configuración {config_file_path}: {e}. Usando valor por defecto."
        )
        return DEFAULT_NODE_NAME
    except Exception as e:
        print(
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
    Incluye medición de tiempo para cada proceso.
    """
    tiempo_inicio_total = time.time()

    # Valor de zoom fijo que queremos aplicar
    ZOOM_LEVEL = 1.5

    # --- Inicio Modificacion: Leer nombre del nodo desde config ---
    node_to_find = get_node_name_from_config()
    print(f"Buscando nodo: '{node_to_find}'")  # Imprimir el nodo que se buscara
    # --- Fin Modificacion ---

    # Método optimizado: buscar directamente por nombre
    tiempo_inicio_busqueda = time.time()
    write_pub = nuke.toNode(node_to_find)
    tiempo_fin_busqueda = time.time()
    print(
        f"Tiempo de búsqueda: {(tiempo_fin_busqueda - tiempo_inicio_busqueda) * 1000:.2f} ms"
    )

    # Si encontramos el nodo, lo seleccionamos, centramos y mostramos sus propiedades
    if write_pub:
        # Verificamos que sea del tipo correcto
        if write_pub.Class() != "Write":
            # --- Inicio Modificacion: Mensaje con nombre dinamico ---
            nuke.message(
                f"Se encontró un nodo llamado '{node_to_find}' pero no es del tipo Write."
            )
            # --- Fin Modificacion ---
            return

        # Deseleccionamos todos los nodos
        tiempo_inicio_deseleccion = time.time()
        for n in nuke.selectedNodes():
            n["selected"].setValue(False)
        tiempo_fin_deseleccion = time.time()
        print(
            f"Tiempo de deselección: {(tiempo_fin_deseleccion - tiempo_inicio_deseleccion) * 1000:.2f} ms"
        )

        # Seleccionamos el nodo Write_Pub
        tiempo_inicio_seleccion = time.time()
        write_pub["selected"].setValue(True)
        tiempo_fin_seleccion = time.time()
        print(
            f"Tiempo de selección: {(tiempo_fin_seleccion - tiempo_inicio_seleccion) * 1000:.2f} ms"
        )

        # Calculamos el centro del nodo Write_Pub
        tiempo_inicio_calculo = time.time()
        xCenter = write_pub.xpos() + write_pub.screenWidth() / 2
        yCenter = write_pub.ypos() + write_pub.screenHeight() / 2
        tiempo_fin_calculo = time.time()
        print(
            f"Tiempo de cálculo de centro: {(tiempo_fin_calculo - tiempo_inicio_calculo) * 1000:.2f} ms"
        )

        # Centramos y aplicamos zoom fijo
        tiempo_inicio_zoom = time.time()
        nuke.zoom(ZOOM_LEVEL, [xCenter, yCenter])
        tiempo_fin_zoom = time.time()
        print(f"Tiempo de zoom: {(tiempo_fin_zoom - tiempo_inicio_zoom) * 1000:.2f} ms")

        # Mostramos el panel de propiedades
        tiempo_inicio_panel = time.time()
        write_pub.showControlPanel()
        tiempo_fin_panel = time.time()
        print(
            f"Tiempo de mostrar panel: {(tiempo_fin_panel - tiempo_inicio_panel) * 1000:.2f} ms"
        )

        tiempo_fin_total = time.time()
        print(
            f"Tiempo total de ejecución: {(tiempo_fin_total - tiempo_inicio_total) * 1000:.2f} ms"
        )
        # --- Inicio Modificacion: Mensaje con nombre dinamico ---
        print(
            f"Nodo '{node_to_find}' encontrado, centrado y enfocado en el panel de propiedades."
        )
        # --- Fin Modificacion ---
    else:
        # Como alternativa, podemos buscar en nodos Write si no se encuentra directamente
        # pero solo si hay pocos nodos Write para no penalizar el rendimiento
        nodos_write = nuke.allNodes("Write")
        if len(nodos_write) < 10:  # Solo buscar si hay pocos nodos Write
            for node in nodos_write:
                # --- Inicio Modificacion: Comparar con node_to_find ---
                if node.name() == node_to_find:
                    # --- Fin Modificacion ---
                    main()  # Volver a ejecutar la función ahora que se ha creado el nodo
                    return

        tiempo_fin_total = time.time()
        print(
            f"Tiempo total de ejecución (error): {(tiempo_fin_total - tiempo_inicio_total) * 1000:.2f} ms"
        )
        # --- Inicio Modificacion: Mensaje con nombre dinamico ---
        nuke.message(
            f"No se encontró ningún nodo Write llamado '{node_to_find}' en el script actual."
        )
        # --- Fin Modificacion ---


# Ejecutar la función cuando se importe este script
# main()
