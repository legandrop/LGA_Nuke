#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
_____________________________________________________________________________________________________

  LGA_NKS_Trim_In v1.0 - 2025 - Lega
  Script para recortar el material antes del playhead en clips seleccionados.
  El clip se recorta tanto en el source como en el timeline, eliminando los frames antes del playhead
  y manteniendo la relación 1:1 para evitar retimes.
  Si el playhead está antes del inicio del clip, extiende el clip hasta el límite mínimo posible.
_____________________________________________________________________________________________________
"""

import hiero.core
import hiero.ui
from PySide2.QtWidgets import QAction
from PySide2.QtGui import QIcon

# Configurar depuración
DEBUG = True

def debug_print(message):
    """Imprime mensajes de depuración si DEBUG está activado."""
    if DEBUG:
        print(message)

def print_clip_properties(clip):
    """Imprime todas las propiedades relevantes de un clip para debugging."""
    if not DEBUG:
        return
    
    try:
        # Información sobre el clip en el timeline
        debug_print("\n=== PROPIEDADES DEL CLIP ===")
        debug_print(f"Nombre: {clip.name()}")
        debug_print(f"Timeline In: {clip.timelineIn()}")
        debug_print(f"Timeline Out: {clip.timelineOut()}")
        debug_print(f"Timeline Duration: {clip.duration()}")
        
        # Información sobre el source del clip
        debug_print(f"Source In: {clip.sourceIn()}")
        debug_print(f"Source Out: {clip.sourceOut()}")
        debug_print(f"Source Duration: {clip.sourceDuration()}")
        
        # Obtener el source item (MediaSource)
        source_item = clip.source()
        if source_item:
            debug_print(f"Media Source: {source_item.name()}")
            debug_print(f"Media File Path: {source_item.mediaSource().fileinfos()[0].filename()}")
            debug_print(f"Media Duration: {source_item.duration()}")
            debug_print(f"Media Start Time: {source_item.sourceIn()}")
            debug_print(f"Media End Time: {source_item.sourceOut()}")
            
        # Información sobre el playback speed
        debug_print(f"Playback Speed: {clip.playbackSpeed()}")
        
        # Espacio adicional para separar clips
        debug_print("=============================\n")
    except Exception as e:
        debug_print(f"Error al imprimir propiedades del clip: {e}")

class TrimInToPlayhead:
    """
    Clase para manejar el recorte del material antes del playhead en el timeline de Nuke Studio (Hiero).
    """
    
    def __init__(self):
        """Inicializa el objeto y crea las acciones del menú."""
        self.setup_actions()
    
    def setup_actions(self):
        """Configura las acciones del menú."""
        self.trim_in_action = QAction("Trim In to Playhead", None)
        self.trim_in_action.triggered.connect(self.trim_in_to_playhead)
        
        # Registrar acción en el menú Timeline
        hiero.core.events.registerInterest("kShowContextMenu/kTimeline", self.timeline_context_menu)
        
        # También podemos agregar un atajo de teclado si es necesario
        # self.trim_in_action.setShortcut("Ctrl+T")
    
    def timeline_context_menu(self, event):
        """Añade nuestra acción al menú contextual del timeline."""
        contextMenu = event.menu
        contextMenu.addAction(self.trim_in_action)
    
    def check_for_overlapping_items(self, track, current_item, new_in):
        """
        Verifica si hay clips que se superpondrían con el nuevo in point.
        
        Args:
            track: La pista donde está el clip
            current_item: El clip actual que estamos modificando
            new_in: El nuevo valor de in point
            
        Returns:
            bool: True si hay superposición, False si no
        """
        try:
            # Aseguramos que new_in sea un entero
            new_in = int(new_in)
            
            items = track.items()
            for item in items:
                if item != current_item:  # No comparar con el mismo clip
                    # Verifica si el nuevo in point superpondría con el final del clip anterior
                    if item.timelineIn() < new_in and new_in <= item.timelineOut():
                        debug_print(f"Superposición detectada con clip: {item.name()} ({item.timelineIn()}-{item.timelineOut()})")
                        return True
            return False
        except Exception as e:
            debug_print(f"Error al verificar superposiciones: {e}")
            return False
    
    def get_min_possible_timeline_in(self, clip):
        """
        Calcula el mínimo in point posible teniendo en cuenta:
        1. El media source (duración del archivo)
        2. El clip anterior en la misma pista (para evitar superposiciones)
        
        Args:
            clip: El clip que estamos analizando
            
        Returns:
            int: El mínimo valor posible para timeline in
        """
        try:
            # Obtenemos información del timeline
            timeline_in = clip.timelineIn()
            timeline_out = clip.timelineOut()
            source_in = clip.sourceIn()
            source_out = clip.sourceOut()
            
            # Obtenemos información del media source
            source_item = clip.source()
            if not source_item:
                debug_print("No se pudo obtener el source item del clip")
                return None
                
            # Obtenemos los límites del media source
            media_start = source_item.sourceIn()  # Típicamente 1001 para secuencias EXR
            media_end = source_item.sourceOut()
            
            # Calculamos cuántos frames hay disponibles en el source antes del source_in actual
            available_source_frames_before = source_in - 0  # source_in actual menos el mínimo posible (0)
            
            # El mínimo in point en el timeline, respetando los límites del media source
            # Convertimos a entero para evitar problemas con valores flotantes
            min_in_media = int(timeline_in - available_source_frames_before)
            
            debug_print(f"Cálculo de límite de media:")
            debug_print(f"  - Media Start: {media_start}")
            debug_print(f"  - Media End: {media_end}")
            debug_print(f"  - Source In: {source_in}")
            debug_print(f"  - Available Source Frames Before: {available_source_frames_before}")
            debug_print(f"  - Timeline In: {timeline_in}")
            debug_print(f"  - Mínimo Timeline In basado en media: {min_in_media}")
            
            # Ahora verificamos si hay clips antes que limitarían la extensión
            parent_track = clip.parent()
            track_items = parent_track.items()
            
            # Ordenamos los items por su posición en el timeline
            sorted_items = sorted(track_items, key=lambda x: x.timelineIn())
            
            # Buscamos el índice del clip actual
            current_index = sorted_items.index(clip)
            
            # Verificamos si hay un clip antes de éste
            min_in_prev_clip = None
            if current_index > 0:
                prev_clip = sorted_items[current_index - 1]
                # El límite sería el final del clip anterior
                min_in_prev_clip = prev_clip.timelineOut()
                debug_print(f"  - Clip anterior: {prev_clip.name()} termina en frame {min_in_prev_clip}")
            
            # Determinar el límite final
            if min_in_prev_clip is not None:
                min_in = max(min_in_media, min_in_prev_clip)
                debug_print(f"  - Límite final (mayor entre media y clip anterior): {min_in}")
            else:
                min_in = min_in_media
                debug_print(f"  - Límite final (solo basado en media): {min_in}")
                
            return min_in
            
        except Exception as e:
            debug_print(f"Error al calcular el mínimo in point: {e}")
            import traceback
            debug_print(traceback.format_exc())
            return None
    
    def extend_clip_to_minimum(self, clip, target_frame):
        """
        Extiende el inicio del clip hasta un frame específico.
        
        Args:
            clip: El clip a extender
            target_frame: El frame objetivo para el nuevo in point
            
        Returns:
            bool: True si la extensión fue exitosa, False en caso contrario
        """
        try:
            # Aseguramos que target_frame sea un entero
            target_frame = int(target_frame)
            
            # Obtenemos los valores actuales
            timeline_in = clip.timelineIn()
            source_in = clip.sourceIn()
            
            # Calculamos la diferencia entre el actual in y el nuevo in
            frame_difference = timeline_in - target_frame
            
            # Calculamos el nuevo source in
            new_source_in = float(source_in) - float(frame_difference)
            
            # Comprobamos que no sea negativo
            if new_source_in < 0:
                debug_print(f"El nuevo source in sería negativo ({new_source_in}). Ajustando a 0.")
                new_source_in = 0
                # Recalculamos el target_frame basado en el nuevo source_in
                target_frame = int(timeline_in - (source_in - new_source_in))
            
            # Establecemos el nuevo source in
            clip.setSourceIn(new_source_in)
            
            # Establecemos el nuevo timeline in
            clip.setTimelineIn(target_frame)
            
            # Imprimimos información sobre el ajuste
            debug_print(f"Clip extendido: {clip.name()}")
            debug_print(f"  - Timeline IN: {timeline_in} -> {target_frame} (diferencia: {frame_difference})")
            debug_print(f"  - Source IN: {source_in} -> {new_source_in}")
            debug_print(f"  - Nota: El playhead estaba antes del clip. Se ha extendido al mínimo posible.")
            
            return True
            
        except RuntimeError as re:
            error_msg = str(re)
            debug_print(f"Error de runtime al extender clip: {error_msg}")
            return False
            
        except TypeError as te:
            error_msg = str(te)
            debug_print(f"Error de tipo al extender clip: {error_msg}")
            debug_print(f"  - Target frame (tipo: {type(target_frame)}): {target_frame}")
            return False
            
        except OverflowError as oe:
            error_msg = str(oe)
            debug_print(f"Error de overflow al extender clip: {error_msg}")
            debug_print(f"  - Target frame (tipo: {type(target_frame)}): {target_frame}")
            return False
            
        except Exception as e:
            debug_print(f"Error inesperado al extender clip: {e}")
            import traceback
            debug_print(traceback.format_exc())
            return False
    
    def trim_material_to_playhead(self, clip, playhead_frame):
        """
        Recorta el material del clip a partir del playhead.
        Ajusta tanto el source in como el timeline in para mantener la relación 1:1.
        
        Args:
            clip: El clip a recortar
            playhead_frame: La posición del playhead
            
        Returns:
            bool: True si el recorte fue exitoso, False en caso contrario
        """
        try:
            # Obtenemos los valores actuales
            timeline_in = clip.timelineIn()
            timeline_out = clip.timelineOut()
            source_in = clip.sourceIn()
            source_out = clip.sourceOut()
            
            # Si el playhead está después del final del clip, no hacemos nada
            if playhead_frame >= timeline_out:
                debug_print(f"El playhead ({playhead_frame}) está después del final del clip {clip.name()} ({timeline_out})")
                return False
            
            # Calculamos cuántos frames debemos recortar desde el inicio
            frames_to_trim = playhead_frame - timeline_in
            
            # Calculamos los nuevos valores
            new_source_in = source_in + frames_to_trim
            new_timeline_in = playhead_frame
            
            # Verificamos que no estemos tratando de ir más allá de los límites del source
            if new_source_in >= source_out:
                debug_print(f"El recorte excedería los límites del source. No se puede recortar.")
                return False
            
            # Guardamos los valores por si necesitamos revertir el cambio
            original_timeline_in = timeline_in
            original_source_in = source_in
            
            try:
                # Primero establecemos el nuevo source in
                clip.setSourceIn(new_source_in)
                
                # Luego el nuevo timeline in
                clip.setTimelineIn(new_timeline_in)
                
            except Exception as e:
                # Si algo sale mal, intentamos revertir los cambios
                debug_print(f"Error durante el recorte: {e}. Intentando revertir cambios...")
                try:
                    clip.setSourceIn(original_source_in)
                    clip.setTimelineIn(original_timeline_in)
                except:
                    debug_print("No se pudieron revertir los cambios.")
                return False
            
            # Imprimimos información sobre el ajuste
            debug_print(f"Clip recortado: {clip.name()}")
            debug_print(f"  - Timeline IN: {timeline_in} -> {new_timeline_in} (recortado {frames_to_trim} frames)")
            debug_print(f"  - Source IN: {source_in} -> {new_source_in} (recortado {frames_to_trim} frames)")
            debug_print(f"  - Frames recortados: {frames_to_trim}")
            
            return True
            
        except RuntimeError as re:
            error_msg = str(re)
            debug_print(f"Error de runtime al recortar clip: {error_msg}")
            return False
            
        except TypeError as te:
            error_msg = str(te)
            debug_print(f"Error de tipo al recortar clip: {error_msg}")
            return False
            
        except Exception as e:
            debug_print(f"Error inesperado al recortar clip: {e}")
            import traceback
            debug_print(traceback.format_exc())
            return False
    
    def trim_in_to_playhead(self):
        """
        Recorta el material antes del playhead en clips seleccionados.
        Ajusta tanto el source como el timeline para mantener la relación 1:1.
        Si el playhead está antes del inicio del clip, extiende el clip hasta el límite mínimo posible.
        """
        seq = hiero.ui.activeSequence()
        if not seq:
            debug_print("\nNo se encontró una secuencia activa.")
            return
            
        te = hiero.ui.getTimelineEditor(seq)
        selected_clips = te.selection()
        
        current_viewer = hiero.ui.currentViewer()
        player = current_viewer.player() if current_viewer else None
        playhead_frame = player.time() if player else None

        if not selected_clips:
            debug_print("No hay clips seleccionados.")
            return
            
        if playhead_frame is None:
            debug_print("Posición del playhead no disponible.")
            return
        
        debug_print(f"Posición del playhead: {playhead_frame}")
        
        for clip in selected_clips:
            try:
                # Imprimimos las propiedades del clip para debugging
                debug_print("\nPROPIEDADES ANTES DEL RECORTE:")
                print_clip_properties(clip)
                
                # Obtenemos los valores actuales del timeline
                timeline_in = clip.timelineIn()
                timeline_out = clip.timelineOut()
                
                # Comprobamos si el playhead está antes del inicio del clip
                if playhead_frame < timeline_in:
                    debug_print(f"El playhead ({playhead_frame}) está antes del inicio del clip {clip.name()} ({timeline_in})")
                    
                    # Calculamos el mínimo in point posible
                    min_in = self.get_min_possible_timeline_in(clip)
                    
                    if min_in is None:
                        debug_print("No se pudo determinar el mínimo in point posible.")
                        continue
                    
                    # Determinamos el frame objetivo para la extensión
                    target_frame = playhead_frame
                    
                    # Si el playhead está antes del límite mínimo, ajustamos al mínimo
                    if playhead_frame < min_in:
                        target_frame = int(min_in)  # Aseguramos que sea entero
                        debug_print(f"El playhead ({playhead_frame}) está antes del límite mínimo ({min_in}). Se ajustará al mínimo.")
                    
                    # Verificamos si hay superposición con otro clip en el frame objetivo
                    parent_track = clip.parent()
                    if self.check_for_overlapping_items(parent_track, clip, target_frame):
                        debug_print(f"No se puede extender: causaría superposición con otro clip")
                        continue
                    
                    # Extendemos el clip hacia atrás
                    success = self.extend_clip_to_minimum(clip, target_frame)
                    if success:
                        # Imprimimos las propiedades actualizadas
                        debug_print("\nPROPIEDADES DESPUÉS DE LA EXTENSIÓN:")
                        print_clip_properties(clip)
                    
                # Si el playhead está dentro del clip, recortamos normalmente
                elif playhead_frame < timeline_out:
                    # Recortamos el material
                    success = self.trim_material_to_playhead(clip, playhead_frame)
                    if success:
                        # Imprimimos las propiedades actualizadas
                        debug_print("\nPROPIEDADES DESPUÉS DEL RECORTE:")
                        print_clip_properties(clip)
                    else:
                        debug_print(f"No se pudo recortar el clip {clip.name()}")
                
                # Si el playhead está después del final del clip, no hacemos nada
                else:
                    debug_print(f"El playhead ({playhead_frame}) está después del final del clip {clip.name()} ({timeline_out})")
                
            except Exception as e:
                debug_print(f"Error al procesar el clip: {e}")
                import traceback
                debug_print(traceback.format_exc())

# Instanciar la clase cuando se importa el módulo
trim_tool = TrimInToPlayhead()

# Función para testing/depuración
def test_trim_in():
    """Función de prueba para ejecutar manualmente desde la consola de Python."""
    trimmer = TrimInToPlayhead()
    trimmer.trim_in_to_playhead()
    return "Test completado"

# Para poder ejecutar la función desde la consola de Python directamente
if __name__ == "__main__":
    test_trim_in()
