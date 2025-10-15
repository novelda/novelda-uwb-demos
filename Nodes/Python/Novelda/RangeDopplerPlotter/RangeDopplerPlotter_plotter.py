from __future__ import annotations

import time
import numpy as np
from dataclasses import dataclass
from pathlib import Path

import pyqtgraph as pg

from pyqtgraph.Qt.QtWidgets import (
    QMainWindow, QWidget, QGridLayout, QVBoxLayout, QHBoxLayout, QLabel, QSlider, QLineEdit,
    QPushButton, QApplication, QCheckBox
    )
from pyqtgraph.Qt.QtGui import QDoubleValidator, QIcon, QImage, QPalette, QColor
import pyqtgraph.Qt.QtCore as QtCore

from RangeDopplerPlotter.surface_plot_widget import Matrix3DPlot, AxisConfig, CameraState

ALL_TX_OFF = 2**16-1

@dataclass
class RDRawSetup:
    num_tx_channels : int
    num_rx_channels : int
    num_bins_range  : int
    num_bins_doppler: int
    fps             : int
    fft_size        : int
    range_offset    : float
    bin_length      : float
    zlim_vec        : np.ndarray[float, 2]
    convert2pwr     : bool

@dataclass
class RDRawPlotData:
    RDRawSetup: RDRawSetup
    rd_dict_data   : dict[tuple[int, int], np.ndarray] # for tx0rx0, (0,0) : dataArray
    trx_mask  : np.ndarray
    timestamp : float
    seq_num   : int

class KeyPressFilter(QtCore.QObject):
    def __init__(self, callback):
        super().__init__()
        self._callback = callback

    def eventFilter(self, obj, event: pg.QtGui.QKeyEvent):
        if event.type() == QtCore.QEvent.KeyPress:
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

class RangeDopplerPlotter:

    def __init__(self, shm_on_exit=None):
        self.plot = None
        self.plot_linear_scale: bool       = False
        self.shm_on_exit = shm_on_exit

        self.x_lim_vec: np.ndarray = None
        self.y_lim_vec: np.ndarray = None
        self.z_lim_vec: np.ndarray = None
        
        self.rd_setup: RDRawSetup = None
        self.rd_plot_data: RDRawPlotData = None

        self.app = None
        self.initialized = False

        self._key_filter = None
        self.mainwin = None

        self.num_saved_frames = 100

        self.paused = False
        self.curr_data_frame_inx = 0
        self.curr_label_frame_max = 0

        self.first_setup_dict = None
        self.first_timestamp = None
        self.is_live = True

        self.did_first_lims_change = False

        self.frame_received_counter = 0
        self.frame_dropped_counter = 0

        # timestamp received : RDRawPlotData
        self.rd_plot_data_buffer: list[RDRawPlotData] = []
        self.plot_dict: dict[tuple[int, int], Matrix3DPlot] = {}

        self.range_axis = AxisConfig("Range", "m", 0, 100, 100)
        self.doppler_axis = AxisConfig("Doppler", "Hz", -50, 50, 100)
        self.power_axis = AxisConfig("Power", "dB", -100, 0, 100)
        from PySide6.QtCore import QLocale
        QLocale.setDefault(QLocale(QLocale.English, QLocale.UnitedStates))

        logo_img_fp = Path(__file__).resolve().parent.parent.parent.parent.parent / "Demos" \
            / "Resources" / "Images" / "Novelda_logo_hvit_150dpi.png"
        self.logo_img = QImage(str(logo_img_fp))

    def make_double_lineedit(self, in_box, first_label, second_label, width=100):
        line_edit_w = QWidget(self.mainwidget)
        line_edit_lay = QHBoxLayout(line_edit_w)
        line_edit_lay.setContentsMargins(0, 0, 0, 0)
        in_box.addWidget(line_edit_w)

        first_label_widget = QLabel(first_label, line_edit_w)
        line_edit_lay.addWidget(first_label_widget, 1)

        second_lineedit = QLineEdit(line_edit_w)
        second_lineedit.setValidator(QDoubleValidator())
        second_lineedit.setFixedWidth(width)
        line_edit_lay.addWidget(second_lineedit, 1, alignment=QtCore.Qt.AlignLeft)

        second_label_widget = QLabel(second_label, line_edit_w)
        line_edit_lay.addWidget(second_label_widget, 1)

        return first_label_widget, second_lineedit, second_label_widget

    def init_window(self):
        if self.app is None:
            self.app = QApplication([])
        if self.mainwin is not None:
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

        self.app.setPalette(pal)

        self.mainwin = PlotMainWin(self.exit)
        self.mainwin.setWindowTitle("Range Doppler Plotter")

        self.mainwidget = QWidget(self.mainwin)
        self.mainwin.setCentralWidget(self.mainwidget)
        vbox_layout = QVBoxLayout(self.mainwidget)

        # top 90%
        grid_container = QWidget(self.mainwidget)
        self.gridLayout = QGridLayout(grid_container)
        self.gridLayout.setSpacing(2)
        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        vbox_layout.addWidget(grid_container, 95)
        vbox_layout.setContentsMargins(0, 0, 0, 0)

        # bottom 10%
        controls_first_w = QWidget(self.mainwidget)
        vbox_layout.addWidget(controls_first_w, 5)
        controls_first_hbox = QHBoxLayout(controls_first_w)
        controls_first_hbox.setContentsMargins(0, 0, 0, 0)

        # info label
        self.infolabel = QLabel("", parent=self.mainwidget)
        self.infolabel.setStyleSheet(f"""
            QLabel {{
                color: #b1b7c0;
                font-size: 10pt;
            }}
        """)

        self.live_or_playback_label = QLabel("", parent=self.mainwidget)
        self.live_or_playback_label.setContentsMargins(1, 5, 1, 5)

        self.time_label = QLabel("", parent=self.mainwidget)
        self.time_label.setStyleSheet(self.infolabel.styleSheet())
        self.time_label.setContentsMargins(1, 5, 1, 5)

        self.hotkey_label = QLabel(text=("Space: play/pause"
                                   "\nLeft/Right Arrow: change current RD plot"
                                   "\nXYZ: orthographic projection on axes"
                                   "\nR: reset camera to default"
                                   "\nRight-Click: place plot marker"
                                   "\nWASD: move plot marker"), 
                                   parent=self.mainwidget
                                    )
        self.hotkey_label.setStyleSheet(self.infolabel.styleSheet())
        self.hotkey_label.setContentsMargins(1, 10, 1, 5)

        self.logo_label = QLabel()
        self.logo_label.setPixmap(pg.QtGui.QPixmap.fromImage(self.logo_img).scaledToWidth(100, QtCore.Qt.SmoothTransformation))
        img_ar = self.logo_img.width() / self.logo_img.height()
        # self.logo_label.setMaximumWidth(100)
        # self.logo_label.setMaximumHeight(int(100/img_ar))

        controls_first_hbox.addStretch(2)
        controls_first_hbox.addWidget(self.logo_label, 1, alignment=QtCore.Qt.AlignLeft | QtCore.Qt.AlignCenter)
        controls_first_hbox.addStretch(20)
        controls_first_hbox.addWidget(self.hotkey_label, 1, alignment=QtCore.Qt.AlignLeft | QtCore.Qt.AlignTop)
        controls_first_hbox.addStretch(2)

        # vert box for live/playback label, and info label below

        live_play_w = QWidget(self.mainwidget)
        live_play_vbox = QVBoxLayout(live_play_w)
        controls_first_hbox.addWidget(live_play_w, 1, alignment=QtCore.Qt.AlignLeft | QtCore.Qt.AlignTop)

        live_play_vbox.setContentsMargins(0, 0, 0, 0)
        live_play_vbox.addWidget(self.live_or_playback_label, 1)
        live_play_vbox.addWidget(self.infolabel, 1)
        live_play_vbox.addStretch(5)

        # -----------------

        controls_first_hbox.addStretch(1)

        # left controls, xy min max
        controls_left_w = QWidget(self.mainwidget)
        controls_left_vbox = QVBoxLayout(controls_left_w)
        controls_first_hbox.addWidget(controls_left_w)

        # right controls, z min max, frame
        controls_right_w = QWidget(self.mainwidget)
        controls_right_vbox = QVBoxLayout(controls_right_w)
        controls_first_hbox.addWidget(controls_right_w)

        self.rangemax_lineedit = self.make_double_lineedit(controls_left_vbox, "Range max:\t", "m")[1]
        self.rangemin_lineedit = self.make_double_lineedit(controls_left_vbox, "Range min:\t", "m")[1]

        self.dopplermax_lineedit = self.make_double_lineedit(controls_left_vbox, "Doppler max:\t", "Hz")[1]
        self.dopplermin_lineedit = self.make_double_lineedit(controls_left_vbox, "Doppler min:\t", "Hz")[1]

        self.zmax_lineedit = self.make_double_lineedit(controls_right_vbox, "Power max:", "dB")[1]
        self.zmin_lineedit = self.make_double_lineedit(controls_right_vbox, "Power min:", "dB")[1]

        _, self.frame_lineedit, self.frame_buffered_label = self.make_double_lineedit(
            controls_right_vbox, "Current RD Plot / total buffered:", "/", width=80)

        # reset limits button, grid label, grid checkbox
        reset_wiref_check_w = QWidget(self.mainwidget)
        reset_wiref_check_hbox = QHBoxLayout(reset_wiref_check_w)
        controls_right_vbox.addWidget(reset_wiref_check_w)

        reset_limits_btn = QPushButton("Reset Limits", self.mainwidget)
        reset_limits_btn.setMaximumWidth(100)
        reset_limits_btn.released.connect(self.reset_limits)

        reset_wiref_check_hbox.addWidget(reset_limits_btn)

        wireframe_checkbox = QCheckBox("Show wireframe", tristate=False)
        wireframe_checkbox.setCheckState(QtCore.Qt.CheckState.Unchecked)
        reset_wiref_check_hbox.addWidget(wireframe_checkbox)
        wireframe_checkbox.stateChanged.connect(self.wireframe_check_changed)

        reset_wiref_check_hbox.addStretch(20)

        # connect line edits to limits_edited
        self.rangemin_lineedit.returnPressed.connect(self.limits_edited)
        self.rangemax_lineedit.returnPressed.connect(self.limits_edited)
        self.dopplermin_lineedit.returnPressed.connect(self.limits_edited)
        self.dopplermax_lineedit.returnPressed.connect(self.limits_edited)
        self.zmin_lineedit.returnPressed.connect(self.limits_edited)
        self.zmax_lineedit.returnPressed.connect(self.limits_edited)
        self.frame_lineedit.returnPressed.connect(self.frame_edited) 

        screen_size = self.app.primaryScreen().size()
        best_ar = 16/10
        self.mainwin.resize(int(screen_size.height()*best_ar), int(screen_size.height()*0.9))
        self.mainwin.move(0, 0)
        self.mainwin.show()

        self.mainwidget.setFocus()

        # add dummy plot to initialize opengl context
        dummy_plot = Matrix3DPlot(self.range_axis, self.doppler_axis, self.power_axis)
        self.gridLayout.addWidget(dummy_plot.local_view, 0, 0)
        self.gridLayout.removeWidget(dummy_plot.local_view)
        dummy_plot.local_view.deleteLater()

        self.waiting_label = QLabel("Waiting for data...", self.mainwidget)
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
        self.gridLayout.addWidget(self.waiting_label, 0, 0)

        controls_first_hbox.addWidget(self.time_label, 1, alignment=QtCore.Qt.AlignLeft | QtCore.Qt.AlignTop)

        controls_first_hbox.addStretch(20)
        controls_left_vbox.addStretch(100)
        controls_right_vbox.addStretch(100)

        if self._key_filter is None:
            self._key_filter = KeyPressFilter(self.keyPressEvent)
            self.app.installEventFilter(self._key_filter)
    
    def wireframe_check_changed(self, newstate: QtCore.Qt.CheckState):
        for plot in self.plot_dict.values():
            plot.wireframe_change_state(newstate == QtCore.Qt.CheckState.Checked.value)
    
    def frame_edited(self):
        if not self.initialized:
            return
        
        curr_frame = int(self.frame_lineedit.text()) - 1
        if 0 <= curr_frame < len(self.rd_plot_data_buffer):
            self.paused = True
            self.curr_data_frame_inx = curr_frame
            self.draw_data_frame(self.rd_plot_data_buffer[self.curr_data_frame_inx])
        else:
            self.frame_lineedit.setText(f"{int(self.curr_data_frame_inx + 1)}")

    def set_label_time(self):
        if self.first_timestamp is None or not self.initialized:
            return

        curr_frame_ts = self.rd_plot_data_buffer[self.curr_data_frame_inx].timestamp
        curr_frame_seq = self.rd_plot_data_buffer[self.curr_data_frame_inx].seq_num
        timetxt = time.strftime('%Y.%m.%d %H:%M:%S', time.localtime(curr_frame_ts/1000))
        rel_time_txt = (curr_frame_ts - self.first_timestamp)/1000
        self.time_label.setText(f"{timetxt}\nSince Start: {rel_time_txt:.1f}s\nSequence number: {curr_frame_seq}"
            f"\nNum frames received: {self.frame_received_counter}"
            f"\nNum frames dropped: {self.frame_dropped_counter}"
            )

    def reset_limits(self):
        if not self.initialized:
            return
        
        range_const_start = self.first_setup_dict.get("default_start_range", 0)

        for plot in self.plot_dict.values():
            if range_const_start > 0:
                plot.change_xlims(range_const_start, self.range_axis.max_val)
            else:
                plot.change_xlims(self.range_axis.min_val, self.range_axis.max_val)

            plot.change_ylims(self.doppler_axis.min_val, self.doppler_axis.max_val)
            plot.change_zlims(self.rd_setup.zlim_vec[0], self.rd_setup.zlim_vec[1])

        self.init_range_doppler_lineedit()
    
    def set_label_info(self):
        frames_btw_pd = self.first_setup_dict["frames_between_pd"]
        num_frames_in_pd = self.first_setup_dict["num_frames_in_pd"]
        fps = self.first_setup_dict["fps"]
        enable_dc_removal = self.first_setup_dict["enable_dc_removal"]
        is_live = self.first_setup_dict.get("is_live", True)
        self.infolabel.setText(
            (f"FPS: {fps}"
            f"\nRangeDoppler integration time: {num_frames_in_pd/fps:.1f} s"
            f"\nRangeDoppler update rate: {frames_btw_pd/fps:.1f} s"
            f"\nEnable DC Removal: {enable_dc_removal}")
        )

        liveplay_color = "#82f17e" if is_live else "#369ee4"
        liveplay_text = "Live" if is_live else "Playback"

        self.live_or_playback_label.setStyleSheet(f"""
        QLabel {{
            color: {liveplay_color};
            font-size: 14pt;
        }}
        """)
        self.live_or_playback_label.setText(liveplay_text)
            
    def set_label_curr_frame(self):
        self.frame_lineedit.setText(f"{int(self.curr_data_frame_inx + 1)}")
        self.frame_buffered_label.setText(f"/ {self.curr_label_frame_max}")

    def init_range_doppler_lineedit(self):
        self.dopplermin_lineedit.setText(f"{self.doppler_axis.min_val:.2f}")
        self.dopplermax_lineedit.setText(f"{self.doppler_axis.max_val:.2f}")

        range_const_start = self.first_setup_dict.get("default_start_range", 0)
        if range_const_start > 0:
            self.rangemin_lineedit.setText(f"{range_const_start:.2f}")
        else:
            self.rangemin_lineedit.setText(f"{self.range_axis.min_val:.2f}")
        self.rangemax_lineedit.setText(f"{self.range_axis.max_val:.2f}")

        self.zmin_lineedit.setText(f"{self.power_axis.curr_min_val:.2f}")
        self.zmax_lineedit.setText(f"{self.power_axis.curr_max_val:.2f}")

    def limits_edited(self):
        if not self.initialized:
            return

        rangemin = float(self.rangemin_lineedit.text())
        rangemax = float(self.rangemax_lineedit.text())
        dopplermin = float(self.dopplermin_lineedit.text())
        dopplermax = float(self.dopplermax_lineedit.text())
        zmin = float(self.zmin_lineedit.text())
        zmax = float(self.zmax_lineedit.text())

        # ensure the new limits are valid
        if rangemin < rangemax and dopplermin < dopplermax and zmin < zmax:
            for plot in self.plot_dict.values():
                plot.change_xlims(rangemin, rangemax)
                plot.change_ylims(dopplermin, dopplermax)
                plot.change_zlims(zmin, zmax)
        else:
            # reset line edits
            self.rangemin_lineedit.setText(f"{self.range_axis.min_val:.2f}")
            self.rangemax_lineedit.setText(f"{self.range_axis.max_val:.2f}")
            self.dopplermin_lineedit.setText(f"{self.doppler_axis.min_val:.2f}")
            self.dopplermax_lineedit.setText(f"{self.doppler_axis.max_val:.2f}")
            self.zmin_lineedit.setText(f"{self.power_axis.curr_min_val:.2f}")
            self.zmax_lineedit.setText(f"{self.power_axis.curr_max_val:.2f}")

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
        for plot in self.plot_dict.values():
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
        self.frame_lineedit.setText(f"{int(self.curr_data_frame_inx + 1)}")

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

    def change_range_lims(self, xlim_min, xlim_max):
        if self.range_axis.min_val != xlim_min or self.range_axis.max_val != xlim_max:
            for plot in self.plot_dict.values():
                plot.change_xlims(xlim_min, xlim_max)
    
    def change_doppler_lims(self, ylim_min, ylim_max):
        if self.doppler_axis.min_val != ylim_min or self.doppler_axis.max_val != ylim_max:
            for plot in self.plot_dict.values():
                plot.change_ylims(ylim_min, ylim_max)

    def plot_or_make_new(self, txrx: tuple[int, int]):
        if txrx in self.plot_dict:
            return self.plot_dict[txrx]

        new_plot = Matrix3DPlot(self.range_axis, self.doppler_axis, self.power_axis, 
                                self.get_title_string(txrx[0], txrx[1]), axis_as_reference=True)
        self.plot_dict[txrx] = new_plot

        self.gridLayout.addWidget(new_plot.local_view, txrx[0], txrx[1])
        new_plot.initialize_plot()

        return new_plot

    def receive_data(self, data: RDRawPlotData | dict):

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

            return

        # data
        if self.rd_setup is None:
            self.rd_setup = data.RDRawSetup
        
        if self.first_timestamp is None:
            self.first_timestamp = data.timestamp

        self.rd_plot_data_buffer.append(data)
        self.frame_received_counter += 1

    def update(self):
        if not len(self.rd_plot_data_buffer):
            return

        if not self.paused:
            self.curr_data_frame_inx = len(self.rd_plot_data_buffer) - 1
            if not (self.rd_plot_data is self.rd_plot_data_buffer[self.curr_data_frame_inx]):
                self.draw_data_frame(self.rd_plot_data_buffer[self.curr_data_frame_inx])

        # Limit the buffer size to avoid memory issues
        bufflim = self.num_saved_frames + 100
        if len(self.rd_plot_data_buffer) > bufflim:
            oldlen = len(self.rd_plot_data_buffer)
            self.rd_plot_data_buffer = self.rd_plot_data_buffer[-self.num_saved_frames:]
            num_removed = oldlen - len(self.rd_plot_data_buffer)
            self.frame_dropped_counter += num_removed
            self.curr_data_frame_inx = np.clip(self.curr_data_frame_inx-num_removed, 0, len(self.rd_plot_data_buffer)-1)
            self.set_label_curr_frame()

        if self.curr_label_frame_max != len(self.rd_plot_data_buffer):
            self.curr_label_frame_max = len(self.rd_plot_data_buffer)
            self.set_label_curr_frame()

    def initialize_axes(self):
        self.x_lim_vec = np.array([0, self.rd_setup.num_bins_range * self.rd_setup.bin_length]) + self.rd_setup.range_offset
        self.y_lim_vec = np.array([-self.rd_setup.num_bins_doppler / 2, self.rd_setup.num_bins_doppler / 2 - 1]) * (self.rd_setup.fps / self.rd_setup.fft_size)
        self.z_lim_vec = self.rd_setup.zlim_vec

        if not self.z_lim_vec.size == 2:
            self.z_lim_vec = np.array([-70.0, 10.0])

        self.range_axis = AxisConfig("Range", "m", self.x_lim_vec[0], self.x_lim_vec[1], num_bins=self.rd_setup.num_bins_range)
        self.doppler_axis = AxisConfig("Doppler", "Hz", self.y_lim_vec[0], self.y_lim_vec[1], num_bins=self.rd_setup.num_bins_doppler)
        self.power_axis = AxisConfig("Power", "dB", self.z_lim_vec[0], self.z_lim_vec[1], num_bins=10)

        self.gridLayout.removeWidget(self.waiting_label)
        self.waiting_label.hide()

        self.test_num_loops = 5

        self.init_range_doppler_lineedit()

        self.initialized = True

    def draw_data_frame(self, frame: RDRawPlotData):
        if not self.initialized:
            self.initialize_axes()

        self.rd_plot_data = frame
        for txrx in frame.rd_dict_data.keys():
            plot = self.plot_or_make_new(txrx)
            data_slice = frame.rd_dict_data[txrx]

            if data_slice is None:
                continue

            # Update the plot with the new data
            plot.update_data(data_slice)

        if not self.did_first_lims_change:
            self.did_first_lims_change = True

            if "default_start_range" in self.first_setup_dict:
                self.rangemin_lineedit.setText(f"{self.first_setup_dict['default_start_range']:.2f}")

            if "x_lim_vec" in self.first_setup_dict:
                self.rangemin_lineedit.setText(f"{self.first_setup_dict['x_lim_vec'][0]:.2f}")
                self.rangemax_lineedit.setText(f"{self.first_setup_dict['x_lim_vec'][1]:.2f}")
            if "y_lim_vec" in self.first_setup_dict:
                self.dopplermin_lineedit.setText(f"{self.first_setup_dict['y_lim_vec'][0]:.2f}")
                self.dopplermax_lineedit.setText(f"{self.first_setup_dict['y_lim_vec'][1]:.2f}")
            
            self.limits_edited()

        self.set_label_curr_frame()
        self.set_label_time()

    def get_title_string(self, tx_channel, rx_channel):
        if self.rd_plot_data.trx_mask[0, 1] == ALL_TX_OFF:
            # Check for AllTxOff
            return f"RangeDoppler - TXOff{tx_channel-1}RX{rx_channel-1}"
         
        return f"RangeDoppler - TX{tx_channel}RX{rx_channel}"

