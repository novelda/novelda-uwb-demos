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
from BasebandPlotter.BasebandPlotter_plotter import BasebandDataFrame

from Utils.semantics import *

class BasebandPlotter:
    def __init__(self, *_):
        self.initialized = False

        self.plot_linear_scale = False

        self.num_frames_in_pd = 0
        self.frames_between_pd = 0
        self.fps = 1
        self.enable_dc_removal = False
        self.plot_linear_scale = False
        self.is_live = True

        self.y_lim_vec = np.array([-70.0, 40.0])

    def set_parameters(self, context, params, sections):
        for section in sections:
            if section not in params:
                continue
            curr_sec = params[section]

            if "FPS" in curr_sec:
                self.fps = float(np.array(curr_sec["FPS"])[0])
            if "YLimVec" in curr_sec:
                try:
                    newylim = np.array(curr_sec["YLimVec"])
                    if newylim.size == 2:
                        self.y_lim_vec = newylim
                except Exception as e:
                    pass
            if "RangeOffset" in curr_sec:
                self.range_offset = float(np.array(curr_sec["RangeOffset"])[0])
            if "BinLength" in curr_sec:
                self.bin_length = float(np.array(curr_sec["BinLength"])[0])
            if "MaxBufferedFrames" in curr_sec:
                self.num_saved_frames = int(np.array(curr_sec["MaxBufferedFrames"])[0])
            if "IsLive" in curr_sec:
                self.is_live = np.array(curr_sec["IsLive"], dtype=bool)[0]
            if "XLimVec" in curr_sec:
                try:
                    newxlim = np.array(curr_sec["XLimVec"])
                    if newxlim.size == 2:
                        self.x_lim_vec = newxlim
                except Exception as e:
                    pass
            if "TxChannelSequence" in curr_sec:
                self.tx_channel_sequence = np.array(curr_sec["TxChannelSequence"], dtype=int)
            if "RxMaskSequence" in curr_sec:
                self.rx_mask_sequence = np.array(curr_sec["RxMaskSequence"], dtype=int)
            if "PlotLinearScale" in curr_sec:
                self.plot_linear_scale = np.array(curr_sec["PlotLinearScale"], dtype=bool)[0]
            if "DCRemoval" in curr_sec:
                self.enable_dc_removal = np.array(curr_sec["DCRemoval"], dtype=bool)[0]
                
    def buildup(self):

        self.shm_blocksize = 1_000_000 # change later to a more dynamic size
        self.shm_numblocks = 20 # to be able to keep up with high fps

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
        ], stdout=subprocess.PIPE, stderr=None, text=True, bufsize=1)

        for line in self.plotting_process.stdout:
            if line.strip() == "PLOTTING_PROCESS_READY":
                break
            
        param_dict = {
            "fps" : self.fps,
            "range_offset" : self.range_offset,
            "bin_length" : self.bin_length,
            "num_saved_frames" : self.num_saved_frames,
            "is_live" : self.is_live,
            "plot_linear_scale" : self.plot_linear_scale,
            "enable_dc_removal" : self.enable_dc_removal,
            "default_start_range" : 0.4
        }

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
            
            trx_mask = np.asarray(frame[SIGNAL_SEMANTIC_RADAR_X7][ARRAY_SEMANTIC_RADAR_TRXMASK])[0]

            chipnum, txactive, rxmask = trx_mask

            # determine type
            data = None
            iscomplex = False
            if ARRAY_SEMANTIC_BBIQ_FLOAT32 in frame[SIGNAL_SEMANTIC_RADAR_X7]:
                data = np.asarray(frame[SIGNAL_SEMANTIC_RADAR_X7][ARRAY_SEMANTIC_BBIQ_FLOAT32])
                iscomplex = True
            elif ARRAY_SEMANTIC_RF_FLOAT32 in frame[SIGNAL_SEMANTIC_RADAR_X7]:
                data = np.asarray(frame[SIGNAL_SEMANTIC_RADAR_X7][ARRAY_SEMANTIC_RF_FLOAT32])
            else:
                raise RuntimeError("There is no data in the radar frame.")

            # construct output dict
            # (chipnum, txactive, rxactive) -> data
            out_dict = {}
            for rx in [1, 2]:

                rx_active = None

                if rxmask & rx:
                    rx_active = rx-1
                else:
                    continue

                if iscomplex:
                    out_dict[(chipnum, txactive, rx_active)] = \
                        np.abs(data[rx_active, 0, :] + 1j * data[rx_active, 1, :])
                else:
                    print("IF data plotting not supported")
            
            bbframe = BasebandDataFrame(
                power_data_dict=out_dict,
                db_data_dict={},
                trx_vec=trx_mask,
                timestamp=frame.timestamp,
                seq_num=frame.sequence_number
            )

            self.send_data(bbframe)


        return None, psf.ProcessResult.Continue