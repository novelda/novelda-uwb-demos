import json
import os
import sys
from pathlib import Path
from datetime import datetime

def prep_rec_dir(preset_json: str, recdir: str, recprefix: str, ignore_keys: list[str]=[]) -> str:
    """
    Prepares the recording directory by ensuring it exists and updating the preset JSON file
    with the recording path.

    Args:
        preset_json (str): Path to the preset JSON file.
        recdir (str): Directory where recordings will be saved.
        recprefix (str): Prefix for the recording files.

    Returns:
        str: The full path to the recording file.
    """
    recdir_path = Path(recdir).resolve()
    base_name = recprefix + datetime.now().strftime("%Y%m%dT%H%M%S")
    
    full_dir = recdir_path / base_name
    os.makedirs(full_dir, exist_ok=True)

    recfp = full_dir / (base_name + ".sig")

    # copy preset json, set playback=True, set recording path
    stp_fp = Path(preset_json).resolve()
    stp: dict = {}
    with open(stp_fp, "r") as f:
        stp = json.load(f)
    
    stp["IsLive"] = False
    stp["PlaybackFile"] = str(recfp)

    for key in ignore_keys:
        stp.pop(key, None)

    json_preset_copy = full_dir / (base_name + "_preset.json")
    with open(json_preset_copy, "w") as f:
        json.dump(stp, f, indent=4)
    
    return str(recfp), str(json_preset_copy)