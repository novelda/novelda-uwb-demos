from __future__ import annotations

import time
import numpy as np
from dataclasses import dataclass
from pathlib import Path
from enum import IntEnum
import json

import pyqtgraph as pg

from pyqtgraph.Qt.QtWidgets import (
    QMainWindow, QWidget, QGridLayout, QVBoxLayout, QHBoxLayout, QLabel, QSlider, QLineEdit,
    QPushButton, QApplication, QCheckBox, QDialog, QFileDialog
    )
from pyqtgraph.Qt.QtGui import QDoubleValidator, QIcon, QImage, QPalette, QColor
import pyqtgraph.Qt.QtCore as QtCore

from RadarDirectBeamPlot.RadarDirectBeamPlotui import Ui_multiRangeDoppWin
from RadarDirectBeamPlot.xy_beam_plotw import XYBeamPlotWidget

from BasebandPlotter.xy_plot_widget import XY2DPlotWidget
from MultiRangeDopplerPlotter.add_plot_dialog import AddPlotDialog
from RadarDirectBeamPlot.ThresholdPickerDialog import PickThreshDialog

@dataclass
class RadarDirectBeamData:
    power_beam_data: np.ndarray
    timestamp      : float
    seq_num        : int

class KeyPressFilter(QtCore.QObject):
    def __init__(self, callback):
        super().__init__()
        self._callback = callback

    def eventFilter(self, obj, event: pg.QtGui.QKeyEvent):

        if event.type() == QtCore.QEvent.KeyPress:
            fw = QApplication.focusWidget()
            if isinstance(fw, QLineEdit) and event.key() in (QtCore.Qt.Key_Left, QtCore.Qt.Key_Right):
                return False  # do not handle; let the line edit move the caret
            return self._callback(event)

        return False

class PlotMainWin(QMainWindow):

    def __init__(self, on_close_func):
        self.on_close_func = on_close_func
        super().__init__()

        icon_fp = Path(__file__).resolve().parent.parent.parent.parent.parent / "Demos" \
            / "Resources" / "Images" / "cropped-NOVELDA-icon-192x192.png"

        icon = QIcon(str(icon_fp))
        self.setWindowIcon(icon)
        

    def closeEvent(self, event):
        self.on_close_func()
        event.accept()

class LimitEditLineHelper:
    def __init__(self, ledit_min: QLineEdit, ledit_max: QLineEdit, default_min, default_max, validator, callback_func):
        self.ledit_min = ledit_min
        self.ledit_max = ledit_max
        self.default_min = default_min
        self.default_max = default_max
        self.validator = validator
        self.callback_func = callback_func
        self.ledit_min.setValidator(validator)
        self.ledit_max.setValidator(validator)

        self.last_min_valid_text = str(default_min)
        self.last_max_valid_text = str(default_max)

        self.ledit_min.returnPressed.connect(self.val_edited)
        self.ledit_max.returnPressed.connect(self.val_edited)

        self.ledit_min.setText(self.last_min_valid_text)
        self.ledit_max.setText(self.last_max_valid_text)

    def val_edited(self):

        if self.ledit_min.text() != self.last_min_valid_text or self.ledit_max.text() != self.last_max_valid_text:
            min_val = float(self.ledit_min.text())
            max_val = float(self.ledit_max.text())
            if min_val >= max_val:
                # revert both
                self.ledit_min.setText(self.last_min_valid_text)
                self.ledit_max.setText(self.last_max_valid_text)
                return
            self.last_min_valid_text = self.ledit_min.text()
            self.last_max_valid_text = self.ledit_max.text()
            self.callback_func(min_val, max_val)
    
    def reset(self):
        mintext = f"{self.default_min:.2f}"
        maxtext = f"{self.default_max:.2f}"
        self.ledit_min.setText(mintext)
        self.ledit_max.setText(maxtext)
        self.last_min_valid_text = mintext
        self.last_max_valid_text = maxtext
        self.callback_func(self.default_min, self.default_max)

class RadarDirectBeamPlotter(Ui_multiRangeDoppWin):

    def __init__(self, shm_on_exit=None):
        self.plot = None
        self.plot_linear_scale: bool       = False
        self.shm_on_exit = shm_on_exit

        self.range_axis_values: np.ndarray = None
        self.doppler_axis_values: np.ndarray = None
        self.power_lim_vec: np.ndarray = None
        
        self.rd_plot_data: RadarDirectBeamData = None

        self.app = None
        self.initialized = False

        self._key_filter = None
        self.mwin = None

        self.num_saved_frames = 10_000

        self.paused = False
        self.curr_data_frame_inx = 0
        self.curr_label_frame_max = 0

        self.first_setup_dict = None
        self.first_timestamp = None
        self.is_live = True

        # timestamp received : RDRawPlotData
        self.rd_plot_data_buffer: list[RadarDirectBeamData] = []

        self.num_bins_range = 0

        self.limits_ledit_text: dict[QLineEdit, str] = {}

        self.const_range_start = None

        self.is_single_angle = False

        self.frame_received_counter = 0
        self.frame_dropped_counter = 0

        self._thresh_line_key = -1

        self._angle_slices = []
        self._range_slices = []

        self.color_map_range = np.array([-60.0, 20.0])
        self.beam_sector_width_deg = 20.0

        self._buff_for_beam_thresh: np.ndarray = None
        
        from PySide6.QtCore import QLocale
        QLocale.setDefault(QLocale(QLocale.English, QLocale.UnitedStates))

        logo_img_fp = Path(__file__).resolve().parent.parent.parent.parent.parent / "Demos" \
            / "Resources" / "Images" / "Novelda_logo_hvit_150dpi.png"
        self.logo_img = QImage(str(logo_img_fp))

    def init_window(self):
        if self.app is None:
            self.app = QApplication([])
        if self.mwin is not None:
            return
        
        self.app.setStyle('Fusion')
        pal = QPalette()
        base_bg = QColor("#3A3E44")   # window/background
        alt_bg  = QColor("#2A2D30")   # alternate
        text_fg = QColor('#E6E6E6')   # text/fg

        pal.setColor(QPalette.Window, base_bg)
        pal.setColor(QPalette.Base, base_bg)
        pal.setColor(QPalette.AlternateBase, alt_bg)
        pal.setColor(QPalette.Button, base_bg)
        pal.setColor(QPalette.ToolTipBase, base_bg)

        pal.setColor(QPalette.WindowText, text_fg)
        pal.setColor(QPalette.Text, text_fg)
        pal.setColor(QPalette.ButtonText, text_fg)
        pal.setColor(QPalette.ToolTipText, text_fg)

        pal.setColor(QPalette.Disabled, QPalette.WindowText, QColor('#8C8C8C'))
        pal.setColor(QPalette.Disabled, QPalette.Text,       QColor('#8C8C8C'))
        pal.setColor(QPalette.Disabled, QPalette.ButtonText, QColor('#8C8C8C'))
        pal.setColor(QPalette.Disabled, QPalette.Base,       QColor('#2E3238'))
        pal.setColor(QPalette.Disabled, QPalette.Button,     QColor('#2E3238'))

        self.app.setPalette(pal)

        self.mwin = PlotMainWin(self.exit)

        self.setupUi(self.mwin)
        self.mwin.setWindowTitle("RadarDirect Beamforming")

        self.mwin.setFocusPolicy(QtCore.Qt.ClickFocus)
        self.centralwidget.setFocusPolicy(QtCore.Qt.ClickFocus)

        self.hotkeyLabel.setText(("Space: play/pause"
                                   "\nLeft/Right Arrow: change current plot"
                                   "\nClick on plot: place plot marker"
                                   "\nR: reset limits"
                                   "\nA/D: move plot marker")
                                    )

        self.logoLabel.setPixmap(pg.QtGui.QPixmap.fromImage(self.logo_img).scaledToWidth(100, QtCore.Qt.SmoothTransformation))

        self.resetLimitsBtn.released.connect(self.reset_limits)

        self.currFrameLEdit.returnPressed.connect(self.frame_edited)

        self.choose_plots_dialog = None

        screen_size = self.app.primaryScreen().size()
        best_ar = 16/10
        self.mwin.resize(int(screen_size.height()*best_ar), int(screen_size.height()*0.9))
        self.mwin.move(0, 0)
        self.mwin.show()

        self.centralwidget.setFocus()

        if self._key_filter is None:
            self._key_filter = KeyPressFilter(self.keyPressEvent)
            self.app.installEventFilter(self._key_filter)
        
        self.beam_plotter = XYBeamPlotWidget(
            color_min=-60.0,
            color_max=20.0
        )

        self.range_baseband_plot = XY2DPlotWidget(
            x_axis_name="Range",
            y_axis_name="Power",
            xaxis_unit="m",
            y_axis_unit="dB",
            plot_label="Range",
            xrange=(-1, 10),
            yrange=(-60, 40),
            xmark_prefix="Rangebin ",
            ymark_prefix=None,
            plot_mark_prefix=None
        )

        self.range_baseband_plot.legend.anchor((1,1), (1,1), offset=(-5, 10))

        self.angle_baseband_plot = XY2DPlotWidget(
            x_axis_name="Angle",
            y_axis_name="Power",
            xaxis_unit="deg",
            y_axis_unit="dB",
            plot_label="Angle",
            xrange=(-90, 90),
            yrange=(-60, 40),
            xmark_prefix="Angle ",
            ymark_prefix=None,
            plot_mark_prefix=None
        )
        self.angle_baseband_plot.legend.anchor((1,1), (1,1), offset=(-5, 10))

        self.plotGridLayout.addWidget(self.beam_plotter, 0, 0, 1, 2)
        self.plotGridLayout.addWidget(self.range_baseband_plot, 1, 0)
        self.plotGridLayout.addWidget(self.angle_baseband_plot, 1, 1)
        self.plotGridLayout.setRowStretch(0, 2)
        self.plotGridLayout.setRowStretch(1, 1)

        self.topDownCheckbox.setCheckState(QtCore.Qt.CheckState.Unchecked)
        self.topDownCheckbox.stateChanged.connect(self.top_down_view_changed)

        self.checkBoxPizzaOrInterp.stateChanged.connect(self.change_beam_plot_mode)

        self.choose_plots_dialog = AddPlotDialog(self.mwin)
        self.choose_plots_dialog.plotParamGroupBox.hide()

        self.rangePickBtn.released.connect(
            lambda: self.open_choose_plots_dialog(
                dim_name="Range",
                dim_unit="m",
                dim_values=self.beam_plotter.range_vec,
                selected_dim_indices=self._range_slices
            )
        )

        self.anglePickBtn.released.connect(
            lambda: self.open_choose_plots_dialog(
                dim_name="Angle",
                dim_unit="deg",
                dim_values=self._az_beam_angles,
                selected_dim_indices=self._angle_slices
            )
        )

        self.threshPickBtn.released.connect(self.open_threshold_picker_dialog)

        self._plot_line_colors = [
            "#1C94E4",
            "#69D17A",
            "#CC713C",
            "#E7FC8A",
            "#1E9C92",
            "#EE64A9",
        ]

        self._thresh_picker_dialog = PickThreshDialog(self.mwin)

    def open_threshold_picker_dialog(self):
        self._thresh_picker_dialog.fill_thresh_ranges_values(
            self.threshold_ranges,
            self.threshold_values
        )

        if self._thresh_picker_dialog.exec() == QDialog.DialogCode.Accepted:
            # parse values
            ranges_text = self._thresh_picker_dialog.threshAtRangesLEdit.text()
            values_text = self._thresh_picker_dialog.threshValuesLEdit.text()

            try:
                ranges = np.array([float(s.strip()) for s in ranges_text.split(",")])
                values = np.array([float(s.strip()) for s in values_text.split(",")])

                if ranges.size != values.size or ranges.size < 1:
                    return  # invalid input, maybe show message somehow?

                self.threshold_ranges = ranges
                self.threshold_values = values

                # update plot
                self.make_thresh_from_vecs(self.threshold_ranges, self.threshold_values)

            except Exception as e:
                pass  # invalid input, maybe show message somehow?
    
    def remove_non_picked_slices(self, selected_dim_indices, plotter: XY2DPlotWidget):
        # if slices have changed, remove old ones
        existing_keys = list(plotter.plot_data_items.keys())
        for key in existing_keys:
            if key not in selected_dim_indices and key != self._thresh_line_key:
                plotter.clear_data(key)
    
    def open_choose_plots_dialog(self, dim_name, dim_unit, dim_values, selected_dim_indices):

        self.choose_plots_dialog.initialize(dim_name, dim_unit, dim_values, selected_dim_indices, 0)

        if self.choose_plots_dialog.exec() == QDialog.DialogCode.Accepted:
            chosen_dim_indices = self.choose_plots_dialog.chosen_dim_indices
            if selected_dim_indices is self._angle_slices:
                self._angle_slices = chosen_dim_indices
                self.remove_non_picked_slices(self._angle_slices, self.range_baseband_plot)
                self.draw_angle_slices()
            elif selected_dim_indices is self._range_slices:
                self._range_slices = chosen_dim_indices
                self.remove_non_picked_slices(self._range_slices, self.angle_baseband_plot)
                self.draw_range_slices()
    
    def change_beam_plot_mode(self):
        state = self.checkBoxPizzaOrInterp.checkState()
        self.beam_plotter.plotting_mode = 1 if state == QtCore.Qt.CheckState.Checked else 0
        if self.rd_plot_data is not None:
            self.draw_data_frame(self.rd_plot_data)

    def gen_angle_slice_list(self, angles: list[float]):
        self._angle_slices.clear()
        for angle in angles:
            closest_inx = (np.abs(self._az_beam_angles - angle)).argmin()
            self._angle_slices.append(closest_inx)
        
        self._angle_slices = np.unique(self._angle_slices).tolist()
    
    def gen_range_slice_list(self, ranges: list[float]):

        self._range_slices.clear()
        for rng in ranges:
            closest_inx = (np.abs(self.beam_plotter.range_vec - rng)).argmin()
            self._range_slices.append(closest_inx)
        self._range_slices = np.unique(self._range_slices).tolist()
    
    def draw_angle_slices(self):
        for inx in self._angle_slices:
            self.range_baseband_plot.plot_or_update_data(
                inx,
                self.beam_plotter.range_vec,
                self.rd_plot_data.power_beam_data[inx],
                line_color=self._plot_line_colors[(len(self.range_baseband_plot.plot_data_items)-1)%len(self._plot_line_colors)],
                legend_label=f"Angle Slice {self._az_beam_angles[inx]:.1f} deg"
            )

    def draw_range_slices(self):
        if self.is_single_angle:
            return
        for inx in self._range_slices:
            self.angle_baseband_plot.plot_or_update_data(
                inx,
                self._az_beam_angles,
                self.rd_plot_data.power_beam_data[:, inx],
                line_color=self._plot_line_colors[(len(self.angle_baseband_plot.plot_data_items))%len(self._plot_line_colors)],
                legend_label=f"Range Slice {self.beam_plotter.range_vec[inx]:.1f} m"
            )

    def range_edited(self, min_val, max_val):
        self.range_baseband_plot.change_xlims(min_val, max_val)
    
    def power_edited(self, min_val, max_val):
        self.range_baseband_plot.change_ylims(min_val, max_val)
        if self.is_single_angle:
            return
        self.angle_baseband_plot.change_ylims(min_val, max_val)
    
    def angle_edited(self, min_val, max_val):
        if self.is_single_angle:
            return
        self.angle_baseband_plot.change_xlims(min_val, max_val)

    def top_down_view_changed(self):
        state = self.topDownCheckbox.checkState()
        self.beam_plotter.set_topdown_view(state)

    def frame_edited(self):
        if not self.initialized:
            return
        
        curr_frame = int(self.currFrameLEdit.text()) - 1
        if 0 <= curr_frame < len(self.rd_plot_data_buffer):
            self.paused = True
            self.curr_data_frame_inx = curr_frame
            self.draw_data_frame(self.rd_plot_data_buffer[self.curr_data_frame_inx])
        else:
            self.currFrameLEdit.setText(f"{int(self.curr_data_frame_inx + 1)}")

    def set_label_time(self):
        if self.first_timestamp is None or not self.initialized:
            return

        curr_frame_ts = self.rd_plot_data_buffer[self.curr_data_frame_inx].timestamp
        curr_frame_seq = self.rd_plot_data_buffer[self.curr_data_frame_inx].seq_num
        timetxt = time.strftime('%Y.%m.%d %H:%M:%S', time.localtime(curr_frame_ts/1000))
        rel_time_txt = (curr_frame_ts - self.first_timestamp)/1000
        self.seqNumTimeLabel.setText(
            f"{timetxt}\nSince Start: {rel_time_txt:.1f}s\nSequence number: {curr_frame_seq}"
            f"\nNum frames received: {self.frame_received_counter}"
            f"\nNum frames dropped: {self.frame_dropped_counter}"
            )

    def reset_limits(self):
        if not self.initialized:
            return
        
        self._range_lim_ledit_helper.reset()
        self._power_lim_ledit_helper.reset()
        self._angle_lim_ledit_helper.reset()

        self.beam_plotter.plot_item.autoRange()


    def set_label_info(self):
        fps = self.first_setup_dict["fps"]
        is_live = self.first_setup_dict.get("is_live", True)
        self.infoParamLabel.setText(
            (f"FPS: {fps}"
            f"\nDC Removal Smooth Coeff: {self.dc_smooth_coeff:.2f}")
        )

        liveplay_color = "#82f17e" if is_live else "#369ee4"
        liveplay_text = "Live" if is_live else "Playback"

        self.liveOrPlaybackLabel.setStyleSheet(f"""
        QLabel {{
            color: {liveplay_color};
            font-size: 14pt;
        }}
        """)
        self.liveOrPlaybackLabel.setText(liveplay_text)
            
    def set_label_curr_frame(self):
        self.currFrameLEdit.setText(f"{int(self.curr_data_frame_inx + 1)}")
        self.totalNumFramesBuffLabel.setText(f"/ {self.curr_label_frame_max}")

    def keyPressEvent(self, event: pg.QtGui.QKeyEvent):
        # if dialogs are in focus, do not handle
        if self.choose_plots_dialog.isVisible():
            return False
        
        if self._thresh_picker_dialog.isVisible():
            return False
        
        if event.key() == QtCore.Qt.Key_Space:
            self.toggle_pause()
            return True

        elif event.key() == QtCore.Qt.Key_Left:
            self.move_frame(-1)
            return True

        elif event.key() == QtCore.Qt.Key_Right:
            self.move_frame(1)
            return True

        elif event.key() == QtCore.Qt.Key_R:
            self.reset_limits()
            return True

        return False

    def move_frame(self, direction: int):
        if not self.initialized or len(self.rd_plot_data_buffer) <= 1:
            return
        self.paused = True
        self.curr_data_frame_inx += direction
        if self.curr_data_frame_inx < 0:
            self.curr_data_frame_inx = 0
        elif self.curr_data_frame_inx >= len(self.rd_plot_data_buffer):
            self.curr_data_frame_inx = len(self.rd_plot_data_buffer) - 1

        self.draw_data_frame(self.rd_plot_data_buffer[self.curr_data_frame_inx])
        self.currFrameLEdit.setText(f"{int(self.curr_data_frame_inx + 1)}")

    def toggle_pause(self):
        if not self.initialized:
            return
        self.paused = not self.paused

        if not self.paused:
            self.update()

    def start_event_loop(self):
        self.app.exec_()

    def exit(self):
        if self.shm_on_exit is not None:
            self.shm_on_exit()
        pg.exit()
    
    def handle_first_setup(self, setup_dict: dict):
        self.first_setup_dict = setup_dict
        if "num_saved_frames" in setup_dict:
            self.num_saved_frames = setup_dict["num_saved_frames"]
            if self.num_saved_frames < 0:
                self.num_saved_frames = 100_000
            else:
                self.num_saved_frames = int(self.num_saved_frames)

        self._drop_frames_threshold = self.num_saved_frames + self.first_setup_dict["fps"]*5

        self.dc_smooth_coeff = self.first_setup_dict.get("dc_smooth_coeff", None)

        self.color_map_range = setup_dict.get("color_map_range", np.array([-60.0, 20.0]))
        self.beam_sector_width_deg = setup_dict.get("beam_sector_width_deg", 20.0)

        self.set_label_info()

        self.beam_plotter.initialize_plot(
            self.first_setup_dict["az_beam_angles"],
            self.first_setup_dict["num_rangebins"],
            range_offset=self.first_setup_dict["range_offset"],
            bin_length=self.first_setup_dict["bin_length"],
            beam_sector_width_deg=self.beam_sector_width_deg
            )
        
        self.beam_plotter.set_colormap_range(self.color_map_range[0], self.color_map_range[1])

        self._az_beam_angles = self.first_setup_dict["az_beam_angles"]
        self.is_single_angle = len(self._az_beam_angles) == 1
        self._az_beam_angles_rad = np.deg2rad(self._az_beam_angles)
        
        self._range_lim_vec = self.first_setup_dict.get("range_lim_vec", [0.0, self.beam_plotter.range_vec[-1]])
        self._angle_lim_vec = self.first_setup_dict.get("angle_lim_vec", [self._az_beam_angles[0], self._az_beam_angles[-1]+40.0])
        self._power_lim_vec = self.first_setup_dict.get("power_lim_vec", [-80.0, 30.0])

        rangediff = self._range_lim_vec[1] - self._range_lim_vec[0]
        self._range_lim_vec[1] += rangediff/5

        self._range_lim_ledit_helper = LimitEditLineHelper(
            self.rangeMinLEdit,
            self.rangeMaxLEdit,
            self._range_lim_vec[0],
            self._range_lim_vec[-1],
            QDoubleValidator(),
            self.range_edited
        )

        self._power_lim_ledit_helper = LimitEditLineHelper(
            self.powerMinLEdit,
            self.powerMaxLEdit,
            self._power_lim_vec[0],
            self._power_lim_vec[-1],
            QDoubleValidator(),
            self.power_edited
        )


        self._angle_lim_ledit_helper = LimitEditLineHelper(
            self.angleMinLEdit,
            self.angleMaxLEdit,
            self._angle_lim_vec[0],
            self._angle_lim_vec[-1],
            QDoubleValidator(),
            self.angle_edited
        )

        self.initialized = True

        self.threshold_ranges = setup_dict.get("threshold_ranges", [])
        self.threshold_values = setup_dict.get("threshold_values", [])

        range_slices_to_plot = setup_dict.get("range_slices_to_plot", [1.0])
        angle_slices_to_plot = setup_dict.get("angle_slices_to_plot", [0.0])

        self.make_thresh_from_vecs(self.threshold_ranges, self.threshold_values)

        self.reset_limits()

        self.gen_angle_slice_list(angle_slices_to_plot)
        self.gen_range_slice_list(range_slices_to_plot)

        if self.is_single_angle:

            for thing in (self.rangePickBtn, self.anglePickBtn,
                        self.angleMinLEdit, self.angleMaxLEdit):
                thing.setDisabled(True)
                thing.setToolTip("Disabled for single angle beamforming")
    
    def make_thresh_from_vecs(self, range_vec: np.ndarray, value_vec: np.ndarray) -> np.ndarray:
        thresh_color = (255, 0, 0)
        if not len(range_vec) or not len(value_vec) or len(range_vec) != len(value_vec):
            self.linear_thresh_vec = None
            self.range_baseband_plot.plot_or_update_data(self._thresh_line_key, np.array([]), np.array([]),
                                                         line_color=thresh_color, legend_label="Threshold")
            return None
        self.linear_thresh_vec = np.interp(
            self.beam_plotter.range_vec,
            range_vec,
            value_vec,
            left=value_vec[0],
            right=value_vec[-1]
        )

        self.range_baseband_plot.plot_or_update_data(self._thresh_line_key, self.beam_plotter.range_vec, self.linear_thresh_vec,
                                               line_color=thresh_color, legend_label="Threshold")
    
        return self.linear_thresh_vec
        
    def receive_data(self, data: RadarDirectBeamData | dict):

        # setup
        if self.first_setup_dict is None:
            if isinstance(data, dict):
                self.handle_first_setup(data)
                return
        
        if self.first_timestamp is None:
            self.first_timestamp = data.timestamp

        self.rd_plot_data_buffer.append(data)
        self.frame_received_counter += 1

    def update(self):
        if not len(self.rd_plot_data_buffer):
            return

        if not self.paused:
            self.curr_data_frame_inx = len(self.rd_plot_data_buffer) - 1
            if self.rd_plot_data is not self.rd_plot_data_buffer[self.curr_data_frame_inx]:
                self.draw_data_frame(self.rd_plot_data_buffer[self.curr_data_frame_inx])

        # Limit the buffer size to avoid memory issues
        if len(self.rd_plot_data_buffer) > self._drop_frames_threshold:
            oldlen = len(self.rd_plot_data_buffer)
            self.rd_plot_data_buffer = self.rd_plot_data_buffer[-self.num_saved_frames:]
            num_removed = oldlen - len(self.rd_plot_data_buffer)
            self.frame_dropped_counter += num_removed
            self.curr_data_frame_inx = np.clip(self.curr_data_frame_inx - num_removed, 0, len(self.rd_plot_data_buffer)-1)
            self.set_label_curr_frame()

        if self.curr_label_frame_max != len(self.rd_plot_data_buffer):
            self.curr_label_frame_max = len(self.rd_plot_data_buffer)
            self.set_label_curr_frame()
        
        self.set_label_time()

    def draw_data_frame(self, frame: RadarDirectBeamData):
        
        self.rd_plot_data = frame

        # generate power and phase beam data if there arent any

        if self.linear_thresh_vec is not None:
            if self._buff_for_beam_thresh is None:
                self._buff_for_beam_thresh = np.empty_like(frame.power_beam_data)

            self._buff_for_beam_thresh[:] = frame.power_beam_data

            self._buff_for_beam_thresh[self._buff_for_beam_thresh < self.linear_thresh_vec] = -200.0
            
            self.beam_plotter.update_data(self._buff_for_beam_thresh)
        else:
            self.beam_plotter.update_data(frame.power_beam_data)
        
        self.draw_angle_slices()
        self.draw_range_slices()
        
        self.set_label_curr_frame()
        self.set_label_time()

    def get_title_string(self):
        return f"PlotName"

