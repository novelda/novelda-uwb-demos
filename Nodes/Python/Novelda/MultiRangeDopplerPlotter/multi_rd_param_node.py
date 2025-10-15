from __future__ import annotations

import numpy as np

import PySignalFlow as psf

from Utils.semantics import *

class MultiRDParamNode:
    def __init__(self, *_):

        self.sent_parameters = False

        self.range_offset = 0.0
        self.bin_length = 0.0
        self.fps = 0.0
        self.fft_size = 0
        self.az_beam_angles = np.array([], dtype=float)
        self.convert2Pwr = False

    def set_parameters(self, context, params, sections):
        for section in sections:
            if section not in params:
                continue
            curr_sec = params[section]

            if "RangeOffset" in curr_sec:
                self.range_offset = float(np.array(curr_sec["RangeOffset"])[0])
            if "BinLength" in curr_sec:
                self.bin_length = float(np.array(curr_sec["BinLength"])[0])
            if "FPS" in curr_sec:
                self.fps = float(np.array(curr_sec["FPS"])[0])
            if "FFTSize" in curr_sec:
                self.fft_size = int(np.array(curr_sec["FFTSize"])[0])
            if "azBeamAngles" in curr_sec:
                self.az_beam_angles = np.array(curr_sec["azBeamAngles"], dtype=float)
            if "Convert2Pwr" in curr_sec:
                self.convert2Pwr = bool(np.array(curr_sec["Convert2Pwr"])[0])
                
    def buildup(self):
        self.param_vec = np.concatenate(
            (np.array([self.range_offset, self.bin_length, self.fps, float(self.convert2Pwr)], dtype=np.float32),
            self.az_beam_angles.astype(np.float32))
        )

    def teardown(self):
        pass

    def process(self, sf):

        timestamp = sf[0].timestamp
        sequence_number = sf[0].sequence_number

        data_arrsem = None

        if ARRAY_SEMANTIC_RANGEDOPPLERPOWER_4D in sf[0][SIGNAL_SEMANTIC_RANGEDOPPLER]:
            data_arrsem = ARRAY_SEMANTIC_RANGEDOPPLERPOWER_4D
        elif ARRAY_SEMANTIC_RANGEDOPPLERPOWER_IQ_4D in sf[0][SIGNAL_SEMANTIC_RANGEDOPPLER]:
            data_arrsem = ARRAY_SEMANTIC_RANGEDOPPLERPOWER_IQ_4D
        else:
            raise RuntimeError("Wrong signal/array semantic in frame")

        out = {
            "timestamp": timestamp,
            "sequence_number": sequence_number,
            "state_changes": [],
            "signals": {
                SIGSEM_RADAR_PARAMETERS: {
                    ARRSEM_RD_BEAM_PARAMS : self.param_vec
                },
                SIGNAL_SEMANTIC_RANGEDOPPLER: {
                    data_arrsem: np.array(sf[0][SIGNAL_SEMANTIC_RANGEDOPPLER][data_arrsem])
                }
            }
        }

        self.sent_parameters = True

        return out, psf.ProcessResult.Continue