from __future__ import annotations

import sys
import subprocess
import time
import os
import tempfile
import numpy as np
from pathlib import Path

import PySignalFlow as psf

from Utils.sharedmem_handler import SharedMemSender
from Utils.semantics import *
from RadarDirectBeamPlot.RadarDirectBeamPlot_plotter import *

DEFAULT_START_RANGE = 0.4  # meters

class RadarDirectBeamPlot:
    def __init__(self, *_):
        self.initialized = False

        self.fps = 1
        self.enable_dc_removal = False
        self.num_saved_frames = -1

        self.az_beam_angles = np.array([])

        self.angle_lim_vec = np.array([])
        self.range_lim_vec = np.array([])
        self.power_lim_vec = np.array([])

        self.threshold_ranges = np.array([])
        self.threshold_values = np.array([])

        self.range_slices_to_plot = np.array([1.0])
        self.angle_slices_to_plot = np.array([0.0])

        self.color_map_range = np.array([-60.0, 20.0])
        self.beam_sector_width_deg = 20.0

        self.dc_smooth_coeff = None

    def set_parameters(self, context, params, sections):
        for section in sections:
            if section not in params:
                continue
            curr_sec = params[section]

            if "FPS" in curr_sec:
                self.fps = float(np.array(curr_sec["FPS"])[0])
            if "RangeOffset" in curr_sec:
                self.range_offset = float(np.array(curr_sec["RangeOffset"])[0])
            if "BinLength" in curr_sec:
                self.bin_length = float(np.array(curr_sec["BinLength"])[0])
            if "MaxBufferedFrames" in curr_sec:
                self.num_saved_frames = int(np.array(curr_sec["MaxBufferedFrames"])[0])
            if "enableDCRemoval" in curr_sec:
                self.enable_dc_removal = np.array(curr_sec["enableDCRemoval"], dtype=bool)[0]
            if "IsLive" in curr_sec:
                self.is_live = np.array(curr_sec["IsLive"], dtype=bool)[0]
            if "azBeamAngles" in curr_sec:
                self.az_beam_angles = np.array(curr_sec["azBeamAngles"], dtype=float)
            if "MframesPerPulse" in curr_sec:
                self.MframesPerPulse = np.array(curr_sec["MframesPerPulse"]).flatten()[0]
            if "PowerLimVec" in curr_sec:
                try:
                    newpowerlim = np.array(curr_sec["PowerLimVec"], dtype=float)
                    if newpowerlim.size == 2:
                        self.power_lim_vec = newpowerlim
                except Exception as e:
                    pass
            if "AngleLimVec" in curr_sec:
                try:
                    newanglelim = np.array(curr_sec["AngleLimVec"], dtype=float)
                    if newanglelim.size == 2:
                        self.angle_lim_vec = newanglelim
                except Exception as e:
                    pass
            if "RangeLimVec" in curr_sec:
                try:
                    newrangelim = np.array(curr_sec["RangeLimVec"], dtype=float)
                    if newrangelim.size == 2:
                        self.range_lim_vec = newrangelim
                except Exception as e:
                    pass
            if "ThresholdAtRanges" in curr_sec:
                self.threshold_ranges = np.array(curr_sec["ThresholdAtRanges"], dtype=float)
            if "ThresholdValues" in curr_sec:
                self.threshold_values = np.array(curr_sec["ThresholdValues"], dtype=float)
            if "DCEstimationSmoothCoeff" in curr_sec:
                self.dc_smooth_coeff = float(np.array(curr_sec["DCEstimationSmoothCoeff"])[0])
            if "RangeSlicesToPlot" in curr_sec:
                self.range_slices_to_plot = np.array(curr_sec["RangeSlicesToPlot"], dtype=float)
            if "AngleSlicesToPlot" in curr_sec:
                self.angle_slices_to_plot = np.array(curr_sec["AngleSlicesToPlot"], dtype=float)
            if "ColorMapRange" in curr_sec:
                try:
                    newcolormaprange = np.array(curr_sec["ColorMapRange"], dtype=float)
                    if newcolormaprange.size == 2:
                        self.color_map_range = newcolormaprange
                except Exception as e:
                    pass
            if "BeamSectorWidthDeg" in curr_sec:
                self.beam_sector_width_deg = float(np.array(curr_sec["BeamSectorWidthDeg"])[0])

    def buildup(self):

        MAX_RANGE_BINS = 192 * 4
        BYTES_PER_FLOAT = 4

        # + 50_000 to make sure theres space
        self.shm_blocksize = len(self.az_beam_angles) * MAX_RANGE_BINS * BYTES_PER_FLOAT + 50_000
        
        self.shm_numblocks = 10 # a lot of blocks to speed up playback loading

        # put verbose=False when released
        self.sharedmem_sender = SharedMemSender(self.shm_blocksize, self.shm_numblocks, verbose=True)

        closesig_file = tempfile.NamedTemporaryFile(prefix="x7_run_", delete=False)
        self.close_path = closesig_file.name
        closesig_file.close()

        # start plotting process
        worker_script = str(Path(__file__).resolve().parent / "RadarDirectBeam_procrunner.py")
        self.plotting_process = subprocess.Popen([
            sys.executable,  # Use the same Python executable
            worker_script,
            self.sharedmem_sender.sharedmem.name,
            f"{self.shm_blocksize}",
            f"{self.shm_numblocks}",
            self.close_path
        # ], stdout=None, stderr=None, text=True, bufsize=1)
        ], stdout=subprocess.PIPE, stderr=None, text=True, bufsize=1)

        param_dict = {
            "fps" : self.fps,
            "range_offset" : self.range_offset,
            "bin_length" : self.bin_length,
            "num_saved_frames" : self.num_saved_frames,
            "is_live" : self.is_live,
            "default_start_range" : DEFAULT_START_RANGE,
            "az_beam_angles" : self.az_beam_angles,
            "num_rangebins" : int(self.MframesPerPulse * 16),
            "threshold_ranges" : self.threshold_ranges,
            "threshold_values" : self.threshold_values,
            "dc_smooth_coeff" : self.dc_smooth_coeff,
            "range_slices_to_plot" : self.range_slices_to_plot,
            "angle_slices_to_plot" : self.angle_slices_to_plot,
            "color_map_range" : self.color_map_range,
            "beam_sector_width_deg" : self.beam_sector_width_deg
        }

        if self.range_lim_vec.size == 2:
            param_dict["range_lim_vec"] = self.range_lim_vec
        if self.angle_lim_vec.size == 2:
            param_dict["angle_lim_vec"] = self.angle_lim_vec
        if self.power_lim_vec.size == 2:
            param_dict["power_lim_vec"] = self.power_lim_vec

        self.send_data(param_dict)

        for line in self.plotting_process.stdout:
            if line.strip() == "PLOTTING_PROCESS_READY":
                break

    def send_data(self, data):
        max_wait = 2
        now = time.time()
        while not self.sharedmem_sender.send_data(data): # busy wait for max speed for huge playback files
            if time.time() - now > max_wait:
                print("Shared memory sender timed out, exiting process")
                self.teardown()
                return

    def extract_radardirect_beam_data(self, frame):

        inc_data = np.asarray(
            frame[SIGNAL_SEMANTIC_RADAR_X7][ARRAY_SEMANTIC_BBIQ_MULTIFRAME_FLOAT32])
    
        # forget elevation
        inc_data = inc_data[0]

        # convert to power
        inc_data = 20*np.log10((np.abs(inc_data[:, 0, :] + 1j*inc_data[:, 1, :])+1e-16))

        self.current_data: np.ndarray = inc_data

        radar_beam_plot_data = RadarDirectBeamData(
            power_beam_data=inc_data,
            timestamp=frame.timestamp,
            seq_num=frame.sequence_number
        )

        # Store for later use and return
        self.radar_beam_plot_data = radar_beam_plot_data
        return radar_beam_plot_data

    def teardown(self):
        max_wait = 2
        now = time.time()
        while not self.sharedmem_sender.are_all_read():
            time.sleep(0.1)
            if time.time() - now > max_wait:
                break

        if os.path.exists(self.close_path):
            os.remove(self.close_path)
        self.sharedmem_sender.cleanup()

    def process(self, sf):

        # Exit if plotting subprocess has closed
        if self.plotting_process.poll() is not None:
            return None, psf.ProcessResult.EndOfData
        
        if not self.sharedmem_sender.check_buff_exists():
            return None, psf.ProcessResult.EndOfData

        for i in range(len(sf)):
            frame = sf[i]
            self.extract_radardirect_beam_data(frame)
            self.send_data(self.radar_beam_plot_data)

        return None, psf.ProcessResult.Continue