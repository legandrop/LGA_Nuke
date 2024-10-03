"""
______________________________________________________________________

  LGA_NKS_Compare_Versions v1.0 - 2024 - Lega
  Crea un nuevo track con una version anterior del clip seleccionado
  y pone al track en modo difference
______________________________________________________________________

"""

import hiero.core
import hiero.ui
from PySide2.QtGui import QColor

def copy_clip():
    # Obtener la secuencia activa en el timeline
    seq = hiero.ui.activeSequence()
    if not seq:
        print("No active sequence found.")
        return None

    # Obtener el timeline editor
    te = hiero.ui.getTimelineEditor(seq)
    selected_clips = te.selection()

    if len(selected_clips) == 0:
        print("*** No clips selected on the track ***")
        return None

    # Copiar el primer clip seleccionado (suponiendo que solo se selecciona uno)
    clip = selected_clips[0]
    if isinstance(clip, hiero.core.EffectTrackItem):
        print(f"Ignored effect item: {clip.name()}")
        return None

    copied_clip = clip.copy()
    print(f"Copied clip: {clip.name()}")
    return copied_clip, clip.timelineIn(), clip.timelineOut() - clip.timelineIn() + 1

def reorder_tracks_and_add_compare(seq):
    # Verificar si ya existe un track llamado "COMPARE"
    compare_track = None
    for track in seq.videoTracks():
        if track.name() == "COMPARE":
            compare_track = track
            break

    # Si no existe un track llamado "COMPARE", encontrar el indice del track "EXR" y crear "COMPARE"
    if not compare_track:
        exr_index = -1
        for index, track in enumerate(seq.videoTracks()):
            if track.name() == "EXR":
                exr_index = index
                break

        if exr_index == -1:
            print("No se encontro un track llamado 'EXR'.")
            return None

        # Obtener la lista de todos los tracks de video
        video_tracks = list(seq.videoTracks())
        print(f"Current video tracks: {[track.name() for track in video_tracks]}")

        # Remover todos los tracks
        for track in video_tracks:
            seq.removeTrack(track)

        # Crear el nuevo track llamado "COMPARE"
        compare_track = hiero.core.VideoTrack("COMPARE")

        # Reinsertar los tracks en el orden deseado, incluyendo el nuevo track antes de "EXR"
        reordered_tracks = video_tracks[:exr_index] + [compare_track] + video_tracks[exr_index:]
        for track in reordered_tracks:
            seq.addTrack(track)

        print(f"Track 'COMPARE' added and moved to index {exr_index}.")
        print(f"Reordered video tracks: {[track.name() for track in reordered_tracks]}")
    else:
        print("Track 'COMPARE' already exists.")
        
    return compare_track

def paste_clip_to_compare(compare_track, copied_clip, start_time, duration):
    if not compare_track or not copied_clip:
        return

    # Pegar el clip en el track COMPARE
    compare_track.addItem(copied_clip)
    copied_clip.setTimelineIn(start_time)
    copied_clip.setTimelineOut(start_time + duration - 1)
    print(f"Pasted clip '{copied_clip.name()}' to track COMPARE at start time {start_time}")

def toggle_blend_mode_for_exr(seq):
    # Volver a encontrar el track llamado "EXR" despues de agregar el track "COMPARE"
    for track in seq.videoTracks():
        if track.name() == "EXR":
            exr_track = track
            break
    else:
        print("No se encontro un track llamado 'EXR'.")
        return

    # Verificar si el blend mode ya esta activado
    if exr_track.isBlendEnabled():
        # Si esta activado, lo desactiva
        exr_track.setBlendEnabled(False)
        print(f"Blend mode desactivado para el track 'EXR'.")
    else:
        # Si no esta activado, lo activa y cambia el modo a "Difference"
        exr_track.setBlendEnabled(True)
        exr_track.setBlendMode("difference")
        print(f"Blend mode 'Difference' activado para el track 'EXR'.")

def self_replace_clip(copied_clip):
    try:
        if isinstance(copied_clip, hiero.core.EffectTrackItem):
            print(f"Ignored effect item: {copied_clip.name()}")
            return

        # Obtener el archivo original del clip copiado
        file_path = copied_clip.source().mediaSource().fileinfos()[0].filename()
        print(f"Replacing clip with file: {file_path}")

        # Reemplazar el clip copiado con el archivo original
        copied_clip.replaceClips(file_path)
        print(f"Clip replaced successfully with {file_path}.")
    except Exception as e:
        print(f"Error replacing clip: {e}")

def scan_and_downgrade_clip_version(clip):
    def get_all_versions(binItem):
        versions = binItem.items()
        return sorted(versions, key=lambda v: int(v.name().split('_v')[-1]))

    vc = hiero.core.VersionScanner()
    bin_item = clip.source().binItem()
    activeVersion = bin_item.activeVersion()
    vc.doScan(activeVersion)

    versions = get_all_versions(bin_item)
    if versions:
        current_version = bin_item.activeVersion()
        current_version_index = versions.index(current_version)
        
        if current_version_index > 0:
            previous_version = versions[current_version_index - 1]
            bin_item.setActiveVersion(previous_version)
            print(f"Changed {clip.name()} to version {previous_version.name()}")
        else:
            print(f"{clip.name()} is already at the oldest version available.")
    else:
        print(f"No versions found for clip: {clip.name()}")

def main(selected_clip=None):
    # Obtener la secuencia activa en el timeline
    seq = hiero.ui.activeSequence()
    if not seq:
        print("No active sequence found.")
        return

    # Iniciar una accion de undo para las primeras operaciones
    project = seq.project()
    project.beginUndo("Copy Clip, Reorder Tracks, Paste Clip to COMPARE, and Set EXR to Difference")

    try:
        # Copiar el clip seleccionado
        if selected_clip:
            copied_clip, start_time, duration = selected_clip.copy(), selected_clip.timelineIn(), selected_clip.timelineOut() - selected_clip.timelineIn() + 1
        else:
            copied_clip, start_time, duration = copy_clip()
        
        if not copied_clip:
            return

        # Guardar el clip original antes de copiarlo
        original_clip = hiero.ui.getTimelineEditor(seq).selection()[0]

        # Reordenar los tracks y agregar el track COMPARE (solo si no existe)
        compare_track = reorder_tracks_and_add_compare(seq)
        if not compare_track:
            return

        # Pegar el clip copiado en el track COMPARE
        paste_clip_to_compare(compare_track, copied_clip, start_time, duration)
        
        # Cambiar el modo del track EXR a "difference"
        toggle_blend_mode_for_exr(seq)
    except Exception as e:
        print(f"Error during operation: {e}")
    finally:
        # Finalizar la primera accion de undo
        project.endUndo()

    # Iniciar una nueva accion de undo para el self replace clip
    project.beginUndo("Self Replace Clip")
    try:
        # Reemplazar el clip copiado en el track COMPARE con el archivo original
        self_replace_clip(copied_clip)
    except Exception as e:
        print(f"Error during self replace clip: {e}")
    finally:
        # Finalizar la segunda accion de undo
        project.endUndo()

    # Iniciar una nueva accion de undo para escanear y bajar la version del nuevo clip
    project.beginUndo("Scan and Downgrade New Clip Version")
    try:
        # Escanear y bajar una version del nuevo clip
        scan_and_downgrade_clip_version(copied_clip)
    except Exception as e:
        print(f"Error during scan and downgrade clip version: {e}")
    finally:
        # Finalizar la tercera accion de undo
        project.endUndo()
