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
from Presence2DPlotter.presence_types import Presence2DDataFrame

from Utils.fnv1a_py import fnv1a_py

class Presence2DPlotter:
    def __init__(self, *_):
        self.initialized = False

        self.plot_linear_scale = False

        self.num_frames_in_pd = 0
        self.frames_between_pd = 0
        self.fps = 0
        self.enable_dc_removal = False
        self.plot_linear_scale = False
        self.is_live = True


        self.DetZoneXYPoints_performance = None
        self.DetZoneIndexBuffer_performance = None
        self.ConfidenceValues_performance = None
        self.OutputTag = None

        self.DetZoneXYPoints_lowpower = None
        self.DetZoneIndexBuffer_lowpower = None
        self.ConfidenceValues_lowpower = None
        self.OutputTag_lowpower = None

        self.CurrentPowerMode = None
        self.plotUpdateFrequency = 1
        self.plotUpdateCounter = 0
        self.maxDets = 10
        self.XYPlot_XLim = [-6.468, 6.648]
        self.XYPlot_YLim = [0, 6]
        self.Range_YLim = [0, 6]
        self.maxHistory = 100
        self.xytrail = 0
        self.AzimRotation_deg = None
        self.FOV_deg = None
        self.dFOVlines_deg = None
        self.COV_deg = None
        self.dCOV_deg = None
        self.Rmax_m = None
        self.dR_rings = None
        self.with_dbg_plot = False

        self.thresh_range_vec = None
        self.noise_floor_val = None
        self.ylim_dB = (-80, 20)
        self.thr_snr_vec = None
        self.thresh_level_adjust = 1.0

        self.MaxBufferedFrames = -1

        self.sigsem_human_pres = "human_presence"
        self.human_presence_arrsem = "human_presence_2d_basic"
        self.detection2d_arrsem = "human_detection_2d_float"

        self.power_per_bin_sigsem = "cluster"
        self.power_per_bin_arrsem = "PowerPerBin"
        self.thresh_data_arrsem = "detection_2d"

        self.new_timestamp_seqnum_tag_in_dict = None
        self.human_presence = None
        self.human_detections2d = None
        self.power_per_bin = None
        self.detection2d = None

        self.RangeLimVec = None
        self.PowerLimVec = None
        self.RadarMode = 0

        self.MaxHistoryTimeplotsInS = 300

    def set_parameters(self, context, params, sections):

        for section in sections:
            if section not in params:
                continue
            curr_sec = params[section]

            for k in ("ShowFOVLines", "ShowXYCoordinates", "HighlightDetection", "InvertedTopView", "TrailBackwardSeconds", "TrailForwardSeconds", "MaxBufferedFrames"):
                if k in curr_sec:
                    val = np.array(curr_sec[k]).flatten()
                    setattr(self, k, val[0] if len(val) == 1 else val)

            if section != fnv1a_py("ULPP2D.lowpower"):

                if "RangeLimVec" in curr_sec:
                    try:
                        newxlim = np.array(curr_sec["RangeLimVec"])
                        if newxlim.size == 2:
                            self.RangeLimVec = newxlim
                    except Exception as e:
                        pass
                
                if "PowerLimVec" in curr_sec:
                    try:
                        newxlim = np.array(curr_sec["PowerLimVec"])
                        if newxlim.size == 2:
                            self.PowerLimVec = newxlim
                    except Exception as e:
                        pass

                if "DetectionZoneXYPoints" in curr_sec:
                    self.DetZoneXYPoints_performance = np.array(curr_sec["DetectionZoneXYPoints"]).flatten()

                if "DetectionZoneXYIndexBuffer" in curr_sec:
                    self.DetZoneIndexBuffer_performance = np.array(curr_sec["DetectionZoneXYIndexBuffer"]).flatten()

                if "ConfidenceValues" in curr_sec:
                    self.ConfidenceValues_performance = np.array(curr_sec["ConfidenceValues"]).flatten()

                if "OutputTag" in curr_sec:
                    self.OutputTag = np.array(curr_sec["OutputTag"]).flatten()[0]

            else:

                if "DetectionZoneXYPoints" in curr_sec:
                    self.DetZoneXYPoints_lowpower = np.array(curr_sec["DetectionZoneXYPoints"]).flatten()

                if "DetectionZoneXYIndexBuffer" in curr_sec:
                    self.DetZoneIndexBuffer_lowpower = np.array(curr_sec["DetectionZoneXYIndexBuffer"]).flatten()

                if "ConfidenceValues" in curr_sec:
                    self.ConfidenceValues_lowpower = np.array(curr_sec["ConfidenceValues"]).flatten()

                if "OutputTag" in curr_sec:
                    self.OutputTag_lowpower = np.array(curr_sec["OutputTag"]).flatten()[0]

            if "FPS" in curr_sec:
                self.fps = np.array(curr_sec["FPS"]).flatten()[0]

            if "IsLive" in curr_sec:
                self.is_live = np.array(curr_sec["IsLive"]).flatten()[0]

            if "CurrentPowerMode" in curr_sec:
                self.CurrentPowerMode = np.array(curr_sec["CurrentPowerMode"]).flatten()[0]

            if "PlotUpdateFrequency" in curr_sec:
                self.plotUpdateFrequency = np.array(curr_sec["PlotUpdateFrequency"]).flatten()[0]

            if "MaxDetections" in curr_sec:
                self.maxDets = np.array(curr_sec["MaxDetections"]).flatten()[0]

            if "XYPlot_XLim" in curr_sec:
                self.XYPlot_XLim = np.array(curr_sec["XYPlot_XLim"]).flatten()

            if "XYPlot_YLim" in curr_sec:
                self.XYPlot_YLim = np.array(curr_sec["XYPlot_YLim"]).flatten()

            if "Range_YLim" in curr_sec:
                self.Range_YLim = np.array(curr_sec["Range_YLim"]).flatten()

            if "MaxHistoryTimeplotsInS" in curr_sec:
                self.MaxHistoryTimeplotsInS = np.array(curr_sec["MaxHistoryTimeplotsInS"]).flatten()[0]

            if "XYTrail" in curr_sec:
                self.xytrail = np.array(curr_sec["XYTrail"]).flatten()[0]

            if "AzimRotation_deg" in curr_sec:
                self.AzimRotation_deg = np.array(curr_sec["AzimRotation_deg"]).flatten()[0]

            if "FOV_deg" in curr_sec:
                self.FOV_deg = np.array(curr_sec["FOV_deg"]).flatten()[0]

            if "dFOVlines_deg" in curr_sec:
                self.dFOVlines_deg = np.array(curr_sec["dFOVlines_deg"]).flatten()[0]

            if "Rmax_m" in curr_sec:
                self.Rmax_m = np.array(curr_sec["Rmax_m"]).flatten()[0]

            if "dR_rings" in curr_sec:
                self.dR_rings = np.array(curr_sec["dR_rings"]).flatten()[0]

            if "WithDebugPlot" in curr_sec:
                self.with_dbg_plot = np.array(curr_sec["WithDebugPlot"]).flatten()[0]

            if "ThrRangeVecBin" in curr_sec:
                self.thresh_range_vec = np.array(curr_sec["ThrRangeVecBin"]).flatten().astype(float)

            if "MaxAbsNoiseFloorVal" in curr_sec:
                self.noise_floor_val = np.array(curr_sec["MaxAbsNoiseFloorVal"]).flatten().astype(float)[0]

            if "YLim_dB" in curr_sec:
                self.ylim_dB = np.array(curr_sec["YLim_dB"]).flatten().astype(float)

            if "ThrSNR_Power" in curr_sec:
                self.thr_snr_vec = np.array(curr_sec["ThrSNR_Power"]).flatten().astype(float)

            if "ThresholdLevelAdjustment_Linear" in curr_sec:
                self.thresh_level_adjust = np.array(curr_sec["ThresholdLevelAdjustment_Linear"]).flatten().astype(float)[0]
            
            if "MframesPerPulse" in curr_sec:
                self.MframesPerPulse = np.array(curr_sec["MframesPerPulse"]).flatten()[0]

            if "DefaultMiddlePlot" in curr_sec:
                self.DefaultMiddlePlot = curr_sec["DefaultMiddlePlot"].values[0]
            
            if "Mode" in curr_sec:
                self.RadarMode = np.array(curr_sec["Mode"])[0]


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
        
        if self.RadarMode == fnv1a_py("Autonomous"):
            self.fps /= 2

        add_detection_zones_from_buffer_dict = {
            "xybuffer_performance" : self.DetZoneXYPoints_performance,
            "xy_index_buffer_performance" : self.DetZoneIndexBuffer_performance,
            "xybuffer_lowpower" : self.DetZoneXYPoints_lowpower,
            "xy_index_buffer_lowpower" : self.DetZoneIndexBuffer_lowpower
        }
        draw_fow_lines_with_tags_dict = {
            "rmax" : self.Rmax_m,
            "d_range" : self.dR_rings,
            "d_angle" : self.dFOVlines_deg,
            "angle_min" : -self.FOV_deg,
            "angle_max" : self.FOV_deg
        }
        json_settings_dict = {
            "show_fov_lines": self.ShowFOVLines if hasattr(self, 'ShowFOVLines') else True,
            "show_xy_coordinates": self.ShowXYCoordinates if hasattr(self, 'ShowXYCoordinates') else True,
            "highlight_detection": self.HighlightDetection if hasattr(self, 'HighlightDetection') else True,
            "inverted_top_view": self.InvertedTopView if hasattr(self, 'InvertedTopView') else False,
            "trail_backward_seconds": self.TrailBackwardSeconds if hasattr(self, 'TrailBackwardSeconds') else 1.0,
            "trail_forward_seconds": self.TrailForwardSeconds if hasattr(self, 'TrailForwardSeconds') else 1.0,
            "DefaultMiddlePlot": self.DefaultMiddlePlot if hasattr(self, 'DefaultMiddlePlot') else "Range",
            "m_frames_per_pulse": self.MframesPerPulse if hasattr(self, 'MframesPerPulse') else 12,
            "MaxHistoryTimeplotsInS" : float(self.MaxHistoryTimeplotsInS),
        }

        param_dict = {
            "fps" : self.fps,
            "is_live" : self.is_live,
            "plot_linear_scale" : self.plot_linear_scale,
            "enable_dc_removal" : self.enable_dc_removal,
            "default_start_range" : 0.0,

            "max_history" : self.xytrail,
            "MaxBufferedFrames" : self.MaxBufferedFrames,
            "confidence_values_performance" : self.ConfidenceValues_performance,
            "confidence_values_lowpower" : self.ConfidenceValues_lowpower,
            "top_view" : self.AzimRotation_deg != 0,
            "xy_xlims" : self.XYPlot_XLim,
            "xy_ylims" : self.XYPlot_YLim,
            "current_power_mode" : self.CurrentPowerMode,
            "output_tag" : self.OutputTag,
            "output_tag_lowpower" : self.OutputTag_lowpower,
            "with_dbg_plot" : self.with_dbg_plot,
            "thresh_range_vec" : self.thresh_range_vec,
            "noise_floor_val" : self.noise_floor_val, #stipla linje i bunn
            "RangeLimVec" : self.RangeLimVec,
            "PowerLimVec" : self.PowerLimVec,
            "thr_snr_vec" : self.thr_snr_vec,
            "thresh_level_adjust" : self.thresh_level_adjust,

            "add_detection_zones_from_buffer": add_detection_zones_from_buffer_dict,
            "draw_fow_lines_with_tags": draw_fow_lines_with_tags_dict,
            "json_settings": json_settings_dict,
        }

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

            #self.plotter.new_timestamp_seqnum_tag_in(frame.timestamp, frame.sequence_number, frame.tag)
            self.new_timestamp_seqnum_tag_in_dict = {
                "timestamp": frame.timestamp,
                "sequence_number": frame.sequence_number,
                "tag": frame.tag
            }

            if self.sigsem_human_pres in frame:

                if self.human_presence_arrsem in frame[self.sigsem_human_pres]:
                    self.human_presence = np.array(frame[self.sigsem_human_pres][self.human_presence_arrsem]).flatten()

                if self.detection2d_arrsem in frame[self.sigsem_human_pres]:
                    self.human_detections2d = np.array(frame[self.sigsem_human_pres][self.detection2d_arrsem])

            if self.power_per_bin_sigsem in frame:
                if self.power_per_bin_arrsem in frame[self.power_per_bin_sigsem]:
                    self.power_per_bin = 5*np.log10(np.array(frame[self.power_per_bin_sigsem][self.power_per_bin_arrsem]))
                if self.thresh_data_arrsem in frame[self.power_per_bin_sigsem]:
                    self.detection2d = np.array(frame[self.power_per_bin_sigsem][self.thresh_data_arrsem]).flatten().astype(float)
        
        # Send data frame if all required data is present
        if (self.human_presence is not None and 
        self.human_detections2d is not None and 
        self.power_per_bin is not None and 
        self.detection2d is not None):

            p2dframe = Presence2DDataFrame(
                new_timestamp_seqnum_tag_in=self.new_timestamp_seqnum_tag_in_dict,
                human_presence=self.human_presence.flatten(),
                human_detections2d=self.human_detections2d.flatten(),
                power_per_bin=self.power_per_bin.flatten().astype(float),
                detection2d=self.detection2d
            )

            self.send_data(p2dframe)

            # reset
            self.human_presence = None
            self.human_detections2d = None
            self.power_per_bin = None
            self.detection2d = None

        return None, psf.ProcessResult.Continue