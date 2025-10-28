from __future__ import annotations

import time
from collections import deque, defaultdict

import numpy as np
from dataclasses import dataclass
from pathlib import Path

import os

from PySide6.QtWidgets import QSizePolicy

# Suppress Qt warnings before importing pyqtgraph
os.environ['QT_LOGGING_RULES'] = "qt.core.qobject.connect=false"

import pyqtgraph as pg

from pyqtgraph.Qt.QtWidgets import (
    QMainWindow, QWidget, QGridLayout, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QApplication, QCheckBox
    )
from pyqtgraph.Qt.QtGui import QDoubleValidator, QIntValidator, QIcon, QImage, QPalette, QColor
import pyqtgraph.Qt.QtCore as QtCore

from Presence2DPlotter.new_main_ui import Ui_MainWindow
from Presence2DPlotter.time_series_plot import TimeSeriesPlot
from Presence2DPlotter.top_view_plot import TopViewPlot
from Presence2DPlotter.presence_types import HumanPresence2DIdx, DetectionZone, Pres2dData, Presence2DDataFrame
from Presence2DPlotter.power_plot import PowerPerBinPlot

from enum import IntEnum

class ThreshData2DIdx(IntEnum):
    RANGE_IDX = 0
    RADIAL_SPEED_IDX = 1
    ANGLE_RAD_IDX = 2
    SIGNALPWR_IDX = 3
    NOISEPWR_IDX = 4
    ANGLE_DIFF_RAD_IDX = 5

class HumanDetection2DIdx(IntEnum):
    INSIDE_STATE_IDX = 0
    X_IDX = 1
    Y_IDX = 2
    SIGNALPWR_IDX = 3
    NOISEPWR_IDX = 4


class Det2dData:
    def __init__(self, data: np.ndarray):
        self.data = data
        self.num_detections = len(data) / len(HumanDetection2DIdx)

    def SNRs(self):
        return 5 * np.log10(self.data[HumanDetection2DIdx.SIGNALPWR_IDX::len(HumanDetection2DIdx)] / self.data[
            HumanDetection2DIdx.NOISEPWR_IDX::len(HumanDetection2DIdx)])

    def Xs(self):
        return self.data[HumanDetection2DIdx.X_IDX::len(HumanDetection2DIdx)]

    def Ys(self):
        return self.data[HumanDetection2DIdx.Y_IDX::len(HumanDetection2DIdx)]


class DataAndTime:
    def __init__(self, data, timestamp) -> None:
        self.data = data
        self.timestamp = timestamp


class KeyPressFilter(QtCore.QObject):
    def __init__(self, callback):
        super().__init__()
        self._callback = callback

    def eventFilter(self, obj, event: pg.QtGui.QKeyEvent):
        if event.type() == QtCore.QEvent.KeyPress:
            return self._callback(event)

        return False


class PlotMainWin(QMainWindow, Ui_MainWindow):

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

class Presence2DPlotter:

    def __init__(self, shm_on_exit=None):
        self.shm_on_exit = shm_on_exit
        self.app = None
        self._key_filter = None
        self.mainwin = None

        self.num_saved_frames = -1
        self.frame_received_counter = 0
        self.frame_dropped_counter = 0

        self.paused = False

        self.curr_data_frame_inx = 0
        self.curr_label_frame_max = 0

        self.first_setup_dict = None
        self.first_timestamp = None

        self.thresh_to_cut = 100

        self.rx_plot_colors = [ "#C94848", "#43A343" ]

        self.fps = None
        self.curr_max_history_timeplots = 300*1000
        self.confidence_values_performance = None
        self.confidence_values_lowpower = None
        self.current_power_mode = None
        self.last_power_mode = self.current_power_mode
        self.output_tag = None
        self.output_tag_lowpower = None
        self.thresh_range_vec = None
        self.noise_floor_val = None
        self.ylims_db = None
        self.thr_snr_vec = None
        self.thresh_level_adjust = None
        self.current_confidence_values = None
        self.current_seqnum = None
        self.current_timestamp = None
        self._latest_detection2d = None
        self.confidence_plot = None
        self.presence_plot = None

        self.zone_colors = [
            pg.mkColor(255, 82, 82, 255),  # red
            pg.mkColor(3, 169, 244, 255),  # blue
            pg.mkColor(139, 195, 74, 255),  # green
            pg.mkColor(255, 193, 7, 255),  # amber
        ]

        self.pixel_width = np.ceil(1200/ 600) # i set something arbitrary here for testing instead of win_size[1]
        self.presence_state = 0
        self.window_shown = False
        self._fov_items = []
        self._fov_visible = True

        self.curr_ppif_data: Presence2DDataFrame = None
        self.ppif_plot_data_buffer: list[Presence2DDataFrame] = []

        self.min_time_history = 10000
        self.max_time_history = 300*1000

        from PySide6.QtCore import QLocale
        QLocale.setDefault(QLocale(QLocale.English, QLocale.UnitedStates))

        logo_img_fp = Path(__file__).resolve().parent.parent.parent.parent.parent / "Demos" \
            / "Resources" / "Images" / "Novelda_logo_hvit_150dpi.png"
        self.logo_img = QImage(str(logo_img_fp))

        # all curves
        self._curves = defaultdict(dict)
        self._hlines = defaultdict(dict)

    def _mount_plot(self, box, title=""):
        lay = box.layout() or QVBoxLayout(box)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(0)

        gfx = pg.GraphicsLayoutWidget()
        gfx.setBackground("#3c4d52")
        lay.addWidget(gfx)

        plot = gfx.addPlot(title=title)
        plot.setAspectLocked(False)
        plot.showGrid(x=True, y=True, alpha=0.25)

        for ax in ("bottom", "left"):
            a = plot.getAxis(ax)
            a.setPen("#E6E6E6")
            a.setTextPen("#E6E6E6")

        return gfx, plot

    def _plot_key(self, plot: pg.PlotItem):
        return plot.objectName() or str(id(plot))

    def _load_or_update_thres_vec(self,
                                  plot: pg.PlotItem,
                                  curve_id: str,
                                  x, y,
                                  color="#FFFFFF",
                                  width=1,
                                  dashed=False, symbol=None, legend_label="Detection Threshold",
                                  *,
                                  hline_id: str,
                                  hline_y: float,
                                  hline_color: str = "#FF5252",
                                  hline_width: int = 1, hline_label="Noise Floor") -> pg.PlotDataItem:

        key = self._plot_key(plot)
        curves = self._curves[key]

        x = np.asarray(x, dtype=float)
        y = np.asarray(y, dtype=float)

        pen = pg.mkPen(color, width=width)
        if dashed:
            pen.setStyle(pg.QtCore.Qt.PenStyle.DashLine)
        if curve_id in curves:
            curves[curve_id].setData(x, y)
            pdi = curves[curve_id]
        else:
            pdi = plot.plot(x, y, pen=pen, symbol=symbol, symbolSize=(6 if symbol else 0), name=legend_label)
            curves[curve_id] = pdi

        if hline_id is not None and hline_y is not None:
            hlines = self._hlines[key]
            if hline_id in hlines:
                hlines[hline_id].setValue(float(hline_y))
            else:
                hpen = pg.mkPen(hline_color, width=hline_width)
                h = pg.InfiniteLine(pos=float(hline_y), angle=0, pen=hpen, name=hline_label)
                h.setZValue(9)
                plot.addItem(h)
                dummy_plot = pg.PlotDataItem([0, 1], [0, 0], pen=hpen, name=hline_label)
                plot.legend.addItem(dummy_plot, hline_label)
                hlines[hline_id] = h

        return pdi

    def _time_zoom_slider(self, val: int):
        self.curr_max_history_timeplots = val*1000
        self.presence_plot.time_history = self.curr_max_history_timeplots
        self.confidence_plot.time_history = self.curr_max_history_timeplots
        self._bm_panel.time_history = self.curr_max_history_timeplots
        # Update the line edit without triggering its signal
        self.mainwin.timeScaleLEdit.blockSignals(True)
        self.mainwin.timeScaleLEdit.setText(str(val))
        self.mainwin.timeScaleLEdit.blockSignals(False)

        # If paused, update the view immediately
        if self.paused and self.ppif_plot_data_buffer and 0 <= self.curr_data_frame_inx < len(self.ppif_plot_data_buffer):
            frame = self.ppif_plot_data_buffer[self.curr_data_frame_inx]
            ts = float(frame.new_timestamp_seqnum_tag_in.get("timestamp", 0.0))

            # Pass max_timestamp to filter data up to current frame
            if self._bm_panel:
                self._bm_panel.browse_set_view(max_timestamp=ts)
            if self.presence_plot:
                self.presence_plot.browse_set_view(max_timestamp=ts)
            if self.confidence_plot:
                self.confidence_plot.browse_set_view(max_timestamp=ts)

    def _time_scale_edited(self):
        try:
            display_val = int(self.mainwin.timeScaleLEdit.text())
            if self.min_time_history <= display_val*1000 <= self.max_time_history:  # Validate display range
                self.curr_max_history_timeplots = display_val*1000
                self.presence_plot.time_history = self.curr_max_history_timeplots
                self.confidence_plot.time_history = self.curr_max_history_timeplots
                self._bm_panel.time_history = self.curr_max_history_timeplots
                # Update slider without triggering its signal
                self.mainwin.timeScaleSlider.blockSignals(True)
                self.mainwin.timeScaleSlider.setValue(display_val)
                self.mainwin.timeScaleSlider.blockSignals(False)

                # If paused, update the view immediately
                if self.paused and self.ppif_plot_data_buffer and 0 <= self.curr_data_frame_inx < len(self.ppif_plot_data_buffer):
                    frame = self.ppif_plot_data_buffer[self.curr_data_frame_inx]
                    ts = float(frame.new_timestamp_seqnum_tag_in.get("timestamp", 0.0))

                    # Pass max_timestamp to filter data up to current frame
                    if self._bm_panel is not None:
                        self._bm_panel.browse_set_view(max_timestamp=ts)
                    if self.presence_plot is not None:
                        self.presence_plot.browse_set_view(max_timestamp=ts)
                    if self.confidence_plot is not None:
                        self.confidence_plot.browse_set_view(max_timestamp=ts)
        except ValueError:
            # Restore previous value if invalid input
            self.mainwin.timeScaleLEdit.setText(str(self._bm_panel.time_history/1000))

    def _init_bm_modes(self):
        self._bm_modes = {
            "Range": {"ylims": (-0.5, 5), "ylabel": "Meters", "yunit": ""},
            "SNR": {"ylims": (-0.5, 100), "ylabel": "dB", "yunit": ""},
            "Degrees": {"ylims": (-95, 95), "ylabel": "Degrees", "yunit": ""}
        }
        self.bm_mode = self.mainwin.choosePlotComboBox.currentText()
        self.mainwin.choosePlotComboBox.currentTextChanged.connect(self._apply_bm_mode)
        self._create_bm_panel()
        self._apply_bm_mode(self.bm_mode)
        self._bm_panel.time_history = self.curr_max_history_timeplots
        self.mainwin.timeScaleLEdit.setText(str(self.curr_max_history_timeplots/1000))

    def _apply_bm_mode(self, mode: str):
        self.bm_mode = mode
        cfg = self._bm_modes.get(mode, {})

        ylabel = cfg.get("ylabel", mode)
        yunit = cfg.get("yunit", "")
        y0, y1 = cfg.get("ylims", (0, 1))

        p = self._bm_panel.plot  # pg.PlotItem

        p.setTitle(mode)
        p.setLabel("bottom", "Time", units="s")
        p.setLabel("left", ylabel, units=yunit)

        # Set fixed Y range with no padding
        p.enableAutoRange('y', False)
        p.setYRange(y0, y1, padding=0)

        self._bm_panel.clear_selection()

        if not self._bm_panel.all_zones_data:
            self._bm_panel.init_new_plot_data(0)

        # Clear existing data
        z = self._bm_panel.all_zones_data[0]
        z.ydata.clear()
        z.timestamps.clear()

        # Rebuild plot data from buffer with new metric
        if self.ppif_plot_data_buffer:
            for frame in self.ppif_plot_data_buffer:
                if frame.detection2d is not None:
                    if frame.detection2d.shape[0] != 0:
                        val = self._bm_eval_metric(frame)
                        ts = float(frame.new_timestamp_seqnum_tag_in.get("timestamp", 0.0))
                        # Only append to ydata list, timestamps stay the same
                        z.ydata.append(float(val))
                        z.timestamps.append(ts)

            # Update plot items
            z.plot_item.setData(z.timestamps, z.ydata)
            if getattr(z, "scatter_item", None) is not None:
                z.scatter_item.setData(z.timestamps, z.ydata)

            # Update panel timestamps
            if z.timestamps:
                self._bm_panel.first_timestamp = z.timestamps[0]
                self._bm_panel.last_timestamp = z.timestamps[-1]

            # Update view
            if not self.paused:
                # Live mode: show most recent data
                self._bm_panel.process_end()
            else:
                # Browse mode: maintain current view
                if self.ppif_plot_data_buffer and 0 <= self.curr_data_frame_inx < len(self.ppif_plot_data_buffer):
                    ts = float(self.ppif_plot_data_buffer[self.curr_data_frame_inx]
                               .new_timestamp_seqnum_tag_in.get("timestamp", 0.0))
                    self._bm_panel.browse_set_view(max_timestamp=ts)

    def _create_bm_panel(self):
        cfg = self._bm_modes.get(self.bm_mode, {})
        ylims = cfg.get("ylims", (0,1))

        self._bm_panel = TimeSeriesPlot(
            name=f"BM: {self.bm_mode}",
            ylims=ylims,
            max_history=self.max_time_history,
            pixel_width=2,
            zone_colors=getattr(self, "zone_colors", []),
            thresh_to_cut=self.thresh_to_cut,
            target_plot=self.plot_bm,
            scatter_overlay=False,
            scatter_only=True
        )
        self._bm_panel.time_history = self.curr_max_history_timeplots
        self._bm_panel.num_saved_frames = self.num_saved_frames


    def _bm_eval_metric(self, frame) -> float:
        if self.bm_mode == "Range":
            return frame.detection2d[0]
        elif self.bm_mode == "SNR":
            return 5 * np.log10(frame.detection2d[3] / frame.detection2d[4])
        else:
            return (frame.detection2d[2] * 180) / np.pi

    def _init_power_per_bin(self, *, color: str = "#00E5FF", width: int = 2):
        self.ppb_plot = PowerPerBinPlot(
            range_vec=self.thresh_range_vec,
            xlims=None,
            ylims_db=None,
            power_line_color=color,
            power_line_width=width
        )
        self.mainwin.topRightPlot.setLayout(QVBoxLayout())
        lay = self.mainwin.topRightPlot.layout()
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(0)
        self.mainwin.topRightPlot.layout().addWidget(self.ppb_plot)


    def _init_conf(self):
        if self.confidence_plot is not None:
            return

        self.confidence_plot = TimeSeriesPlot(
            name="Confidence",
            ylims=(0, 100),
            max_history=self.max_time_history,
            pixel_width=2,
            zone_colors=self.last_dets_colors,
            thresh_to_cut=self.thresh_to_cut,
            target_plot=self.plot_br,
            scatter_overlay=True,
            scatter_only=False
        )

        # disable y-zooming with wheel
        self.confidence_plot.plot.setMouseEnabled(x=False, y=False)
        if self.top_view_plot is not None:
            self.top_view_plot.confidence_plot = self.confidence_plot
        if self.confidence_values_lowpower is not None:
            self.confidence_plot.confidence_values_lowpower = self.confidence_values_lowpower
        if self.confidence_values_performance is not None:
            self.confidence_plot.confidence_values_performance = self.confidence_values_performance

        self.confidence_plot.num_saved_frames = self.num_saved_frames
        self.confidence_plot.update_threshold_lines()

    def _init_presence(self):
        if self.presence_plot is not None:
            return

        self.presence_plot = TimeSeriesPlot(
            name="Presence",
            ylims=(0, 1),
            max_history=self.max_time_history,
            pixel_width=2,
            zone_colors=self.last_dets_colors,
            thresh_to_cut=self.thresh_to_cut,
            target_plot=self.plot_bl,
            scatter_overlay=True,
            scatter_only=False
        )
        # disable y-zooming with wheel
        self.presence_plot.plot.setMouseEnabled(x=False, y=False)
        self.presence_plot.plot.getAxis('left').setTicks([[(0, "0"), (1, "1")]])
        self.presence_plot.plot.getAxis('left').setLabel("Presence State", units="")
        if self.top_view_plot is not None:
            self.top_view_plot.presence_plot = self.presence_plot

        self.presence_plot.num_saved_frames = self.num_saved_frames

    def apply_dark_theme(self, app: QApplication):
        app.setStyle('Fusion')
        pal = QPalette()
        base_bg = QColor("#3A3E44")
        alt_bg = QColor("#2A2D30")
        text_fg = QColor("#E6E6E6")

        pal.setColor(QPalette.Window, base_bg)
        pal.setColor(QPalette.Base, base_bg)
        pal.setColor(QPalette.AlternateBase, alt_bg)
        pal.setColor(QPalette.Button, base_bg)
        pal.setColor(QPalette.ToolTipBase, base_bg)

        pal.setColor(QPalette.WindowText, text_fg)
        pal.setColor(QPalette.Text, text_fg)
        pal.setColor(QPalette.ButtonText, text_fg)
        pal.setColor(QPalette.ToolTipText, text_fg)

        app.setPalette(pal)
        return text_fg

    def init_window(self):
        if self.app is None:
            self.app = QApplication([])
            text_fg = self.apply_dark_theme(self.app)
        if self.mainwin is not None:
            return

        self.mainwin = PlotMainWin(self.exit)
        self.mainwin.setWindowTitle("some Plotter")
        self.mainwin.setupUi(self.mainwin)

        # Set vertical line colors
        line_color = "#3c4d52"
        for i in range(4):
            line = getattr(self.mainwin, f"vertLine{i}", None)
            if line is not None:
                line.setStyleSheet(f"color: {line_color};")
        for i in range(3):
            line = getattr(self.mainwin, f"horizontalLine{i}")
            if line is not None:
                line.setStyleSheet(f"color: {line_color};")

        cb = self.mainwin.choosePlotComboBox
        cb.clear()
        cb.addItems(["Range", "SNR", "Degrees"])
        cb.setCurrentIndex(0)

        gfx_top, plot_top = self._mount_plot(self.mainwin.topPlotBox, "Sector Plot")
        self.top_view_plot = TopViewPlot(
            gfx=gfx_top,
            plot=plot_top,
            zone_colors=self.zone_colors
        )
        self.top_view_plot.parent_plotter = self
        self.gfx_bl, self.plot_bl = self._mount_plot(self.mainwin.bottomLeftPlot, "Presence")
        self.plot_bl.setMouseEnabled(x=False, y=True)
        self.gfx_br, self.plot_br = self._mount_plot(self.mainwin.bottomRightPlot, "Confidence")
        self.plot_br.setMouseEnabled(x=False, y=True)
        self.gfx_bm, self.plot_bm = self._mount_plot(self.mainwin.bottomMiddlePlot, "Detections?")
        self.plot_bm.setMouseEnabled(x=False, y=True)
        self.plot_bm.setMenuEnabled(False)
        self.plot_bm.hideButtons()

        self.plot_top = self.top_view_plot.plot
        self.gfx_top = self.top_view_plot.gfx
        self.plot = self.plot_top

        self.current_seqnum = 0

        self.last_dets = []
        self.last_dets_colors = [
            pg.mkColor(255, 0, 0, 255),
            pg.mkColor(0, 0, 255, 255),
        ]

        self.mainwin.hotkeyLabel.setText("Space: play/pause"
                                         "\nLeft/Right Arrow: change current frame"
                                         "\nLeft Click: mark closest point"
                                         "\nA/D: move marker")

        self.mainwin.logoLabel.setPixmap(pg.QtGui.QPixmap.fromImage(self.logo_img).scaledToWidth(100, QtCore.Qt.SmoothTransformation))
        self.mainwin.resetLimitsBtn.clicked.connect(self.reset_limits)
        self.mainwin.invertTopPlotBtn.clicked.connect(self.invert_top_view)
        self.mainwin.showFovLinesCheckBox.toggled.connect(self.set_fov_visible)
        self.mainwin.timeScaleSlider.setRange(1, 100)
        self.mainwin.timeScaleSlider.setValue(86)
        self.mainwin.timeScaleSlider.setTracking(True)
        self.mainwin.timeScaleSlider.valueChanged.connect(self._time_zoom_slider)
        self.mainwin.timeScaleLEdit.returnPressed.connect(self._time_scale_edited)

        self.mainwin.currFrameLEdit.returnPressed.connect(self.frame_edited)
        self.mainwin.currFrameLEdit.focusInEvent = self._frame_edit_focus_in_base
        self.mainwin.currFrameLEdit.focusOutEvent = self._frame_edit_focus_out_base
        self._frame_edit_has_focus = False

        self.mainwin.rangeMinLEdit.returnPressed.connect(self.limits_edited)
        self.mainwin.rangeMaxLEdit.returnPressed.connect(self.limits_edited)
        self.mainwin.powerMaxLEdit.returnPressed.connect(self.limits_edited)
        self.mainwin.powerMinLEdit.returnPressed.connect(self.limits_edited)

        doubleValid = QDoubleValidator()
        self.mainwin.rangeMinLEdit.setValidator(doubleValid)
        self.mainwin.rangeMaxLEdit.setValidator(doubleValid)
        self.mainwin.powerMinLEdit.setValidator(doubleValid)
        self.mainwin.powerMaxLEdit.setValidator(doubleValid)

        self.mainwin.currFrameLEdit.setValidator(QIntValidator(1, 1_000_000_000))

        self.mainwin.trailBwdLEdit.returnPressed.connect(self._set_bwd_trail)
        self.mainwin.trailFwdLEdit.returnPressed.connect(self._set_fwd_trail)

        doubleTrailValid = QDoubleValidator(0.0, 999.0, 2)
        self.mainwin.trailBwdLEdit.setValidator(doubleTrailValid)
        self.mainwin.trailFwdLEdit.setValidator(doubleTrailValid)

        self.mainwin.showXYcheckBox.toggled.connect(self._toggle_xy_coordinates)

        if self._key_filter is None:
            self._key_filter = KeyPressFilter(self.keyPressEvent)
            self.app.installEventFilter(self._key_filter)

    def show_ui(self):
        if not self.window_shown:
            self.mainwin.show()
            self.window_shown = True

    def set_label_info(self):
        fps = self.first_setup_dict["fps"]
        if self.fps is None:
            self.fps = fps

        self.mainwin.infoParamLabel.setText(
            f"FPS: {fps}"
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
        self._init_trail_line_edits()

    def _init_trail_line_edits(self):
        if self.fps is not None:
            initial_bwd_seconds = self.top_view_plot.trail_back / self.fps
            initial_fwd_seconds = self.top_view_plot.trail_fwd / self.fps
            self.mainwin.trailBwdLEdit.setText(f"{initial_bwd_seconds:.2f}")
            self.mainwin.trailFwdLEdit.setText(f"{initial_fwd_seconds:.2f}")

    def _set_bwd_trail(self):
        text = self.mainwin.trailBwdLEdit.text()
        if text:
            try:
                desired_seconds = float(text)
                dots_num = int(desired_seconds * self.fps)
                self.top_view_plot.trail_back = dots_num
                # Calculate actual seconds after rounding and update the display
                actual_seconds = dots_num / self.fps
                self.mainwin.trailBwdLEdit.setText(f"{actual_seconds:.2f}")
            except ValueError:
                # Invalid input, restore previous value
                actual_seconds = self.top_view_plot.trail_back / self.fps
                self.mainwin.trailBwdLEdit.setText(f"{actual_seconds:.2f}")
        self.mainwin.trailBwdLEdit.clearFocus()
        self.rerender_plots()

    def _set_fwd_trail(self):
        text = self.mainwin.trailFwdLEdit.text()
        if text:
            try:
                desired_seconds = float(text)
                dots_num = int(desired_seconds * self.fps)
                self.top_view_plot.trail_fwd = dots_num
                # Calculate actual seconds after rounding and update the display
                actual_seconds = dots_num / self.fps
                self.mainwin.trailFwdLEdit.setText(f"{actual_seconds:.2f}")
            except ValueError:
                # Invalid input, restore previous value
                actual_seconds = self.top_view_plot.trail_fwd / self.fps
                self.mainwin.trailFwdLEdit.setText(f"{actual_seconds:.2f}")
        self.mainwin.trailFwdLEdit.clearFocus()
        self.rerender_plots()

    def invert_top_view(self):
        self.top_view_plot.invert_top_view()


    def _toggle_xy_coordinates(self, visible: bool):
        self.top_view_plot._toggle_xy_coordinates(visible)

        # Force immediate visibility update when paused OR when at the last frame (effectively paused)
        at_last_frame = (self.ppif_plot_data_buffer and
                         self.curr_data_frame_inx == len(self.ppif_plot_data_buffer) - 1)

        if self.paused or at_last_frame:
            if visible:
                # Make the existing coordinate label visible immediately
                self.top_view_plot.coord_proxy.setVisible(True)
            else:
                # Hide it when unchecking
                self.top_view_plot.coord_proxy.setVisible(False)

    def human_presence_data_in(self, data: np.ndarray, detection2d: np.ndarray = None,
                               append_series: bool = True, ts: float | None = None):
        
        frame_ts = float(ts if ts is not None else self.current_timestamp)
        
        num_elements_in_human_pres = len(HumanPresence2DIdx)
        num_pres2d_msg = len(data) / num_elements_in_human_pres

        all_human_msgs: list[Pres2dData] = []
        for i in range(int(num_pres2d_msg)):
            all_human_msgs.append(
                Pres2dData(data[i * num_elements_in_human_pres: (i + 1) * num_elements_in_human_pres], None,
                           self.current_timestamp))

        self.presence_state = 0
        self.top_view_plot.deactivate_all_zones()

        for i in range(len(self.top_view_plot.detection_zones)):

            curr_pres2data = None
            for pres2data in all_human_msgs:
                if pres2data.zone_num == i:
                    curr_pres2data = pres2data
                    break

            if curr_pres2data is not None:
                self.presence_state = curr_pres2data.inside_state or self.presence_state

                if append_series:
                    self.confidence_plot.add_data(curr_pres2data.zone_num, curr_pres2data.confidence, frame_ts)
                    self.presence_plot.add_data(curr_pres2data.zone_num, curr_pres2data.inside_state, frame_ts)

                snr = 0.0
                if detection2d is not None and detection2d.shape[0] != 0:
                    snr = 5 * np.log10(detection2d[3] / detection2d[4])
                self.top_view_plot.set_last_det(curr_pres2data.zone_num, curr_pres2data.x, curr_pres2data.y, snr)
                self.top_view_plot._trail_record(curr_pres2data.zone_num, curr_pres2data.x, curr_pres2data.y, self.curr_data_frame_inx)
                self.top_view_plot.set_det_zone_active(self.top_view_plot.detection_zones[curr_pres2data.zone_num], curr_pres2data.inside_state)
            else:
                if append_series:
                    self.confidence_plot.add_data(i, 0, frame_ts)
                    self.presence_plot.add_data(i, 0, frame_ts)

    def new_timestamp_seqnum_tag_in(self, timestamp, seqnum, tag):
        if self.first_timestamp is None:
            self.first_timestamp = timestamp

        self.current_seqnum = seqnum
        self.current_timestamp = timestamp

        if tag == 0 or tag == self.output_tag:
            self.current_power_mode = 0
        elif tag == self.output_tag_lowpower:
            self.current_power_mode = 1
        else:
            raise ValueError("Presence2D plotter: Unknown tag")

        if self.last_power_mode != self.current_power_mode:
            self.set_current_power_mode_params()


    def set_current_power_mode_params(self):
        if self.current_power_mode == 0:  # performance
            self.current_confidence_values = self.confidence_values_performance
            self.top_view_plot.switch_zone_to_performance()
        else:  # lowpower
            self.current_confidence_values = self.confidence_values_lowpower
            self.top_view_plot.switch_zone_to_lowpower()

    def set_fov_visible(self, visible: bool):
        self.top_view_plot.set_fov_visible(visible)

    def toggle_fov(self):
        self.top_view_plot.toggle_fov()

    def frame_edited(self):
        try:
            curr_frame = int(self.mainwin.currFrameLEdit.text()) - 1  # Convert to 0-based index
            if 0 <= curr_frame < len(self.ppif_plot_data_buffer):
                self.paused = True
                self.curr_data_frame_inx = curr_frame
                frame = self.ppif_plot_data_buffer[self.curr_data_frame_inx]

                # Update timestamp and tag
                tsnt = frame.new_timestamp_seqnum_tag_in
                self.new_timestamp_seqnum_tag_in(tsnt["timestamp"], tsnt["sequence_number"], tsnt["tag"])

                self.draw_data_frame(frame, live=False, from_line_edit=True)
            else:
                # Invalid frame number, restore previous value
                self.mainwin.currFrameLEdit.setText(str(int(self.curr_data_frame_inx + 1)))
        except ValueError:
            # Invalid input, restore previous value
            self.mainwin.currFrameLEdit.setText(str(int(self.curr_data_frame_inx + 1)))

        self.mainwin.currFrameLEdit.clearFocus()

    def _frame_edit_focus_in_base(self, event):
        """Base handler that's directly assigned to the widget's focusInEvent"""
        QLineEdit = pg.QtWidgets.QLineEdit
        QLineEdit.focusInEvent(self.mainwin.currFrameLEdit, event)
        self._frame_edit_has_focus = True
        self.mainwin.currFrameLEdit.setReadOnly(False)
        self.mainwin.currFrameLEdit.selectAll()

    def _frame_edit_focus_out_base(self, event):
        """Base handler that's directly assigned to the widget's focusOutEvent"""
        QLineEdit = pg.QtWidgets.QLineEdit
        QLineEdit.focusOutEvent(self.mainwin.currFrameLEdit, event)
        self._frame_edit_has_focus = False
        self.mainwin.currFrameLEdit.setText(str(int(self.curr_data_frame_inx + 1)))
        self.mainwin.currFrameLEdit.setReadOnly(True)

    def set_label_curr_frame(self):
        # Only update the frame number if the edit field doesn't have focus
        if not self._frame_edit_has_focus:
            if not self.paused:
                self.mainwin.currFrameLEdit.setText(f"{int(self.curr_data_frame_inx + 1)}")
        self.mainwin.totalNumFramesBuffLabel.setText(f"/ {self.curr_label_frame_max}")

    def set_label_time(self):
        if self.first_timestamp is None:
            return

        curr_frame_ts = self.ppif_plot_data_buffer[self.curr_data_frame_inx].new_timestamp_seqnum_tag_in["timestamp"]
        curr_frame_seq = self.ppif_plot_data_buffer[self.curr_data_frame_inx].new_timestamp_seqnum_tag_in["sequence_number"]
        timetxt = time.strftime('%Y.%m.%d %H:%M:%S', time.localtime(curr_frame_ts/1000))
        rel_time_txt = (curr_frame_ts - self.first_timestamp)/1000
        self.mainwin.seqNumTimeLabel.setText(
            f"{timetxt}\nSince Start: {rel_time_txt:.1f}s\nSequence number: {curr_frame_seq}"
            f"\nNum frames received: {self.frame_received_counter}"
            f"\nNum frames dropped: {self.frame_dropped_counter}"
            )

    def reset_limits(self):
        self._set_xylims()
        self._set_ylims_db()
        self._p_c_reset_limits()

    def _p_c_reset_limits(self):
        if hasattr(self, '_p_xlims'):
            self.plot_bl.setYRange(0, 1)
        if hasattr(self, '_c_xlims'):
            self.plot_br.setYRange(0, 100)
        if hasattr(self, '_bm_xlims'):
            if hasattr(self, '_bm_modes') and hasattr(self, 'bm_mode'):
                cfg = self._bm_modes.get(self.bm_mode, {})
                y0, y1 = cfg.get("ylims", (0, 1))
                self.plot_bm.setYRange(y0, y1, padding=0)

    def limits_edited(self):
        xmin = float(self.mainwin.rangeMinLEdit.text())
        xmax = float(self.mainwin.rangeMaxLEdit.text())
        ymin = float(self.mainwin.powerMinLEdit.text())
        ymax = float(self.mainwin.powerMaxLEdit.text())

        # ensure the new limits are valid
        if xmin < xmax and ymin < ymax:
            self.ppb_plot.set_x_range(xmin, xmax)
            self.ppb_plot.set_y_range(ymin, ymax)
        else:
            # reset line edits
            self.mainwin.rangeMinLEdit.setText(f"{self.xaxis_lims[0]:.2f}")
            self.mainwin.rangeMaxLEdit.setText(f"{self.xaxis_lims[1]:.2f}")
            self.mainwin.powerMinLEdit.setText(f"{self.yaxis_lims[0]:.2f}")
            self.mainwin.powerMaxLEdit.setText(f"{self.yaxis_lims[1]:.2f}")

    def keyPressEvent(self, event: pg.QtGui.QKeyEvent):

        focus_plot = None
        if event.key() in (QtCore.Qt.Key_A, QtCore.Qt.Key_D):
            if hasattr(self, 'ppb_plot') and self.ppb_plot.hasFocus():
                focus_plot = self.ppb_plot
            elif hasattr(self, 'gfx_br') and self.gfx_br.hasFocus():
                focus_plot = self.confidence_plot
            elif hasattr(self, 'gfx_bl') and self.gfx_bl.hasFocus():
                focus_plot = self.presence_plot
            elif hasattr(self, 'gfx_bm') and self.gfx_bm.hasFocus():
                focus_plot = self._bm_panel

        if event.key() == QtCore.Qt.Key_Space:
            self.toggle_pause()
            return True
        elif event.key() == QtCore.Qt.Key_Left:
            self.move_frame(-1)
            return True
        elif event.key() == QtCore.Qt.Key_Right:
            self.move_frame(1)
            return True
        elif event.key() == QtCore.Qt.Key_A:
            self._move_marker(focus_plot, -1)
            return True
        elif event.key() == QtCore.Qt.Key_D:
            self._move_marker(focus_plot, 1)
            return True


        return False

    def _move_marker(self, focus_plot, direction: int):
        """Move the marker on the currently focused plot."""
        if focus_plot is None:
            return

        max_ts = None
        if self.paused and self.ppif_plot_data_buffer and 0 <= self.curr_data_frame_inx < len(
                self.ppif_plot_data_buffer):
            max_ts = self.ppif_plot_data_buffer[self.curr_data_frame_inx].new_timestamp_seqnum_tag_in["timestamp"]

        focus_plot.move_marker(direction, max_ts)

    def move_frame(self, direction: int):
        if len(self.ppif_plot_data_buffer) <= 1:
            return
        if not self.paused:
            self.paused = True
            self.curr_data_frame_inx = len(self.ppif_plot_data_buffer) - 1

        self.curr_data_frame_inx += direction
        if self.curr_data_frame_inx < 0:
            self.curr_data_frame_inx = 0
        elif self.curr_data_frame_inx >= len(self.ppif_plot_data_buffer):
            self.curr_data_frame_inx = len(self.ppif_plot_data_buffer) - 1

        frame = self.ppif_plot_data_buffer[self.curr_data_frame_inx]

        tsnt = frame.new_timestamp_seqnum_tag_in
        self.new_timestamp_seqnum_tag_in(tsnt["timestamp"], tsnt["sequence_number"], tsnt["tag"])

        self.draw_data_frame(frame, live=False)

        self.mainwin.currFrameLEdit.setText(f"{int(self.curr_data_frame_inx + 1)}")

    def rerender_plots(self):
        if len(self.ppif_plot_data_buffer) <= 1:
            return

        frame = self.ppif_plot_data_buffer[self.curr_data_frame_inx]
        tsnt = frame.new_timestamp_seqnum_tag_in
        self.new_timestamp_seqnum_tag_in(tsnt["timestamp"], tsnt["sequence_number"], tsnt["tag"])
        self.draw_data_frame(frame, live=False)


    def toggle_pause(self):
        was_paused = self.paused
        self.paused = not self.paused

        if was_paused and not self.paused:
            # Always jump to the latest frame
            if self.ppif_plot_data_buffer:
                self.curr_data_frame_inx = len(self.ppif_plot_data_buffer) - 1
                latest_frame = self.ppif_plot_data_buffer[self.curr_data_frame_inx]
                tsnt = latest_frame.new_timestamp_seqnum_tag_in
                self.new_timestamp_seqnum_tag_in(tsnt["timestamp"], tsnt["sequence_number"], tsnt["tag"])

            # force plot updates
            self.move_frame(-1)
            self.move_frame(1)
            self.paused = False

        if not self.paused:
            self.update()

    def start_event_loop(self):
        self.app.exec_()

    def exit(self):
        if self.shm_on_exit is not None:
            self.shm_on_exit()
        pg.exit()

    def _set_xylims(self):
        self.top_view_plot._set_xylims()

    def _set_ylims_db(self):

        if self.RangeLimVec is not None:
            self.ppb_plot.set_x_range(self.RangeLimVec[0], self.RangeLimVec[-1])
        else:
            self.ppb_plot.set_x_range(self.default_start_range, self.thresh_range_vec[-1])
        
        if self.PowerLimVec is not None:
            self.ppb_plot.set_y_range(self.PowerLimVec[0], self.PowerLimVec[-1])
        else:
            self.ppb_plot.set_y_range(-80.0, 20.0)

        self.mainwin.powerMinLEdit.setText(f"{self.ppb_plot.ylims_db[0]:.2f}")
        self.mainwin.powerMaxLEdit.setText(f"{self.ppb_plot.ylims_db[1]:.2f}")
        self.mainwin.rangeMinLEdit.setText(f"{self.ppb_plot.xlims[0]:.2f}")
        self.mainwin.rangeMaxLEdit.setText(f"{self.ppb_plot.xlims[1]:.2f}")

    def receive_data(self, data: dict | Presence2DDataFrame):
        if self.first_setup_dict is None:
            if isinstance(data, dict):
                self._handle_initial_setup(data)
                return

        # Data processing logic
        self._process_data_frame(data)
        self.frame_received_counter += 1

    def _render_live_frame(self, idx: int):
        """Render a frame in live mode."""
        latest = self.ppif_plot_data_buffer[idx]
        if self.curr_ppif_data is latest:
            return
        self.curr_data_frame_inx = idx
        self.draw_data_frame(latest, live=True)

    def _update_paused_data(self, data: Presence2DDataFrame, idx: int):
        """Update data structures when paused without rendering."""
        self.top_view_plot._record_trail_from_human_presence(data.human_presence, idx)
        self.top_view_plot._render_trail_browse()
        ts = float(data.new_timestamp_seqnum_tag_in.get("timestamp", 0.0))
        self._append_presence_series_only(data.human_presence, ts)

    def _handle_initial_setup(self, data: dict):
        """Handle initial setup from configuration dictionary."""
        self.first_setup_dict = data
        self.set_label_info()

        # Setup fps-related params
        if "fps" in data:
            self.skip_n_counter = int(data["fps"] / 50)

        # Copy attributes from setup dict
        for k in ("max_history", "MaxHistoryTimeplotsInS", "confidence_values_performance",
                  "confidence_values_lowpower", "top_view", "xy_xlims", "xy_ylims",
                  "current_power_mode", "output_tag", "output_tag_lowpower",
                  "with_dbg_plot", "thresh_range_vec", "noise_floor_val",
                  "thr_snr_vec", "thresh_level_adjust", "range_offset", "bin_length", "MaxBufferedFrames",
                  "default_start_range", "RangeLimVec", "PowerLimVec"):
            if k in data:
                setattr(self, k, data[k])

        # limit x-vals for power plot
        self.m_frames_per_pulse = data["json_settings"].get("m_frames_per_pulse", 192)
        num_bins = int(self.m_frames_per_pulse * 16)
        self.thresh_range_vec = self.thresh_range_vec[:num_bins]
        self.thr_snr_vec = self.thr_snr_vec[:num_bins]

        self._set_max_frames()
        self._setup_plots()
        self._apply_zones_and_fov(data)

        self._set_ylims_db()

        if "json_settings" in data:
            self._apply_json_settings(data["json_settings"])

        self.show_ui()

    def _set_max_frames(self):
        if self.MaxBufferedFrames > -1:
            self.num_saved_frames = int(self.MaxBufferedFrames)
        else:
            self.num_saved_frames = 100000
        
        self.thresh_to_cut = self.num_saved_frames + self.first_setup_dict.get("fps", 20)*5

    def _setup_plots(self):
        """Initialize all plots with configuration."""
        if hasattr(self, 'top_view_plot') and self.top_view_plot:
            self.top_view_plot.xy_xlims = self.xy_xlims
            self.top_view_plot.xy_ylims = self.xy_ylims

        self._presence_window_ms = 0
        self._conf_window_ms = 0

        self._set_xylims()
        self._init_conf()
        self._init_presence()

        self.top_view_plot.confidence_plot = self.confidence_plot
        self.top_view_plot.presence_plot = self.presence_plot

        self._init_bm_modes()
        self._init_power_per_bin()
        
        self.ppb_plot.add_const_plot(
            line_x=self.thresh_range_vec,
            line_y=5 * np.log10(self.thr_snr_vec * self.thresh_level_adjust * self.noise_floor_val),
            pen=pg.mkPen("#FFC107", width=1),
            name="Detection Threshold"
        )

        self.ppb_plot.add_const_plot(
            line_x=self.thresh_range_vec,
            line_y=np.full_like(self.thresh_range_vec, 5 * np.log10(self.noise_floor_val)),
            pen=pg.mkPen("#FF5252", width=1),
            name="Noise Floor"
        )

    def _apply_zones_and_fov(self, data: dict):
        """Apply detection zones and FOV configuration."""
        if "add_detection_zones_from_buffer" in data:
            d = data["add_detection_zones_from_buffer"]
            self.top_view_plot.add_detection_zones_from_buffer(
                d["xybuffer_performance"],
                d["xy_index_buffer_performance"],
                d["xy_index_buffer_lowpower"],
                d["xy_index_buffer_lowpower"]
            )

        if "draw_fow_lines_with_tags" in data:
            d = data["draw_fow_lines_with_tags"]
            self.top_view_plot.draw_fov_lines_with_tags(
                d["rmax"], d["d_range"], d["d_angle"],
                d["angle_min"], d["angle_max"]
            )

    def _process_data_frame(self, data: Presence2DDataFrame):
        """Process incoming data frame."""
        self.new_timestamp_seqnum_tag_in(
            data.new_timestamp_seqnum_tag_in["timestamp"],
            data.new_timestamp_seqnum_tag_in["sequence_number"],
            data.new_timestamp_seqnum_tag_in["tag"]
        )

        self.ppif_plot_data_buffer.append(data)
        idx = len(self.ppif_plot_data_buffer) - 1
        ts = float(data.new_timestamp_seqnum_tag_in.get("timestamp", 0.0))

        # Update detection metric plot
        if data.detection2d is not None:
            if self._bm_panel and not self._bm_panel.all_zones_data:
                self._bm_panel.init_new_plot_data(0)
            if self._bm_panel:
                if data.detection2d.shape[0] != 0:
                    val = self._bm_eval_metric(data)
                    self._bm_panel.add_data(0, float(val), ts)
                else:
                    self._bm_panel.add_data(0, np.nan, ts)

        # Handle live vs paused rendering
        if not self.paused:
            self._render_live_frame(idx)
        else:
            self._update_paused_data(data, idx)

    def _apply_json_settings(self, settings: dict):
        """Apply settings from JSON configuration."""
        # Time zoom
        if "MaxHistoryTimeplotsInS" in settings:
            timehist = max(self.min_time_history, int(settings["MaxHistoryTimeplotsInS"])*1000)
            self.max_time_history = timehist
            self.curr_max_history_timeplots = self.max_time_history/10
            if hasattr(self, 'presence_plot') and self.presence_plot:
                self.presence_plot.time_history = self.curr_max_history_timeplots
            if hasattr(self, 'confidence_plot') and self.confidence_plot:
                self.confidence_plot.time_history = self.curr_max_history_timeplots
            if hasattr(self, '_bm_panel') and self._bm_panel:
                self._bm_panel.time_history = self.curr_max_history_timeplots
            # Update UI
            self.mainwin.timeScaleLEdit.blockSignals(True)
            self.mainwin.timeScaleLEdit.setText(str(self.curr_max_history_timeplots/1000))
            self.mainwin.timeScaleLEdit.blockSignals(False)
        
        self.curr_max_history_timeplots = self.max_time_history/10
        self.mainwin.timeScaleSlider.setMinimum(self.min_time_history/1000)
        self.mainwin.timeScaleSlider.setMaximum(self.max_time_history/1000)
        self.mainwin.timeScaleSlider.blockSignals(True)
        self.mainwin.timeScaleSlider.setValue(self.curr_max_history_timeplots/1000)
        self.mainwin.timeScaleSlider.blockSignals(False)

        # FOV lines
        if "show_fov_lines" in settings:
            show = bool(settings["show_fov_lines"])
            self.mainwin.showFovLinesCheckBox.setChecked(show)

        # XY coordinates
        if "show_xy_coordinates" in settings:
            show = bool(settings["show_xy_coordinates"])
            self.mainwin.showXYcheckBox.setChecked(show)

        # Inverted top view
        if "inverted_top_view" in settings and bool(settings["inverted_top_view"]):
            self.top_view_plot.invert_top_view()

        # Trail settings (convert seconds to frames when fps is available)
        if self.fps is not None:
            if "trail_backward_seconds" in settings:
                if settings["trail_backward_seconds"] != -1:
                    seconds = float(settings["trail_backward_seconds"])
                    self.top_view_plot.trail_back = int(seconds * self.fps)
                    corrected_seconds = float(self.top_view_plot.trail_back / self.fps)
                    self.mainwin.trailBwdLEdit.setText(str(f"{corrected_seconds:.2f}"))

            if "trail_forward_seconds" in settings:
                if settings["trail_forward_seconds"] != -1:
                    seconds = float(settings["trail_forward_seconds"])
                    self.top_view_plot.trail_fwd = int(seconds * self.fps)
                    corrected_seconds = float(self.top_view_plot.trail_fwd / self.fps)
                    self.mainwin.trailFwdLEdit.setText(str(f"{corrected_seconds:.2f}"))


        # Setup num_saved_frames
        #if "MaxBufferedFrames" in settings:
        #    if settings["MaxBufferedFrames"] != -1:
        #        self.num_saved_frames = int(settings["MaxBufferedFrames"])
        #    else:
        #        self.num_saved_frames = 100000

        # Power plot limits
        if "range_min" in settings and "range_max" in settings:
            rmin = float(settings["range_min"])
            rmax = float(settings["range_max"])
            if rmin < rmax and rmin >= 0:
                self.mainwin.rangeMinLEdit.setText(f"{rmin:.2f}")
                self.mainwin.rangeMaxLEdit.setText(f"{rmax:.2f}")

        if "power_min" in settings and "power_max" in settings:
            pmin = float(settings["power_min"])
            pmax = float(settings["power_max"])
            if pmin < pmax:
                self.mainwin.powerMinLEdit.setText(f"{pmin:.2f}")
                self.mainwin.powerMaxLEdit.setText(f"{pmax:.2f}")

        # Default plot mode (0=Range, 1=SNR, 2=Degrees)
        if "DefaultMiddlePlot" in settings:
            try:
                mode_idx = ["range", "snr", "degrees"].index(settings["DefaultMiddlePlot"].lower())
            except:
                mode_idx = 0
            if 0 <= mode_idx < self.mainwin.choosePlotComboBox.count():
                self.mainwin.choosePlotComboBox.setCurrentIndex(mode_idx)
        
        if "m_frames_per_pulse" in settings:
            self.m_frames_per_pulse = int(settings["m_frames_per_pulse"])

    def _append_presence_series_only(self, hp_array, ts: float):
        """Append presence/confidence data to the series without updating the display.
        Used when paused to store incoming data for later viewing."""
        if hp_array is None:
            return

        num_elements_in_human_pres = len(HumanPresence2DIdx)
        n = int(len(hp_array) / num_elements_in_human_pres)
        ts = getattr(self, "current_timestamp", None)
        if ts is None:
            return

        zones_with_data = set()

        # Ensure series exist and add data directly to the internal lists
        for i in range(n):
            seg = hp_array[i * num_elements_in_human_pres: (i + 1) * num_elements_in_human_pres]
            pres = Pres2dData(seg, None, ts)
            zones_with_data.add(pres.zone_num)

            if self.confidence_plot is not None:
                self.confidence_plot.add_data(pres.zone_num, float(pres.confidence), ts)

            if self.presence_plot is not None:
                self.presence_plot.add_data(pres.zone_num, float(pres.inside_state), ts)

        # Fill missing zones with 0 at the same timestamp
        for zone_idx in range(len(self.top_view_plot.detection_zones)):
            if zone_idx not in zones_with_data:
                if self.confidence_plot is not None:
                    self.confidence_plot.add_data(zone_idx, 0.0, ts)
                if self.presence_plot is not None:
                    self.presence_plot.add_data(zone_idx, 0.0, ts)


    def draw_data_frame(self, frame: Presence2DDataFrame, live: bool, from_line_edit: bool = False):

        if live:
            did_pres = False

            if frame.human_presence is not None:
                ts = float(frame.new_timestamp_seqnum_tag_in.get("timestamp", 0.0))
                self.human_presence_data_in(frame.human_presence, frame.detection2d, append_series=True, ts=ts)
                did_pres = True

            self._update_plot_window_and_limits(self._bm_panel, '_bm_window_ms', '_bm_xlims')
            if did_pres:
                self._update_plot_window_and_limits(self.presence_plot, '_presence_window_ms', '_p_xlims')
                self._update_plot_window_and_limits(self.confidence_plot, '_conf_window_ms', '_c_xlims')

            self.top_view_plot._render_trail_live()

        else:
            if frame.human_presence is not None:
                self.human_presence_data_in(frame.human_presence, frame.detection2d, append_series=False)

            max_ts = frame.new_timestamp_seqnum_tag_in["timestamp"]
            if self._bm_panel is not None:
                self._bm_panel.browse_set_view(max_timestamp=max_ts)
            if self.presence_plot is not None:
                self.presence_plot.browse_set_view(max_timestamp=max_ts)
            if self.confidence_plot is not None:
                self.confidence_plot.browse_set_view(max_timestamp=max_ts)

            self.top_view_plot._render_trail_browse()


        #If we have detection data, show it with the detection marker
        if frame.detection2d.shape[0] != 0:
            pass
        else:
            # No detection, just update power data
            show_no_det = frame.detection2d is not None and frame.detection2d.shape[0] == 0
            self.top_view_plot.deactivate_all_last_dets(show_no_detection=show_no_det)

        if frame.detection2d.shape[0] != 0:
            range_pos = frame.detection2d[0]
        else:
            show_no_det = frame.detection2d is not None and frame.detection2d.shape[0] == 0
            self.top_view_plot.deactivate_all_last_dets(show_no_detection=show_no_det)
        
        self.ppb_plot.update(frame)

        self.set_label_time()

        if self.curr_label_frame_max != len(self.ppif_plot_data_buffer):
            self.curr_label_frame_max = len(self.ppif_plot_data_buffer)
            self.set_label_curr_frame()

    def _update_plot_window_and_limits(self, plot_obj, window_attr: str, xlims_attr: str):
        """Update window size and x-limits for a time series plot."""
        if plot_obj is not None:
            plot_obj.process_end()
            x0, x1 = plot_obj.plot.viewRange()[0]
            setattr(self, window_attr, x1 - x0)
            setattr(self, xlims_attr, [x0, x1])

    def update(self):
        if not len(self.ppif_plot_data_buffer):
            return

        fps = self.first_setup_dict.get("fps", 20)

        # Limit the buffer size to avoid memory issues
        if len(self.ppif_plot_data_buffer) > self.thresh_to_cut:
            oldlen = len(self.ppif_plot_data_buffer)
            self.ppif_plot_data_buffer = self.ppif_plot_data_buffer[-self.num_saved_frames:]
            num_removed = oldlen - len(self.ppif_plot_data_buffer)
            self.frame_dropped_counter += num_removed
            self.curr_data_frame_inx = np.clip(self.curr_data_frame_inx - num_removed, 0,
                                               len(self.ppif_plot_data_buffer) - 1)
            self.set_label_curr_frame()

        if self.curr_label_frame_max != len(self.ppif_plot_data_buffer):
            self.curr_label_frame_max = len(self.ppif_plot_data_buffer)
            self.set_label_curr_frame()
        
        self.set_label_time()
    
