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
from MultiRangeDopplerPlotter.BeamedRD_plotter import *

DEFAULT_START_RANGE = 0.4  # meters

class MultiRangeDopplerPlotter:
    def __init__(self, *_):
        self.initialized = False

        self.plot_linear_scale = False

        self.num_frames_in_pd = 0
        self.frames_between_pd = 0
        self.fps = 1
        self.enable_dc_removal = False
        self.num_saved_frames = -1

        self.az_beam_angles = np.array([])

        self.angle_lim_vec = np.array([-90.0, 90.0])

        self.range_slices_to_plot = np.array([1.0])
        self.doppler_slices_to_plot = np.array([0.0])
        self.angle_slices_to_plot = np.array([0.0])
        self.grid_cols_per_row = 2

    def set_parameters(self, context, params, sections):
        for section in sections:
            if section not in params:
                continue
            curr_sec = params[section]

            if "FPS" in curr_sec:
                self.fps = float(np.array(curr_sec["FPS"])[0])
            if "FFTSize" in curr_sec:
                self.fft_size = int(np.array(curr_sec["FFTSize"])[0])
            if "PowerLimVec" in curr_sec:
                try:
                    newzlim = np.array(curr_sec["PowerLimVec"])
                    if newzlim.size == 2:
                        self.power_lim_vec = newzlim
                except Exception as e:
                    pass
            if "RangeOffset" in curr_sec:
                self.range_offset = float(np.array(curr_sec["RangeOffset"])[0])
            if "BinLength" in curr_sec:
                self.bin_length = float(np.array(curr_sec["BinLength"])[0])
            if "NumFramesInPD" in curr_sec:
                self.num_frames_in_pd = int(np.array(curr_sec["NumFramesInPD"])[0])
            if "MaxBufferedFrames" in curr_sec:
                self.num_saved_frames = int(np.array(curr_sec["MaxBufferedFrames"])[0])
            if "FramesBetweenPD" in curr_sec:
                self.frames_between_pd = int(np.array(curr_sec["FramesBetweenPD"])[0])
            if "enableDCRemoval" in curr_sec:
                self.enable_dc_removal = np.array(curr_sec["enableDCRemoval"], dtype=bool)[0]
            if "IsLive" in curr_sec:
                self.is_live = np.array(curr_sec["IsLive"], dtype=bool)[0]
            if "azBeamAngles" in curr_sec:
                self.az_beam_angles = np.array(curr_sec["azBeamAngles"], dtype=float)
            if "RangeLimVec" in curr_sec:
                try:
                    newxlim = np.array(curr_sec["RangeLimVec"])
                    if newxlim.size == 2:
                        self.range_lim_vec = newxlim
                except Exception as e:
                    pass
            if "DopplerLimVec" in curr_sec:
                try:
                    newylim = np.array(curr_sec["DopplerLimVec"])
                    if newylim.size == 2:
                        self.doppler_lim_vec = newylim
                except Exception as e:
                    pass
            if "AngleLimVec" in curr_sec:
                try:
                    newalim = np.array(curr_sec["AngleLimVec"])
                    if newalim.size == 2:
                        self.angle_lim_vec = newalim
                except Exception as e:
                    pass
            if "RangeSlicesToPlot" in curr_sec:
                try:
                    self.range_slices_to_plot = np.array(curr_sec["RangeSlicesToPlot"], dtype=float)
                except Exception as e:
                    pass
            if "DopplerSlicesToPlot" in curr_sec:
                try:
                    self.doppler_slices_to_plot = np.array(curr_sec["DopplerSlicesToPlot"], dtype=float)
                except Exception as e:
                    pass
            if "AngleSlicesToPlot" in curr_sec:
                try:
                    self.angle_slices_to_plot = np.array(curr_sec["AngleSlicesToPlot"], dtype=float)
                except Exception as e:
                    pass
            if "GridColsPerRow" in curr_sec:
                self.grid_cols_per_row = int(np.array(curr_sec["GridColsPerRow"])[0])

    def buildup(self):

        MAX_RANGE_BINS = 192
        MAX_AGGREGATED_FRAMES = 4
        BYTES_PER_FLOAT = 4

        # + 50_000 to make sure theres space
        self.shm_blocksize = len(self.az_beam_angles) * self.fft_size * MAX_RANGE_BINS * MAX_AGGREGATED_FRAMES * BYTES_PER_FLOAT + 50_000
        
        self.shm_numblocks = 10 # a lot of blocks to speed up playback loading

        # put verbose=False when released
        self.sharedmem_sender = SharedMemSender(self.shm_blocksize, self.shm_numblocks, verbose=True)

        closesig_file = tempfile.NamedTemporaryFile(prefix="x7_run_", delete=False)
        self.close_path = closesig_file.name
        closesig_file.close()

        # start plotting process
        worker_script = str(Path(__file__).resolve().parent / "beamedRD_procrunner.py")
        self.plotting_process = subprocess.Popen([
            sys.executable,  # Use the same Python executable
            worker_script,
            self.sharedmem_sender.sharedmem.name,
            f"{self.shm_blocksize}",
            f"{self.shm_numblocks}",
            self.close_path
        ], stdout=subprocess.PIPE, stderr=None, text=True, bufsize=1)

        for line in self.plotting_process.stdout:
            if line.strip() == "PLOTTING_PROCESS_READY":
                break

        param_dict = {
            "fps" : self.fps,
            "fft_size" : self.fft_size,
            "range_offset" : self.range_offset,
            "bin_length" : self.bin_length,
            "num_frames_in_pd" : self.num_frames_in_pd,
            "frames_between_pd" : self.frames_between_pd,
            "num_saved_frames" : self.num_saved_frames,
            "enable_dc_removal" : self.enable_dc_removal,
            "is_live" : self.is_live,
            "default_start_range" : DEFAULT_START_RANGE,
            "az_beam_angles" : self.az_beam_angles,
            "range_slices_to_plot" : self.range_slices_to_plot,
            "doppler_slices_to_plot" : self.doppler_slices_to_plot,
            "angle_slices_to_plot" : self.angle_slices_to_plot,
            "grid_cols_per_row" : self.grid_cols_per_row
        }

        if hasattr(self, "power_lim_vec"):
            if self.power_lim_vec.size == 2:
                param_dict["power_lim_vec"] = self.power_lim_vec

        if hasattr(self, "range_lim_vec"):
            if self.range_lim_vec.size == 2:
                param_dict["range_lim_vec"] = self.range_lim_vec

        if hasattr(self, "doppler_lim_vec"):
            if self.doppler_lim_vec.size == 2:
                param_dict["doppler_lim_vec"] = self.doppler_lim_vec

        if hasattr(self, "angle_lim_vec"):
            if self.angle_lim_vec.size == 2:
                param_dict["angle_lim_vec"] = self.angle_lim_vec

        self.send_data(param_dict)

    def send_data(self, data):
        max_wait = 2
        now = time.time()
        while not self.sharedmem_sender.send_data(data): # busy wait for max speed for huge playback files
            if time.time() - now > max_wait:
                print("Shared memory sender timed out, exiting process")
                self.teardown()
                return

    def extract_rangedoppler_data(self, frame):

        self.current_data = np.asarray(
            frame[SIGNAL_SEMANTIC_RANGEDOPPLER][ARRAY_SEMANTIC_RANGEDOPPLERPOWER_4D])[0]
    
        self.current_data = 10 * np.log10(self.current_data + 1e-12)

        # make setup info
        rd_setup = MultiRDSetup(
            fps              = self.fps,
            fft_size         = self.fft_size,
            range_offset     = self.range_offset,
            bin_length       = self.bin_length,
        )

        # make the full data struct
        # no need to put in the setup info every single time, but compared to the size of the total data
        # and total processing the info struct is insignificant
        rd_plot_data = MultiRDPlotData(
            multi_rd_setup=rd_setup,
            rd_data=self.current_data,
            timestamp=frame.timestamp,
            seq_num=frame.sequence_number
        )

        # Store for later use and return
        self.rd_plot_data = rd_plot_data
        return rd_plot_data

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
            self.extract_rangedoppler_data(frame)
            self.send_data(self.rd_plot_data)

        return None, psf.ProcessResult.Continue