from __future__ import annotations

import numpy as np

import PySignalFlow as psf

from Utils.semantics import *

class RadarDirectParamNode:
    def __init__(self, *_):

        self.sent_parameters = False

    def set_parameters(self, context, params, sections):
        for section in sections:
            if section not in params:
                continue
            curr_sec = params[section]

            if "RangeOffset" in curr_sec:
                self.range_offset = float(np.array(curr_sec["RangeOffset"])[0])
            if "BinLength" in curr_sec:
                self.bin_length = float(np.array(curr_sec["BinLength"])[0])
            if "RangeDecimation" in curr_sec:
                self.range_decimation = int(np.array(curr_sec["RangeDecimation"])[0])
                
    def buildup(self):
        pass

    def teardown(self):
        pass

    def process(self, sf):

        timestamp = sf[0].timestamp
        sequence_number = sf[0].sequence_number

        data_arrsem = None

        if ARRAY_SEMANTIC_BBIQ_FLOAT32 in sf[0][SIGNAL_SEMANTIC_RADAR_X7]:
            data_arrsem = ARRAY_SEMANTIC_BBIQ_FLOAT32
        elif ARRAY_SEMANTIC_RF_FLOAT32 in sf[0][SIGNAL_SEMANTIC_RADAR_X7]:
            data_arrsem = ARRAY_SEMANTIC_RF_FLOAT32

        out = {
            "timestamp": timestamp,
            "sequence_number": sequence_number,
            "state_changes": [],
            "signals": {
                SIGSEM_RADAR_PARAMETERS: {
                    ARRSEM_BIN_LENGTH: np.array([self.bin_length], dtype=np.float32),
                    ARRSEM_RANGE_OFFSET: np.array([self.range_offset], dtype=np.float32),
                    ARRSEM_RANGE_DECIMATION: np.array([self.range_decimation], dtype=np.int32),
                },
                SIGNAL_SEMANTIC_RADAR_X7: {
                    data_arrsem: np.array(sf[0][SIGNAL_SEMANTIC_RADAR_X7][data_arrsem]),
                    ARRAY_SEMANTIC_RADAR_TRXMASK: np.array(sf[0][SIGNAL_SEMANTIC_RADAR_X7][ARRAY_SEMANTIC_RADAR_TRXMASK]),
                }
            }
        }

        self.sent_parameters = True

        return out, psf.ProcessResult.Continue