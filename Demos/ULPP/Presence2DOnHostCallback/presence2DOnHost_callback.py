from pathlib import Path
from datetime import datetime
import os
import sys
import json

import numpy as np

import PySignalFlow as psf

from Utils.param_maker import ParamMaker
from Utils.misc import prep_rec_dir
from Presence2DPlotter.Presence2DHelper import Presence2DHelper

class Presence2DOnHostCallback:

    def __init__(self):
        self._callback_func = None
        self._json_preset = None
        self.presence2D_helper = Presence2DHelper()

    def run_with_callback_preset(self, callback_func, preset_json_path):

        self._callback_func = callback_func
        self._json_preset = preset_json_path

        flow = psf.Flow()

        liveflow_fp = str(Path(__file__).resolve().parent / "Flows" / "ULPP_Presence2DOnHost_RadarDirectLiveCallback_Python.sfl") 
        playbackflow_fp = str(Path(__file__).resolve().parent / "Flows" / "ULPP_Presence2DOnHost_RadarDirectPlaybackCallback_Python.sfl")

        stp_fp = str(Path(self._json_preset).resolve())

        stp: dict[str, str] = None
        with open(stp_fp, "r") as f:
            stp = json.load(f)

        islive = stp["IsLive"]

        pm = ParamMaker()

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
                raise FileNotFoundError(f"Playback file for Presence2DOnHost not specified or not found!")
            pm["fileSource"]["Path"] = f"\"{in_fp}\""

        for sec, dct in stp.items():
            if isinstance(dct, dict):
                for param, val in dct.items():
                    pm[sec][param] = val

        record = stp["DoRecording"]
        recdir = stp["RecordingDirectory"]
        recprefix = stp["RecordingPrefix"]

        if record and islive:
            recfp, _ = prep_rec_dir(str(stp_fp), recdir, recprefix)
            pm["fileSink"]["Enabled"] = "true" if record else "false"
            pm["fileSink"]["Path"] = f"\"{str(recfp)}\""

        flow_to_load = None

        if islive:
            flow_to_load = liveflow_fp
        else:
            flow_to_load = playbackflow_fp

        print("Running X7 ULPP Presence2DHost(callback) with preset: ", self._json_preset)
        flow.load(flow_to_load)
        flow.set_output_tap(self._actual_tapout_func)
        flow.set_parameters(parameter_string=pm.get_as_string())
        flow.run()

    def _actual_tapout_func(self, node_key, frame):

        seq_num = frame.sequence_number
        timestamp = frame.timestamp

        sigsem = "human_presence"
        human_presence_arrsem = "human_presence_2d_basic"

        if sigsem in frame:

            if human_presence_arrsem in frame[sigsem]:
                human_presence = np.array(frame[sigsem][human_presence_arrsem]).flatten()
        else:
            raise RuntimeError("There is no data in the radar frame.")

        self.presence2D_helper.new_human_presence_2d_data(seq_num, timestamp, human_presence)
        return self._callback_func(self.presence2D_helper)

