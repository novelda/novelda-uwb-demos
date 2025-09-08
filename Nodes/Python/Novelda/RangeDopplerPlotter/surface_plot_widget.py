from enum import IntEnum
from dataclasses import dataclass
import pyqtgraph as pg
import pyqtgraph.opengl as gl
import numpy as np

from Utils.colormap import colorize, colorize_1d

import qimage2ndarray

from OpenGL.GL import glDeleteTextures
from pyqtgraph.Qt import QtCore, QtGui

QKeys = QtCore.Qt.Key

from pyqtgraph.opengl.GLGraphicsItem import GLGraphicsItem

from pyqtgraph.Qt.QtWidgets import QLabel, QWidget

from PySide6.QtGui import QFontDatabase


USED_KEYS = (QKeys.Key_Space, QKeys.Key_Left, QKeys.Key_Right,
             QKeys.Key_R, QKeys.Key_W, QKeys.Key_A, QKeys.Key_S, QKeys.Key_D,
             QKeys.Key_X, QKeys.Key_Z, QKeys.Key_Y)


class SurfaceMark:
    def __init__(self):
        
        self.xbin: int = -1
        self.ybin: int = -1
        self.zval: float = -1e10
        self.label: QLabel = None
        self.line: gl.GLLinePlotItem = None


# for for pyqtgraphs alpha blending with depth test, not needed right now  
# class DepthBlendLine(gl.GLLinePlotItem):
#     """Semi-transparent line with depth test so it is hidden when behind opaque meshes."""
#     def paint(self):
#         from OpenGL.GL import (
#             glEnable, glBlendFunc, glDisable,
#             GL_BLEND, GL_DEPTH_TEST,
#             GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA,
#             glPolygonOffset, GL_POLYGON_OFFSET_FILL
#         )
#         # Enable depth test so existing depth buffer occludes the line
#         glEnable(GL_DEPTH_TEST)
#         # Enable blending for alpha
#         glEnable(GL_BLEND)
#         glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
#         # Small polygon offset to reduce z-fighting with surface (optional)
#         glEnable(GL_POLYGON_OFFSET_FILL)
#         glPolygonOffset(1.0, 1.0)
#         super().paint()
#         # (Leave states enabled; pyqtgraph draws everything with depth anyway.)


class AxisConfig:
    """Configuration for a plot axis."""
    def __init__(self, name, unit, min_val, max_val, num_bins):
        self.name = name
        self.unit = unit
        self.min_val = np.float64(min_val)
        self.max_val = np.float64(max_val)
        self.num_bins = num_bins

        self.curr_min_val = np.float64(self.min_val)
        self.curr_max_val = np.float64(self.max_val)
    
    def bin2val(self, binval):
        return (binval / self.num_bins) * (self.max_val - self.min_val) + self.min_val

    def val2bin(self, val):
        """Remember, it returns float"""
        return (val - self.min_val) / (self.max_val - self.min_val) * self.num_bins

    def clone(self):
        """Return an independent copy so plots don't share mutable state."""
        c = AxisConfig(self.name, self.unit, self.min_val, self.max_val, self.num_bins)
        c.curr_min_val = self.curr_min_val
        c.curr_max_val = self.curr_max_val
        return c

class Origin(IntEnum):
    BottomLeft      = 1
    BottomCenter    = 2
    BottomRight     = 3
    CenterLeft      = 4
    Center          = 5
    CenterRight     = 6
    TopLeft         = 7
    TopCenter       = 8
    TopRight        = 9

class NoArrowGLViewWidget(gl.GLViewWidget):

    def __init__(self, *a, **k):
        super().__init__(*a, **k)
        self._pick_callback = None  # set by Matrix3DPlot
        self._press_callback = None

        #self.parent_plot = None  # set by Matrix3DPlot

    def keyPressEvent(self, event: pg.QtGui.QKeyEvent):
        if event.key() in USED_KEYS:
            self._press_callback(event)
            return
        super().keyPressEvent(event)
    
    def mousePressEvent(self, event: pg.QtGui.QMouseEvent):
        if (event.button() == QtCore.Qt.MouseButton.RightButton):
            self._pick_callback(event)
            event.accept()
            return
        
        super().mousePressEvent(event)
    
    def wheelEvent(self, event: pg.QtGui.QWheelEvent):
        if self.parent_plot.curr_cam_state != CameraState.DEFAULT:
            event.accept()
            return
        super().wheelEvent(event)

    def mouseMoveEvent(self, event: pg.QtGui.QMouseEvent):
        # disable panning with ctrl + left click
        if (event.buttons() & QtCore.Qt.MouseButton.LeftButton and
            event.modifiers() & QtCore.Qt.KeyboardModifier.ControlModifier):
            event.accept()
            return

        if (event.buttons() & QtCore.Qt.MouseButton.LeftButton and
            self.parent_plot.curr_cam_state != CameraState.DEFAULT):
            event.accept()
            return
        
        super().mouseMoveEvent(event)

class GLTextImage(gl.GLImageItem):

    def __init__(self, text, fontsize=13, origin=Origin.Center):
        font = QFontDatabase.systemFont(QFontDatabase.GeneralFont)
        font.setPointSize(fontsize)
        fontmetrics = QtGui.QFontMetrics(font)
        font_rect = fontmetrics.size(QtCore.Qt.TextFlag.TextExpandTabs,text)
        self.width = font_rect.width() #fontmetrics.width(text)
        self.height = font_rect.height() #fontmetrics.height()
        self.img = QtGui.QImage(QtCore.QSize(self.width, self.height), QtGui.QImage.Format_ARGB32)
        self.img.fill(QtGui.QColor(0, 0, 0, 0))
        painter = QtGui.QPainter()
        painter.begin(self.img)
        painter.setPen(QtGui.QColor(255, 255, 255))
        painter.setFont(font)
        painter.drawText(0, 0, self.width, self.height, QtCore.Qt.AlignLeft, text)
        self.origin_transform = QtGui.QTransform(1, 0, 0, 1, 0, 0) # TopLeft
        if origin == Origin.TopCenter:
            self.origin_transform = QtGui.QTransform(1, 0, 0, 1, self.width/2, 0)
        elif origin == Origin.TopRight:
            self.origin_transform = QtGui.QTransform(1, 0, 0, 1, self.width, 0)
        elif origin == Origin.CenterLeft:
            self.origin_transform = QtGui.QTransform(1, 0, 0, 1, 0, self.height/2)
        elif origin == Origin.Center:
            self.origin_transform = QtGui.QTransform(1, 0, 0, 1, self.width/2, self.height/2)
        elif origin == Origin.CenterRight:
            self.origin_transform = QtGui.QTransform(1, 0, 0, 1, self.width, self.height/2)
        elif origin == Origin.BottomLeft:
            self.origin_transform = QtGui.QTransform(1, 0, 0, 1, 0, self.height)
        elif origin == Origin.BottomCenter:
            self.origin_transform = QtGui.QTransform(1, 0, 0, 1, self.width/2, self.height)
        elif origin == Origin.BottomRight:
            self.origin_transform = QtGui.QTransform(1, 0, 0, 1, self.width, self.height)
            
        painter.setTransform(self.origin_transform)
        painter.end()
        arr = qimage2ndarray.byte_view(self.img)
        gl.GLImageItem.__init__(self, arr, smooth=True)
        
    
    def get_scale(self, t):
        sx = QtGui.QVector3D(t[0][0],t[1][0],t[2][0]).length()
        sy = QtGui.QVector3D(t[0][1],t[1][1],t[2][1]).length()
        sz = QtGui.QVector3D(t[0][2],t[1][2],t[2][2]).length()
        return QtGui.QVector3D(sx, sy, sz)
    
    def get_rotation(self, t):
        scale = self.get_scale(t)
        sx, sy, sz = scale.x(), scale.y(), scale.z()
        rot = pg.Transform3D( t[0][0]/sx, t[0][1]/sy, t[0][2]/sz, 0, 
                              t[1][0]/sx, t[1][1]/sy, t[1][2]/sz, 0, 
                              t[2][0]/sx, t[2][1]/sy, t[2][2]/sz, 0, 
                              0, 0, 0, 1)
        return rot

    def get_position(self, t):
        return QtGui.QVector3D(t[0][3], t[1][3], t[2][3])

    def get_position_of_origin_in_world_coordinates(self):
        self.prev_transform = self.transform()
        t = self.prev_transform.matrix()
        scale = self.get_scale(t)
        scaled_origin_x = self.origin_transform.dy() * scale.x()
        scaled_origin_y = self.origin_transform.dx() * scale.y()

        original_origin_vec = QtGui.QVector3D(scaled_origin_x, scaled_origin_y, 0) # origin relative to top left corner of QImage in its original rotation
        curr_rotation = self.get_rotation(t)
        curr_origin_vec = curr_rotation.mapVector(original_origin_vec)
        curr_pos = self.get_position(t)

        origin_pos = curr_pos + curr_origin_vec
        return origin_pos

    def translateToCenter(self):
        pos_translation = self.get_position_of_origin_in_world_coordinates() * -1
        self.translate(pos_translation.x(), pos_translation.y(), pos_translation.z(), False)
        self.center_transform = self.transform()

    def translateToPrevPos(self, from_position):
        t = self.prev_transform.matrix()
        t2 = from_position.matrix()
        a = self.get_position(t)-self.get_position(t2)
        self.translate(a.x(), a.y(), a.z(), False)

    def translateFromCenterToPrevPos(self):
        self.translateToPrevPos(self.center_transform)
    
    def rotateAroundOrigin(self, angle, x, y, z):
        self.translateToCenter()
        self.rotate(angle,x,y,z,local=False)
        self.translateFromCenterToPrevPos()

    def removeRotation(self):
        t = self.transform().matrix()
        curr_origin_pos = self.get_position_of_origin_in_world_coordinates()
        scale = self.get_scale(t)
        tr = pg.Transform3D()
        tr.scale(scale.x(), scale.y(), scale.z())
        self.setTransform(tr)
        self.translate(curr_origin_pos.x() + self.origin_transform.dy() * -scale.x(), curr_origin_pos.y() + self.origin_transform.dx() * -scale.y(), curr_origin_pos.z())

    def removeRotationAndTranslation(self):
        self.removeRotation()
        self.translateToCenter()

    def lookAtCamera(self, camera_params, local = False):
        # self.translateToCenter()
        cameraTransform = QtGui.QMatrix4x4()
        cameraTransform.rotate(180+camera_params['elevation'],0,1,0)
        cameraTransform.rotate(180-camera_params['azimuth']-90,1,0,0)
        # cameraTransform.rotate(camera_params['elevation'],1,0,0)
        # cameraTransform.rotate(camera_params['azimuth'],0,0,1)

        eye_position = cameraTransform.mapVector(QtGui.QVector3D(camera_params['distance'],0,0))
        # center_pos = camera_params['center']
        center_pos = QtGui.QVector3D(0,0,0)

        up_dir = cameraTransform.mapVector(QtGui.QVector3D(0,0,-1))
        self.lookAt(eye_position, center_pos, up_dir, local=False)
        # print("eye: ",eye_position)

    def lookAt(self, eye_position, center_pos, up_dir, local=False):
        """
        Multiplies this matrix by a viewing matrix derived from an eye point. 
        The center value indicates the center of the view that the eye is looking at. 
        The up value indicates which direction should be considered up with respect to the eye.

        Note: The up vector must not be parallel to the line of sight from eye to center.
        """
        self.removeRotation()
        tr = pg.Transform3D(np.asarray(self.transform().copyDataTo()).reshape(4,4))
        tr.lookAt(eye_position, center_pos, up_dir)
        self.removeRotationAndTranslation()
        self.applyTransform(self.get_rotation(tr.matrix()), False)
        self.translateFromCenterToPrevPos()

    def __del__(self):
        if hasattr(self, 'texture'):
            if self.texture is not None:
                glDeleteTextures(int(self.texture))
                del self.texture


class ClippedGLSurfacePlotItem(gl.GLSurfacePlotItem):
    """GLSurfacePlotItem with axis-aligned XY clipping rectangle in item-local coords."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._clip_rect = None  # (xmin, xmax, ymin, ymax) in item-local coords

    def set_clip_rect(self, xmin, xmax, ymin, ymax):
        self._clip_rect = (float(xmin), float(xmax), float(ymin), float(ymax))
        self.update()

    def clear_clip(self):
        self._clip_rect = None
        self.update()

    def paint(self):
        if self._clip_rect is None:
            return super().paint()

        from OpenGL.GL import (
            glClipPlane, glEnable, glDisable,
            GL_CLIP_PLANE0, GL_CLIP_PLANE1, GL_CLIP_PLANE2, GL_CLIP_PLANE3
        )
        xmin, xmax, ymin, ymax = self._clip_rect

        # Keep points where all plane equations >= 0
        planes = [
            (GL_CLIP_PLANE0, (+1.0, 0.0, 0.0, -xmin)),  # x - xmin >= 0
            (GL_CLIP_PLANE1, (-1.0, 0.0, 0.0, +xmax)),  # xmax - x >= 0
            (GL_CLIP_PLANE2, (0.0, +1.0, 0.0, -ymin)),  # y - ymin >= 0
            (GL_CLIP_PLANE3, (0.0, -1.0, 0.0, +ymax)),  # ymax - y >= 0
        ]

        try:
            for enum, (a,b,c,d) in planes:
                glClipPlane(enum, (a, b, c, d))
                glEnable(enum)
            super().paint()
        finally:
            for enum, _ in planes:
                glDisable(enum)

class CameraState(IntEnum):
    ORTHO_X = 0
    ORTHO_Y = 1
    ORTHO_Z = 2
    DEFAULT = 3

@dataclass
class CameraSetup:
    distance: float
    azimuth: float
    elevation: float
    fov: float

class Matrix3DPlot(object):
    def __init__(self, 
                 x_axis_config: AxisConfig,
                 y_axis_config: AxisConfig, 
                 z_axis_config: AxisConfig,
                 plot_label="",
                 camera_distance=35,
                 camera_azimuth=-45,
                 background_color="#024254",
                 axis_as_reference=False):
        
        self.initialized = False
        
        # Set default axis configurations if not provided
        if not axis_as_reference:
            self.x_axis = x_axis_config.clone()
            self.y_axis = y_axis_config.clone()
            self.z_axis = z_axis_config.clone()
        else:
            self.x_axis = x_axis_config
            self.y_axis = y_axis_config
            self.z_axis = z_axis_config

        self.camera_distance = camera_distance
        self.camera_azimuth = camera_azimuth
        
        self.local_view = NoArrowGLViewWidget()
        self.local_view.setBackgroundColor(background_color)
        
        # For screen-space text overlays
        self.text_overlays = []
        
        # Connect to resize events to reposition labels
        self.local_view.resizeEvent = self.on_resize_event

        self.local_view._pick_callback = self.click_plot_info_label
        self.local_view._press_callback = self.hotkey_callback
        self.local_view.parent_plot = self
        self._last_pick_label = None
        
        # Store label positioning info for dynamic repositioning
        self.label_positions = []

        self.data_view = None

        self.things_to_trans: list[GLGraphicsItem] = []

        self.wireframe_line: gl.GLLinePlotItem = None
        self.wireframe_data: np.ndarray = None
        self.wireframe_on = False
        self.inx_wire_rows = []
        self.inx_wire_cols = []

        self.surface_mark: SurfaceMark = SurfaceMark()

        self.current_data: np.ndarray = None
        
        if plot_label:
            self.add_screen_text_overlay(plot_label, position="bottom-left")
        
        self.xaxis_labels: list[GLTextImage] = []
        self.yaxis_labels: list[GLTextImage] = []
        self.zaxis_labels: list[GLTextImage] = []

        self.color_bar_glimg: gl.GLImageItem = None

        self.axes_labels_trans_dct: dict[GLTextImage, dict[CameraState, pg.Transform3D]] = {}
        self.colorbar_trans_dct: dict[CameraState, pg.Transform3D] = {}

        self.camera_setups: dict[CameraState, CameraSetup] = {
            CameraState.ORTHO_X: CameraSetup(distance=2900*5, azimuth=-90, elevation=0, fov=0.1),
            CameraState.ORTHO_Y: CameraSetup(distance=2900*5, azimuth=0, elevation=0, fov=0.1),
            CameraState.ORTHO_Z: CameraSetup(distance=4200*5, azimuth=0, elevation=90, fov=0.1),
            CameraState.DEFAULT: CameraSetup(distance=self.camera_distance, azimuth=self.camera_azimuth, elevation=28, fov=60),
        }

        self.curr_cam_state = CameraState.DEFAULT
    
    def hotkey_callback(self, event: pg.QtGui.QKeyEvent):
        if event.key() == QKeys.Key_W:
            self.place_surface_mark(self.surface_mark.xbin-1, self.surface_mark.ybin)
        if event.key() == QKeys.Key_A:
            self.place_surface_mark(self.surface_mark.xbin, self.surface_mark.ybin-1)
        if event.key() == QKeys.Key_S:
            self.place_surface_mark(self.surface_mark.xbin+1, self.surface_mark.ybin)
        if event.key() == QKeys.Key_D:
            self.place_surface_mark(self.surface_mark.xbin, self.surface_mark.ybin+1)
    
    def world2data(self, pos: np.ndarray):
        """3D point convert"""
        if self._xscale_world is None:
            raise Exception("No saved transform for world2data conversion.")
        return np.array([
            (pos[0] - self._xtrans_world) / self._xscale_world,
            (pos[1] - self._ytrans_world) / self._yscale_world,
            (pos[2] - self._ztrans_world) / self._zscale_world,
        ])

    def data2world(self, pos: np.ndarray):
        """3D point convert"""
        if self._xscale_world is None:
            raise Exception("No saved transform for data2world conversion.")
        return np.array([
            pos[0] * self._xscale_world + self._xtrans_world,
            pos[1] * self._yscale_world + self._ytrans_world,
            pos[2] * self._zscale_world + self._ztrans_world,
        ])

    def _qmat4_to_np(self, m: QtGui.QMatrix4x4) -> np.ndarray:
        """Convert QMatrix4x4 to numpy 4x4 (float64) honoring column-major storage."""
        return np.array(m.data(), dtype=float).reshape((4, 4), order='F')

    def get_ray(self, x_coord: int, y_coord: int) -> tuple[np.ndarray, np.ndarray]:
        """
        Return (origin, direction) in world space for a click at widget-local pixel (x_coord, y_coord).
        Adjusts for device pixel ratio (HiDPI) so logical mouse coords line up with the GL viewport.
        """
        # Fetch Qt device pixel ratio (Qt6: devicePixelRatioF)
        try:
            dpr = float(self.local_view.devicePixelRatioF())
        except AttributeError:
            dpr = float(self.local_view.devicePixelRatio())

        # Scale logical (DIP) coordinates to physical if DPR != 1
        phys_x = x_coord * dpr
        phys_y = y_coord * dpr

        x0, y0, width, height = self.local_view.getViewport()

        # Optional sanity: if (width, height) look already logical (close to widget size),
        # and DPR != 1, skip scaling. Heuristic safeguard:
        widget_w = self.local_view.width()
        widget_h = self.local_view.height()
        if dpr != 1.0 and abs(width - widget_w * dpr) > 2 and abs(width - widget_w) <= 2:
            # Viewport seems logical already; undo scaling
            phys_x = x_coord
            phys_y = y_coord

        nx = ((phys_x - x0) / width) * 2.0 - 1.0
        ny = 1.0 - ((phys_y - y0) / height) * 2.0  # flip Y

        proj = self._qmat4_to_np(self.local_view.projectionMatrix())
        view = self._qmat4_to_np(self.local_view.viewMatrix())

        inv_view = np.linalg.inv(view)
        inv_pv = np.linalg.inv(proj @ view)

        near_ndc = np.array([nx, ny, -1.0, 1.0])
        far_ndc  = np.array([nx, ny,  1.0, 1.0])

        near_world = inv_pv @ near_ndc
        far_world  = inv_pv @ far_ndc
        near_world /= near_world[3]
        far_world  /= far_world[3]

        cam_world = (inv_view @ np.array([0.0, 0.0, 0.0, 1.0]))[:3]
        direction = far_world[:3] - cam_world
        direction /= np.linalg.norm(direction)
        return cam_world, direction
    
    def click_plot_info_label(self, event: pg.QtGui.QMouseEvent):

        min_dist = 1.5
        
        pos = event.position() if hasattr(event, "position") else event.pos()
        xbin, ybin, zval, closest_dist = self.get_point_of_click_surface(int(pos.x()), int(pos.y()), min_dist=min_dist)

        if xbin is None or closest_dist > 4:
            self.remove_surface_mark()
            return
        
        self.place_surface_mark(int(xbin), int(ybin))
    
    def place_surface_mark(self, xbin: int, ybin: int):
        if self.current_data is None:
            return
        
        if xbin < 0 or xbin >= self.x_axis.num_bins or ybin < 0 or ybin >= self.y_axis.num_bins:
            return

        zval = self.current_data[xbin, ybin]

        if self.surface_mark.xbin == xbin and self.surface_mark.ybin == ybin and self.surface_mark.zval == zval:
            return
        
        self.surface_mark.xbin = xbin
        self.surface_mark.ybin = ybin
        self.surface_mark.zval = zval

        # generate line data in the same way as wireframe, but only one row and one column
        line_data = []
        for xi in range(self.x_axis.num_bins):
            line_data.append([float(xi), float(ybin), self.current_data[xi, ybin] + 0.1])
        line_data.append([np.nan, np.nan, np.nan])  # separator

        for yi in range(self.y_axis.num_bins):
            line_data.append([float(xbin), float(yi), self.current_data[xbin, yi] + 0.1])
        
        line_data = np.asarray(line_data, dtype=np.float32)

        if self.surface_mark.line is not None:
            self.surface_mark.line.setData(pos=line_data)
            self.surface_mark.line.show()
        else:
            self.surface_mark.line = gl.GLLinePlotItem(pos=line_data,
                                                       color=(0, 1, 0, 1),
                                                       width=2,
                                                       antialias=True,
                                                       mode='line_strip',
                                                       glOptions='opaque')

            self.local_view.addItem(self.surface_mark.line)
            self.things_to_trans.append(self.surface_mark.line)
        
        # label
        text = f"Range={self.x_axis.bin2val(xbin):.2f}m\nDoppler={self.y_axis.bin2val(ybin):.2f}Hz\nPower={zval:.2f}dB"
        if self.surface_mark.label is None:
            self.surface_mark.label = self.add_screen_text_overlay(text, position="bottom-right")
        else:
            self.surface_mark.label.setText(text)
            self.update_label_positions()
            self.surface_mark.label.show()
        
        self.scale_data_view()

    def remove_surface_mark(self):
        if self.surface_mark.line is None:
            return

        self.surface_mark.line.hide()
        self.surface_mark.label.hide()

    def get_point_of_click_surface(self, screen_x, screen_y, min_dist=1.0, prefer_frontmost=True):
        """
        Return (x_bin, y_bin, z_val, distance_to_ray).
        
        Selection logic:
        1. Compute perpendicular distance of every surface point to the pick ray.
        2. If prefer_frontmost is True:
            - Form a mask of points with perpendicular distance <= min_dist and t >= 0 (in front of camera).
            - If any, choose the one with smallest t (closest to camera along the ray).
        3. Fallback: if no masked points, choose globally closest perpendicular distance (original behavior).
        """
        if not self.initialized or self.current_data is None:
            return (None, None, None, np.inf)

        rayorg, raydir = self.get_ray(screen_x, screen_y)

        # Transform to data space
        rayorg = self.world2data(rayorg)
        scale_vec = np.array([1.0 / self._xscale_world,
                              1.0 / self._yscale_world,
                              1.0 / self._zscale_world])
        raydir = raydir * scale_vec
        raydir /= np.linalg.norm(raydir)

        xp = self.data_view._x  # (Nx,)
        yp = self.data_view._y  # (Ny,)
        zp = self.data_view._z  # (Nx,Ny)

        ox, oy, oz = rayorg
        dx, dy, dz = raydir

        vx = xp[:, None] - ox            # (Nx,1)
        vy = yp[None, :] - oy            # (1,Ny)
        vz = zp - oz                     # (Nx,Ny)

        t = vx * dx + vy * dy + vz * dz  # projection scalar (Nx,Ny)

        px = vx - t * dx
        py = vy - t * dy
        pz = vz - t * dz
        dist2 = px*px + py*py + pz*pz

        # Default: closest perpendicular distance
        imin_global = np.argmin(dist2)
        gx, gy = np.unravel_index(imin_global, dist2.shape)

        chosen_xi, chosen_yi = gx, gy

        if prefer_frontmost:
            thresh2 = min_dist * min_dist
            # Points within tube & in front (t >= 0)
            mask = (dist2 <= thresh2) & (t >= 0)
            if np.any(mask):
                # Among masked points choose smallest t (closest to camera)
                masked_t = t[mask]
                # Indices of masked points
                idxs = np.where(mask)
                imin_local = np.argmin(masked_t)
                chosen_xi = idxs[0][imin_local]
                chosen_yi = idxs[1][imin_local]

        d2 = dist2[chosen_xi, chosen_yi]
        return xp[chosen_xi], yp[chosen_yi], zp[chosen_xi, chosen_yi], float(np.sqrt(d2))

    def wireframe_change_state(self, checked: bool):
        if self.wireframe_line is None:
            return
        
        self.wireframe_on = checked
        
        if checked:
            self.update_wireframe()
            self.wireframe_line.show()
        else:
            self.wireframe_line.hide()

    def switch_cam_state(self, newstate: CameraState):

        if self.curr_cam_state == CameraState.DEFAULT and not self.current_data is None:
            self.camera_setups[CameraState.DEFAULT].azimuth = self.local_view.opts['azimuth']
            self.camera_setups[CameraState.DEFAULT].elevation = self.local_view.opts['elevation']
            self.camera_setups[CameraState.DEFAULT].distance = self.local_view.opts['distance']

        camsetup = self.camera_setups[newstate]
        self.local_view.setCameraPosition(
            azimuth=camsetup.azimuth, 
            elevation=camsetup.elevation, 
            distance=camsetup.distance)
        self.local_view.opts['fov'] = camsetup.fov
        self.curr_cam_state = newstate

        self.scale_data_view()

    def draw_wireframe(self):
        color = (0.6, 0.6, 0.6, 1)
        width = 1

        x_bins = self.x_axis.num_bins
        y_bins = self.y_axis.num_bins

        points = []
        self.inx_wire_rows = []
        self.inx_wire_cols = []

        for yi in range(y_bins):
            start_index = len(points)
            for xi in range(x_bins):
                points.append([float(xi), float(yi), 10.0])  # placeholder Z
            end_index = len(points)
            self.inx_wire_rows.append(np.arange(start_index, end_index, dtype=np.int32))
            points.append([np.nan, np.nan, np.nan])  # separator

        for xi in range(x_bins):
            start_index = len(points)
            for yi in range(y_bins):
                points.append([float(xi), float(yi), 10.0])  # placeholder Z
            end_index = len(points)
            self.inx_wire_cols.append(np.arange(start_index, end_index, dtype=np.int32))
            points.append([np.nan, np.nan, np.nan])  # separator

        self.wireframe_data = np.asarray(points, dtype=np.float32)

        self.wireframe_line = gl.GLLinePlotItem(pos=self.wireframe_data,
                                                color=color,
                                                width=width,
                                                antialias=True,
                                                mode='line_strip',
                                                glOptions='opaque')
        
        self.local_view.addItem(self.wireframe_line)
        self.wireframe_line.hide()

        self.things_to_trans.append(self.wireframe_line)
    
    def update_wireframe(self):
        if self.current_data is None or self.wireframe_line is None:
            return

        x_bins, y_bins = self.current_data.shape

        # Rows: direct copy
        for yi, idxs in enumerate(self.inx_wire_rows):
            if yi >= y_bins:
                break
            self.wireframe_data[idxs, 2] = self.current_data[:, yi] + 0.1

        # Columns: copy each column
        for xi, idxs in enumerate(self.inx_wire_cols):
            if xi >= x_bins:
                break
            self.wireframe_data[idxs, 2] = self.current_data[xi, :] + 0.1

        # Push updated positions
        self.wireframe_line.setData(pos=self.wireframe_data)
    
    def set_clip_rect_local(self, xmin, xmax, ymin, ymax):
        if self.data_view is not None:
            self.data_view.set_clip_rect(xmin, xmax, ymin, ymax)

    def add_screen_text_overlay(self, text, x=10, y=10, color="white", font_size=12, position="custom"):
        label = QLabel(text)
        label.setParent(self.local_view)
        label.setStyleSheet(f"""
            QLabel {{
                color: {color};
                font-size: {font_size}pt;
                font-weight: bold;
                background-color: rgba(0, 0, 0, 100);
                padding: 5px;
                border-radius: 3px;
            }}
        """)
        
        # Store positioning info for dynamic updates
        label_info = {
            'label': label,
            'position': position,
            'custom_x': x,
            'custom_y': y,
            'margin': 4
        }
        
        # Position the label
        self.position_label(label_info)
        
        label.show()
        self.text_overlays.append(label)
        self.label_positions.append(label_info)
        return label

    def position_label(self, label_info):
        """Position a label based on its stored positioning info."""
        label: QLabel = label_info['label']
        position = label_info['position']
        
        # Get current widget dimensions
        widget_width = max(self.local_view.width(), 100)  # Minimum width to prevent issues
        widget_height = max(self.local_view.height(), 100)  # Minimum height to prevent issues
        
        if position == "custom":
            x, y = label_info['custom_x'], label_info['custom_y']
        else:
            # Ensure label is sized properly
            label.adjustSize()
            label_width = label.width()
            label_height = label.height()
            
            margin = label_info['margin']
            
            if position == "top-left":
                x, y = margin, margin
            elif position == "top-right":
                x, y = widget_width - label_width - margin, margin
            elif position == "bottom-left":
                x, y = margin, widget_height - label_height - margin
            elif position == "bottom-right":
                x, y = widget_width - label_width - margin, widget_height - label_height - margin
            else:
                x, y = margin, margin  # Default to top-left
        
        # Ensure label stays within widget bounds
        x = max(0, min(x, widget_width - label.width()))
        y = max(0, min(y, widget_height - label.height()))
        
        label.move(x, y)

    def on_resize_event(self, event):
        if hasattr(gl.GLViewWidget, 'resizeEvent'):
            super(gl.GLViewWidget, self.local_view).resizeEvent(event)
        
        # Reposition all labels
        for label_info in self.label_positions:
            self.position_label(label_info)

    def get_widget_dimensions(self):
        return (self.local_view.width(), self.local_view.height())

    def update_label_positions(self):
        for label_info in self.label_positions:
            self.position_label(label_info)

    def initialize_plot(self, x_data_bins=None, y_data_bins=None):
        """
        Initialize the 3D plot with grids, labels, and colorbar.
        
        Args:
            x_data_bins: Number of bins for X axis data (defaults to axis config)
            y_data_bins: Number of bins for Y axis data (defaults to axis config)
        """
        if self.initialized:
            return
            
        # Use provided bins or fall back to axis configuration
        x_bins = x_data_bins or self.x_axis.num_bins
        y_bins = y_data_bins or self.y_axis.num_bins
        
        # Set camera position
        self.switch_cam_state(CameraState.DEFAULT)
        
        # Add grid lines
        self._add_grids()
        
        # Add colorbar
        self._add_colorbar()
        
        # Add axis labels
        self._add_axis_labels()
        
        # Create surface plot item
        x = np.arange(x_bins)
        y = np.arange(y_bins)
        
        self.data_view = ClippedGLSurfacePlotItem(
            x=x,
            y=y,
            smooth=True,
            computeNormals=False
        )

        self.data_view.setGLOptions('opaque')

        self.things_to_trans.append(self.data_view)

        self.local_view.addItem(self.data_view)

        self.draw_wireframe()
        
        # Scale and position the surface
        self.scale_data_view()
        
        self.initialized = True

    def _add_grids(self):
        view = self.local_view
        
        # Y grid (horizontal)
        y_grid = gl.GLGridItem()
        y_grid.setSpacing(x=1, y=2, z=1)
        y_grid.scale(1, 0.5, 1)
        y_grid.rotate(90, 1, 0, 0)
        y_grid.translate(0, 10, 0)
        view.addItem(y_grid)
        
        # Z grid (vertical)
        z_grid = gl.GLGridItem()
        z_grid.setSpacing(x=2, y=1, z=1)
        z_grid.scale(0.5, 1, 1)
        z_grid.rotate(90, 0, 1, 0)
        z_grid.translate(-10, 0, 0)
        view.addItem(z_grid)

    def _add_colorbar(self):
        view = self.local_view
        
        # Create colorbar
        c = (colorize(np.array([np.arange(0, 100)])) * 255).astype(np.ubyte)
        c = np.concatenate([c, [[[255]]*100]], axis=2)
        rgba = np.repeat(c, 10, axis=0)
        self.color_bar_glimg = gl.GLImageItem(data=rgba)
        self.color_bar_glimg.scale(0.1, 0.1, 1)
        self.color_bar_glimg.rotate(90, 1, 0, 0)
        # self.color_bar_glimg.rotate(90, 0, 0, 1)
        self.color_bar_glimg.translate(10, 10, -5)
        view.addItem(self.color_bar_glimg)
        self.colorbar_trans_dct[self.curr_cam_state] = self.color_bar_glimg.transform()


    def fix_colorbar_labels_camera_state(self):
        return  # Disabled for now, implement later
        for label in self.zaxis_labels:
            if self.curr_cam_state in self.axes_labels_trans_dct[label]:
                label.setTransform(self.axes_labels_trans_dct[label][self.curr_cam_state])

        if self.curr_cam_state in self.colorbar_trans_dct:
            self.color_bar_glimg.setTransform(self.colorbar_trans_dct[self.curr_cam_state])

    def _add_colorbar_labels(self):
        view = self.local_view

        colorbar_width = 10
        
        # Z axis labels on colorbar
        z_mid = GLTextImage(f'{(self.z_axis.curr_max_val + self.z_axis.curr_min_val)/2:.1f} {self.z_axis.unit}')
        z_mid.scale(0.05, 0.05, 0.05)
        z_mid.rotate(90, 0, 1, 0)
        z_mid.rotate(-90, 0, 0, 1)
        z_mid.translateToCenter()
        z_mid.translate(10, 10, 0)
        z_mid.translate(0, colorbar_width + (z_mid.width/2)*1.3, 0, local=True)
        view.addItem(z_mid)
        self.zaxis_labels.append(z_mid)
        self.axes_labels_trans_dct[z_mid] = {}
        self.axes_labels_trans_dct[z_mid][CameraState.DEFAULT] = z_mid.transform()

        z_min_label = GLTextImage(f'{self.z_axis.curr_min_val:.1f} {self.z_axis.unit}')
        z_min_label.scale(0.05, 0.05, 0.05)
        z_min_label.rotate(90, 0, 1, 0)
        z_min_label.rotate(-90, 0, 0, 1)
        z_min_label.translateToCenter()
        z_min_label.translate(10, 10, -5)
        z_min_label.translate(-z_min_label.height/2, colorbar_width + (z_min_label.width/2)*1.3, 0, local=True)
        view.addItem(z_min_label)
        self.zaxis_labels.append(z_min_label)
        self.axes_labels_trans_dct[z_min_label] = {}
        self.axes_labels_trans_dct[z_min_label][CameraState.DEFAULT] = z_min_label.transform()

        z_max_label = GLTextImage(f'{self.z_axis.curr_max_val:.1f} {self.z_axis.unit}')
        z_max_label.scale(0.05, 0.05, 0.05)
        z_max_label.rotate(90, 0, 1, 0)
        z_max_label.rotate(-90, 0, 0, 1)
        z_max_label.translateToCenter()
        z_max_label.translate(10, 10, 5)
        z_max_label.translate(z_max_label.height/2, colorbar_width + (z_max_label.width/2)*1.3, 0, local=True)
        view.addItem(z_max_label)
        self.zaxis_labels.append(z_max_label)
        self.axes_labels_trans_dct[z_max_label] = {}
        self.axes_labels_trans_dct[z_max_label][CameraState.DEFAULT] = z_max_label.transform()

    def _add_axis_labels(self):
        """Add axis labels to the plot."""
        view = self.local_view
        
        # X axis labels
        x_min_label = GLTextImage(f'{self.x_axis.curr_min_val:.1f} {self.x_axis.unit}')
        x_min_label.scale(0.05, 0.05, 0.05)
        x_min_label.rotate(90, 0, 1, 0)
        x_min_label.rotate(-90, 0, 0, 1)
        x_min_label.translate(-10, 10, 5)
        x_min_label.translate(-x_min_label.height, 0, 0, local=True)
        view.addItem(x_min_label)
        self.xaxis_labels.append(x_min_label)
        self.axes_labels_trans_dct[x_min_label] = {}
        self.axes_labels_trans_dct[x_min_label][CameraState.DEFAULT] = x_min_label.transform()

        x_max_label = GLTextImage(f'{self.x_axis.curr_max_val:.1f} {self.x_axis.unit}')
        x_max_label.scale(0.05, 0.05, 0.05)
        x_max_label.rotate(90, 0, 1, 0)
        x_max_label.rotate(-90, 0, 0, 1)
        x_max_label.translate(10, 10, 5)
        x_max_label.translate(-x_max_label.height, -x_max_label.width, 0, local=True)
        view.addItem(x_max_label)
        self.xaxis_labels.append(x_max_label)
        self.axes_labels_trans_dct[x_max_label] = {}
        self.axes_labels_trans_dct[x_max_label][CameraState.DEFAULT] = x_max_label.transform()

        x_mid_label = GLTextImage(f'{(self.x_axis.curr_min_val + self.x_axis.curr_max_val)/2:.1f} {self.x_axis.unit}')
        x_mid_label.scale(0.05, 0.05, 0.05)
        x_mid_label.rotate(90, 0, 1, 0)
        x_mid_label.rotate(-90, 0, 0, 1)
        x_mid_label.translate(0, 10, 5)
        x_mid_label.translate(-x_mid_label.height, -x_mid_label.width//2, 0, local=True)
        view.addItem(x_mid_label)
        self.xaxis_labels.append(x_mid_label)
        self.axes_labels_trans_dct[x_mid_label] = {}
        self.axes_labels_trans_dct[x_mid_label][CameraState.DEFAULT] = x_mid_label.transform()

        # Y axis labels
        y_min_label = GLTextImage(f'{self.y_axis.curr_min_val:.1f} {self.y_axis.unit}')
        y_min_label.scale(0.05, 0.05, 0.05)
        y_min_label.rotate(90, 0, 1, 0)
        y_min_label.translate(-10, -10, 5)
        y_min_label.translate(-y_min_label.height, 0, 0, local=True)
        view.addItem(y_min_label)
        self.yaxis_labels.append(y_min_label)
        self.axes_labels_trans_dct[y_min_label] = {}
        self.axes_labels_trans_dct[y_min_label][CameraState.DEFAULT] = y_min_label.transform()

        y_max_label = GLTextImage(f'{self.y_axis.curr_max_val:.1f} {self.y_axis.unit}')
        y_max_label.scale(0.05, 0.05, 0.05)
        y_max_label.rotate(90, 0, 1, 0)
        y_max_label.translate(-10, 10, 5)
        y_max_label.translate(-y_max_label.height, -y_max_label.width, 0, local=True)
        view.addItem(y_max_label)
        self.yaxis_labels.append(y_max_label)
        self.axes_labels_trans_dct[y_max_label] = {}
        self.axes_labels_trans_dct[y_max_label][CameraState.DEFAULT] = y_max_label.transform()

        y_center_label = GLTextImage(f'{(self.y_axis.curr_min_val + self.y_axis.curr_max_val)/2:.1f} {self.y_axis.unit}')
        y_center_label.scale(0.05, 0.05, 0.05)
        y_center_label.rotate(90, 0, 1, 0)
        y_center_label.translate(-10, 0, 5)
        y_center_label.translate(-y_center_label.height, -y_center_label.width//2, 0, local=True)
        view.addItem(y_center_label)
        self.yaxis_labels.append(y_center_label)
        self.axes_labels_trans_dct[y_center_label] = {}
        self.axes_labels_trans_dct[y_center_label][CameraState.DEFAULT] = y_center_label.transform()

        self._add_colorbar_labels()

    def _remove_axis_labels(self):
        for xlabel in self.xaxis_labels:
            self.local_view.removeItem(xlabel)
        
        for ylabel in self.yaxis_labels:
            self.local_view.removeItem(ylabel)
        
        for zlabel in self.zaxis_labels:
            self.local_view.removeItem(zlabel)
        
        self.xaxis_labels.clear()
        self.yaxis_labels.clear()
        self.zaxis_labels.clear()

    def scale_data_view(self):
        if not len(self.things_to_trans):
            return
        
        for thing in self.things_to_trans:
            thing.resetTransform()
        
        toxbin = self.x_axis.val2bin(self.x_axis.curr_max_val)
        fromxbin = self.x_axis.val2bin(self.x_axis.curr_min_val)

        toybin = self.y_axis.val2bin(self.y_axis.curr_max_val)
        fromybin = self.y_axis.val2bin(self.y_axis.curr_min_val)

        self.xscale = self.x_axis.num_bins / (toxbin - fromxbin)

        self.yscale = self.y_axis.num_bins / (toybin - fromybin)

        self.set_clip_rect_local(fromxbin, toxbin, fromybin, toybin)

        xscale = 20.0/self.x_axis.num_bins * self.xscale
        yscale = 20.0/self.y_axis.num_bins * self.yscale
        zscale = 10.0/(self.z_axis.curr_max_val - self.z_axis.curr_min_val)

        xtrans = -(20.0/self.x_axis.num_bins * self.xscale) * fromxbin - 10.0
        ytrans = -(20.0/self.y_axis.num_bins * self.yscale) * fromybin - 10.0
        ztrans = -(10.0/(self.z_axis.curr_max_val - self.z_axis.curr_min_val)) * self.z_axis.curr_min_val - 5.0

        # store for inverse
        self._xscale_world = xscale
        self._yscale_world = yscale
        self._zscale_world = zscale
        self._xtrans_world = xtrans
        self._ytrans_world = ytrans
        self._ztrans_world = ztrans

        for thing in self.things_to_trans:
            thing.scale(xscale, yscale, zscale)
            thing.translate(xtrans, ytrans, ztrans)

        if self.surface_mark.label is None:
            return
        
        if not self.surface_mark.label.isHidden() and self.curr_cam_state == CameraState.ORTHO_Z:
            self.surface_mark.line.translate(0,0, 100)

    def change_ylims(self, ymin, ymax):
        self.y_axis.curr_min_val = ymin
        self.y_axis.curr_max_val = ymax

        self._remove_axis_labels()
        self._add_axis_labels()
        self.scale_data_view()
    
    def change_xlims(self, xmin, xmax):
        self.x_axis.curr_min_val = xmin
        self.x_axis.curr_max_val = xmax

        self._remove_axis_labels()
        self._add_axis_labels()
        self.scale_data_view()
    
    def change_zlims(self, zmin, zmax):
        self.z_axis.curr_min_val = zmin
        self.z_axis.curr_max_val = zmax

        self._remove_axis_labels()
        self._add_axis_labels()
        self.scale_data_view()

        self.update_data(self.data_view._z if self.data_view is not None else np.zeros((self.y_axis.num_bins, self.x_axis.num_bins)))

    def update_data(self, z_data: np.ndarray):
        """
        Update the surface plot with new data.
        
        Args:
            z_data: 2D numpy array of Z values
        """
        if not self.initialized:
            self.initialize_plot()

        self.current_data = np.maximum(z_data, self.z_axis.curr_min_val)

        if self.wireframe_on:
            self.update_wireframe()
        
        self.data_view.setData(z=self.current_data, 
                               colors=colorize(self.current_data, z_min=self.z_axis.curr_min_val, 
                                               z_max=self.z_axis.curr_max_val))
        
        if self.surface_mark.label is not None:
            if not self.surface_mark.label.isHidden():
                self.place_surface_mark(self.surface_mark.xbin, self.surface_mark.ybin)
