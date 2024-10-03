import hiero.core 
import hiero.ui 

def print_effects_in_tracks(track_names): 
    # Get the active sequence 
    seq = hiero.ui.activeSequence() 

    if not seq: 
        print("No active sequence found.") 
        return 

    # Iterate over the video tracks in the sequence 
    for track in seq.videoTracks(): 
        if track.name() in track_names: 
            print(f"\nTrack '{track.name()}':") 
            items = track.subTrackItems() 
            if not items: 
                print(f"  Track '{track.name()}' has no items.") 
                continue 
            for idx, item in enumerate(items): 
                # Check if the item is an effect 
                item = item[0] 
                if isinstance(item, hiero.core.EffectTrackItem): 
                    effect_name = item.name() if hasattr(item, 'name') else "Unnamed Effect" 
                    print(f"  Effect {idx+1}: {effect_name}") 
                else: 
                    print(f"  Clip {idx+1}: Not an effect.") 

# List of tracks to inspect 
tracks_to_inspect = ["BurnIn", "EXR"] 
# Call the function to print effects in the specified tracks 
print_effects_in_tracks(tracks_to_inspect)