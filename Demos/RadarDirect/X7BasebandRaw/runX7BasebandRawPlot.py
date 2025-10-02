from pathlib import Path
from datetime import datetime
import os
import sys
import json

import PySignalFlow as psf

from Utils.param_maker import ParamMaker

def run_with_setup(setup_json: str):

    flow = psf.Flow()

    liveflow_fp = str(Path(__file__).resolve().parent / "Flows" / "LiveHostPlot_Baseband_Python.sfl") 
    playbackflow_fp = str(Path(__file__).resolve().parent / "Flows" / "PlaybackHostPlot_Baseband_Python.sfl")

    live_dcremoval_fp = str(Path(__file__).resolve().parent / "Flows" / "LiveHostPlot_Baseband_DCRemoval_Python.sfl")
    playback_dcremoval_fp = str(Path(__file__).resolve().parent / "Flows" / "PlaybackHostPlot_Baseband_DCRemoval_Python.sfl")

    stp_fp = str(Path(setup_json).resolve())

    stp: dict[str, str] = None
    with open(stp_fp, "r") as f:
        stp = json.load(f)

    islive = stp["IsLive"]
    is_dc_removal = stp["DCRemoval"]

    pm = ParamMaker()
    pm["BBPlottingParameters"]["IsLive"] = "true" if islive else "false"
    pm["BBPlottingParameters"]["DCRemoval"] = "true" if is_dc_removal else "false"

    ba22 = stp["BA22FirmwarePath"]
    filesource_in = stp["PlaybackFile"]

    if islive:
        pm["ConnectionParameters"]["BA22FirmwarePath"] = f"\"{ba22}\""
    else:
        in_fp = Path(filesource_in).resolve()
        if not os.path.isfile(in_fp):
            raise FileNotFoundError(f"Playback file {in_fp} not found!")
        pm["fileSource"]["Path"] = f"\"{in_fp}\""

    for sec, dct in stp.items():
        if isinstance(dct, dict):
            for param, val in dct.items():
                pm[sec][param] = val

    record = stp["DoRecording"]
    recdir = stp["RecordingDirectory"]
    recprefix = stp["RecordingPrefix"]
    recfp = Path(recdir).resolve() / (str(recprefix) +  datetime.now().strftime("%Y%m%dT%H%M%S") + ".sig")

    if record:
        pm["fileSink"]["Enabled"] = "true" if record else "false"
        pm["fileSink"]["Path"] = f"\"{str(recfp)}\""
        os.makedirs(os.path.dirname(recfp), exist_ok=True)

    print("Running RadarDirect plotting with preset: ", setup_json)

    flow_to_load = None

    if islive:
        flow_to_load = live_dcremoval_fp if is_dc_removal else liveflow_fp
    else:
        flow_to_load = playback_dcremoval_fp if is_dc_removal else playbackflow_fp

    flow.load(flow_to_load)
    flow.set_parameters(parameter_string=pm.get_as_string())
    flow.run()

if __name__ == "__main__":
    setup_json = str(Path(__file__).resolve().parent / "Presets" / "default_preset.json")
    if len(sys.argv) > 1:
        setup_json = str(Path(sys.argv[1]).resolve())
    
    run_with_setup(setup_json)