import hiero.core
import hiero.ui
import nuke
import os

# ============================
# Configuracion de Variables
# ============================

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
BOX_INDEX_TO_MODIFY = 3          # Indice del cuarto valor en la tupla (0-based)
BOX_ADJUSTMENT_INITIAL = 350     # Incremento cuando se cambia a TOGGLE_SECONDARY_VALUE
BOX_ADJUSTMENT_SECONDARY = -350  # Decremento cuando se cambia a TOGGLE_INITIAL_VALUE

# ============================
# Funciones Principales
# ============================

def print_effects_in_tracks(track_name):
    """
    Imprime todos los efectos en el track especificado.
    """
    # Obtener la secuencia activa
    seq = hiero.ui.activeSequence()

    if not seq:
        print("No se encontro una secuencia activa.")
        return

    # Iterar sobre las pistas de video en la secuencia
    for track in seq.videoTracks():
        if track.name() == track_name:
            print(f"\nTrack '{track.name()}':")
            items = track.subTrackItems()
            if not items:
                print(f"  El track '{track.name()}' no tiene items.")
                continue
            for idx, item in enumerate(items):
                # Asumimos que cada item es una lista o tupla y tomamos el primer elemento
                effect_item = item[0]
                if isinstance(effect_item, hiero.core.EffectTrackItem):
                    effect_name = effect_item.name() if hasattr(effect_item, 'name') else "Efecto sin nombre"
                    print(f"  Efecto {idx+1}: {effect_name}")
                else:
                    print(f"  Clip {idx+1}: No es un efecto.")

def toggle_opacity_and_adjust_box(effect_item):
    """
    Realiza un toggle en la propiedad principal del efecto y ajusta la propiedad 'box'.
    """
    if not isinstance(effect_item, hiero.core.EffectTrackItem):
        print("El item proporcionado no es un efecto.")
        return

    # Obtener el nodo asociado al efecto
    node = effect_item.node()
    if not node:
        print("No se encontro un nodo asociado al efecto.")
        return

    # Verificar si el nodo tiene la propiedad principal para toggle
    if MAIN_TOGGLE_PROPERTY not in node.knobs():
        print(f"El nodo del efecto no tiene una propiedad '{MAIN_TOGGLE_PROPERTY}'.")
        return

    # Obtener el valor actual de la propiedad principal
    try:
        current_toggle_value = node[MAIN_TOGGLE_PROPERTY].value()
        print(f"\nValor actual de '{MAIN_TOGGLE_PROPERTY}': {current_toggle_value} (Tipo: {type(current_toggle_value).__name__})")
    except Exception as e:
        print(f"No se pudo obtener el valor de '{MAIN_TOGGLE_PROPERTY}': {e}")
        return

    # Determinar el nuevo valor de la propiedad principal y el ajuste de 'box'
    if current_toggle_value == TOGGLE_INITIAL_VALUE:
        new_toggle_value = TOGGLE_SECONDARY_VALUE
        box_adjustment = BOX_ADJUSTMENT_INITIAL
        toggle_action = f"cambiar '{MAIN_TOGGLE_PROPERTY}' a {new_toggle_value} y sumar {BOX_ADJUSTMENT_INITIAL} al cuarto valor de '{BOX_PROPERTY}'"
    elif current_toggle_value == TOGGLE_SECONDARY_VALUE:
        new_toggle_value = TOGGLE_INITIAL_VALUE
        box_adjustment = BOX_ADJUSTMENT_SECONDARY
        toggle_action = f"cambiar '{MAIN_TOGGLE_PROPERTY}' a {new_toggle_value} y restar {abs(BOX_ADJUSTMENT_SECONDARY)} al cuarto valor de '{BOX_PROPERTY}'"
    else:
        # Si el valor actual no es ninguno de los esperados, establecer a valor inicial y ajustar
        new_toggle_value = TOGGLE_INITIAL_VALUE
        box_adjustment = BOX_ADJUSTMENT_SECONDARY
        toggle_action = f"cambiar '{MAIN_TOGGLE_PROPERTY}' a {new_toggle_value} y restar {abs(BOX_ADJUSTMENT_SECONDARY)} al cuarto valor de '{BOX_PROPERTY}'"

    # Aplicar el nuevo valor de la propiedad principal
    try:
        node[MAIN_TOGGLE_PROPERTY].setValue(new_toggle_value)
        print(f"'{MAIN_TOGGLE_PROPERTY}' ha sido {toggle_action}. Nuevo valor: {new_toggle_value}")
    except Exception as e:
        print(f"No se pudo establecer el nuevo valor de '{MAIN_TOGGLE_PROPERTY}': {e}")
        return

    # Verificar si el nodo tiene la propiedad 'box'
    if BOX_PROPERTY not in node.knobs():
        print(f"El nodo del efecto no tiene una propiedad '{BOX_PROPERTY}'. No se puede ajustar.")
        return

    # Obtener el valor actual de 'box'
    try:
        current_box = node[BOX_PROPERTY].value()
        if not isinstance(current_box, (tuple, list)) or len(current_box) <= BOX_INDEX_TO_MODIFY:
            print(f"La propiedad '{BOX_PROPERTY}' no tiene el formato esperado (debe ser una tupla o lista con al menos {BOX_INDEX_TO_MODIFY + 1} elementos).")
            return
        print(f"Valor actual de '{BOX_PROPERTY}': {current_box} (Tipo: {type(current_box).__name__})")
    except Exception as e:
        print(f"No se pudo obtener el valor de '{BOX_PROPERTY}': {e}")
        return

    # Ajustar el cuarto valor de 'box'
    try:
        # Convertir a lista para modificar
        new_box = list(current_box)
        new_box[BOX_INDEX_TO_MODIFY] += box_adjustment
        # Convertir de nuevo a tupla
        new_box = tuple(new_box)
        node[BOX_PROPERTY].setValue(new_box)
        print(f"'{BOX_PROPERTY}' ha sido ajustado. Nuevo valor: {new_box}")
    except Exception as e:
        print(f"No se pudo ajustar el valor de '{BOX_PROPERTY}': {e}")

def main():
    """
    Funcion principal que coordina la impresion de efectos y la modificacion del efecto especifico.
    """
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
        print(f"No se encontro el track '{TRACK_NAME}'.")
        return

    # Iterar sobre los items del track para encontrar el efecto que contiene la palabra clave
    items = target_track.subTrackItems()
    if not items:
        print(f"El track '{target_track.name()}' no tiene items.")
        return

    target_effect = None
    for item in items:
        effect_item = item[0]
        if isinstance(effect_item, hiero.core.EffectTrackItem):
            if EFFECT_NAME_SEARCH in effect_item.name():
                target_effect = effect_item
                break

    if target_effect:
        print(f"\nEfecto que contiene '{EFFECT_NAME_SEARCH}' encontrado:")
        print(f"Nombre del efecto: {target_effect.name()}")
        toggle_opacity_and_adjust_box(target_effect)
    else:
        print(f"No se encontro ningun efecto que contenga la palabra '{EFFECT_NAME_SEARCH}' en el nombre.")

# Ejecutar el script principal
if __name__ == "__main__":
    main()
