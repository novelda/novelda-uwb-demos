from enum import IntEnum
from dataclasses import dataclass
from typing import Any

import pyqtgraph as pg
import pyqtgraph.opengl as gl
import numpy as np
from pyqtgraph.Qt import QtCore, QtGui

QKeys = QtCore.Qt.Key

from pyqtgraph.Qt.QtWidgets import QLabel, QWidget

USED_KEYS = (QKeys.Key_A, QKeys.Key_D)

class XY2DPlotWidget(pg.PlotWidget):
    def __init__(self, 
                 x_axis_name: str,
                 y_axis_name: str,
                 xaxis_unit: str = "",
                 y_axis_unit: str = "",
                 plot_label="",
                 xrange=None,
                 yrange=None,
                 background_color="#3C4D52",
                 show_grid=True,
                 xmark_prefix=None,
                 ymark_prefix=None,
                 plot_mark_prefix=None):

        super().__init__()
        
        self.initialized = False

        self.xmark_prefix = xmark_prefix if xmark_prefix is not None else x_axis_name
        self.ymark_prefix = ymark_prefix if ymark_prefix is not None else y_axis_name
        self.plot_mark_prefix = plot_mark_prefix if plot_mark_prefix is not None else "Plot"

        self.xaxis_unit = xaxis_unit
        self.yaxis_unit = y_axis_unit
        self.xaxis_name = x_axis_name
        self.yaxis_name = y_axis_name

        self.plot_item: pg.PlotItem = self.getPlotItem()
        self.plot_item.setLabel('bottom', x_axis_name, units=xaxis_unit)
        self.plot_item.setLabel('left', y_axis_name, units=y_axis_unit)
        self.plot_item.setTitle(plot_label)
        self.plot_item.setMenuEnabled(False)
        self.setBackground(background_color)

        self.legend = self.plot_item.addLegend()

        self.plot_data_items: dict[Any, pg.PlotDataItem] = {}
        # key: identifier (e.g., rxactive)
        # maybe we put in real(data) or imag(data) depending on what we want to plot

        # disable auto range
        self.plot_item.enableAutoRange(enable=False, axis='xy')

        # disable auto scale button
        self.plot_item.hideButtons()

        self.plot_item.scene().sigMouseClicked.connect(self.on_plot_clicked)

        # increase axis labels and tick font size
        # increase axis labels and tick font size without specifying a font family
        tick_font = QtGui.QFont()
        tick_font.setPointSize(12)

        label_font = QtGui.QFont()
        label_font.setPointSize(14)

        textpen = pg.mkPen(color='w', width=2)

        for axis_name in ("bottom", "left"):
            axis_item: pg.AxisItem = self.plot_item.getAxis(axis_name)
            axis_item.setStyle(tickFont=tick_font)
            axis_item.label.setFont(label_font)
            axis_item.setTextPen(textpen)

        if show_grid:
            self.plot_item.showGrid(x=True, y=True, alpha=0.3)

        if xrange is not None:
            self.plot_item.setXRange(xrange[0], xrange[1])
        if yrange is not None:
            self.plot_item.setYRange(yrange[0], yrange[1])

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

        # on resize, update label position
        vb = self.plot_item.vb
        vb.sigXRangeChanged.connect(self.update_click_label_pos)
        vb.sigYRangeChanged.connect(self.update_click_label_pos)
        vb.sigResized.connect(self.update_click_label_pos)

        self.curr_rangebin_mark = None
        self.curr_mark_identifier = None

    def update_click_label_pos(self):
        # Keep the label inside the axes box near the top-right with a small padding
        (x0, x1), (y0, y1) = self.plot_item.viewRange()
        pad_x = 0.02 * (x1 - x0)  # 2% padding
        pad_y = 0.02 * (y1 - y0)
        self.click_point_label.setPos(x1 - pad_x, y1 - pad_y)
    
    def keyPressEvent(self, event: pg.QtGui.QKeyEvent):
        if event.key() in USED_KEYS:
            self._press_callback(event)
            return
        super().keyPressEvent(event)
    
    def _press_callback(self, event: pg.QtGui.QKeyEvent):
        if event.key() == QKeys.Key_A:
            if self.curr_rangebin_mark is not None and self.curr_rangebin_mark > 0:
                self.mark_point(self.curr_rangebin_mark - 1, self.curr_mark_identifier)
        elif event.key() == QKeys.Key_D:
            if self.curr_rangebin_mark is not None:
                self.mark_point(self.curr_rangebin_mark + 1, self.curr_mark_identifier)
    
    def mark_point(self, idx, identifier):
        if identifier not in self.plot_data_items:
            return
        
        plot_data_item = self.plot_data_items[identifier]
        x_data = plot_data_item._dataset.x
        y_data = plot_data_item._dataset.y
        if x_data is None or y_data is None:
            return
        if idx < 0 or idx >= len(x_data):
            return
        x_val = x_data[idx]
        y_val = y_data[idx]

        self.click_point_label.setText(
            f"{self.plot_mark_prefix}{identifier}\n{self.xmark_prefix}{idx}\n{self.xaxis_name}: {x_val:.3f}\n{self.ymark_prefix}: {y_val:.3f}"
            )

        self.click_point_label.show()
        self.click_point_circle.setData([x_val], [y_val])
        self.click_point_circle.show()

        self.curr_rangebin_mark = idx
        self.curr_mark_identifier = identifier
    
    def clear_mark(self):
        self.click_point_label.hide()
        self.click_point_circle.hide()
        self.curr_rangebin_mark = None
        self.curr_mark_identifier = None

    def on_plot_clicked(self, event):
        # Only handle clicks inside the plot's ViewBox
        vb = self.plot_item.vb
        if not vb.sceneBoundingRect().contains(event.scenePos()):
            self.click_point_label.hide()
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

        closest = None
        min_px_dist = float('inf')

        for identifier, plot_data_item in self.plot_data_items.items():
            x_data = plot_data_item._dataset.x
            y_data = plot_data_item._dataset.y

            if x_data is None or y_data is None:
                continue
            # Compute distance in pixel space
            dx = (x_data - x_click) * sx
            dy = (y_data - y_click) * sy
            distances = np.hypot(dx, dy)
            idx = np.argmin(distances)
            d = float(distances[idx])
            if d < min_px_dist:
                min_px_dist = d
                closest = (idx, identifier)

        if closest is not None and min_px_dist <= max_px_radius:
            idx, ident = closest
            self.mark_point(idx, ident)
        else:
            self.clear_mark()

    def hotkey_callback(self, event: pg.QtGui.QKeyEvent):
        pass

    def plot_or_update_data(self, identifier: Any, x_data: np.ndarray, y_data: np.ndarray,
                            line_color="#FFFFFF", line_width=2, legend_label=None):
        if identifier in self.plot_data_items:
            # update existing plot
            self.plot_data_items[identifier].setData(x_data, y_data)
        else:
            # create new plot
            plot_data_item = self.plot_item.plot(x_data, y_data, pen=pg.mkPen(line_color, width=2))
            self.plot_data_items[identifier] = plot_data_item
            if legend_label is not None:
                self.legend.addItem(plot_data_item, legend_label)
        
        if self.curr_mark_identifier == identifier:
            # re-mark the point if it was marked before
            self.mark_point(self.curr_rangebin_mark, identifier)

    def initialize_plot(self, x_data_bins=None, y_data_bins=None):
        if self.initialized:
            return
        
        self.update_click_label_pos()
        
        self.initialized = True
    
    def change_xlims(self, xmin, xmax):
        self.plot_item.setXRange(xmin, xmax)

    def change_ylims(self, ymin, ymax):
        self.plot_item.setYRange(ymin, ymax)
    
    def set_xaxis_label_unit(self, label, unit: str):
        self.xaxis_unit = unit
        self.xaxis_name = label
        self.plot_item.setLabel('bottom', self.xaxis_name, units=unit)
    
    def set_yaxis_label_unit(self, label, unit: str):
        self.yaxis_unit = unit
        self.yaxis_name = label
        self.plot_item.setLabel('left', self.yaxis_name, units=unit)
