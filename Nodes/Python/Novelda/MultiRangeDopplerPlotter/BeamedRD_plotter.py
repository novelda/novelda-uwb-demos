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

from RangeDopplerPlotter.surface_plot_widget import Matrix3DPlot, AxisConfig, CameraState

from MultiRangeDopplerPlotter.BeamedRDui import Ui_multiRangeDoppWin
from MultiRangeDopplerPlotter.add_plot_dialog import AddPlotDialog

@dataclass
class MultiRDSetup:
    fps             : int
    fft_size        : int
    range_offset    : float
    bin_length      : float

@dataclass
class MultiRDPlotData:
    multi_rd_setup: MultiRDSetup
    rd_data : np.ndarray
    timestamp : float
    seq_num   : int

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

class AxisCombos(IntEnum):
    RANGE_DOPPLER = 0
    ANGLE_RANGE = 1
    ANGLE_DOPPLER = 2

class SpecificSurfacePlot(Matrix3DPlot):
    def spec_set_type(self, axis_combo: AxisCombos):
        self.spec_axis_combo = axis_combo
    
    def spec_get_type(self) -> AxisCombos:
        return self.spec_axis_combo

    def spec_make_active(self, active: bool):
        self.spec_is_active = active
    
    def spec_get_active(self) -> bool:
        if hasattr(self, "spec_is_active"):
            return self.spec_is_active
        return False
    
    def spec_change_lims_range(self, new_min: float, new_max: float, instant_update=True):
        if not self.spec_get_active():
            return
        if self.spec_axis_combo == AxisCombos.RANGE_DOPPLER:
            self.change_xlims(new_min, new_max, instant_update=instant_update)
        elif self.spec_axis_combo == AxisCombos.ANGLE_RANGE:
            self.change_ylims(new_min, new_max, instant_update=instant_update)
    
    def spec_change_lims_doppler(self, new_min: float, new_max: float, instant_update=True):
        if not self.spec_get_active():
            return
        if self.spec_axis_combo == AxisCombos.RANGE_DOPPLER or self.spec_axis_combo == AxisCombos.ANGLE_DOPPLER:
            self.change_ylims(new_min, new_max, instant_update=instant_update)
    
    def change_zlims(self, zmin, zmax, instant_update=True):
        if not self.spec_get_active():
            return
        return super().change_zlims(zmin, zmax, instant_update=instant_update)
    
    def spec_change_lims_angle(self, new_min: float, new_max: float, instant_update=True):
        if not self.spec_get_active():
            return
        if self.spec_axis_combo == AxisCombos.ANGLE_RANGE:
            self.change_xlims(new_min, new_max, instant_update=instant_update)
        elif self.spec_axis_combo == AxisCombos.ANGLE_DOPPLER:
            self.change_xlims(new_min, new_max, instant_update=instant_update)

class MultiRangeDopplerPlotter(Ui_multiRangeDoppWin):

    def __init__(self, shm_on_exit=None):
        self.plot = None
        self.plot_linear_scale: bool       = False
        self.shm_on_exit = shm_on_exit

        self.range_axis_values: np.ndarray = None
        self.doppler_axis_values: np.ndarray = None
        self.power_lim_vec: np.ndarray = None
        
        self.rd_setup: MultiRDSetup = None
        self.rd_plot_data: MultiRDPlotData = None

        self.app = None
        self.initialized = False

        self._key_filter = None
        self.mwin = None

        self.num_saved_frames = 10_000

        self.cols_per_row = 2

        self.paused = False
        self.curr_data_frame_inx = 0
        self.curr_label_frame_max = 0

        self.first_setup_dict = None
        self.first_timestamp = None
        self.is_live = True

        self.did_first_lims_change = False

        # timestamp received : RDRawPlotData
        self.rd_plot_data_buffer: list[MultiRDPlotData] = []

        self.range_axis = AxisConfig("Range", "m", 0, 100, 100)
        self.doppler_axis = AxisConfig("Doppler", "Hz", -50, 50, 100)
        self.power_axis = AxisConfig("Power", "dB", -100, 0, 100)
        self.angle_axis = AxisConfig("Angle", "deg", -60, 60, 100)

        self.num_bins_range = 0
        self.num_bins_doppler = 0

        self.range_axis_values = np.array([])
        self.doppler_axis_values = np.array([])
        self.angle_axis_values = np.array([])

        self.unpicked_range_indices = np.array([0, 1], dtype=int)
        self.unpicked_angle_indices = np.array([0, 1], dtype=int)
        self.unpicked_doppler_indices = np.array([0, 1], dtype=int)

        self.curr_axis_combo = AxisCombos.RANGE_DOPPLER
        self.name_to_combo_dict = {
            "Range - Doppler": AxisCombos.RANGE_DOPPLER,
            "Range - Angle": AxisCombos.ANGLE_RANGE,
            "Angle - Doppler": AxisCombos.ANGLE_DOPPLER
        }

        self.limits_ledit_text: dict[QLineEdit, str] = {}

        self.const_range_start = None

        self.unpicked_range_index_to_plot: dict[int, SpecificSurfacePlot] = {}
        self.unpicked_angle_index_to_plot: dict[int, SpecificSurfacePlot] = {}
        self.unpicked_doppler_index_to_plot: dict[int, SpecificSurfacePlot] = {}

        self.curr_active_unpicked_dict: dict[int, SpecificSurfacePlot] =  self.unpicked_angle_index_to_plot

        self.all_plots: list[SpecificSurfacePlot] = []

        self.is_single_angle = False

        self.frame_received_counter = 0
        self.frame_dropped_counter = 0
        
        from PySide6.QtCore import QLocale
        QLocale.setDefault(QLocale(QLocale.English, QLocale.UnitedStates))

        logo_img_fp = Path(__file__).resolve().parent.parent.parent.parent.parent / "Demos" \
            / "Resources" / "Images" / "Novelda_logo_hvit_150dpi.png"
        self.logo_img = QImage(str(logo_img_fp))

    def add_plot_to_grid(self, plot: SpecificSurfacePlot, index: int):
        row = index // self.cols_per_row
        col = index % self.cols_per_row
        self.plotGridLayout.addWidget(plot.local_view, row, col)

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
        self.mwin.setWindowTitle("Range Doppler Plotter")

        self.setupUi(self.mwin)

        self.mwin.setFocusPolicy(QtCore.Qt.ClickFocus)
        self.centralwidget.setFocusPolicy(QtCore.Qt.ClickFocus)

        self.hotkeyLabel.setText(("Space: play/pause"
                                   "\nLeft/Right Arrow: change current RD plot"
                                   "\nXYZ: orthographic projection on axes"
                                   "\nR: reset camera to default"
                                   "\nRight-Click: place plot marker"
                                   "\nWASD: move plot marker")
                                    )

        self.logoLabel.setPixmap(pg.QtGui.QPixmap.fromImage(self.logo_img).scaledToWidth(100, QtCore.Qt.SmoothTransformation))

        self.resetLimitsBtn.released.connect(self.reset_limits)

        self.showWireCheckbox.setCheckState(QtCore.Qt.CheckState.Unchecked)
        self.showWireCheckbox.stateChanged.connect(self.wireframe_check_changed)

        # connect line edits to limits_edited
        self.rangeMinLEdit.returnPressed.connect(self.range_limits_edited)
        self.rangeMaxLEdit.returnPressed.connect(self.range_limits_edited)
        self.dopplerMinLEdit.returnPressed.connect(self.doppler_limits_edited)
        self.dopplerMaxLEdit.returnPressed.connect(self.doppler_limits_edited)
        self.powerMinLEdit.returnPressed.connect(self.power_limits_edited)
        self.powerMaxLEdit.returnPressed.connect(self.power_limits_edited)
        self.angleMinLEdit.returnPressed.connect(self.angle_limits_edited)
        self.angleMaxLEdit.returnPressed.connect(self.angle_limits_edited)
        self.currFrameLEdit.returnPressed.connect(self.frame_edited)

        self.rangeMinLEdit.setValidator(QDoubleValidator())
        self.rangeMaxLEdit.setValidator(QDoubleValidator())
        self.dopplerMinLEdit.setValidator(QDoubleValidator())
        self.dopplerMaxLEdit.setValidator(QDoubleValidator())
        self.powerMinLEdit.setValidator(QDoubleValidator())
        self.powerMaxLEdit.setValidator(QDoubleValidator())
        self.angleMinLEdit.setValidator(QDoubleValidator())
        self.angleMaxLEdit.setValidator(QDoubleValidator())

        self.choosePlotsBtn.clicked.connect(self.open_choose_plots_dialog)
        self.savePlotOptionsJsonBtn.clicked.connect(self.save_plot_config_to_json)
        self.loadPlotOptionJsonBtn.clicked.connect(self.load_plot_config_from_json)

        self.choose_plots_dialog = None

        # populate combo box
        for name in self.name_to_combo_dict.keys():
            self.axisPickComboBox.addItem(name)
        
        self.axisPickComboBox.currentTextChanged.connect(self.axis_combo_changed)

        screen_size = self.app.primaryScreen().size()
        best_ar = 16/10
        self.mwin.resize(int(screen_size.height()*best_ar), int(screen_size.height()*0.9))
        self.mwin.move(0, 0)
        self.mwin.show()

        self.centralwidget.setFocus()

        # add and remove dummy plot to initialize opengl context
        dummy_plot = SpecificSurfacePlot(self.range_axis, self.doppler_axis, self.power_axis)
        self.plotGridLayout.addWidget(dummy_plot.local_view, 0, 0)
        self.plotGridLayout.removeWidget(dummy_plot.local_view)
        dummy_plot.local_view.deleteLater()

        self.waiting_label = QLabel("Waiting for data...", self.centralwidget)
        self.waiting_label.setStyleSheet(f"""
            QLabel {{
                color: white;
                font-size: 20pt;
                font-weight: bold;
                background-color: rgba(0, 0, 0, 100);
                padding: 5px;
                border-radius: 3px;
            }}
        """)
        self.plotGridLayout.addWidget(self.waiting_label, 0, 0)

        if self._key_filter is None:
            self._key_filter = KeyPressFilter(self.keyPressEvent)
            self.app.installEventFilter(self._key_filter)
    
    def load_plot_config_from_json(self):
        file_name = ""
        file_name, _ = QFileDialog.getOpenFileName(
            self.centralwidget,
            "Load Plot Config",
            "",
            "JSON files (*.json);;All Files (*)"
        )

        as_path = Path(file_name)
        if not as_path.is_file():
            return
        
        dct = {}
        try:
            with open(as_path, 'r') as f:
                dct = json.load(f)

        except Exception as e:
            print(f"Error loading JSON: {e}")
            return

        if "MultiRDPlottingParameters" not in dct:
            return
        
        params = dct["MultiRDPlottingParameters"]
        if "MaxBufferedFrames" in params:
            try:
                max_buf = int(params["MaxBufferedFrames"])
                if max_buf != self.num_saved_frames and max_buf >= 1:
                    self.num_saved_frames = max_buf
            except:
                pass
        
        def set_limvec_from_params(edit_min: QLineEdit, edit_max: QLineEdit, str_val: str, edited_func):
            try:
                str_val = str_val.strip("{} ")
                parts = str_val.split(',')
                if len(parts) == 2:
                    minval = float(parts[0].strip())
                    maxval = float(parts[1].strip())
                    edit_min.setText(f"{minval:.3f}")
                    edit_max.setText(f"{maxval:.3f}")
                    edited_func()
            except:
                pass
        
        if "PowerLimVec" in params:
            set_limvec_from_params(self.powerMinLEdit, self.powerMaxLEdit, params["PowerLimVec"], self.power_limits_edited)
        if "RangeLimVec" in params:
            set_limvec_from_params(self.rangeMinLEdit, self.rangeMaxLEdit, params["RangeLimVec"], self.range_limits_edited)
        if "DopplerLimVec" in params:
            set_limvec_from_params(self.dopplerMinLEdit, self.dopplerMaxLEdit, params["DopplerLimVec"], self.doppler_limits_edited)
        if "AngleLimVec" in params:
            set_limvec_from_params(self.angleMinLEdit, self.angleMaxLEdit, params["AngleLimVec"], self.angle_limits_edited)

        def set_slices_to_plot(str_val: str, axis_values: np.ndarray, unpicked_indices: np.ndarray, unpicked_dict: dict[int, SpecificSurfacePlot]):
            try:
                str_val = str_val.strip("{} ")
                parts = str_val.split(',')
                new_indices = []
                for part in parts:
                    val = float(part.strip())
                    idx = (np.abs(axis_values - val)).argmin()
                    if idx not in new_indices:
                        new_indices.append(idx)
                new_arr = np.asarray(new_indices, dtype=int)
                unpicked_indices.resize(new_arr.shape, refcheck=False)
                if new_arr.size:
                    unpicked_indices[:] = new_arr
                self.remove_plots(unpicked_dict)
            except:
                pass

        if "RangeSlicesToPlot" in params:
            set_slices_to_plot(params["RangeSlicesToPlot"], self.range_axis_values, self.unpicked_range_indices, self.unpicked_range_index_to_plot)
        if "DopplerSlicesToPlot" in params:
            set_slices_to_plot(params["DopplerSlicesToPlot"], self.doppler_axis_values, self.unpicked_doppler_indices, self.unpicked_doppler_index_to_plot)
        if "AngleSlicesToPlot" in params:
            set_slices_to_plot(params["AngleSlicesToPlot"], self.angle_axis_values, self.unpicked_angle_indices, self.unpicked_angle_index_to_plot)
        
        if "GridColsPerRow" in params:
            try:
                cols_per_row = int(params["GridColsPerRow"])
                if 1 <= cols_per_row <= 15 and cols_per_row != self.cols_per_row:
                    self.cols_per_row = cols_per_row
                    # re-add all current plots to grid
                    for i, plot in enumerate(self.curr_active_unpicked_dict.values()):
                        self.plotGridLayout.removeWidget(plot.local_view)
                        self.add_plot_to_grid(plot, i)
            except:
                pass
    
    def save_plot_config_to_json(self):
        file_name = ""
        file_name, _ = QFileDialog.getSaveFileName(
            self.centralwidget,
            "Save Plot Config",
            "",
            "JSON files (*.json);;All Files (*)"
        )

        as_path = Path(file_name)
        if not as_path.parent.is_dir():
            return
        
        params = {
            "MaxBufferedFrames" : str(self.num_saved_frames),
            "PowerLimVec" : "{" + f"{self.power_axis.curr_min_val:.3f}, {self.power_axis.curr_max_val:.3f}" + "}",
            "RangeLimVec" : "{" + f"{self.range_axis.curr_min_val:.3f}, {self.range_axis.curr_max_val:.3f}" + "}",
            "DopplerLimVec" : "{" + f"{self.doppler_axis.curr_min_val:.3f}, {self.doppler_axis.curr_max_val:.3f}" + "}",
            "AngleLimVec" : "{" + f"{self.angle_axis.curr_min_val:.3f}, {self.angle_axis.curr_max_val:.3f}" + "}",
            "RangeSlicesToPlot" : "{" + ", ".join([f"{self.range_axis_values[idx]:.3f}" for idx in self.unpicked_range_indices]) + "}",
            "DopplerSlicesToPlot" : "{" + ", ".join([f"{self.doppler_axis_values[idx]:.3f}" for idx in self.unpicked_doppler_indices]) + "}",
            "AngleSlicesToPlot" : "{" + ", ".join([f"{self.angle_axis_values[idx]:.3f}" for idx in self.unpicked_angle_indices]) + "}",
            "GridColsPerRow" : str(self.cols_per_row)
        }

        out_dct = {}
        if as_path.exists():
            with open(as_path, 'r') as f:
                try:
                    out_dct = json.load(f)
                except:
                    out_dct = {}
        
        out_dct["MultiRDPlottingParameters"] = params
        try:
            with open(as_path, 'w') as f:
                json.dump(out_dct, f, indent=4)
        except Exception as e:
            print(f"Error saving JSON: {e}")
            return
        
    def open_choose_plots_dialog(self):
        if self.choose_plots_dialog is None:
            self.choose_plots_dialog = AddPlotDialog(self.mwin)
        
        if self.curr_axis_combo == AxisCombos.RANGE_DOPPLER:
            dim_name = "Angle"
            dim_unit = "deg"
            dim_values = self.angle_axis_values
            selected_dim_indices = self.unpicked_angle_indices.tolist()
        elif self.curr_axis_combo == AxisCombos.ANGLE_RANGE:
            dim_name = "Doppler"
            dim_unit = "Hz"
            dim_values = self.doppler_axis_values
            selected_dim_indices = self.unpicked_doppler_indices.tolist()
        elif self.curr_axis_combo == AxisCombos.ANGLE_DOPPLER:
            dim_name = "Range"
            dim_unit = "m"
            dim_values = self.range_axis_values
            selected_dim_indices = self.unpicked_range_indices.tolist()
        
        self.choose_plots_dialog.initialize(dim_name, dim_unit, dim_values, selected_dim_indices, self.cols_per_row)

        if self.choose_plots_dialog.exec() == QDialog.DialogCode.Accepted:
            chosen_dim_indices = self.choose_plots_dialog.chosen_dim_indices
            cols_per_row = int(self.choose_plots_dialog.gridColPerRowLEdit.text())
            if self.cols_per_row != cols_per_row:
                self.cols_per_row = cols_per_row
                # re-add all current plots to grid
                for i, plot in enumerate(self.curr_active_unpicked_dict.values()):
                    self.plotGridLayout.removeWidget(plot.local_view)
                    self.add_plot_to_grid(plot, i)
                    
            if self.curr_axis_combo == AxisCombos.RANGE_DOPPLER:
                self.unpicked_angle_indices = np.array(chosen_dim_indices, dtype=int)
                self.remove_plots(self.unpicked_angle_index_to_plot)
            elif self.curr_axis_combo == AxisCombos.ANGLE_RANGE:
                self.unpicked_doppler_indices = np.array(chosen_dim_indices, dtype=int)
                self.remove_plots(self.unpicked_doppler_index_to_plot)
            elif self.curr_axis_combo == AxisCombos.ANGLE_DOPPLER:
                self.unpicked_range_indices = np.array(chosen_dim_indices, dtype=int)
                self.remove_plots(self.unpicked_range_index_to_plot)

        self.draw_data_frame(self.rd_plot_data_buffer[self.curr_data_frame_inx])

    def change_axis_combo(self, new_combo: AxisCombos):
        if new_combo != self.curr_axis_combo and not self.is_single_angle:
            
            # hide and remove all current plots
            for plot in self.curr_active_unpicked_dict.values():
                plot.spec_make_active(False)
                self.plotGridLayout.removeWidget(plot.local_view)
                plot.local_view.hide()
            
            # restore the plots of new_combo
            if new_combo == AxisCombos.RANGE_DOPPLER:
                self.curr_active_unpicked_dict = self.unpicked_angle_index_to_plot
            elif new_combo == AxisCombos.ANGLE_RANGE:
                self.curr_active_unpicked_dict = self.unpicked_doppler_index_to_plot
            elif new_combo == AxisCombos.ANGLE_DOPPLER:
                self.curr_active_unpicked_dict = self.unpicked_range_index_to_plot

            for cnt, plot in enumerate(self.curr_active_unpicked_dict.values()):
                plot.spec_make_active(True)
                self.add_plot_to_grid(plot, cnt)
                plot.wireframe_change_state(self.showWireCheckbox.checkState() == QtCore.Qt.CheckState.Checked)
                plot.local_view.show()

            self.curr_axis_combo = new_combo
            self.draw_data_frame(self.rd_plot_data_buffer[self.curr_data_frame_inx])

    def axis_combo_changed(self, new_text: str):
        if new_text in self.name_to_combo_dict.keys():
            new_combo = self.name_to_combo_dict[new_text]
            self.change_axis_combo(new_combo)
    
    def wireframe_check_changed(self, newstate: QtCore.Qt.CheckState):
        for plot in self.curr_active_unpicked_dict.values():
            plot.wireframe_change_state(newstate == QtCore.Qt.CheckState.Checked.value)
    
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
    
        self.init_range_doppler_lineedit()

        for plot in self.all_plots:
            plot.spec_change_lims_range(self.range_axis.curr_min_val, self.range_axis.curr_max_val, instant_update=False)
            plot.spec_change_lims_doppler(self.doppler_axis.curr_min_val, self.doppler_axis.curr_max_val, instant_update=False)
            plot.change_zlims(self.power_axis.curr_min_val, self.power_axis.curr_max_val, instant_update=False)
            plot.spec_change_lims_angle(self.angle_axis.curr_min_val, self.angle_axis.curr_max_val, instant_update=False)
            plot.update_changed_lims()

    def set_label_info(self):
        frames_btw_pd = self.first_setup_dict["frames_between_pd"]
        num_frames_in_pd = self.first_setup_dict["num_frames_in_pd"]
        fps = self.first_setup_dict["fps"]
        enable_dc_removal = self.first_setup_dict["enable_dc_removal"]
        is_live = self.first_setup_dict.get("is_live", True)
        self.infoParamLabel.setText(
            (f"FPS: {fps}"
            f"\nRangeDoppler integration time: {num_frames_in_pd/fps:.1f} s"
            f"\nRangeDoppler update rate: {frames_btw_pd/fps:.1f} s"
            f"\nEnable DC Removal: {enable_dc_removal}")
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

    def init_range_doppler_lineedit(self):

        if "range_lim_vec" in self.first_setup_dict:
            if self.first_setup_dict["range_lim_vec"].size == 2:
                self.range_axis.curr_min_val = self.first_setup_dict["range_lim_vec"][0]
                self.range_axis.curr_max_val = self.first_setup_dict["range_lim_vec"][1]
        if "doppler_lim_vec" in self.first_setup_dict:
            if self.first_setup_dict["doppler_lim_vec"].size == 2:
                self.doppler_axis.curr_min_val = self.first_setup_dict["doppler_lim_vec"][0]
                self.doppler_axis.curr_max_val = self.first_setup_dict["doppler_lim_vec"][1]
        if "power_lim_vec" in self.first_setup_dict:
            if self.first_setup_dict["power_lim_vec"].size == 2:
                self.power_axis.curr_min_val = self.first_setup_dict["power_lim_vec"][0]
                self.power_axis.curr_max_val = self.first_setup_dict["power_lim_vec"][1]
        if "angle_lim_vec" in self.first_setup_dict:
            if self.first_setup_dict["angle_lim_vec"].size == 2:
                self.angle_axis.curr_min_val = self.first_setup_dict["angle_lim_vec"][0]
                self.angle_axis.curr_max_val = self.first_setup_dict["angle_lim_vec"][1]
        
        if "default_start_range" in self.first_setup_dict:
            self.range_axis.curr_min_val = self.first_setup_dict["default_start_range"]

        self.limits_ledit_text[self.dopplerMinLEdit] = f"{self.doppler_axis.curr_min_val:.2f}"
        self.limits_ledit_text[self.dopplerMaxLEdit] = f"{self.doppler_axis.curr_max_val:.2f}"
        self.limits_ledit_text[self.rangeMinLEdit] = f"{self.range_axis.curr_min_val:.2f}"
        self.limits_ledit_text[self.rangeMaxLEdit] = f"{self.range_axis.curr_max_val:.2f}"
        self.limits_ledit_text[self.powerMinLEdit] = f"{self.power_axis.curr_min_val:.2f}"
        self.limits_ledit_text[self.powerMaxLEdit] = f"{self.power_axis.curr_max_val:.2f}"
        self.limits_ledit_text[self.angleMinLEdit] = f"{self.angle_axis.curr_min_val:.2f}"
        self.limits_ledit_text[self.angleMaxLEdit] = f"{self.angle_axis.curr_max_val:.2f}"

        self.dopplerMinLEdit.setText(self.limits_ledit_text[self.dopplerMinLEdit])
        self.dopplerMaxLEdit.setText(self.limits_ledit_text[self.dopplerMaxLEdit])

        self.rangeMinLEdit.setText(self.limits_ledit_text[self.rangeMinLEdit])
        self.rangeMaxLEdit.setText(self.limits_ledit_text[self.rangeMaxLEdit])

        self.powerMinLEdit.setText(self.limits_ledit_text[self.powerMinLEdit])
        self.powerMaxLEdit.setText(self.limits_ledit_text[self.powerMaxLEdit])

        self.angleMinLEdit.setText(self.limits_ledit_text[self.angleMinLEdit])
        self.angleMaxLEdit.setText(self.limits_ledit_text[self.angleMaxLEdit])

    def range_limits_edited(self):
        if not self.initialized:
            return
        
        if self.rangeMinLEdit.text() == self.limits_ledit_text[self.rangeMinLEdit] and \
           self.rangeMaxLEdit.text() == self.limits_ledit_text[self.rangeMaxLEdit]:
            return

        rangemin = float(self.rangeMinLEdit.text())
        rangemax = float(self.rangeMaxLEdit.text())

        if rangemin < rangemax:
            for plot in self.all_plots:
                plot.spec_change_lims_range(rangemin, rangemax)
        else:
            self.rangeMinLEdit.setText(self.limits_ledit_text[self.rangeMinLEdit])
            self.rangeMaxLEdit.setText(self.limits_ledit_text[self.rangeMaxLEdit])
        
        self.limits_ledit_text[self.rangeMinLEdit] = self.rangeMinLEdit.text()
        self.limits_ledit_text[self.rangeMaxLEdit] = self.rangeMaxLEdit.text()

    def doppler_limits_edited(self):
        if not self.initialized:
            return
        
        if self.dopplerMinLEdit.text() == self.limits_ledit_text[self.dopplerMinLEdit] and \
           self.dopplerMaxLEdit.text() == self.limits_ledit_text[self.dopplerMaxLEdit]:
            return

        dopplermin = float(self.dopplerMinLEdit.text())
        dopplermax = float(self.dopplerMaxLEdit.text())

        if dopplermin < dopplermax:
            for plot in self.all_plots:
                plot.spec_change_lims_doppler(dopplermin, dopplermax)
        else:
            self.dopplerMinLEdit.setText(self.limits_ledit_text[self.dopplerMinLEdit])
            self.dopplerMaxLEdit.setText(self.limits_ledit_text[self.dopplerMaxLEdit])
        
        self.limits_ledit_text[self.dopplerMinLEdit] = self.dopplerMinLEdit.text()
        self.limits_ledit_text[self.dopplerMaxLEdit] = self.dopplerMaxLEdit.text()

    def power_limits_edited(self):
        if not self.initialized:
            return
        
        if self.powerMinLEdit.text() == self.limits_ledit_text[self.powerMinLEdit] and \
           self.powerMaxLEdit.text() == self.limits_ledit_text[self.powerMaxLEdit]:
            return

        zmin = float(self.powerMinLEdit.text())
        zmax = float(self.powerMaxLEdit.text())

        if zmin < zmax:
            for plot in self.all_plots:
                plot.change_zlims(zmin, zmax)
        else:
            self.powerMinLEdit.setText(self.limits_ledit_text[self.powerMinLEdit])
            self.powerMaxLEdit.setText(self.limits_ledit_text[self.powerMaxLEdit])
        
        self.limits_ledit_text[self.powerMinLEdit] = self.powerMinLEdit.text()
        self.limits_ledit_text[self.powerMaxLEdit] = self.powerMaxLEdit.text()

    def angle_limits_edited(self):
        if not self.initialized:
            return
        
        if self.angleMinLEdit.text() == self.limits_ledit_text[self.angleMinLEdit] and \
           self.angleMaxLEdit.text() == self.limits_ledit_text[self.angleMaxLEdit]:
            return

        angle_min = float(self.angleMinLEdit.text())
        angle_max = float(self.angleMaxLEdit.text())

        if angle_min < angle_max:
            for plot in self.all_plots:
                plot.spec_change_lims_angle(angle_min, angle_max)
        else:
            self.angleMinLEdit.setText(self.limits_ledit_text[self.angleMinLEdit])
            self.angleMaxLEdit.setText(self.limits_ledit_text[self.angleMaxLEdit])
        
        self.limits_ledit_text[self.angleMinLEdit] = self.angleMinLEdit.text()
        self.limits_ledit_text[self.angleMaxLEdit] = self.angleMaxLEdit.text()

    def keyPressEvent(self, event: pg.QtGui.QKeyEvent):
        if event.key() == QtCore.Qt.Key_Space:
            self.toggle_pause()
            return True

        elif event.key() == QtCore.Qt.Key_Left:
            self.move_frame(-1)
            return True

        elif event.key() == QtCore.Qt.Key_Right:
            self.move_frame(1)
            return True
        
        elif event.key() == QtCore.Qt.Key_Z:
            self.set_cam_state(CameraState.ORTHO_Z)
            return True

        elif event.key() == QtCore.Qt.Key_X:
            self.set_cam_state(CameraState.ORTHO_X)
            return True

        elif event.key() == QtCore.Qt.Key_Y:
            self.set_cam_state(CameraState.ORTHO_Y)
            return True

        elif event.key() == QtCore.Qt.Key_R:
            self.set_cam_state(CameraState.DEFAULT)
            return True

        return False

    def set_cam_state(self, state: CameraState):
        for plot in self.all_plots:
            plot.switch_cam_state(state)

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

    def plot_or_make_new(self, axis_combo: AxisCombos, index: int) -> SpecificSurfacePlot:
        new_plot = None
        num_existing = None

        if axis_combo == AxisCombos.RANGE_DOPPLER:
            if index in self.unpicked_angle_index_to_plot:
                return self.unpicked_angle_index_to_plot[index]
            
            new_plot = SpecificSurfacePlot(self.range_axis, self.doppler_axis, self.power_axis, 
                                self.get_title_string(self.unpicked_angle_indices[index]), axis_as_reference=False)
            self.unpicked_angle_index_to_plot[index] = new_plot
            num_existing = len(self.unpicked_angle_index_to_plot)

        elif axis_combo == AxisCombos.ANGLE_RANGE:
            if index in self.unpicked_doppler_index_to_plot:
                return self.unpicked_doppler_index_to_plot[index]
            new_plot = SpecificSurfacePlot(self.angle_axis, self.range_axis, self.power_axis, 
                                self.get_title_string(self.unpicked_doppler_indices[index]), axis_as_reference=False)
            self.unpicked_doppler_index_to_plot[index] = new_plot
            num_existing = len(self.unpicked_doppler_index_to_plot)

        elif axis_combo == AxisCombos.ANGLE_DOPPLER:
            if index in self.unpicked_range_index_to_plot:
                return self.unpicked_range_index_to_plot[index]
            new_plot = SpecificSurfacePlot(self.angle_axis, self.doppler_axis, self.power_axis, 
                                self.get_title_string(self.unpicked_range_indices[index]), axis_as_reference=False)
            self.unpicked_range_index_to_plot[index] = new_plot
            num_existing = len(self.unpicked_range_index_to_plot)

        rangemin = float(self.rangeMinLEdit.text())
        rangemax = float(self.rangeMaxLEdit.text())
        dopplermin = float(self.dopplerMinLEdit.text())
        dopplermax = float(self.dopplerMaxLEdit.text())
        zmin = float(self.powerMinLEdit.text())
        zmax = float(self.powerMaxLEdit.text())
        angle_min = float(self.angleMinLEdit.text())
        angle_max = float(self.angleMaxLEdit.text())
        new_plot.initialize_plot()
        
        new_plot.spec_set_type(axis_combo)
        new_plot.spec_make_active(True)
        new_plot.spec_change_lims_angle(angle_min, angle_max, instant_update=False)
        new_plot.spec_change_lims_doppler(dopplermin, dopplermax, instant_update=False)
        new_plot.spec_change_lims_range(rangemin, rangemax, instant_update=False)
        new_plot.change_zlims(zmin, zmax, instant_update=False)
        new_plot.update_changed_lims()
        new_plot.wireframe_change_state(self.showWireCheckbox.checkState() == QtCore.Qt.CheckState.Checked)

        self.add_plot_to_grid(new_plot, num_existing-1)
        self.all_plots.append(new_plot)

        return new_plot

    def receive_data(self, data: MultiRDPlotData | dict):

        # setup
        if isinstance(data, dict):
            self.first_setup_dict = data
            self.set_label_info()
            if "fps" in data and "num_frames_in_pd" in data:
                fps = data["fps"]
                framespd = data["num_frames_in_pd"]
                self.waiting_label.setText(f"Waiting for data... expected {int(framespd/fps)} seconds after start")
            if "num_saved_frames" in data:
                self.num_saved_frames = data["num_saved_frames"]
                if self.num_saved_frames < 0:
                    self.num_saved_frames = 100_000
                elif self.num_saved_frames < 1:
                    self.num_saved_frames = 1
            if "az_beam_angles" in data:
                self.angle_axis_values = data["az_beam_angles"]
            if "grid_cols_per_row" in data:
                self.cols_per_row = int(data["grid_cols_per_row"])
                if self.cols_per_row < 1:
                    self.cols_per_row = 2
            self.init_range_doppler_lineedit()

            return

        # data
        if self.rd_setup is None:
            self.rd_setup = data.multi_rd_setup
        
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
        if len(self.rd_plot_data_buffer) > self.num_saved_frames + 100:
            oldlen = len(self.rd_plot_data_buffer)
            self.rd_plot_data_buffer = self.rd_plot_data_buffer[-self.num_saved_frames:]
            num_removed = oldlen - len(self.rd_plot_data_buffer)
            self.frame_dropped_counter += num_removed
            self.curr_data_frame_inx = np.clip(self.curr_data_frame_inx - num_removed, 0, len(self.rd_plot_data_buffer)-1)
            self.set_label_curr_frame()

        if self.curr_label_frame_max != len(self.rd_plot_data_buffer):
            self.curr_label_frame_max = len(self.rd_plot_data_buffer)
            self.set_label_curr_frame()

    def initialize_axes(self):
        self.range_axis_values = np.linspace(0, self.num_bins_range * self.rd_setup.bin_length, num=self.num_bins_range) + self.rd_setup.range_offset
        self.doppler_axis_values = np.linspace(-self.num_bins_doppler / 2, self.num_bins_doppler / 2 - 1, num=self.num_bins_doppler) * (self.rd_setup.fps / self.rd_setup.fft_size)
        self.power_lim_vec = self.first_setup_dict.get("power_lim_vec", np.array([-60.0, 20.0]))

        self.range_axis = AxisConfig("Range", "m", self.range_axis_values[0], self.range_axis_values[-1], num_bins=self.num_bins_range)
        self.doppler_axis = AxisConfig("Doppler", "Hz", self.doppler_axis_values[0], self.doppler_axis_values[-1], num_bins=self.num_bins_doppler)
        self.power_axis = AxisConfig("Power", "dB", self.power_lim_vec[0], self.power_lim_vec[1], num_bins=10)
        self.angle_axis = AxisConfig("Angle", "deg", self.angle_axis_values[0], self.angle_axis_values[-1], num_bins=len(self.angle_axis_values))

        self.plotGridLayout.removeWidget(self.waiting_label)
        self.waiting_label.hide()

        self.init_range_doppler_lineedit()

        if "range_slices_to_plot" in self.first_setup_dict:
            slices = self.first_setup_dict["range_slices_to_plot"]
            self.unpicked_range_indices = np.unique(np.array([np.argmin(np.abs(self.range_axis_values - s)) for s in slices], dtype=int))
        
        if "doppler_slices_to_plot" in self.first_setup_dict:
            slices = self.first_setup_dict["doppler_slices_to_plot"]
            self.unpicked_doppler_indices = np.unique(np.array([np.argmin(np.abs(self.doppler_axis_values - s)) for s in slices], dtype=int))

        if "angle_slices_to_plot" in self.first_setup_dict:
            slices = self.first_setup_dict["angle_slices_to_plot"]
            self.unpicked_angle_indices = np.unique(np.array([np.argmin(np.abs(self.angle_axis_values - s)) for s in slices], dtype=int))

        self.initialized = True
    
    def remove_plots(self, dct: dict[int, SpecificSurfacePlot]):
        for plot in dct.values():
            if plot in self.all_plots:
                self.all_plots.remove(plot)
            self.plotGridLayout.removeWidget(plot.local_view)
            plot.local_view.hide()
            plot.local_view.deleteLater()
        dct.clear()

    def draw_data_frame(self, frame: MultiRDPlotData):
        
        if not self.initialized:
            self.is_single_angle = (frame.rd_data.shape[0] == 1)
            if self.is_single_angle:
                self.axisPickComboBox.setDisabled(True)
                self.angleMinLEdit.setDisabled(True)
                self.angleMaxLEdit.setDisabled(True)
                self.axisPickComboBox.setToolTip("Only one angle is present in the data, cannot change axis combination")
            self.num_bins_range = frame.rd_data.shape[1]
            self.num_bins_doppler = frame.rd_data.shape[2]
            self.initialize_axes()
        
        self.rd_plot_data = frame

        if self.curr_axis_combo == AxisCombos.RANGE_DOPPLER:
            for inx, angle_inx in enumerate(self.unpicked_angle_indices):
                plot = self.plot_or_make_new(AxisCombos.RANGE_DOPPLER, inx)
                plot.update_data(frame.rd_data[angle_inx])
        elif self.curr_axis_combo == AxisCombos.ANGLE_RANGE:
            for inx, doppler_inx in enumerate(self.unpicked_doppler_indices):
                plot = self.plot_or_make_new(AxisCombos.ANGLE_RANGE, inx)
                plot.update_data(frame.rd_data[:, :, doppler_inx])
        elif self.curr_axis_combo == AxisCombos.ANGLE_DOPPLER:
            for inx, range_inx in enumerate(self.unpicked_range_indices):
                plot = self.plot_or_make_new(AxisCombos.ANGLE_DOPPLER, inx)
                plot.update_data(frame.rd_data[:, range_inx, :])

        self.set_label_curr_frame()
        self.set_label_time()

    def get_title_string(self, index: int):
        if self.curr_axis_combo == AxisCombos.RANGE_DOPPLER:
            return f"Angle = {self.angle_axis_values[index]:.2f} deg"
        elif self.curr_axis_combo == AxisCombos.ANGLE_RANGE:
            return f"Doppler = {self.doppler_axis_values[index]:.2f} Hz"
        elif self.curr_axis_combo == AxisCombos.ANGLE_DOPPLER:
            return f"Range = {self.range_axis_values[index]:.2f} m"
        return ""

