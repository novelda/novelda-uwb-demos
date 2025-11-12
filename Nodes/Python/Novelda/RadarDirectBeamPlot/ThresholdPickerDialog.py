import numpy as np

from RadarDirectBeamPlot.ThresholdPicker_ui import *


class PickThreshDialog(QDialog, Ui_Dialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setupUi(self)
    
    def fill_thresh_ranges_values(self, ranges: np.ndarray, values: np.ndarray):
        ranges_str = ", ".join([f"{r:.2f}" for r in ranges])
        values_str = ", ".join([f"{v:.2f}" for v in values])

        self.threshAtRangesLEdit.setText(ranges_str)
        self.threshValuesLEdit.setText(values_str)