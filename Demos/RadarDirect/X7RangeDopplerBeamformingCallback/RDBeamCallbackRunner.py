from pathlib import Path
from datetime import datetime
import os
import sys
import json

import numpy as np

import PySignalFlow as psf

from Utils.param_maker import ParamMaker
from Utils.semantics import *
from Utils.misc import prep_rec_dir

class RangeDopplerBeamHelper:
    def __init__(self, range_offset: float, bin_length: float, fps: float, azimuth_angles: np.ndarray, convert2pwr=False):
        self.range_offset = range_offset
        self.bin_length = bin_length
        self.fps = fps
        self.azimuth_angles = np.array(azimuth_angles, copy=True)

        # this will be initialised on first process call
        self.range_bins = 0
        self.fftSize = 0
        self.convert2pwr = convert2pwr

        self.initialized = False

    def update(self, rd_beams_shape: np.ndarray):
        if self.initialized:
            return

        numAngles = rd_beams_shape[0]
        if numAngles != len(self.azimuth_angles):
            raise ValueError("Azimuth angles do not match number of angles in data")

        self.range_bins = rd_beams_shape[1]
        self.fftSize = rd_beams_shape[2] if self.convert2pwr else rd_beams_shape[2]/2

        self.range_vector = np.arange(self.range_offset, self.range_offset + self.range_bins*self.bin_length, self.bin_length)
        df = self.fps / self.fftSize
        self.fft_vector = np.arange(-self.fps/2, self.fps/2, df)
        self.doppler_vector = self.fft_vector

        self.initialized = True

    def get_range_offset(self) -> float:
        """
            Returns:
                float: The range in meters for the first rangebin.
        """
        return self.range_offset

    def get_bin_length(self) -> float:
        """
            Returns:
                float: The distance in meters between two rangebins.
        """
        return self.bin_length

    def get_range_bins(self) -> int:
        """
            Returns:
                int: The number of rangebins.
        """
        return self.range_bins

    def get_fft_size(self) -> int:
        """
            Returns:
                int: The fft-size corresponding to the number of doppler bins.
        """
        return self.fftSize

    def get_range_vector(self) -> np.ndarray:
        """
            Returns:
                np.ndarray: The range vector in meters for each range bin.
        """
        return self.range_vector

    def get_fft_vector(self) -> np.ndarray:
        """
             Returns:
                np.ndarray: The doppler vector in Hertz for each doppler bin.
        """
        return self.fft_vector

    def get_doppler_vector(self) -> np.ndarray:
        """
            Same as get_fft_vector

            Returns:
                np.ndarray: The doppler vectorvin Hertz for each doppler bin.
        """
        return self.get_fft_vector()

    def get_azimuth_angles(self) -> np.ndarray:
        """
            Returns:
                np.ndarray: The doppler in Hertz for each doppler bin.
         """
        return self.azimuth_angles


class RDBeamformingCallback:

    def __init__(self):
        self._callback_func = None
        self._json_preset = None
        self._range_decimation = -1
        self.rd_beam_helper = None

    def run_with_callback_preset(self, callback_func, preset_json_path):

        self._callback_func = callback_func
        self._json_preset = preset_json_path

        flow = psf.Flow()

        liveflow_fp = str(Path(__file__).resolve().parent / "Flows" / "LiveHost_RangeDopplerBeamformingCallback_Python.sfl") 
        playbackflow_fp = str(Path(__file__).resolve().parent / "Flows" / "PlaybackHost_RangeDopplerBeamformingCallback_Python.sfl")

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
                raise FileNotFoundError(f"Playback file for X7RangeDopplerBeamforming not specified or not found!")
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

        print("Running X7RangeDopplerBeamforming(callback) with preset: ", self._json_preset)
        flow.load(flow_to_load)
        flow.set_output_tap(self._actual_tapout_func)
        flow.set_parameters(parameter_string=pm.get_as_string())
        flow.run()

    def _actual_tapout_func(self, node_key, frame):

        if self.rd_beam_helper is None:
            if SIGSEM_RADAR_PARAMETERS in frame:
                param_vec = np.array(frame[SIGSEM_RADAR_PARAMETERS][ARRSEM_RD_BEAM_PARAMS])
                self.rd_beam_helper = RangeDopplerBeamHelper(
                    param_vec[0], param_vec[1], param_vec[2], param_vec[4:], bool(param_vec[3])
                )
                
        seq_num = frame.sequence_number
        timestamp = frame.timestamp

        data: np.ndarray = None
        if ARRAY_SEMANTIC_RANGEDOPPLERPOWER_4D in frame[SIGNAL_SEMANTIC_RANGEDOPPLER]:
            data = np.asarray(frame[SIGNAL_SEMANTIC_RANGEDOPPLER][ARRAY_SEMANTIC_RANGEDOPPLERPOWER_4D])[0]
        elif ARRAY_SEMANTIC_RANGEDOPPLERPOWER_IQ_4D in frame[SIGNAL_SEMANTIC_RANGEDOPPLER]:
            data = np.asarray(frame[SIGNAL_SEMANTIC_RANGEDOPPLER][ARRAY_SEMANTIC_RANGEDOPPLERPOWER_IQ_4D])[0]
        else:
            raise RuntimeError("There is no data in the RD frame.")

        self.rd_beam_helper.update(data.shape)

        return self._callback_func(data, seq_num, timestamp, 
            self.rd_beam_helper)
