import numpy as np
import pyqtgraph as pg
from collections import deque
from enum import IntEnum
from pyqtgraph.Qt.QtWidgets import (
    QMainWindow, QWidget, QGridLayout, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QApplication, QCheckBox, QGraphicsWidget, QGraphicsTextItem, QGraphicsView
    )
from pyqtgraph.Qt import QtGui, QtCore

from Presence2DPlotter.presence_types import HumanPresence2DIdx, DetectionZone, Pres2dData

def xy_to_radar(x, y):
    return y, x # "y" axis is already inverted in pyqtgraph

def polar_to_xy(r, theta):
    return r * np.cos(theta), r * np.sin(theta)

class TopViewPlot:
    def __init__(self, gfx, plot, zone_colors, confidence_plot=None, presence_plot=None):
        self.parent_plotter = None
        self.confidence_plot = confidence_plot
        self.presence_plot = presence_plot
        self.gfx, self.plot = gfx, plot
        self.zone_colors = zone_colors
        self.detection_zones = []
        self.last_dets = []
        self.last_dets_colors = [
            pg.mkColor(255, 0, 0, 255),
            pg.mkColor(0, 0, 255, 255),
        ]
        self._fov_items = []
        self._fov_visible = True
        self._trail_items = {}
        self._trail_hist = {}
        self.top_view = True
        self._xy_coordinates_visible = True

        # Configure plot
        self.plot.setMenuEnabled(False)
        self.plot.hideButtons()

        # more params
        self.pixel_width = 2
        self.last_det_size = 10
        self.trail_alpha_min = 50
        self.trail_alpha_max = 255
        self.trail_size_min = 3.0
        self.trail_size_max = 8.0
        self.trail_back = 10
        self.trail_fwd = 10
        self.trail_color_past = (255, 64, 64, 255)
        self.trail_color_future = (80, 180, 255, 255)
        self.xy_xlims = [-4.28, 4.28]
        self.xy_ylims = [0, 6]
        self.curr_data_frame_inx = 0
        self.ppif_plot_data_buffer = []
        self.current_zone = None
        self.performance_zone = None
        self.lowpower_zone = None

        # coordinate widget
        label = QLabel()
        label.setStyleSheet("""
                QLabel {
                    background-color:rgba(60, 77, 82, 0.9);
                    border: 1.2px solid rgba(230, 230, 230, 1);
                    border-radius: 5px;
                    padding: 4px;
                    color: white;
                    font-size: 12px;
                }
            """)
        label.setFixedSize(100, 58)

        # Embed it in the graphics scene via proxy
        self.coord_proxy = self.plot.scene().addWidget(label)
        self.coord_label = label
        self.coord_proxy.setVisible(False)

        # Color pens/brushes for zones
        self.yes_det_color_pen = pg.mkPen('g', width=2)
        self.yes_det_color_brush = pg.mkBrush(0, 255, 0, 50)
        self.no_det_color_pen = pg.mkPen('r', width=2)
        self.no_det_color_brush = pg.mkBrush(255, 0, 0, 30)


    def _set_xylims(self):
        self.xy_ylims = [self.xy_ylims[0], self.xy_xlims[1]]
        self.plot.setXRange(self.xy_xlims[0], self.xy_xlims[1], padding=0)
        self.plot.setYRange(self.xy_ylims[0], self.xy_ylims[1], padding=0)

    def invert_top_view(self):
        if not self.top_view:
            self.plot.invertY(False)
            self.top_view = True
        else:
            self.plot.invertY(True)
            self.top_view = False

    def _toggle_xy_coordinates(self, visible: bool):
        self._xy_coordinates_visible = visible
        if not visible:
            self.coord_proxy.setVisible(False)

    def add_detection_zone(self, xy_array: np.ndarray):
        new_zone = DetectionZone(xy_array)

        xpoints = np.append(xy_array[0::2], xy_array[0])
        ypoints = np.append(xy_array[1::2], xy_array[1])

        qpath = pg.arrayToQPath(x=ypoints, y=xpoints, connect='all')

        qgraphicspathitem = pg.QtWidgets.QGraphicsPathItem(qpath)
        new_zone.plot_item = qgraphicspathitem
        self.set_det_zone_active(new_zone, False)

        self.plot.addItem(new_zone.plot_item)
        self.detection_zones.append(new_zone)

        self.last_dets.append(self.plot.plot([0], [0], symbol="o",
                                                 symbolBrush=pg.mkBrush(self.last_dets_colors[len(self.last_dets)],
                                                                        width=self.pixel_width),
                                                 symbolSize=self.last_det_size))

        self.last_dets[-1].setZValue(10)
        self.last_dets[-1].setVisible(False)

        zone_idx = len(self.detection_zones) - 1
        trail = pg.ScatterPlotItem(pen=None)
        trail.setZValue(5)
        trail.setVisible(True)
        self.plot.addItem(trail)

        self._trail_items[zone_idx] = trail
        self._trail_hist[zone_idx] = deque(maxlen=max(self.trail_back, 200))

        self.confidence_plot.init_new_plot_data(len(self.detection_zones) - 1)
        self.presence_plot.init_new_plot_data(len(self.detection_zones) - 1)

        return new_zone

    def add_detection_zones_from_buffer(self, xybuffer_performance: np.ndarray, xy_index_buffer_performance: np.ndarray,
                                        xybuffer_lowpower: np.ndarray, xy_index_buffer_lowpower: np.ndarray):

        inx_buff = np.append(xy_index_buffer_performance * 2, len(xybuffer_performance))
        for i in range(len(inx_buff) - 1):  # assumes one zone for now
            self.performance_zone = self.add_detection_zone(xybuffer_performance[int(inx_buff[i]):int(inx_buff[i + 1])])

        self.current_zone = self.performance_zone

        if xybuffer_lowpower is None or len(xybuffer_lowpower) == 0:
            return

        inx_buff = np.append(xy_index_buffer_lowpower, len(xybuffer_lowpower) * 2)
        for i in range(len(inx_buff) - 1):  # assumes one zone for now
            self.lowpower_zone = self.add_detection_zone(xybuffer_lowpower[int(inx_buff[i]):int(inx_buff[i + 1])])

    def set_det_zone_active(self, zone: DetectionZone, active: bool):
        if active:
            zone.plot_item.setPen(self.yes_det_color_pen)
            zone.plot_item.setBrush(self.yes_det_color_brush)
        else:
            zone.plot_item.setPen(self.no_det_color_pen)
            zone.plot_item.setBrush(self.no_det_color_brush)

    def deactivate_all_zones(self):
        for zone in self.detection_zones:
            self.set_det_zone_active(zone, False)

    def deactivate_all_last_dets(self, show_no_detection: bool = False):
        for det in self.last_dets:
            det.setVisible(False)

        if show_no_detection:
           self._show_no_detection_message()
        else:
            self.coord_proxy.setVisible(False)

    def set_last_det(self, zone_inx, x, y, snr):
        self.last_dets[zone_inx].setData([y], [x])
        self.last_dets[zone_inx].setVisible(True)

        # Update coordinate display
        text = f"X: {x:.2f}m\nY: {y:.2f}m\nSNR: {snr:.2f}dB"
        self.coord_label.setText(text)

        #self.coord_label.adjustSize()

        # Position in view coordinates (top-left corner with offset)
        view = self.plot.getViewBox().parentWidget()
        view_pos = view.mapFromScene(self.plot.sceneBoundingRect().topLeft())
        self.coord_proxy.setPos(view_pos.x() + 30, view_pos.y() + 30)

        if self._xy_coordinates_visible:
            self.coord_proxy.setVisible(True)


    def draw_fov_lines_with_tags(self, rmax, d_range, d_angle, angle_min, angle_max):

        angle_min = angle_min * np.pi / 180
        angle_max = angle_max * np.pi / 180
        d_angle = d_angle * np.pi / 180

        num_ranges = int(rmax / d_range) + 1
        ranges = np.linspace(0, rmax, num_ranges)

        num_angles = int((angle_max - angle_min) / d_angle) + 1
        angles = np.linspace(angle_min, angle_max, num_angles)

        for r in ranges:
            highres_angles = np.linspace(angle_min, angle_max, int(15 * r))
            x, y = polar_to_xy(r, highres_angles)
            x, y = xy_to_radar(x, y)
            itm = self.plot.plot(x, y, pen=pg.mkPen('w', width=1))
            itm.setVisible(self._fov_visible)
            self._fov_items.append(itm)

        for a in angles:
            x, y = polar_to_xy(ranges, a)
            x, y = xy_to_radar(x, y)
            itm = self.plot.plot(x, y, pen=pg.mkPen('w', width=1))
            itm.setVisible(self._fov_visible)
            self._fov_items.append(itm)

        angle_label_offset = rmax * 0.1 if not self.top_view else 0

        dist_label_offset = 0.5 if self.top_view else 0

        for r in ranges:
            x, y = polar_to_xy(r, angle_min)
            x, y = xy_to_radar(x, y)
            new_text_item = pg.TextItem(f'{r:.0f}m', color='w')
            #self.plot.addItem(new_text_item)
            new_text_item.setPos(x, y - dist_label_offset)
            new_text_item.setVisible(self._fov_visible)
            self._fov_items.append(new_text_item)

        for a in angles:
            x, y = polar_to_xy(rmax, a)
            x, y = xy_to_radar(x, y)
            new_text_item = pg.TextItem(f'{a * 180 / np.pi:.0f}\u00B0', color='w')
            self.plot.addItem(new_text_item)
            new_text_item.setPos(x, y + angle_label_offset)
            new_text_item.setVisible(self._fov_visible)
            self._fov_items.append(new_text_item)

    def set_fov_visible(self, visible: bool):
        self._fov_visible = bool(visible)
        for it in self._fov_items:
            it.setVisible(self._fov_visible)

    def toggle_fov(self):
        self.set_fov_visible(not self._fov_visible)

    def _alpha_ramp(self, rank: int, total: int) -> int:
        if total <= 1:
            return int(self.trail_alpha_max)
        t = rank / (total - 1)  # 0..1
        a = self.trail_alpha_max + (self.trail_alpha_min - self.trail_alpha_max) * t
        return max(0, min(255, int(a)))

    def _size_ramp(self, rank: int, total: int) -> float:
        if total <= 1:
            return float(self.trail_size_max)
        t = rank / (total - 1)  # 0..1
        s = self.trail_size_max + (self.trail_size_min - self.trail_size_max) * t
        return float(s)

    def _render_trail_live(self):
        if not self._trail_hist:
            return

        if hasattr(self, 'parent_plotter') and self.parent_plotter:
            cur = self.parent_plotter.curr_data_frame_inx
        else:
            cur = self.curr_data_frame_inx

        for zone_idx, hist in self._trail_hist.items():
            if zone_idx not in self._trail_items:
                continue
            # take only entries with frame_idx <= cur (past), last N
            past = [(fi, x, y) for (fi, x, y) in hist if fi <= cur][-self.trail_back:]
            if not past:
                self._trail_items[zone_idx].setData([], [])
                continue
            # newest first for alpha ramp
            past.sort(key=lambda t: t[0], reverse=True)  # newest first
            N = len(past)
            spots = []
            for rank, (_, x, y) in enumerate(past):
                a = self._alpha_ramp(rank, N)
                s = self._size_ramp(rank, N)
                r, g, b, _ = self.trail_color_past
                spots.append({'pos': (y, x), 'size': s, 'brush': pg.mkBrush(r, g, b, a)})
            self._trail_items[zone_idx].setData(spots)


    def _render_trail_browse(self):
        if hasattr(self, 'parent_plotter') and self.parent_plotter:
            ppif_buffer = self.parent_plotter.ppif_plot_data_buffer
            curr_idx = self.parent_plotter.curr_data_frame_inx
        else:
            ppif_buffer = self.ppif_plot_data_buffer
            curr_idx = self.curr_data_frame_inx

        if not ppif_buffer:
            return

        idx = max(0, min(curr_idx, len(ppif_buffer) - 1))
        back = int(getattr(self, "trail_back", 10))
        fwd = int(getattr(self, "trail_fwd", 10))

        # ensure scatter items exist per zone
        if not hasattr(self, "_trail_items"):
            self._trail_items = {}
        num_zones = len(self.detection_zones) if hasattr(self, "detection_zones") else 0
        for z in range(num_zones):
            if z not in self._trail_items:
                sp = pg.ScatterPlotItem(pen=None)  # size per-spot later
                sp.setZValue(5)
                sp.setVisible(True)
                self.plot.addItem(sp)
                self._trail_items[z] = sp

        # colors
        pr, pgc, pb, pa = getattr(self, "trail_color_past", (255, 64, 64, 255))
        fr, fgc, fb, fa = getattr(self, "trail_color_future", (80, 180, 255, 255))

        # compute past/future windows (indices)
        lo_past = max(0, idx - back)
        hi_past = idx  # exclusive
        lo_fut = idx + 1
        hi_fut = min(len(ppif_buffer), idx + 1 + fwd)

        # cache positions per frame
        pos_cache = {}
        for j in range(lo_past, hi_past):
            pos_cache[j] = self._extract_zone_positions(ppif_buffer[j])
        for j in range(lo_fut, hi_fut):
            pos_cache[j] = self._extract_zone_positions(ppif_buffer[j])

        # build the spots
        for z in range(num_zones):
            spots = []

            # Past spots
            past_idxs = list(range(hi_past - 1, lo_past - 1, -1))
            Np = len(past_idxs)
            for rank, j in enumerate(past_idxs):
                xy = pos_cache.get(j, {}).get(z)
                if not xy:
                    continue
                x, y = xy
                a = self._alpha_ramp(rank, Np) if hasattr(self, "_alpha_ramp") else 200
                s = self._size_ramp(rank, Np) if hasattr(self, "_size_ramp") else 6
                spots.append({'pos': (y, x), 'size': s, 'brush': pg.mkBrush(pr, pgc, pb, a)})

            # Future spots
            fut_idxs = list(range(lo_fut, hi_fut))
            Nf = len(fut_idxs)
            for rank, j in enumerate(fut_idxs):
                xy = pos_cache.get(j, {}).get(z)
                if not xy:
                    continue
                x, y = xy
                a = self._alpha_ramp(rank, Nf) if hasattr(self, "_alpha_ramp") else 160
                s = self._size_ramp(rank, Nf) if hasattr(self, "_size_ramp") else 5
                spots.append({'pos': (y, x), 'size': s, 'brush': pg.mkBrush(fr, fgc, fb, a)})

            # push to the scatter for this zone
            if z in self._trail_items:
                self._trail_items[z].setData(spots)


    def _record_trail_from_human_presence(self, hp_array, frame_idx: int):
        if hp_array is None:
            return
        num_elems = len(HumanPresence2DIdx)
        n = int(len(hp_array) / num_elems)
        for i in range(n):
            seg = hp_array[i * num_elems:(i + 1) * num_elems]
            pres = Pres2dData(seg, None, None)
            self._trail_record(pres.zone_num, pres.x, pres.y, frame_idx)


    def _trail_record(self, zone_idx: int, x: float, y: float, frame_idx: int):
        if zone_idx not in self._trail_hist:
            self._trail_hist[zone_idx] = deque(maxlen=max(self.trail_back + self.trail_fwd, 200))
        self._trail_hist[zone_idx].append((frame_idx, float(x), float(y)))


    def _extract_zone_positions(self, frame) -> dict[int, tuple[float, float]]:
        hp = getattr(frame, "human_presence", None)
        if hp is None:
            return {}
        num = len(HumanPresence2DIdx)
        nmsg = len(hp) // num
        out = {}
        for i in range(nmsg):
            seg = hp[i * num:(i + 1) * num]
            p = Pres2dData(seg, None, None)  # you already use this type
            # only record valid zones
            out[p.zone_num] = (p.x, p.y)
        return out

    def _show_no_detection_message(self) -> None:
        """Show info box with 'No detection' message."""
        if self.coord_proxy is None:
            label = QLabel()
            label.setStyleSheet("""
                QLabel {
                    background-color: rgba(60, 77, 82, 0.9);
                    border: 1.2px solid rgba(230, 230, 230, 1);
                    border-radius: 5px;
                    padding: 4px;
                    color: white;
                    font-size: 12px;
                }
            """)
            self.coord_proxy = self.plot.scene().addWidget(label)
            self.coord_label = label

        self.coord_label.setText("No detection")

        # Position in view coordinates (top-left corner with offset)
        view = self.plot.getViewBox().parentWidget()
        view_pos = view.mapFromScene(self.plot.sceneBoundingRect().topLeft())
        self.coord_proxy.setPos(view_pos.x() + 30, view_pos.y() + 30)

        if self._xy_coordinates_visible:
            self.coord_proxy.setVisible(True)


    def switch_zone_to_performance(self):
        self.current_zone = self.performance_zone
        self.performance_zone.plot_item.setVisible(True)
        if self.lowpower_zone is not None:
            self.lowpower_zone.plot_item.setVisible(False)


    def switch_zone_to_lowpower(self):
        self.current_zone = self.lowpower_zone
        self.performance_zone.plot_item.setVisible(False)
        self.lowpower_zone.plot_item.setVisible(True)
