from __future__ import annotations

import time
import numpy as np
from dataclasses import dataclass
from pathlib import Path

import os
# Suppress Qt warnings before importing pyqtgraph
os.environ['QT_LOGGING_RULES'] = "qt.core.qobject.connect=false"

import pyqtgraph as pg

from pyqtgraph.Qt.QtWidgets import (
    QMainWindow, QWidget, QGridLayout, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QApplication, QCheckBox
    )
from pyqtgraph.Qt.QtGui import QDoubleValidator, QIntValidator, QIcon, QImage, QPalette, QColor
import pyqtgraph.Qt.QtCore as QtCore

from BasebandPlotter.xy_plot_widget import XY2DPlotWidget

from BasebandPlotter.generatedBasebandUI import Ui_BasebandUIwin

ALL_TX_OFF = 2**16-1

@dataclass
class BasebandDataFrame:
    power_data_dict: dict[(int, int, int), np.ndarray]
    db_data_dict: dict[(int, int, int), np.ndarray]
    trx_vec: np.ndarray
    timestamp: int
    seq_num: int

class KeyPressFilter(QtCore.QObject):
    def __init__(self, callback):
        super().__init__()
        self._callback = callback

    def eventFilter(self, obj, event: pg.QtGui.QKeyEvent):
        if event.type() == QtCore.QEvent.KeyPress:
            return self._callback(event)

        return False

class PlotMainWin(QMainWindow, Ui_BasebandUIwin):

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

class BasebandPlotter:

    def __init__(self, shm_on_exit=None):
        self.plot = None
        self.plot_linear_scale: bool = False
        self.shm_on_exit = shm_on_exit
        
        self.app = None
        self.initialized = False

        self._key_filter = None
        self.mainwin = None

        self.num_saved_frames = -1

        self.paused = False

        self.curr_data_frame_inx = 0
        self.curr_label_frame_max = 0

        self.first_setup_dict = None
        self.first_timestamp = None
        self.is_live = True

        self.did_first_lims_change = False

        self.xaxis_vals: np.ndarray = None

        self.xaxis_lims: np.ndarray = None
        self.yaxis_lims: np.ndarray = None

        self.xaxis_name: str = "Range"
        self.xaxis_name_unit: str = "m"
        self.yaxis_name: str = "Power"
        self.yaxis_name_unit: str = "dB"
        self.yaxis_name_lin_unit: str = "lin"

        self.skip_n_frames = 0
        self.skip_n_counter = 0
        self.skip_all_to_draw = []
        self.skip_curr_drawn = []

        self.rx_plot_colors = [ "#C94848", "#43A343" ]

        self.frame_received_counter = 0
        self.frame_dropped_counter = 0

        self.curr_bbif_data: BasebandDataFrame = None

        # timestamp received : RDRawPlotData
        self.bbif_plot_data_buffer: list[BasebandDataFrame] = []
        self.per_plot_data_reg: dict[(int, int), BasebandDataFrame] = {}

        # (chipnum, txactive) -> plot widget
        self.plot_dict: dict[(int, int), XY2DPlotWidget] = {}

        from PySide6.QtCore import QLocale
        QLocale.setDefault(QLocale(QLocale.English, QLocale.UnitedStates))

        logo_img_fp = Path(__file__).resolve().parent.parent.parent.parent.parent / "Demos" \
            / "Resources" / "Images" / "Novelda_logo_hvit_150dpi.png"
        self.logo_img = QImage(str(logo_img_fp))


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
        self.mainwin.setWindowTitle("Baseband Plotter")

        self.mainwin.setupUi(self.mainwin)

        # self.infolabel.setStyleSheet(f"""
        #     QLabel {{
        #         color: #b1b7c0;
        #         font-size: 10pt;
        #     }}
        # """)

        self.mainwin.hotkeyLabel.setText("Space: play/pause"
                                   "\nLeft/Right Arrow: change current RD plot"
                                   "\nLeft Click: mark nearest point"
                                   "\nA/D: move marker")


        self.mainwin.logoLabel.setPixmap(pg.QtGui.QPixmap.fromImage(self.logo_img).scaledToWidth(100, QtCore.Qt.SmoothTransformation))
        img_ar = self.logo_img.width() / self.logo_img.height()

        # -----------------

        self.mainwin.linearScaleCheckbox.stateChanged.connect(self.lin_db_checkbox_changed)
        self.mainwin.resetLimitsBtn.clicked.connect(self.reset_limits)

        # connect line edits to limits_edited
        self.mainwin.rangeMinLEdit.returnPressed.connect(self.limits_edited)
        self.mainwin.rangeMaxLEdit.returnPressed.connect(self.limits_edited)
        self.mainwin.powerMaxLEdit.returnPressed.connect(self.limits_edited)
        self.mainwin.powerMinLEdit.returnPressed.connect(self.limits_edited)
        self.mainwin.currFrameLEdit.returnPressed.connect(self.frame_edited)

        doubleValid = QDoubleValidator()
        self.mainwin.rangeMinLEdit.setValidator(doubleValid)
        self.mainwin.rangeMaxLEdit.setValidator(doubleValid)
        self.mainwin.powerMinLEdit.setValidator(doubleValid)
        self.mainwin.powerMaxLEdit.setValidator(doubleValid)

        self.mainwin.currFrameLEdit.setValidator(QIntValidator(1, 1_000_000_000))

        screen_size = self.app.primaryScreen().size()
        best_ar = 20/10
        self.mainwin.resize(int(screen_size.height()*best_ar*0.6), int(screen_size.height()*0.6))
        self.mainwin.move(0, 0)
        self.mainwin.show()

        self.mainwin.centralWidget().setFocus()

        if self._key_filter is None:
            self._key_filter = KeyPressFilter(self.keyPressEvent)
            self.app.installEventFilter(self._key_filter)
    
    def lin_db_checkbox_changed(self):
        self.plot_linear_scale = self.mainwin.linearScaleCheckbox.isChecked()

        # might seem like spaghetti, but it actually works,
        # in draw_data_frame it will set self.per_plot_data_reg[txrx] = frame,
        # txrx is this txrx and frame is this frame, so no change
        for chiptx, data in self.per_plot_data_reg.items():
            self.draw_data_frame(data)

        if self.plot_linear_scale:
            for plot in self.plot_dict.values():
                plot.set_yaxis_label_unit(self.yaxis_name, self.yaxis_name_lin_unit)

        else:
            for plot in self.plot_dict.values():
                plot.set_yaxis_label_unit(self.yaxis_name, self.yaxis_name_unit)
    
    def frame_edited(self):
        if not self.initialized:
            return
        
        self.mainwin.currFrameLEdit
        
        curr_frame = int(self.mainwin.currFrameLEdit.text()) - 1
        if 0 <= curr_frame < len(self.bbif_plot_data_buffer):
            self.paused = True
            self.curr_data_frame_inx = curr_frame
            self.draw_data_frame(self.bbif_plot_data_buffer[self.curr_data_frame_inx])
        else:
            self.mainwin.currFrameLEdit.setText(f"{int(self.curr_data_frame_inx + 1)}")

    def set_label_time(self):
        if self.first_timestamp is None or not self.initialized:
            return

        curr_frame_ts = self.bbif_plot_data_buffer[self.curr_data_frame_inx].timestamp
        curr_frame_seq = self.bbif_plot_data_buffer[self.curr_data_frame_inx].seq_num
        timetxt = time.strftime('%Y.%m.%d %H:%M:%S', time.localtime(curr_frame_ts/1000))
        rel_time_txt = (curr_frame_ts - self.first_timestamp)/1000
        self.mainwin.seqNumTimeLabel.setText(
            f"{timetxt}\nSince Start: {rel_time_txt:.1f}s\nSequence number: {curr_frame_seq}"
            f"\nNum frames received: {self.frame_received_counter}"
            f"\nNum frames dropped: {self.frame_dropped_counter}"
            )

    def reset_limits(self):
        if not self.initialized:
            return

        for plot in self.plot_dict.values():
            plot.change_xlims(self.xaxis_lims[0], self.xaxis_lims[1])
            plot.change_ylims(self.yaxis_lims[0], self.yaxis_lims[1])

        self.init_lims_lineedit()
    
    def set_label_info(self):
        
        # get shit and put into label
        fps = self.first_setup_dict["fps"]
        is_dcremoval = self.first_setup_dict.get("enable_dc_removal", False)

        self.mainwin.infoParamLabel.setText(
            f"FPS: {fps}"
            f"\nDC Removal: {'Enabled' if is_dcremoval else 'Disabled'}"
            )

        is_live = self.first_setup_dict["is_live"]

        liveplay_color = "#82f17e" if is_live else "#369ee4"
        liveplay_text = "Live" if is_live else "Playback"

        self.mainwin.liveOrPlaybackLabel.setStyleSheet(f"""
        QLabel {{
            color: {liveplay_color};
            font-size: 14pt;
        }}
        """)
        self.mainwin.liveOrPlaybackLabel.setText(liveplay_text)
            
    def set_label_curr_frame(self):
        self.mainwin.currFrameLEdit.setText(f"{int(self.curr_data_frame_inx + 1)}")
        self.mainwin.totalNumFramesBuffLabel.setText(f"/ {self.curr_label_frame_max}")

    def init_lims_lineedit(self):
        self.mainwin.rangeMinLEdit.setText(f"{self.xaxis_lims[0]:.2f}")
        self.mainwin.rangeMaxLEdit.setText(f"{self.xaxis_lims[1]:.2f}")
        self.mainwin.powerMinLEdit.setText(f"{self.yaxis_lims[0]:.2f}")
        self.mainwin.powerMaxLEdit.setText(f"{self.yaxis_lims[1]:.2f}")

    def limits_edited(self):
        if not self.initialized:
            return

        xmin = float(self.mainwin.rangeMinLEdit.text())
        xmax = float(self.mainwin.rangeMaxLEdit.text())
        ymin = float(self.mainwin.powerMinLEdit.text())
        ymax = float(self.mainwin.powerMaxLEdit.text())

        # ensure the new limits are valid
        if xmin < xmax and ymin < ymax:
            for plot in self.plot_dict.values():
                plot.change_xlims(xmin, xmax)
                plot.change_ylims(ymin, ymax)
        else:
            # reset line edits
            self.mainwin.rangeMinLEdit.setText(f"{self.xaxis_lims[0]:.2f}")
            self.mainwin.rangeMaxLEdit.setText(f"{self.xaxis_lims[1]:.2f}")
            self.mainwin.powerMinLEdit.setText(f"{self.yaxis_lims[0]:.2f}")
            self.mainwin.powerMaxLEdit.setText(f"{self.yaxis_lims[1]:.2f}")

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

        return False

    def move_frame(self, direction: int):
        if not self.initialized or len(self.bbif_plot_data_buffer) <= 1:
            return
        self.paused = True

        self.curr_data_frame_inx += direction
        if self.curr_data_frame_inx < 0:
            self.curr_data_frame_inx = 0
        elif self.curr_data_frame_inx >= len(self.bbif_plot_data_buffer):
            self.curr_data_frame_inx = len(self.bbif_plot_data_buffer) - 1

        self.draw_data_frame(self.bbif_plot_data_buffer[self.curr_data_frame_inx])
        self.mainwin.currFrameLEdit.setText(f"{int(self.curr_data_frame_inx + 1)}")

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
    
    def plot_or_make_new(self, txrx_key: tuple[int, int, int]):
        # txrx: (chipnum, txactive, rxactive)

        chip, tx, rx = txrx_key
        if tx == ALL_TX_OFF:
            # handle AllTxOff
            pass

        if (chip, tx) in self.plot_dict:
            return self.plot_dict[(chip, tx)]

        new_plot = XY2DPlotWidget(
            x_axis_name=self.xaxis_name,
            y_axis_name=self.yaxis_name,
            xaxis_unit=self.xaxis_name_unit,
            y_axis_unit=self.yaxis_name_unit,
            plot_label=self.get_title_string(txrx_key),
            xrange=self.xaxis_lims,
            yrange=self.yaxis_lims,
            xmark_prefix="Rangebin ",
            ymark_prefix=None,
            plot_mark_prefix="Rx"
        )

        self.plot_dict[(chip, tx)] = new_plot

        self.mainwin.plotGridLayout.addWidget(new_plot, chip, tx)
        new_plot.initialize_plot()

        return new_plot

    def receive_data(self, data: dict | BasebandDataFrame):
        # (chipnum, txactive, rxactive) -> data

        # setup
        if self.first_setup_dict is None:
            if isinstance(data, dict):
                # treat it as setup data
                self.first_setup_dict = data
                self.set_label_info()
                if "num_saved_frames" in data:
                    self.num_saved_frames = data["num_saved_frames"]
                    if self.num_saved_frames < 0:
                        self.num_saved_frames = 100_000
                    elif self.num_saved_frames < 1:
                        self.num_saved_frames = 1
                
                if "fps" in data:
                    self.skip_n_counter = int(data["fps"] / 50)

                return
        
        if self.first_timestamp is None:
            self.first_timestamp = data.timestamp

        self.bbif_plot_data_buffer.append(data)
        self.frame_received_counter += 1

        # logic for skipping frames to draw, to keep up with live data
        # make sure to draw all TX and then skip some frames

        lasttx = data.trx_vec[1] # if this is a new tx, add it to the list of all to draw
        if lasttx not in self.skip_all_to_draw:
            self.skip_all_to_draw.append(lasttx)
        
        if len(self.skip_all_to_draw) == len(self.skip_curr_drawn) and self.skip_n_frames > 0:
            if self.skip_n_counter >= self.skip_n_frames:
                self.skip_n_counter = 0
                self.skip_curr_drawn.clear()
            else:
                self.skip_n_counter += 1
                return

        if lasttx not in self.skip_curr_drawn:
            self.skip_curr_drawn.append(lasttx)

        if not self.paused:
            self.curr_data_frame_inx = len(self.bbif_plot_data_buffer) - 1
            if self.curr_bbif_data is self.bbif_plot_data_buffer[self.curr_data_frame_inx]:
                return
            self.draw_data_frame(self.bbif_plot_data_buffer[self.curr_data_frame_inx])

        if not self.initialized:
            self.initialize_axes()

    def update(self):
        if not len(self.bbif_plot_data_buffer):
            return
        
        fps = self.first_setup_dict.get("fps", 20)

        # Limit the buffer size to avoid memory issues
        if len(self.bbif_plot_data_buffer) > self.num_saved_frames + fps*5:
            oldlen = len(self.bbif_plot_data_buffer)
            self.bbif_plot_data_buffer = self.bbif_plot_data_buffer[-self.num_saved_frames:]
            num_removed = oldlen - len(self.bbif_plot_data_buffer)
            self.frame_dropped_counter += num_removed
            self.curr_data_frame_inx = np.clip(self.curr_data_frame_inx - num_removed, 0, len(self.bbif_plot_data_buffer)-1)
            self.set_label_curr_frame()
        
        if self.curr_label_frame_max != len(self.bbif_plot_data_buffer):
            self.curr_label_frame_max = len(self.bbif_plot_data_buffer)
            self.set_label_curr_frame()

    def initialize_axes(self):

        if not len(self.bbif_plot_data_buffer) or self.first_setup_dict is None:
            return
        
        first_data = self.bbif_plot_data_buffer[0].power_data_dict

        first_rx_data = first_data.values().__iter__().__next__()

        num_rangebins = first_rx_data.shape[-1]
        bin_length = self.first_setup_dict["bin_length"]

        self.x_axis_vals = np.linspace(0, bin_length*num_rangebins, num_rangebins) \
            + self.first_setup_dict["range_offset"]
        
        self.xaxis_lims = np.array([self.x_axis_vals[0], self.x_axis_vals[-1]])
        if "x_lim_vec" in self.first_setup_dict:
            xlim = self.first_setup_dict["x_lim_vec"]
            if xlim.size == 2:
                self.xaxis_lims = xlim
        
        if "default_start_range" in self.first_setup_dict:
            dsr = self.first_setup_dict["default_start_range"]
            if self.xaxis_lims[0] < dsr < self.xaxis_lims[1]:
                self.xaxis_lims[0] = dsr
        
        self.yaxis_lims = np.array([-100, 20])
        if "y_lim_vec" in self.first_setup_dict:
            ylim = self.first_setup_dict["y_lim_vec"]
            if ylim.size == 2:
                self.yaxis_lims = ylim
        
        if self.first_setup_dict["plot_linear_scale"]:
            self.yaxis_name = "Power (linear)"
            self.plot_linear_scale = True
        
        # maybe we later want rangebins on x axis instead of range in meters
        self.xaxis_name = "Range"

        self.initialized = True

        self.init_lims_lineedit()

    def draw_data_frame(self, frame: BasebandDataFrame):
        if not self.initialized:
            self.initialize_axes()

        self.curr_bbif_data = frame
        for txrx, data in frame.power_data_dict.items():
            # this txrx is the key, so not the real trx vec
            # rx here is an index, goes 0, 1

            if not self.plot_linear_scale:
                if txrx in frame.db_data_dict:
                    data = frame.db_data_dict[txrx]
                else:
                    data = 20 * np.log10(data + 1e-16)  # avoid log(0)
                    frame.db_data_dict[txrx] = data

            plot = self.plot_or_make_new(txrx)
            # rx is the key, in this class we handle the tx
            self.per_plot_data_reg[txrx[:2]] = frame
            plot.plot_or_update_data(
                identifier=txrx[2],
                x_data=self.x_axis_vals,
                y_data=data,
                line_color=self.rx_plot_colors[txrx[2]],
                legend_label=f"RX{txrx[2]}"
            )

        self.set_label_curr_frame()
        self.set_label_time()

    def get_title_string(self, trx_vec: tuple[int, int, int]) -> str:
        # not handling chip number here, just tx and rx, maybe later
        if trx_vec[1] == ALL_TX_OFF:
            # Check for AllTxOff
            return f"TxOFF"

        return f"TX{trx_vec[1]}"
