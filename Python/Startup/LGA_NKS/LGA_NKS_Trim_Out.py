#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
LGA_NKS_Trim_Out v1.0
Script para cortar el punto de salida de clips seleccionados en la posición del playhead.
Modifica tanto el Source Out como el Destination Out para evitar crear retimes.
Si el playhead excede los límites, se ajusta al máximo posible automáticamente.
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

class TrimOutToPlayhead:
    """
    Clase para manejar el recorte de clips en el timeline de Nuke Studio (Hiero).
    """
    
    def __init__(self):
        """Inicializa el objeto y crea las acciones del menú."""
        self.setup_actions()
    
    def setup_actions(self):
        """Configura las acciones del menú."""
        self.trim_out_action = QAction("Trim Out to Playhead", None)
        self.trim_out_action.triggered.connect(self.trim_out_to_playhead)
        
        # Registrar acción en el menú Timeline
        hiero.core.events.registerInterest("kShowContextMenu/kTimeline", self.timeline_context_menu)
        
        # También podemos agregar un atajo de teclado si es necesario
        # self.trim_out_action.setShortcut("Ctrl+T")
    
    def timeline_context_menu(self, event):
        """Añade nuestra acción al menú contextual del timeline."""
        contextMenu = event.menu
        contextMenu.addAction(self.trim_out_action)
    
    def check_for_overlapping_items(self, track, current_item, new_out):
        """
        Verifica si hay clips que se superpondrían con el nuevo out point.
        
        Args:
            track: La pista donde está el clip
            current_item: El clip actual que estamos modificando
            new_out: El nuevo valor de out point
            
        Returns:
            bool: True si hay superposición, False si no
        """
        try:
            # Aseguramos que new_out sea un entero
            new_out = int(new_out)
            
            items = track.items()
            for item in items:
                if item != current_item:  # No comparar con el mismo clip
                    # Verifica si el nuevo out point superpondría con el inicio del siguiente clip
                    if item.timelineIn() <= new_out and new_out < item.timelineOut():
                        debug_print(f"Superposición detectada con clip: {item.name()} ({item.timelineIn()}-{item.timelineOut()})")
                        return True
            return False
        except Exception as e:
            debug_print(f"Error al verificar superposiciones: {e}")
            return False
    
    def get_max_possible_timeline_out(self, clip):
        """
        Calcula el máximo out point posible teniendo en cuenta:
        1. El media source (duración del archivo)
        2. El siguiente clip en la misma pista (para evitar superposiciones)
        
        Args:
            clip: El clip que estamos analizando
            
        Returns:
            int: El máximo valor posible para timeline out
        """
        try:
            # Obtenemos información del timeline
            timeline_in = clip.timelineIn()
            source_in = clip.sourceIn()
            
            # Obtenemos información del media source
            source_item = clip.source()
            if not source_item:
                debug_print("No se pudo obtener el source item del clip")
                return None
                
            # Obtenemos los límites del media source
            media_start = source_item.sourceIn()  # Típicamente 1001 para secuencias EXR
            media_end = source_item.sourceOut()   # Final del media (1285 en tu ejemplo)
            
            # Calculamos cuántos frames hay disponibles en el source después del source_in actual
            available_source_frames = media_end - (media_start + source_in)
            
            # El máximo out point en el timeline, respetando los límites del media source
            # Convertimos a entero para evitar problemas con valores flotantes
            max_out_media = int(timeline_in + available_source_frames)
            
            debug_print(f"Cálculo de límite de media:")
            debug_print(f"  - Media Start: {media_start}")
            debug_print(f"  - Media End: {media_end}")
            debug_print(f"  - Source In: {source_in}")
            debug_print(f"  - Available Source Frames: {available_source_frames}")
            debug_print(f"  - Timeline In: {timeline_in}")
            debug_print(f"  - Máximo Timeline Out basado en media: {max_out_media}")
            
            # Ahora verificamos si hay clips después que limitarían la extensión
            parent_track = clip.parent()
            track_items = parent_track.items()
            
            # Ordenamos los items por su posición en el timeline
            sorted_items = sorted(track_items, key=lambda x: x.timelineIn())
            
            # Buscamos el índice del clip actual
            current_index = sorted_items.index(clip)
            
            # Verificamos si hay un clip después de éste
            max_out_next_clip = None
            if current_index < len(sorted_items) - 1:
                next_clip = sorted_items[current_index + 1]
                # El límite sería el inicio del siguiente clip
                max_out_next_clip = next_clip.timelineIn()
                debug_print(f"  - Siguiente clip: {next_clip.name()} en frame {max_out_next_clip}")
            
            # Determinar el límite final
            if max_out_next_clip is not None:
                max_out = min(max_out_media, max_out_next_clip)
                debug_print(f"  - Límite final (menor entre media y siguiente clip): {max_out}")
            else:
                max_out = max_out_media
                debug_print(f"  - Límite final (solo basado en media): {max_out}")
                
            return max_out
            
        except Exception as e:
            debug_print(f"Error al calcular el máximo out point: {e}")
            import traceback
            debug_print(traceback.format_exc())
            return None
    
    def adjust_clip_out(self, clip, target_frame, is_max_limit=False):
        """
        Ajusta el punto de salida de un clip a un frame específico.
        
        Args:
            clip: El clip a ajustar
            target_frame: El frame objetivo para el nuevo out point
            is_max_limit: Indica si estamos ajustando al límite máximo posible
            
        Returns:
            bool: True si el ajuste fue exitoso, False en caso contrario
        """
        try:
            # Aseguramos que target_frame sea un entero
            target_frame = int(target_frame)
            
            # Obtenemos los valores actuales
            timeline_in = clip.timelineIn()
            timeline_out = clip.timelineOut()
            source_in = clip.sourceIn()
            source_out = clip.sourceOut()
            
            # Calculamos la diferencia entre el actual out y el nuevo out
            frame_difference = timeline_out - target_frame
            
            # Calculamos el nuevo source out
            new_source_out = float(source_out) - float(frame_difference)
            
            # Establecemos el nuevo source out
            clip.setSourceOut(new_source_out)
            
            # Establecemos el nuevo destination out
            clip.setTimelineOut(target_frame)
            
            # Imprimimos información sobre el ajuste
            operation = "extendido" if timeline_out < target_frame else "recortado"
            
            debug_print(f"Clip {operation}: {clip.name()}")
            debug_print(f"  - Timeline OUT: {timeline_out} -> {target_frame} (diferencia: {frame_difference})")
            debug_print(f"  - Source OUT: {source_out} -> {new_source_out}")
            
            if is_max_limit:
                debug_print(f"Nota: El playhead excedía el límite máximo. Se ha ajustado al máximo posible.")
            
            return True
            
        except RuntimeError as re:
            error_msg = str(re)
            debug_print(f"Error de runtime al ajustar clip: {error_msg}")
            return False
            
        except TypeError as te:
            error_msg = str(te)
            debug_print(f"Error de tipo al ajustar clip: {error_msg}")
            debug_print(f"  - Target frame (tipo: {type(target_frame)}): {target_frame}")
            return False
            
        except OverflowError as oe:
            error_msg = str(oe)
            debug_print(f"Error de overflow al ajustar clip: {error_msg}")
            debug_print(f"  - Target frame (tipo: {type(target_frame)}): {target_frame}")
            return False
            
        except Exception as e:
            debug_print(f"Error inesperado al ajustar clip: {e}")
            import traceback
            debug_print(traceback.format_exc())
            return False
    
    def trim_out_to_playhead(self):
        """
        Corta el punto de salida (OUT) de clips seleccionados en la posición del playhead.
        Si el playhead excede los límites, se ajusta al máximo posible automáticamente.
        Modifica tanto el Source Out como el Destination Out para mantener la relación 1:1 y evitar retimes.
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
                
                # Calculamos la posición del playhead relativa al inicio del clip
                playhead_offset_from_clip_start = playhead_frame - timeline_in
                
                # Obtenemos la información del source (mediasource) del clip
                source_in = clip.sourceIn()
                source_out = clip.sourceOut()
                
                # Calculamos el máximo out point posible
                max_out = self.get_max_possible_timeline_out(clip)
                
                # Calculamos la duración máxima posible desde el inicio
                max_duration = max_out - timeline_in if max_out else None
                
                debug_print(f"Información adicional:")
                debug_print(f"  - Playhead offset desde inicio del clip: {playhead_offset_from_clip_start}")
                debug_print(f"  - Máximo timeline out posible: {max_out}")
                debug_print(f"  - Duración máxima posible: {max_duration}")
                
                # Verificamos que el playhead esté después del inicio del clip
                if playhead_frame < timeline_in:
                    debug_print(f"El playhead ({playhead_frame}) está antes del inicio del clip {clip.name()} ({timeline_in})")
                    continue
                
                # Determinamos el frame objetivo para el ajuste
                target_frame = playhead_frame
                is_max_limit = False
                
                # Si el playhead excede el límite máximo, ajustamos al máximo
                if max_out and playhead_frame > max_out:
                    target_frame = int(max_out)  # Aseguramos que sea entero
                    is_max_limit = True
                    debug_print(f"El playhead ({playhead_frame}) excede el límite máximo ({max_out}). Se ajustará al máximo.")
                
                # Verificamos si hay superposición con otro clip en el frame objetivo
                parent_track = clip.parent()
                if self.check_for_overlapping_items(parent_track, clip, target_frame):
                    debug_print(f"No se puede recortar: causaría superposición con otro clip")
                    continue
                
                # Ajustamos el clip al frame objetivo (playhead o máximo)
                success = self.adjust_clip_out(clip, target_frame, is_max_limit)
                if success:
                    # Imprimimos las propiedades actualizadas
                    debug_print("\nPROPIEDADES DESPUÉS DEL RECORTE:")
                    print_clip_properties(clip)
                
            except Exception as e:
                debug_print(f"Error al recortar el clip: {e}")
                import traceback
                debug_print(traceback.format_exc())

# Instanciar la clase cuando se importa el módulo
trim_tool = TrimOutToPlayhead()

# Función para testing/depuración
def test_trim_out():
    """Función de prueba para ejecutar manualmente desde la consola de Python."""
    trimmer = TrimOutToPlayhead()
    trimmer.trim_out_to_playhead()
    return "Test completado"

# Para poder ejecutar la función desde la consola de Python directamente
if __name__ == "__main__":
    test_trim_out()
