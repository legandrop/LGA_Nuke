import hiero.core
import hiero.ui
import nuke

# Obtener la secuencia activa y el editor de línea de tiempo
seq = hiero.ui.activeSequence()
if seq:  # Asegurarse de que hay una secuencia activa
    te = hiero.ui.getTimelineEditor(seq)
    selected_clips = te.selection()

    # Iterar sobre los elementos seleccionados
    if selected_clips:
        for clip in selected_clips:
            # Verificar si el elemento es un clip de video o un efecto
            if isinstance(clip, hiero.core.EffectTrackItem):
                # Es un efecto, imprimir su nombre
                print("Effect name:", clip.name())

                # Obtener información adicional del efecto
                node = clip.node()
                if node:
                    print("Effect node:", node.name())
                    
                    # Verificar si el nodo tiene errores
                    if clip.nodeHasError():
                        print("The effect node has an error.")
                    else:
                        print("The effect node is valid.")

                    # Imprimir todas las propiedades (knobs) del nodo
                    print("Node properties:")
                    for knob in node.knobs():
                        try:
                            value = node[knob].value()
                            print(f"{knob}: {value} (Type: {type(value)})")
                        except Exception as e:
                            print(f"Could not retrieve value for knob {knob}: {e}")

                    # Verificar si el knob 'font' existe y su tipo de valor
                    if "font" in node.knobs():
                        font_value = node['font'].value()
                        print(f"Font knob value: {font_value} (Type: {type(font_value)})")
                        
                        # Verificar el tipo de valor y decidir si se puede modificar
                        if isinstance(font_value, str):
                            print(f"Current font: {font_value}")
                            node['font'].setValue('Arial')  # Cambiar el font a Arial
                        else:
                            print("The 'font' knob is not a text value and cannot be set as a string.")

                # Imprimir una descripción del objeto
                print("Effect description:", clip.toString())
            else:
                # Es un clip de video, imprimir el nombre del archivo
                file_path = clip.source().mediaSource().fileinfos()[0].filename()
                print("Clip name:", os.path.basename(file_path))
    else:
        print("No clips selected on the timeline.")
else:
    print("No active sequence found.")
