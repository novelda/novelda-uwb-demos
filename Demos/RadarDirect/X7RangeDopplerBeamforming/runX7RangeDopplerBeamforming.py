from pathlib import Path
import json
import os
import sys
from datetime import datetime

import PySignalFlow as psf

from Utils.param_maker import ParamMaker
from Utils.misc import prep_rec_dir

def run_with_setup(setup_json: str):

    flow = psf.Flow()

    liveflow_fp = str(Path(__file__).resolve().parent / "Flows" / "LiveHostPlot_RangeDopplerBeamforming_Python.sfl") 
    playbackflow_fp = str(Path(__file__).resolve().parent / "Flows" / "PlaybackHostPlot_RangeDopplerBeamforming_Python.sfl")
    stp_fp = str(Path(setup_json).resolve())

    stp: dict[str, str] = None
    with open(stp_fp, "r") as f:
        stp = json.load(f)

    islive = stp["IsLive"]

    pm = ParamMaker()
    pm["MultiRDPlottingParameters"]["IsLive"] = "true" if islive else "false"

    ba22 = stp["BA22FirmwarePath"]
    filesource_in = stp["PlaybackFile"]

    if islive:
        pm["ConnectionParameters"]["BA22FirmwarePath"] = f"\"{ba22}\""
        ba22_fp = Path(ba22).resolve()
        if not os.path.isfile(ba22_fp):
            raise FileNotFoundError(f"BA22 firmware file not specified or not found!")
    else:
        in_fp = Path(filesource_in).resolve()
        if not os.path.isfile(in_fp):
            raise FileNotFoundError(f"Playback file for X7RangeDopplerBeamforming not specified or not found!")
        pm["fileSource"]["Path"] = f"\"{in_fp}\""

    for sec, dct in stp.items():
        if isinstance(dct, dict):
            for param, val in dct.items():
                pm[sec][param] = val
    
    # override Convert2Pwr for plotting demo
    pm["RangeDoppler4D"]["Convert2Pwr"] = "true"

    record = stp["DoRecording"]
    recdir = stp["RecordingDirectory"]
    recprefix = stp["RecordingPrefix"]

    if record and islive:
        recfp, _ = prep_rec_dir(str(stp_fp), recdir, recprefix)
        pm["fileSink"]["Enabled"] = "true" if record else "false"
        pm["fileSink"]["Path"] = f"\"{str(recfp)}\""

    print("Running X7 Range-Doppler Beamforming with preset: ", setup_json)
    flow.load(liveflow_fp if islive else playbackflow_fp)
    flow.set_parameters(parameter_string=pm.get_as_string())
    flow.run()

if __name__ == "__main__":
    setup_json = str(Path(__file__).resolve().parent / "Presets" / "default_preset.json")
    if len(sys.argv) > 1:
        setup_json = str(Path(sys.argv[1]).resolve())
    
    run_with_setup(setup_json)