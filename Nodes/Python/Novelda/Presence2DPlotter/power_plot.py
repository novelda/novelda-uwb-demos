from dataclasses import dataclass

import pyqtgraph as pg
import numpy as np
from pyqtgraph.Qt import QtCore, QtGui

QKeys = QtCore.Qt.Key

from Presence2DPlotter.presence_types import Presence2DDataFrame

class PowerPerBinPlot(pg.PlotWidget):
    def __init__(self, 
                range_vec: np.ndarray,
                xlims=None,
                ylims_db=None,
                background_color="#3C4D52",
                power_line_color="#00E5FF",
                power_line_width=2
    ):

        super().__init__()
        
        self.initialized = False

        self.ylims_db = ylims_db
        self.xaxis_vals = range_vec
        self.xlims = xlims

        self.xaxis_unit = "m"
        self.yaxis_unit = "dB"
        self.xaxis_name = "Range"
        self.yaxis_name = "Power"

        self.xmark_prefix = "Range bin"

        self.plot_item: pg.PlotItem = self.getPlotItem()
        self.plot_item.setLabel('bottom', self.xaxis_name, units=self.xaxis_unit)
        self.plot_item.setLabel('left', self.yaxis_name, units=self.yaxis_unit)
        self.plot_item.setTitle("Power per bin")
        self.plot_item.setMenuEnabled(False)
        self.setBackground(background_color)

        self.legend = self.plot_item.addLegend()
        self.legend.anchor((1,0), (1,0), offset=(-10, 10))  # top-right corner

        # disable auto range
        self.plot_item.enableAutoRange(enable=False, axis='xy')

        # disable auto scale button
        self.plot_item.hideButtons()

        self.plot_item.scene().sigMouseClicked.connect(self.on_plot_clicked)

        # increase axis labels and tick font size
        # increase axis labels and tick font size without specifying a font family
        tick_font = QtGui.QFont()
        tick_font.setPointSize(10)

        label_font = QtGui.QFont()
        label_font.setPointSize(11)

        textpen = pg.mkPen(color='w', width=2)

        for axis_name in ("bottom", "left"):
            axis_item: pg.AxisItem = self.plot_item.getAxis(axis_name)
            axis_item.setStyle(tickFont=tick_font)
            axis_item.label.setFont(label_font)
            axis_item.setTextPen(textpen)

        self.plot_item.showGrid(x=True, y=True, alpha=0.25)

        if xlims is not None:
            self.plot_item.setXRange(xlims[0], xlims[1])
        if ylims_db is not None:
            self.plot_item.setYRange(ylims_db[0], ylims_db[1])

        border_pen = pg.mkPen(color='w', width=2)
        border_fill = pg.mkBrush(color=(225, 225, 225, 230))

        self.click_point_label = pg.TextItem("", anchor=(1,0), color='k', border=border_pen, fill=border_fill,
                                             )
        self.click_point_label.setZValue(100)  # Bring to front above plot lines
        self.plot_item.addItem(self.click_point_label)
        self.click_point_label.hide()
        self.click_point_circle = pg.ScatterPlotItem(size=10, pen=pg.mkPen('k'), brush=pg.mkBrush(125, 125, 125, 255))
        self.plot_item.addItem(self.click_point_circle)
        self.click_point_circle.setZValue(100)
        self.click_point_circle.hide()

        # Detection label and red marker
        self.detection_label = pg.TextItem("", anchor=(0, 0), color='k', border=border_pen, fill=border_fill)
        self.detection_label.setZValue(100)
        self.plot_item.addItem(self.detection_label)
        self.detection_label.hide()

        self.detection_point_circle = pg.ScatterPlotItem(size=10, pen=pg.mkPen('r'), brush=pg.mkBrush(255, 0, 0, 255))
        self.plot_item.addItem(self.detection_point_circle)
        self.detection_point_circle.setZValue(100)
        self.detection_point_circle.hide()

        # on resize, update label position
        vb = self.plot_item.vb
        vb.sigXRangeChanged.connect(self.update_click_label_pos)
        vb.sigYRangeChanged.connect(self.update_click_label_pos)
        vb.sigResized.connect(self.update_click_label_pos)

        self.curr_rangebin_mark = None

        self.power_plot_data_item = pg.PlotDataItem(x=[], y=[], pen=pg.mkPen(power_line_color, width=power_line_width), name="Power per bin")
        self.plot_item.addItem(self.power_plot_data_item)

        # Anchor bottoms so label height stays inside the view
        self.click_point_label.setAnchor((1, 1))   # bottom-right
        self.detection_label.setAnchor((0, 1))     # bottom-left
    
    def add_const_plot(self, line_x, line_y, pen, name):
        newthing = pg.PlotDataItem(x=line_x, y=line_y, pen=pen, name=name)
        self.plot_item.addItem(newthing)
        return newthing

    def update_click_label_pos(self):
        (x0, x1), (y0, y1) = self.plot_item.viewRange()
        vb = self.plot_item.vb

        # Convert a pixel margin to data units
        w = max(1.0, vb.width())
        h = max(1.0, vb.height())
        data_per_px_x = (x1 - x0) / w
        data_per_px_y = (y1 - y0) / h

        margin_px = 10.0
        left_extra_px = 50.0

        # Bottom y in data units (a few pixels above the axis)
        y_bot = y0 + margin_px * data_per_px_y

        # this one on the bottom-right
        x_right = x1 - margin_px * data_per_px_x
        self.click_point_label.setPos(x_right, y_bot)

        # this one on the bottom-left
        x_left = x0 + (margin_px + left_extra_px) * data_per_px_x
        self.detection_label.setPos(x_left, y_bot)
    
    def move_marker(self, direction, max_ts):
        if self.curr_rangebin_mark is None:
            return
        self.mark_point(self.curr_rangebin_mark+direction)
    
    def mark_point(self, idx):

        x_data = self.power_plot_data_item._dataset.x
        y_data = self.power_plot_data_item._dataset.y
        if x_data is None or y_data is None:
            return
        if idx < 0 or idx >= len(x_data):
            return
        x_val = x_data[idx]
        y_val = y_data[idx]

        clr = "#7D7D7D"

        # HTML with a gray circular bullet"
        html = (
            f"<div>"
            f"<span style='color:{clr};font-weight:bold'>&#9679;</span> Clicked Point<br>"
            f"Range bin: {idx}<br>"
            f"{self.xaxis_name}: {x_val:.3f} {self.xaxis_unit}<br>"
            f"{self.yaxis_name}: {y_val:.3f} {self.yaxis_unit}"
            f"</div>"
        )
        self.click_point_label.setHtml(html)

        self.click_point_label.show()
        self.click_point_circle.setData([x_val], [y_val])
        self.click_point_circle.show()

        self.curr_rangebin_mark = idx
        self.update_click_label_pos()
    
    def clear_mark(self):
        self.click_point_label.hide()
        self.click_point_circle.hide()
        self.curr_rangebin_mark = None

    def on_plot_clicked(self, event):
        # Only handle clicks inside the plot's ViewBox
        vb = self.plot_item.vb
        if not vb.sceneBoundingRect().contains(event.scenePos()):
            self.click_point_label.hide()
            return
        
        x_data = self.power_plot_data_item._dataset.x
        y_data = self.power_plot_data_item._dataset.y

        if x_data is None or y_data is None:
            self.clear_mark()
            return

        # Map click to data coordinates
        pos = vb.mapSceneToView(event.scenePos())
        x_click, y_click = pos.x(), pos.y()

        # Compute pixel-per-data scaling to measure distance in screen space
        (x0, x1), (y0, y1) = self.plot_item.viewRange()
        w = vb.width()
        h = vb.height()
        if w <= 0 or h <= 0 or x1 == x0 or y1 == y0:
            self.click_point_label.hide()
            return

        sx = w / (x1 - x0)  # pixels per x-unit
        sy = h / (y1 - y0)  # pixels per y-unit

        # Selection radius in pixels
        max_px_radius = 20.0

        closest_idx = None
        min_px_dist = float('inf')

        # Compute distance in pixel space
        dx = (x_data - x_click) * sx
        dy = (y_data - y_click) * sy
        distances = np.hypot(dx, dy)
        idx = np.argmin(distances)
        d = float(distances[idx])
        if d < min_px_dist:
            min_px_dist = d
            closest_idx = idx

        if closest_idx is not None and min_px_dist <= max_px_radius:
            self.mark_point(closest_idx)
        else:
            self.clear_mark()
    
    def show_detection(self, x: float, y: float, title: str = "Detection"):
        """Show a detection marker (red) and a label with a red dot."""
        # Place/update red circle on the data point
        self.detection_point_circle.setData([x], [y])
        self.detection_point_circle.show()

        # HTML with a red circular bullet
        html = (
            f"<div>"
            f"<span style='color:#d33;font-weight:bold'>&#9679;</span> {title}<br>"
            f"{self.xaxis_name}: {x:.3f} {self.xaxis_unit}<br>"
            f"{self.yaxis_name}: {y:.3f} {self.yaxis_unit}"
            f"</div>"
        )
        self.detection_label.setHtml(html)
        self.detection_label.show()

        # Ensure label stays at top-left on resize/zoom
        self.update_click_label_pos()
    
    def clear_detection(self):
        self.detection_label.hide()
        self.detection_point_circle.hide()

    def update(self, frame: Presence2DDataFrame):
        self.power_plot_data_item.setData(x=self.xaxis_vals, y=frame.power_per_bin)

        # if detection exists, update its position
        if frame.detection2d.shape[0] != 0:
            self.show_detection(x=frame.detection2d[0], y=5*np.log10(frame.detection2d[3]))
        else:
            self.clear_detection()

        if self.click_point_circle.isVisible() and self.curr_rangebin_mark is not None:
            # update the click label position
            self.mark_point(self.curr_rangebin_mark)

    def initialize(self, range_vals: np.ndarray):
        self.initialized = True
        self.xaxis_vals = range_vals
    
    def set_y_range(self, min_db: float, max_db: float):
        self.plot_item.setYRange(min_db, max_db)
        self.ylims_db = (min_db, max_db)
    
    def set_x_range(self, min_range: float, max_range: float):
        self.plot_item.setXRange(min_range, max_range)
        self.xlims = (min_range, max_range)
    
    def set_xaxis_label_unit(self, label, unit: str):
        self.xaxis_unit = unit
        self.xaxis_name = label
        self.plot_item.setLabel('bottom', self.xaxis_name, units=unit)
    
    def set_yaxis_label_unit(self, label, unit: str):
        self.yaxis_unit = unit
        self.yaxis_name = label
        self.plot_item.setLabel('left', self.yaxis_name, units=unit)
