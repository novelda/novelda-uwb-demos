from pathlib import Path
from datetime import datetime
import os
import sys
import json

import numpy as np

import PySignalFlow as psf

from Utils.param_maker import ParamMaker
from Utils.semantics import *

class RadarDirectCallback:

    def __init__(self):
        self._callback_func = None
        self._json_preset = None
        self._range_offset = -1.0
        self._bin_length = -1.0
        self._range_decimation = -1

    def run_with_callback_preset(self, callback_func, preset_json_path):

        self._callback_func = callback_func
        self._json_preset = preset_json_path

        flow = psf.Flow()

        liveflow_fp = str(Path(__file__).resolve().parent / "Flows" / "LiveHost_RadarDirect_Python.sfl") 
        playbackflow_fp = str(Path(__file__).resolve().parent / "Flows" / "PlaybackHost_RadarDirect_Python.sfl")

        live_dcremoval_fp = str(Path(__file__).resolve().parent / "Flows" / "LiveHost_RadarDirect_DCRemoval_Python.sfl")
        playback_dcremoval_fp = str(Path(__file__).resolve().parent / "Flows" / "PlaybackHost_RadarDirect_DCRemoval_Python.sfl")

        stp_fp = str(Path(self._json_preset).resolve())

        stp: dict[str, str] = None
        with open(stp_fp, "r") as f:
            stp = json.load(f)

        islive = stp["IsLive"]
        is_dc_removal = stp["DCRemoval"]

        pm = ParamMaker()
        pm["RDPlottingParameters"]["IsLive"] = "true" if islive else "false"

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
                raise FileNotFoundError(f"Playback file for X7BasebandRaw not specified or not found!")
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

        flow_to_load = None

        if islive:
            flow_to_load = live_dcremoval_fp if is_dc_removal else liveflow_fp
        else:
            flow_to_load = playback_dcremoval_fp if is_dc_removal else playbackflow_fp

        print("Running RadarDirect(callback) with preset: ", self._json_preset)
        flow.load(flow_to_load)
        flow.set_output_tap(self._actual_tapout_func)
        flow.set_parameters(parameter_string=pm.get_as_string())
        flow.run()

    def _actual_tapout_func(self, node_key, frame):

        if SIGSEM_RADAR_PARAMETERS in frame:
            self._range_offset = np.asarray(frame[SIGSEM_RADAR_PARAMETERS][ARRSEM_RANGE_OFFSET])[0]
            self._bin_length = np.asarray(frame[SIGSEM_RADAR_PARAMETERS][ARRSEM_BIN_LENGTH])[0]
            self._range_decimation = np.asarray(frame[SIGSEM_RADAR_PARAMETERS][ARRSEM_RANGE_DECIMATION])[0]

        seq_num = frame.sequence_number
        timestamp = frame.timestamp

        trx_mask = np.asarray(frame[SIGNAL_SEMANTIC_RADAR_X7][ARRAY_SEMANTIC_RADAR_TRXMASK])[0]

        data = None
        if ARRAY_SEMANTIC_BBIQ_FLOAT32 in frame[SIGNAL_SEMANTIC_RADAR_X7]:
            data = np.asarray(frame[SIGNAL_SEMANTIC_RADAR_X7][ARRAY_SEMANTIC_BBIQ_FLOAT32])
        elif ARRAY_SEMANTIC_RF_FLOAT32 in frame[SIGNAL_SEMANTIC_RADAR_X7]:
            data = np.asarray(frame[SIGNAL_SEMANTIC_RADAR_X7][ARRAY_SEMANTIC_RF_FLOAT32])
        else:
            raise RuntimeError("There is no data in the radar frame.")

        return self._callback_func(trx_mask, data, seq_num, timestamp, 
            self._range_offset, self._bin_length)

