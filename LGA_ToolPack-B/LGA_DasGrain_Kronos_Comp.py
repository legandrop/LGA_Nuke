"""
_____________________________________________________________________________________________________________________

  LGA_DasGrain_Kronos_Comp v1.1 | Lega
  Herramienta  para sincronizar la intensidad del grano de un nodo Dasgrain con los valores de interpolación de Kronos.
  Esto mantiene una apariencia consistente del grano incluso cuando Kronos interpola frames.
_____________________________________________________________________________________________________________________

"""

import nuke


def add_amount_knobs(node, kronos_node):
    """Añade un tab 'KroComp' con knobs 'Intensity' y 'KronosFrame', y modifica el knob 'luminance' existente"""
    if "Intensity" not in node.knobs():
        # Crear el nuevo tab
        tab = nuke.Tab_Knob("KroComp", "KroComp")
        node.addKnob(tab)

        # Crear el knob Intensity
        intensity_knob = nuke.Double_Knob("Intensity", "Intensity")
        intensity_knob.setRange(0.5, 1.5)
        intensity_knob.setValue(1.2)  # Valor inicial 1.2
        node.addKnob(intensity_knob)

        # Añadir un divider después del knob Intensity
        divider = nuke.Text_Knob("divider", "")
        node.addKnob(divider)

        # Crear el knob KronosFrame
        kronos_frame_knob = nuke.Double_Knob("KronosFrame", "Kronos Frame")
        kronos_frame_knob.setExpression(f"parent.{kronos_node.name()}.timingFrame2")
        node.addKnob(kronos_frame_knob)

        # Añadir flags para mejorar la apariencia
        node.knob("Intensity").setFlag(nuke.STARTLINE)
        node.knob("KronosFrame").setFlag(nuke.STARTLINE)

        print(
            f"Se ha añadido el tab 'KroComp' con los knobs 'Intensity' y 'KronosFrame' al nodo {node.name()}."
        )
    else:
        print(f"El nodo {node.name()} ya tiene un knob llamado 'Intensity'.")

    # Modificar el knob 'luminance' existente
    luminance_knob = node.knob("luminance")
    if luminance_knob:
        luminance_expression = f"""
        [expr {{
            abs(fmod([value parent.{kronos_node.name()}.timingFrame2], 1) - 0.5) >= 0.36 ? 
            1 : 
            (2 - [value this.Intensity])
        }}]
        """
        luminance_knob.setExpression(luminance_expression)
        print(
            f"Se ha modificado la expresión del knob 'luminance' en el nodo {node.name()}."
        )
    else:
        print(f"No se encontró el knob 'luminance' en el nodo {node.name()}.")


def main():
    selected_nodes = nuke.selectedNodes()
    if len(selected_nodes) < 2:
        print("Por favor, selecciona al menos un nodo DasGrain y un nodo Kronos.")
        return

    dasgrain_node = None
    kronos_node = None

    for node in selected_nodes:
        if node.Class() == "Group" and node.name().startswith("DasGrain"):
            dasgrain_node = node
        elif node.Class() == "Kronos" or node.name().startswith("Kronos"):
            kronos_node = node

    if not dasgrain_node or not kronos_node:
        print("Por favor, asegúrate de seleccionar un nodo DasGrain y un nodo Kronos.")
        return

    add_amount_knobs(dasgrain_node, kronos_node)


# Llamar a main() para iniciar la aplicacion
if __name__ == "__main__":
    main()
