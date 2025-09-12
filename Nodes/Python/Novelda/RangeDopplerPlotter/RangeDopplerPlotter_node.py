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
from RangeDopplerPlotter.RangeDopplerPlotter_plotter import *

SIGNAL_SEMANTIC_RANGEDOPPLER = "rangedoppler"
ARRAY_SEMANTIC_RANGEDOPPLER_POWER_AGGREGATED_RAWCHANNELS = "rangedoppler_power_aggregated_rawchannels"
ARRAY_SEMANTIC_RANGEDOPPLER_IQ_AGGREGATED_RAWCHANNELS = "rangedoppler_iq_aggregated_rawchannels"
ARRAY_SEMANTIC_RADAR_TRXMASK = "radar_trx_mask"

DEFAULT_START_RANGE = 0.4  # meters

class RangeDopplerPlotter:
    def __init__(self, *_):
        self.initialized = False

        self.plot_linear_scale = False

        self.num_frames_in_pd = 0
        self.frames_between_pd = 0
        self.fps = 1
        self.enable_dc_removal = False

        self.z_lim_vec = np.array([-70.0, 10.0])
        self.num_saved_frames = -1  # all

    def set_parameters(self, context, params, sections):
        for section in sections:
            if section not in params:
                continue
            curr_sec = params[section]

            if "FPS" in curr_sec:
                self.fps = float(np.array(curr_sec["FPS"])[0])
            if "FFTSize" in curr_sec:
                self.fft_size = int(np.array(curr_sec["FFTSize"])[0])
            if "ZLimVec" in curr_sec:
                newzlim = np.array(curr_sec["ZLimVec"])
                if newzlim.size == 2:
                    self.z_lim_vec = newzlim
            if "RangeOffset" in curr_sec:
                self.range_offset = float(np.array(curr_sec["RangeOffset"])[0])
            if "BinLength" in curr_sec:
                self.bin_length = float(np.array(curr_sec["BinLength"])[0])
            if "Convert2Pwr" in curr_sec:
                self.convert2pwr = np.array(curr_sec["Convert2Pwr"], dtype=bool)[0]
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
            if "XLimVec" in curr_sec:
                newxlim = np.array(curr_sec["XLimVec"])
                if newxlim.size == 2:
                    self.x_lim_vec = newxlim
            if "YLimVec" in curr_sec:
                newylim = np.array(curr_sec["YLimVec"])
                if newylim.size == 2:
                    self.y_lim_vec = newylim
                
    def buildup(self):

        MAX_RANGE_BINS = 192
        MAX_AGGREGATED_FRAMES = 4
        BYTES_PER_FLOAT = 4

        # + 50_000 to make sure theres space
        self.shm_blocksize = self.fft_size * MAX_RANGE_BINS * MAX_AGGREGATED_FRAMES * BYTES_PER_FLOAT + 50_000
        
        self.shm_numblocks = 10 # a lot of blocks to speed up playback loading
        self.convert2pwr = True

        # put verbose=False when released
        self.sharedmem_sender = SharedMemSender(self.shm_blocksize, self.shm_numblocks, verbose=True)

        closesig_file = tempfile.NamedTemporaryFile(prefix="x7_run_", delete=False)
        self.close_path = closesig_file.name
        closesig_file.close()

        # start plotting process
        worker_script = str(Path(__file__).resolve().parent / "x7plotting_proc_runner.py")
        self.plotting_process = subprocess.Popen([
            sys.executable,  # Use the same Python executable
            worker_script,
            self.sharedmem_sender.sharedmem.name,
            f"{self.shm_blocksize}",
            f"{self.shm_numblocks}",
            self.close_path
        ], stdout=None, stderr=None, text=True, bufsize=1)

        param_dict = {
            "fps" : self.fps,
            "fft_size" : self.fft_size,
            "range_offset" : self.range_offset,
            "bin_length" : self.bin_length,
            "convert2pwr" : self.convert2pwr,
            "num_frames_in_pd" : self.num_frames_in_pd,
            "frames_between_pd" : self.frames_between_pd,
            "num_saved_frames" : self.num_saved_frames,
            "enable_dc_removal" : self.enable_dc_removal,
            "is_live" : self.is_live,
            "default_start_range" : DEFAULT_START_RANGE
        }

        if hasattr(self, "z_lim_vec"):
            if self.z_lim_vec.size == 2:
                param_dict["z_lim_vec"] = self.z_lim_vec

        if hasattr(self, "x_lim_vec"):
            if self.x_lim_vec.size == 2:
                param_dict["x_lim_vec"] = self.x_lim_vec

        if hasattr(self, "y_lim_vec"):
            if self.y_lim_vec.size == 2:
                param_dict["y_lim_vec"] = self.y_lim_vec

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

        if self.convert2pwr:
            self.current_data = np.asarray(
                frame[SIGNAL_SEMANTIC_RANGEDOPPLER][ARRAY_SEMANTIC_RANGEDOPPLER_POWER_AGGREGATED_RAWCHANNELS]
            )
        else:
            self.current_data = np.asarray(
                frame[SIGNAL_SEMANTIC_RANGEDOPPLER][ARRAY_SEMANTIC_RANGEDOPPLER_IQ_AGGREGATED_RAWCHANNELS]
            )

        trx_mask = np.asarray(
            frame[SIGNAL_SEMANTIC_RANGEDOPPLER][ARRAY_SEMANTIC_RADAR_TRXMASK]
        )

        self.num_tx_channels, self.num_rx_channels, self.num_bins_range, self.num_bins_doppler = self.current_data.shape

        # prepare container for per (physical_tx, rx) power matrices
        per_channel_data = {}

        for tx_loop in range(self.num_tx_channels):
            physical_tx = int(trx_mask[tx_loop, 1])  # already 0-based (assumption)

            for rx in range(self.num_rx_channels):
                rd_slice = self.current_data[tx_loop, rx, :, :]  # shape (range, doppler or doppler*2 for IQ)

                if not self.convert2pwr:
                    i_comp = rd_slice[:, 0::2]
                    q_comp = rd_slice[:, 1::2]
                    rd_slice = i_comp * i_comp + q_comp * q_comp
                    if rx == 0 and tx_loop == 0:  # adjust doppler bins once
                        self.num_bins_doppler = rd_slice.shape[1]

                if not self.plot_linear_scale:
                    rd_slice[rd_slice == 0] = 1e-16
                    rd_slice = 10 * np.log10(rd_slice)

                per_channel_data[(physical_tx, rx)] = rd_slice

        # make setup info
        rd_setup = RDRawSetup(
            num_tx_channels  = self.num_tx_channels,
            num_rx_channels  = self.num_rx_channels,
            num_bins_range   = self.num_bins_range,
            num_bins_doppler = self.num_bins_doppler,
            fps              = self.fps,
            fft_size         = self.fft_size,
            range_offset     = self.range_offset,
            bin_length       = self.bin_length,
            zlim_vec         = self.z_lim_vec,
            convert2pwr      = self.convert2pwr,
        )

        # make the full data struct
        # no need to put in the setup info every single time, but compared to the size of the total data
        # and total processing the info struct is insignificant
        rd_plot_data = RDRawPlotData(
            RDRawSetup=rd_setup,
            rd_dict_data=per_channel_data,
            trx_mask=trx_mask,
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