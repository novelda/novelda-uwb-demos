from dataclasses import dataclass
from enum import IntEnum
import numpy as np
import pyqtgraph as pg

class HumanPresence2DIdx(IntEnum):
    STATE_IDX = 0
    X_IDX = 1
    Y_IDX = 2
    CONFIDENCE_IDX = 3

class DetectionZone:
    def __init__(self, xy_array: np.ndarray) -> None:
        self.xy_array = xy_array
        self.plot_item: pg.PlotDataItem = None

class Pres2dData:
    def __init__(self, data: np.ndarray, plot_item: pg.PlotDataItem, timestamp: float):
        self.data = data
        self.plot_item = plot_item
        self.timestamp = timestamp

        self.x = self.data[HumanPresence2DIdx.X_IDX] / 100
        self.y = self.data[HumanPresence2DIdx.Y_IDX] / 100
        self.state_int16 = self.data[HumanPresence2DIdx.STATE_IDX]
        self.confidence = self.data[HumanPresence2DIdx.CONFIDENCE_IDX]

        self.inside_state = self.state_int16 & 255
        self.zone_num = self.state_int16 >> 8

@dataclass
class Presence2DDataFrame:
    new_timestamp_seqnum_tag_in: dict[str, float]
    human_presence: np.ndarray
    human_detections2d: np.ndarray
    power_per_bin: np.ndarray
    detection2d: np.ndarray