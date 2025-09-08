from pathlib import Path
import json
import os
from datetime import datetime

import PySignalFlow as psf
from Utils.param_maker import ParamMaker

flow = psf.Flow()

liveflow_fp = str(Path(__file__).resolve().parent / "Flows" / "LiveHostPlot_X7RangeDopplerRaw_Python.sfl") 
playbackflow_fp = str(Path(__file__).resolve().parent / "Flows" / "PlaybackHostPlot_X7RangeDopplerRaw_Python.sfl")
stp_fp = str(Path(__file__).resolve().parent / "rd_raw_setup.json")

stp: dict[str, str] = None
with open(stp_fp, "r") as f:
    stp = json.load(f)

islive = stp["IsLive"]

pm = ParamMaker()

ba22 = stp["BA22FirmwarePath"]
filesource_in = stp["PlaybackFile"]

if islive:
    pm["ConnectionParameters"]["BA22FirmwarePath"] = f"\"{ba22}\""
else:
    pm["fileSource"]["Path"] = f"\"{filesource_in}\""

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


flow.load(liveflow_fp if islive else playbackflow_fp)
flow.set_parameters(parameter_string=pm.get_as_string())
flow.run()