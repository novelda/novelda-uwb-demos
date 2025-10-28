
import numpy as np

class Presence2DHelper:
    def __init__(self):
        self.first_frame = False
        self.timestamp_0 = None
        self.timestamp = None
        self.sequence_number = None

    def new_human_presence_2d_data(self, sequence_number: int, timestamp: int, human2D_vector: np.ndarray):
        self.sequence_number = sequence_number
        self.timestamp = timestamp
        self.human2D_vector = human2D_vector

        if not self.first_frame:
            self.first_frame = True
            self.timestamp_0 = self.timestamp

    def get_sequence_number(self):
        return self.sequence_number

    def get_timestamp(self):
        return self.timestamp

    def get_time_since_start(self) -> float:
        return (self.timestamp - self.timestamp_0) / 1000.0

    def get_human2D_vector(self) -> np.ndarray:
        return self.human2D_vector

    def get_presence_state(self) -> bool:
        return bool(self.human2D_vector[0])

    def get_x_meters(self) -> float:
        return float(self.human2D_vector[1]/100.0)

    def get_y_meters(self) -> float:
        return float(self.human2D_vector[2]/100.0)

    def get_confidence(self) -> int:
        return int(self.human2D_vector[3])