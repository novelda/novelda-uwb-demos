"""
Time series plot widget for presence and confidence visualization.
Extracted from Presence2DPlotter_plotter.py for better modularity.
"""

import numpy as np
import pyqtgraph as pg
from typing import Optional


class TimeSeriesPlot:
    """
    A reusable time-series plot widget that can display multiple zones
    with scatter overlay and automatic data trimming.
    """
    
    class ZonePlotData:
        """Data container for a single zone's plot data."""
        def __init__(self, zone_idx: int) -> None:
            self.zone_idx = zone_idx
            self.ydata: list[float] = []
            self.plot_item: Optional[pg.PlotDataItem] = None
            self.timestamps: list[float] = []
            self.scatter_item: Optional[pg.ScatterPlotItem] = None

    def __init__(
        self,
        name: str,
        ylims: tuple[float, float],
        max_history: float,
        pixel_width: float,
        zone_colors: list,
        thresh_to_cut: int,
        target_plot: Optional[pg.PlotItem] = None,
        win_w: int = 800,
        win_h: int = 600,
        win_pos_x: int = 0,
        win_pos_y: int = 0,
        scatter_overlay: bool = True,
        scatter_only: bool = False
    ) -> None:
        """
        Initialize a time series plot.
        
        Args:
            name: Plot title
            ylims: Y-axis limits as (min, max)
            pixel_width: Width of plot lines in pixels
            zone_colors: List of colors for different zones
            target_plot: Existing PlotItem to use (if None, creates new window)
            win_w, win_h: Window dimensions (if creating new window)
            win_pos_x, win_pos_y: Window position (if creating new window)
            scatter_overlay: Whether to add scatter dots on top of line
            scatter_only: Whether to only show scatter (no line)
        """
        self.num_saved_frames = None
        self.name = name
        self.time_history = max_history # seconds
        self.pixel_width = pixel_width
        self.zone_colors = zone_colors
        self.scatter_overlay = scatter_overlay
        self.scatter_only = scatter_only
        self.confidence_values_lowpower = None
        self.confidence_values_performance = None

        self.current_marker_index: Optional[int] = None
        self.current_marker_zone: Optional[int] = None

        self.thresh_to_cut = thresh_to_cut

        # Create or use existing plot
        if target_plot is None:
            self.win = pg.GraphicsLayoutWidget(show=True, title=name)
            self.win.resize(win_w, win_h)
            self.win.move(win_pos_x, win_pos_y)
            self.win.setBackground('w')
            self.plot = self.win.addPlot(title=name)
        else:
            self.win = None
            self.plot = target_plot

        # Configure plot appearance
        self.plot.setMenuEnabled(False)
        self.plot.hideButtons()
        self.plot.setLabel("bottom", "Time (s)")
        self.plot.getAxis('bottom').enableAutoSIPrefix(False)
        self.plot.getAxis('bottom').setPen('w')
        self.plot.getAxis('bottom').setTextPen('w')
        self.plot.getAxis('left').enableAutoSIPrefix(False)
        self.plot.getAxis('left').setPen('w')
        self.plot.getAxis('left').setTextPen('w')
        self.plot.setLabel("left", "Value")
        self.plot.setRange(xRange=[-1, 1], yRange=ylims)

        # State tracking
        self.first_timestamp: Optional[float] = None
        self.last_timestamp: Optional[float] = None
        self.current_static_lines: list = []
        self.all_zones_data: list[TimeSeriesPlot.ZonePlotData] = []

        self.info_box: Optional[pg.QtWidgets.QGraphicsProxyWidget] = None
        self.info_label: Optional[pg.QtWidgets.QLabel] = None
        self.highlight_point: Optional[pg.ScatterPlotItem] = None
        self.plot.scene().sigMouseClicked.connect(self.on_plot_clicked)

        self.plot.getAxis("bottom").setStyle(stopAxisAtTick=(False, False))

    def _safe_set_zone_data(self, z: "TimeSeriesPlot.ZonePlotData", x, y) -> None:
        """
        Safely set plot and scatter data by removing non-finite values.
        If all points are NaN/inf or lists are empty, set empty arrays to avoid
        pyqtgraph All-NaN slice warnings in ScatterPlotItem.
        """
        if not x or not y:
            z.plot_item.setData([], [])
            if z.scatter_item is not None:
                z.scatter_item.setData([], [])
            return

        xn = np.asarray(x, dtype=float)
        yn = np.asarray(y, dtype=float)
        mask = np.isfinite(xn) & np.isfinite(yn)
        xn = xn[mask]
        yn = yn[mask]

        if xn.size == 0:
            z.plot_item.setData([], [])
            if z.scatter_item is not None:
                z.scatter_item.setData([], [])
        else:
            z.plot_item.setData(xn, yn)
            if z.scatter_item is not None:
                z.scatter_item.setData(xn, yn)

    def update_threshold_lines(self) -> None:
        """
        Update threshold lines based on confidence values.
        Clears existing threshold lines and redraws them.
        """
        # Remove existing threshold lines
        for line in self.current_static_lines:
            self.plot.removeItem(line)
        self.current_static_lines.clear()

        # Draw low power threshold (if available)
        if self.confidence_values_lowpower is not None and len(self.confidence_values_lowpower) >= 4:
            threshold_low = self.confidence_values_lowpower[2]
            threshold_high = self.confidence_values_lowpower[3]
            self.plot_static_line(
                threshold_low,
                "",
                (255, 150, 0, 200)  # Orange
            )
            self.plot_static_line(
                threshold_high,
                "",
                (255, 100, 0, 200)  # Darker orange
            )

        # Draw performance threshold (if available)
        if self.confidence_values_performance is not None and len(self.confidence_values_performance) >= 4:
            threshold_low = self.confidence_values_performance[2]
            threshold_high = self.confidence_values_performance[3]
            self.plot_static_line(
                threshold_low,
                "",
                (0, 150, 255, 200)  # Blue
            )
            self.plot_static_line(
                threshold_high,
                "",
                (0, 100, 255, 200)  # Darker blue
            )

    def init_new_plot_data(self, zone_idx: int) -> ZonePlotData:
        """Initialize plot data for a new zone."""
        new_zone_data = TimeSeriesPlot.ZonePlotData(zone_idx)
        
        # Get zone color
        if self.zone_colors:
            color = self.zone_colors[zone_idx % len(self.zone_colors)]
        else:
            color = (200, 200, 200, 255)  # fallback gray

        # Create the line plot item
        new_zone_data.plot_item = self.plot.plot(
            [], [],
            pen=pg.mkPen(color, width=self.pixel_width),
            connect="finite" # might not be neccesary
        )

        # Configure based on plot mode
        if self.scatter_only:
            # Hide the line and enable symbols on the same PlotDataItem
            new_zone_data.plot_item.setPen(None)
            new_zone_data.plot_item.setSymbol('o')
            new_zone_data.plot_item.setSymbolSize(max(4, self.pixel_width + 2))
            new_zone_data.plot_item.setSymbolBrush(pg.mkBrush(color))
            new_zone_data.scatter_item = None
            new_zone_data.plot_item.scatter.sigClicked.connect(
                lambda item, points: self.on_point_clicked(points, zone_idx)
            )
        elif self.scatter_overlay:
            # Create separate scatter overlay
            new_zone_data.scatter_item = pg.ScatterPlotItem(
                [], [], size=5, pen=None, brush=pg.mkBrush(color)
            )
            self.plot.addItem(new_zone_data.scatter_item)
            new_zone_data.scatter_item.sigClicked.connect(
                lambda item, points: self.on_point_clicked(points, zone_idx)
            )
        else:
            # Only line (no scatter)
            new_zone_data.scatter_item = None

        self.all_zones_data.append(new_zone_data)
        return new_zone_data

    def on_plot_clicked(self, event):
        """Handle clicks on the plot background (not on data points)."""
        # Check if click was on a data point (event is already handled)
        if event.isAccepted():
            return

        # Click was on background - deselect
        self.clear_selection()

    def clear_selection(self):
        """Clear the current point selection."""
        if self.highlight_point is not None:
            self.plot.removeItem(self.highlight_point)
            self.highlight_point = None

        if self.info_box is not None:
            self.info_box.setVisible(False)

    def on_point_clicked(self, points, zone_idx: int) -> None:
        """Handle click on a data point."""
        if len(points) == 0:
            return

        point = points[0]
        x, y = point.pos()

        # Find the index of this point in the zone's data
        z = self.all_zones_data[zone_idx]
        try:
            idx = z.timestamps.index(x)
            self.current_marker_index = idx
            self.current_marker_zone = zone_idx
        except ValueError:
            self.current_marker_index = None
            self.current_marker_zone = None

        # Calculate elapsed time
        elapsed = (x - self.first_timestamp) / 1000 if self.first_timestamp else 0

        # Remove previous highlight
        if self.highlight_point is not None:
            self.plot.removeItem(self.highlight_point)

        # Create highlight point
        self.highlight_point = pg.ScatterPlotItem(
            [x], [y], size=10,
            pen=pg.mkPen('w', width=2),
            brush=pg.mkBrush(50, 0, 13)
        )
        self.plot.addItem(self.highlight_point)

        # Show info box
        self.show_info_box(x, y, value=y, elapsed=elapsed)

    def move_marker(self, direction: int, max_timestamp: Optional[float]) -> None:
        """Move the selection marker left (-1) or right (+1)."""
        if self.current_marker_index is None or self.current_marker_zone is None:
            return

        z = self.all_zones_data[self.current_marker_zone]

        if not z.timestamps:
            return

        # Calculate new index
        new_idx = self.current_marker_index + direction

        # Keep searching until we find a non-NaN value or reach the boundary
        while 0 <= new_idx < len(z.timestamps):
            # In paused mode, don't search beyond the filtered data
            if max_timestamp is not None and z.timestamps[new_idx] > max_timestamp:
                return

            # Check if this value is valid (not NaN)
            if not np.isnan(z.ydata[new_idx]):
                break

            # Move to next position in the same direction
            new_idx += direction
        else:
            # Reached boundary without finding valid data
            return

        self.current_marker_index = new_idx

        # Get the new point's data
        x = z.timestamps[new_idx]
        y = z.ydata[new_idx]

        # Update highlight
        if self.highlight_point is not None:
            self.plot.removeItem(self.highlight_point)

        self.highlight_point = pg.ScatterPlotItem(
            [x], [y], size=10,
            pen=pg.mkPen('w', width=2),
            brush=pg.mkBrush(50, 0, 13)
        )
        self.plot.addItem(self.highlight_point)

        # Update info box
        elapsed = (x - self.first_timestamp) / 1000 if self.first_timestamp else 0
        self.show_info_box(x, y, value=y, elapsed=elapsed)

        return

    def show_info_box(self, x: float, y: float, value: float, elapsed: float) -> None:
        """Show an info box at the specified position."""
        from PySide6.QtWidgets import QLabel

        # Create or update the label
        if self.info_box is None:
            label = QLabel()
            label.setStyleSheet("""
                QLabel {
                    background-color: rgba(60, 77, 82, 0.9);
                    border: 1.2px solid rgba(230, 230, 230, 1);
                    border-radius: 5px;
                    padding: 4px;
                    color: white;
                    font-size: 9pt;
                }
            """)

            # Create proxy widget
            self.info_box = self.plot.scene().addWidget(label)
            self.info_label = label

        # Update text with HTML formatting
        text = f"""
        Value: {value:.2f}<br>
        Elapsed: {elapsed:.2f}s
        """
        self.info_label.setText(text)

        # Get the GraphicsView (the actual widget displaying the scene)
        view = self.plot.getViewBox().parentWidget()

        # Position in view coordinates (top-left corner with offset)
        view_pos = view.mapFromScene(self.plot.sceneBoundingRect().topLeft())
        self.info_box.setPos(view_pos.x() + 4, view_pos.y() + 4)

        self.info_box.setVisible(True)


    def add_data(self, zone_idx: int, data: float, timestamp: float) -> None:
        """
        Add a new data point for a specific zone.
        Does NOT update the display - call process_end() or browse_set_view() to update.
        """
        if self.first_timestamp is None:
            self.first_timestamp = timestamp
        self.last_timestamp = timestamp

        # Ensure zone exists
        while zone_idx >= len(self.all_zones_data):
            self.init_new_plot_data(len(self.all_zones_data))

        z = self.all_zones_data[zone_idx]

        # Append new sample with monotonic timestamp enforcement per zone
        ts = float(timestamp)
        if z.timestamps and ts < z.timestamps[-1]:
            # Guard against out-of-order appends (e.g., due to paused/browse race)
            ts = z.timestamps[-1] + 1e-3  # 0.001 ms bump to keep non-decreasing

        z.timestamps.append(ts)
        z.ydata.append(float(data))

    def browse_set_view(self, max_timestamp: Optional[float] = None) -> None:
        """Set the view range for browsing mode (when paused)."""
        # Find earliest timestamp across all zones
        earliest = None
        for z in self.all_zones_data:
            if z.timestamps:
                t0 = z.timestamps[0]
                earliest = t0 if earliest is None else min(earliest, t0)

        if earliest is None:
            return

        if self.first_timestamp is None:
            self.first_timestamp = earliest

        # Filter and update all zone plots
        for z in self.all_zones_data:
            if not z.timestamps:
                continue

            if max_timestamp is not None:
                # Find indices where timestamp <= max_timestamp
                # Always refilter from the complete dataset to ensure no gaps
                filtered_timestamps = []
                filtered_ydata = []
                for i, t in enumerate(z.timestamps):
                    if t <= max_timestamp:
                        filtered_timestamps.append(t)
                        filtered_ydata.append(z.ydata[i])

                # Update the plot with filtered data
                
                self._safe_set_zone_data(z, filtered_timestamps, filtered_ydata)
            else:
                # No filtering - show all accumulated data (live mode or unpause)
                self._safe_set_zone_data(z, z.timestamps, z.ydata)

        # Calculate view range
        left = max(earliest, max_timestamp - self.time_history)
        right = left + self.time_history*1.04

        self.plot.enableAutoRange('x', False)
        self.plot.setXRange(left, right, padding=0)

        elapsed_text = f"{(max_timestamp - self.first_timestamp) / 1000:.1f}"

        self.plot.getAxis("bottom").setTicks([[(max_timestamp, elapsed_text)]])


    def plot_static_line(self, y: float, label: str, color: tuple) -> None:
        """Add a horizontal static line (e.g., threshold)."""
        newline = pg.InfiniteLine(
            y, angle=0,
            pen=pg.mkPen(color, width=self.pixel_width),
            label=label
        )
        self.plot.addItem(newline)
        self.current_static_lines.append(newline)


    def cut_data_to_max_history(self, zone_idx: int) -> Optional[float]:
        z = self.all_zones_data[zone_idx]
        max_frames = int(self.num_saved_frames)
        if len(z.timestamps) > self.thresh_to_cut:
            z.timestamps = z.timestamps[-max_frames:]
            z.ydata = z.ydata[-max_frames:]
            # NaN-safe update
            self._safe_set_zone_data(z, z.timestamps, z.ydata)
        return z.timestamps[0] if z.timestamps else None

    def process_end(self) -> None:
        """
        Process end of data update - trim and update view for live mode.
        Call this after adding data in live mode.
        """
        if not self.all_zones_data or self.last_timestamp is None:
            return

        max_ts = 0
        have_any = False

        # Trim all zones and find the max timestamp
        for i in range(len(self.all_zones_data)):
            new_max_ts = self.cut_data_to_max_history(i)
            if new_max_ts is None:
                continue
            have_any = True
            if new_max_ts > max_ts:
                max_ts = new_max_ts

        if not have_any or max_ts is None:
            return

        # Update all zones with latest accumulated data
        for z in self.all_zones_data:
            if z.timestamps:
                self._safe_set_zone_data(z, z.timestamps, z.ydata)

        # Calculate view window
        left = max(self.last_timestamp-self.time_history, max_ts)
        right = left + self.time_history*1.04

        self.plot.enableAutoRange('x', False)
        self.plot.setXRange(left, right, padding=0)

        # Update time axis label
        self.plot.getAxis("bottom").setTicks(
            [[(self.last_timestamp, f"{(self.last_timestamp - self.first_timestamp) / 1000:.1f}")]]
        )


    def clear_all_data(self) -> None:
        """Clear all data from all zones."""
        for z in self.all_zones_data:
            z.timestamps.clear()
            z.ydata.clear()
            z.plot_item.setData([], [])
            if z.scatter_item is not None:
                z.scatter_item.setData([], [])
        
        self.first_timestamp = None
        self.last_timestamp = None

    def set_y_range(self, y_min: float, y_max: float, padding: float = 0.0) -> None:
        """Set the Y-axis range."""
        self.plot.enableAutoRange('y', False)
        self.plot.setYRange(y_min, y_max, padding=padding)
