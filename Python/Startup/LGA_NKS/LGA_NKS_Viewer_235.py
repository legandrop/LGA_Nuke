"""
__________________________________________________________

  LGA_NKS_Viewer_235 v1.2 - 2024 - Lega
  Ajusta el overlay del viewer a 2.35:1 y 
  alterna los estilos de máscara entre None, Half y Full
  a la vez que sube en Y al texto Frame del track BurnIn
__________________________________________________________


"""

import hiero.core
import hiero.ui
import nuke
import os


# Variable global para activar o desactivar los prints
DEBUG = False

def debug_print(*message):
    if DEBUG:
        print(*message)


# ============================
# Configuración de Variables
# ============================

# Configuración para la rotación de estilos de máscara
ASPECT_RATIO = "2.35:1"  # Aspecto a aplicar al viewer

# Definición de estilos de máscara en orden de rotación
MASK_STYLE_ORDER = [
    hiero.ui.Player.MaskOverlayStyle.eMaskOverlayNone,
    hiero.ui.Player.MaskOverlayStyle.eMaskOverlayHalf,
    hiero.ui.Player.MaskOverlayStyle.eMaskOverlayFull
]

# Nombre del track a inspeccionar
TRACK_NAME = "BurnIn"

# Palabra clave para buscar el efecto
EFFECT_NAME_SEARCH = "Frame"

# Propiedad principal para toggle
MAIN_TOGGLE_PROPERTY = "opacity"

# Valores para toggle de la propiedad principal
TOGGLE_INITIAL_VALUE = 1.0    # Valor inicial (e.g., 1.0)
TOGGLE_SECONDARY_VALUE = 0.9  # Valor secundario (e.g., 0.9)

# Propiedad de 'box' y ajustes relacionados
BOX_PROPERTY = "box"
BOX_INDEX_TO_MODIFY = 3          # Índice del cuarto valor en la tupla (0-based)
BOX_ADJUSTMENT_INITIAL = 350     # Incremento cuando se cambia a TOGGLE_SECONDARY_VALUE
BOX_ADJUSTMENT_SECONDARY = -350  # Decremento cuando se cambia a TOGGLE_INITIAL_VALUE

# ============================
# Funciones Principales
# ============================

def rotate_overlay_style(viewer):
    """
    Rota el estilo de máscara del viewer al siguiente en el orden definido.
    """
    current_style = viewer.maskOverlayStyle()
    try:
        current_index = MASK_STYLE_ORDER.index(current_style)
        next_index = (current_index + 1) % len(MASK_STYLE_ORDER)
        new_style = MASK_STYLE_ORDER[next_index]
    except ValueError:
        # Si el estilo actual no está en la lista, comenzar desde el principio
        new_style = MASK_STYLE_ORDER[0]
    
    return new_style

def print_effects_in_tracks(track_name):
    """
    Imprime todos los efectos en el track especificado.
    """
    # Obtener la secuencia activa
    seq = hiero.ui.activeSequence()

    if not seq:
        debug_print("No se encontró una secuencia activa.")
        return

    # Iterar sobre las pistas de video en la secuencia
    for track in seq.videoTracks():
        if track.name() == track_name:
            debug_print(f"\nTrack '{track.name()}':")
            items = track.subTrackItems()
            if not items:
                debug_print(f"  El track '{track.name()}' no tiene items.")
                continue
            for idx, item in enumerate(items):
                # Asumimos que cada item es una lista o tupla y tomamos el primer elemento
                effect_item = item[0]
                if isinstance(effect_item, hiero.core.EffectTrackItem):
                    effect_name = effect_item.name() if hasattr(effect_item, 'name') else "Efecto sin nombre"
                    debug_print(f"  Efecto {idx+1}: {effect_name}")
                else:
                    debug_print(f"  Clip {idx+1}: No es un efecto.")

def toggle_opacity_and_adjust_box(effect_item, new_mask_style):
    """
    Realiza un toggle en la propiedad principal del efecto y ajusta la propiedad 'box'
    según el nuevo estilo de máscara.
    """
    if not isinstance(effect_item, hiero.core.EffectTrackItem):
        debug_print("El item proporcionado no es un efecto.")
        return

    # Obtener el nodo asociado al efecto
    node = effect_item.node()
    if not node:
        debug_print("No se encontró un nodo asociado al efecto.")
        return

    # Verificar si el nodo tiene la propiedad principal para toggle
    if MAIN_TOGGLE_PROPERTY not in node.knobs():
        debug_print(f"El nodo del efecto no tiene una propiedad '{MAIN_TOGGLE_PROPERTY}'.")
        return

    # Obtener el valor actual de la propiedad principal
    try:
        current_toggle_value = node[MAIN_TOGGLE_PROPERTY].value()
        debug_print(f"\nValor actual de '{MAIN_TOGGLE_PROPERTY}': {current_toggle_value} (Tipo: {type(current_toggle_value).__name__})")
    except Exception as e:
        debug_print(f"No se pudo obtener el valor de '{MAIN_TOGGLE_PROPERTY}': {e}")
        return

    # Determinar el nuevo valor de la propiedad principal y el ajuste de 'box' según el nuevo estilo de máscara
    if new_mask_style == hiero.ui.Player.MaskOverlayStyle.eMaskOverlayNone or new_mask_style == hiero.ui.Player.MaskOverlayStyle.eMaskOverlayHalf:

        desired_opacity = TOGGLE_INITIAL_VALUE  # 1.0
        if current_toggle_value != desired_opacity:
            new_toggle_value = desired_opacity
            box_adjustment = BOX_ADJUSTMENT_SECONDARY if current_toggle_value == TOGGLE_SECONDARY_VALUE else 0
            toggle_action = f"cambiar '{MAIN_TOGGLE_PROPERTY}' a {new_toggle_value}"
        else:
            debug_print(f"'{MAIN_TOGGLE_PROPERTY}' ya está en {desired_opacity}. No se realizará ningún cambio.")
            return
    elif new_mask_style == hiero.ui.Player.MaskOverlayStyle.eMaskOverlayFull:
        desired_opacity = TOGGLE_SECONDARY_VALUE  # 0.9
        if current_toggle_value == TOGGLE_INITIAL_VALUE:
            new_toggle_value = desired_opacity
            box_adjustment = BOX_ADJUSTMENT_INITIAL
            toggle_action = f"cambiar '{MAIN_TOGGLE_PROPERTY}' a {new_toggle_value} y sumar {BOX_ADJUSTMENT_INITIAL} al cuarto valor de '{BOX_PROPERTY}'"
        elif current_toggle_value == TOGGLE_SECONDARY_VALUE:
            debug_print(f"'{MAIN_TOGGLE_PROPERTY}' ya está en {desired_opacity}. No se realizará ningún cambio.")
            return
        else:
            # Si el valor actual no es ninguno de los esperados, establecer a valor secundario y ajustar
            new_toggle_value = desired_opacity
            box_adjustment = BOX_ADJUSTMENT_INITIAL
            toggle_action = f"cambiar '{MAIN_TOGGLE_PROPERTY}' a {new_toggle_value} y sumar {BOX_ADJUSTMENT_INITIAL} al cuarto valor de '{BOX_PROPERTY}'"
    else:
        debug_print("Estilo de máscara no reconocido. No se realizará ningún cambio.")
        return

    # Aplicar el nuevo valor de la propiedad principal
    try:
        node[MAIN_TOGGLE_PROPERTY].setValue(new_toggle_value)
        debug_print(f"'{MAIN_TOGGLE_PROPERTY}' ha sido {toggle_action}. Nuevo valor: {new_toggle_value}")
    except Exception as e:
        debug_print(f"No se pudo establecer el nuevo valor de '{MAIN_TOGGLE_PROPERTY}': {e}")
        return

    # Verificar si se necesita ajustar 'box'
    if box_adjustment != 0:
        # Verificar si el nodo tiene la propiedad 'box'
        if BOX_PROPERTY not in node.knobs():
            debug_print(f"El nodo del efecto no tiene una propiedad '{BOX_PROPERTY}'. No se puede ajustar.")
            return

        # Obtener el valor actual de 'box'
        try:
            current_box = node[BOX_PROPERTY].value()
            if not isinstance(current_box, (tuple, list)) or len(current_box) <= BOX_INDEX_TO_MODIFY:
                debug_print(f"La propiedad '{BOX_PROPERTY}' no tiene el formato esperado (debe ser una tupla o lista con al menos {BOX_INDEX_TO_MODIFY + 1} elementos).")
                return
            debug_print(f"Valor actual de '{BOX_PROPERTY}': {current_box} (Tipo: {type(current_box).__name__})")
        except Exception as e:
            debug_print(f"No se pudo obtener el valor de '{BOX_PROPERTY}': {e}")
            return

        # Ajustar el cuarto valor de 'box'
        try:
            # Convertir a lista para modificar
            new_box = list(current_box)
            new_box[BOX_INDEX_TO_MODIFY] += box_adjustment
            # Convertir de nuevo a tupla
            new_box = tuple(new_box)
            node[BOX_PROPERTY].setValue(new_box)
            debug_print(f"'{BOX_PROPERTY}' ha sido ajustado. Nuevo valor: {new_box}")
        except Exception as e:
            debug_print(f"No se pudo ajustar el valor de '{BOX_PROPERTY}': {e}")

def main():
    """
    Función principal que coordina la rotación de estilos de máscara y la modificación del efecto específico.
    """
    # Rotar el estilo de máscara del viewer
    viewer = hiero.ui.currentViewer()

    # Verificar si se encontró el viewer
    if viewer is not None:
        try:
            # Obtener el estilo actual y determinar el nuevo estilo
            current_style = viewer.maskOverlayStyle()
            new_style = rotate_overlay_style(viewer)
            viewer.setMaskOverlayStyle(new_style)
            debug_print(f"\nEstilo de máscara cambiado de {current_style} a {new_style}")

            # Aplicar siempre el aspecto 2.35:1
            viewer.setMaskOverlayFromRemote(ASPECT_RATIO)
            debug_print(f"Aspecto {ASPECT_RATIO} aplicado al viewer")

            # Determinar el nombre del nuevo estilo para lógica posterior
            if new_style == hiero.ui.Player.MaskOverlayStyle.eMaskOverlayNone:
                new_mask_style = "None"
            elif new_style == hiero.ui.Player.MaskOverlayStyle.eMaskOverlayHalf:
                new_mask_style = "Half"
            elif new_style == hiero.ui.Player.MaskOverlayStyle.eMaskOverlayFull:
                new_mask_style = "Full"
            else:
                new_mask_style = "Unknown"

            debug_print(f"Nuevo estilo de máscara: {new_mask_style}")

        except AttributeError as e:
            debug_print(f"Error al manipular el viewer: {e}")
    else:
        debug_print("No se pudo obtener el viewer actual.")

    # Imprimir todos los efectos en el track especificado
    print_effects_in_tracks(TRACK_NAME)

    # Obtener la secuencia activa nuevamente
    seq = hiero.ui.activeSequence()
    if not seq:
        return

    # Buscar el track especificado
    target_track = None
    for track in seq.videoTracks():
        if track.name() == TRACK_NAME:
            target_track = track
            break

    if not target_track:
        debug_print(f"No se encontró el track '{TRACK_NAME}'.")
        return

    # Iterar sobre los items del track para encontrar el efecto que contiene la palabra clave
    items = target_track.subTrackItems()
    if not items:
        debug_print(f"El track '{target_track.name()}' no tiene items.")
        return

    target_effect = None
    for item in items:
        effect_item = item[0]
        if isinstance(effect_item, hiero.core.EffectTrackItem):
            if EFFECT_NAME_SEARCH in effect_item.name():
                target_effect = effect_item
                break

    if target_effect:
        debug_print(f"\nEfecto que contiene '{EFFECT_NAME_SEARCH}' encontrado:")
        debug_print(f"Nombre del efecto: {target_effect.name()}")
        toggle_opacity_and_adjust_box(target_effect, new_style)
    else:
        debug_print(f"No se encontró ningún efecto que contenga la palabra '{EFFECT_NAME_SEARCH}' en el nombre.")

# Ejecutar el script principal
if __name__ == "__main__":
    main()
