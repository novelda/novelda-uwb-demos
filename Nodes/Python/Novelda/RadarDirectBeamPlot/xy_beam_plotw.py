import numpy as np

import pyqtgraph as pg
import pyqtgraph.opengl as gl
from pyqtgraph.Qt import QtCore, QtGui

QKeys = QtCore.Qt.Key

from pyqtgraph.Qt.QtWidgets import QLabel, QWidget

from scipy import ndimage as ndi

USED_KEYS = (QKeys.Key_A, QKeys.Key_D)

class XYBeamPlotWidget(pg.PlotWidget):
    def __init__(self, 
                 plot_label="",
                 color_min=None,
                 color_max=None,
                 background_color="#3C4D52",
                 img_shape_hw=(300, 600)
    ):

        super().__init__()
        
        self.initialized = False

        self.image_shape = img_shape_hw


        self.plot_item: pg.PlotItem = self.getPlotItem()

        self.plot_item.setTitle(plot_label)
        self.plot_item.setMenuEnabled(False)
        self.background_color = background_color
        self.setBackground(background_color)

        # disable auto scale button
        self.plot_item.hideButtons()

        # increase axis labels and tick font size
        # increase axis labels and tick font size without specifying a font family
        tick_font = QtGui.QFont()
        tick_font.setPointSize(12)

        label_font = QtGui.QFont()
        label_font.setPointSize(14)

        self.setAspectLocked(True)

        self.image_item = pg.ImageItem(axisOrder='row-major') # (H, W) -> (W, H) to fit with plotting
        self.addItem(self.image_item)

        cmap = pg.colormap.get('viridis')
        self.colorbar = pg.ColorBarItem(values=(color_min, color_max), colorMap=cmap)
        self.colorbar.setImageItem(self.image_item, insert_in=self.plot_item)
        self.colorbar.setVisible(True)

        self._fov_items: list[pg.PlotDataItem] = []

        self.img_data = None

        self._angle_idx_img: np.ndarray | None = None
        self._range_idx_img: np.ndarray | None = None
        self._invalid_mask: np.ndarray | None = None
        self._bin_length: float | None = None
        self._scale_px_per_m: float | None = None
        self._x0: int | None = None
        self._y0: int | None = None

        self._overlay_items: list[pg.GraphicsObject] = []

        self.top_view = False

        self.hideAxis('left')
        self.hideAxis('bottom')

        self.plotting_mode = 0 # 0 for interpolated between angles, (not 0) for small sector for each angle
        
        self._sec_angle_inx_img: np.ndarray = None
        # self._sec_range_inx_img: np.ndarray = None
        self._sec_invalid_mask: np.ndarray = None

    def keyPressEvent(self, event: pg.QtGui.QKeyEvent):
        if event.key() in USED_KEYS:
            self._press_callback(event)
            return
        super().keyPressEvent(event)
    
    def _press_callback(self, event: pg.QtGui.QKeyEvent):
        if event.key() == QKeys.Key_A:
            pass
        elif event.key() == QKeys.Key_D:
            pass

    def hotkey_callback(self, event: pg.QtGui.QKeyEvent):
        pass

    def _precompute_inverse_map(self):

        H, W = self.image_shape
        x = np.arange(W, dtype=np.float64)  # cols
        y = np.arange(H, dtype=np.float64)  # rows
        Xp, Yp = np.meshgrid(x, y)          # shape (H, W)

        # Use the chosen origin (x0, y0) in pixels; y points up when plotted
        dx_m = (Xp - self._x0) / self._scale_px_per_m
        dy_m = (Yp - self._y0) / self._scale_px_per_m

        range_m = np.hypot(dx_m, dy_m) - self.range_vec[0]  # -range_offset to get higher indices at the start

        angle_rad = np.arctan2(dx_m, dy_m) * -1 # flip angles for radar coords

        angle_idx_img = np.interp(angle_rad, self.az_radians, np.arange(len(self.az_radians)), left=np.nan, right=np.nan)

        # Map range -> fractional bin index (uniform grid)
        range_idx_img = (range_m) / self._bin_length

        # Invalid outside angular FOV or range bounds
        invalid = (
            np.isnan(angle_idx_img)
            | (range_m < self._starting_range - self.range_vec[0])
            | (range_m > self._actual_range_vec[-1] - self.range_vec[0]) # range_m is offset by  (- self.range_vec[0])
        )

        self._angle_idx_img = angle_idx_img
        self._range_idx_img = range_idx_img
        self._invalid_mask = invalid

        # ----------------
        # generate sector map for plotting mode 1
        # each beam will have its own mini sector without interpolating between neightbouring beams

        max_sec_rad = np.full_like(self.az_radians, self.beam_sector_width_rad)
        # all beam sections have same rad width? lets start with that
        if len(self.az_radians) > 1:
            azdiff = (self.az_radians[1:] - self.az_radians[:-1]) / 2.0
            azdiff[azdiff > self.beam_sector_width_rad] = self.beam_sector_width_rad
            max_sec_rad[:-1] = azdiff
            max_sec_rad[-1] = max_sec_rad[-2]

        self._sec_angle_inx_img = np.ones_like(self._angle_idx_img, dtype=int)
        self._sec_invalid_mask = np.ones_like(self._invalid_mask, dtype=bool)

        for ii, az in enumerate(self.az_radians):
            thismax = max_sec_rad[ii]
            if ii > 0 or ii < len(self.az_radians)-1:
                thismax = min(max_sec_rad[ii], max_sec_rad[ii-1])

            mask = (angle_rad > az-thismax) & (angle_rad < az+thismax)
            self._sec_angle_inx_img[mask] = ii
            self._sec_invalid_mask[mask] = False
        
        self._sec_invalid_mask |= (
            (range_m < self._starting_range - self.range_vec[0]) 
            | (range_m > self._actual_range_vec[-1] - self.range_vec[0])
        )
            
    def radar2img(self, x, y):
        return self._x0 + x*self._scale_px_per_m, self._y0 + y*self._scale_px_per_m

    def set_topdown_view(self, state):
        self.top_view = state == QtCore.Qt.CheckState.Checked
        self.invertY(self.top_view)
        self.invertX(self.top_view)
    
    def draw_lines_for_each_beam(self):
        # draw lines showing each beam direction, and text showing the angle
        for az in self.az_radians:
            x, y = self.radar2img(-np.sin(az)*self.range_vec[-1], np.cos(az)*self.range_vec[-1])
            pen = pg.mkPen("#EE9D40", width=1)
            itm = pg.PlotDataItem(x=[self._x0, x], y=[self._y0, y], pen=pen)
            self.addItem(itm)

            text_item = pg.TextItem(f'{np.rad2deg(az):.1f}\u00B0', color="#F3BA7A", anchor=(0.5,0.5))
            unit = np.array([x, y]) - np.array([self._x0, self._y0])
            unit = unit / np.linalg.norm(unit)
            offset = unit * -20  # 20 pixels away from line end
            text_item.setPos(x + offset[0], y + offset[1])
            text_item.setZValue(10)
            self.addItem(text_item)

    def initialize_plot(self, az_angles: np.ndarray, num_range_bins: int, 
                        range_offset: float, bin_length: float, starting_range: float=0.0, beam_sector_width_deg: float=20.0):
        """
        If starting_range != 0.0 things won't look exactly right in the plot
        """
        if self.initialized:
            return
        
        self.az_radians = np.deg2rad(az_angles).astype(np.float32)
        self.range_vec = np.linspace(0, num_range_bins * bin_length, num=num_range_bins, dtype=np.float32) + float(range_offset)
        self.beam_sector_width_rad = np.deg2rad(beam_sector_width_deg)/2.0

        self._actual_range_vec = self.range_vec[self.range_vec >= 0.0]
        self._actual_zero_val = self._actual_range_vec[0]

        self._starting_range = starting_range

        self._bin_length = float(bin_length)

        H, W = self.image_shape  # shape is (rows, cols)

        self._x0 = int(W // 2)  # middle
        self._y0 = int(0)       # bottom
        self.img_origin = np.array([self._x0, self._y0], dtype=np.int64)

        usable_h = float(H) # maybe put something around the plot img ?
        self._scale_px_per_m = (usable_h) / (self._actual_range_vec[-1] - self._actual_zero_val)

        self._precompute_inverse_map()

        self.draw_fov_lines_with_tags(
            rmax=self.range_vec[-1],
            d_range=1.0,
            d_angle=10.0,
            angle_min=-90,
            angle_max=90
        )

        self.draw_lines_for_each_beam()

        self.initialized = True
    
    def set_colormap_range(self, color_min: float, color_max: float):
        self.colorbar.setLevels(low=color_min, high=color_max)
    
    def update_data(self, beam_data: np.ndarray):
        if not self.initialized:
            pass

        if self.img_data is None:
            self.img_data = np.zeros_like(self._angle_idx_img, dtype=np.float32)

        ang_inx = self._angle_idx_img if self.plotting_mode==0 else self._sec_angle_inx_img
        inv_mask = self._invalid_mask if self.plotting_mode==0 else self._sec_invalid_mask

        ndi.map_coordinates(
            beam_data,
            [ang_inx, self._range_idx_img],
            output=self.img_data,
            order=1,
            mode="constant",
            cval=np.nan,
            prefilter=False
        )

        # Mask outside FOV/range to NaN or 0
        self.img_data[inv_mask] = np.nan

        self.image_item.setImage(self.img_data, autoLevels=False)

    
    def draw_fov_lines_with_tags(self, rmax, d_range, d_angle, angle_min, angle_max):

        angle_min *= -1
        angle_max *= -1

        angle_min = angle_min * np.pi / 180
        angle_max = angle_max * np.pi / 180
        d_angle = d_angle * np.pi / 180

        num_ranges = int(rmax / d_range) + 1
        ranges = np.linspace(0, rmax-self._actual_zero_val, num_ranges)

        num_angles = int((angle_min - angle_max) / d_angle + 1)
        angles = np.linspace(angle_min, angle_max, num_angles)

        fov_pen = pg.mkPen('w', width=1)

        for r in ranges:
            highres_angles = np.linspace(angle_min, angle_max, int(60 * r))
            x, y = self.radar2img(r*np.sin(highres_angles), r*np.cos(highres_angles))
            itm = pg.PlotDataItem(x=x, y=y, pen=fov_pen)
            #itm.setVisible(self._fov_visible)
            self._fov_items.append(itm)

        for ang in angles:
            x, y = self.radar2img(ranges*np.sin(ang), ranges*np.cos(ang))
            itm = pg.PlotDataItem(x=x, y=y, pen=fov_pen)
            #itm.setVisible(self._fov_visible)
            self._fov_items.append(itm)

        angle_label_offset = rmax * 0.1 

        dist_label_offset = 0.0

        for r in ranges:
            x, y = self.radar2img(r*np.sin(angle_min), r*np.cos(angle_min))
            new_text_item = pg.TextItem(f'{r:.0f}m', color='w', anchor=(0,0))
            new_text_item.setPos(x, y - dist_label_offset)
            self._fov_items.append(new_text_item)

        for a in angles:
            x, y = self.radar2img(rmax*np.sin(a), rmax*np.cos(a))
            new_text_item = pg.TextItem(f'{-a * 180 / np.pi:.0f}\u00B0', color='w', anchor=(0,1) if a>0 else (1,1))
            new_text_item.setPos(x, y + angle_label_offset)
            self._fov_items.append(new_text_item)
        
        for itm in self._fov_items:
            self.addItem(itm)
    
    def change_xlims(self, xmin, xmax):
        self.setXRange(xmin, xmax)

    def change_ylims(self, ymin, ymax):
        self.setYRange(ymin, ymax)
    
    def set_xaxis_label_unit(self, label, unit: str):
        self.xaxis_unit = unit
        self.xaxis_name = label
        self.plot_item.setLabel('bottom', self.xaxis_name, units=unit)
    
    def set_yaxis_label_unit(self, label, unit: str):
        self.yaxis_unit = unit
        self.yaxis_name = label
        self.plot_item.setLabel('left', self.yaxis_name, units=unit)
