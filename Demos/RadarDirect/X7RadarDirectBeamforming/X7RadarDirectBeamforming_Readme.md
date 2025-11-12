# X7 RadarDirect Beamforming demo

This document describes the X7 RadarDirect Beamforming demo and how to configure it.

## Description of the X7 RadarDirect Beamforming demo

The X7 RadarDirect Beamforming demo uses the Novelda X7 RadarDirect radar application for streaming complex baseband frames from the X7 chip. In this demo, the X7 is configured in alternating Tx, dual Rx mode. First, the baseband frames go through a static removal process, implemented as a single-pole IIR filter, on each of the 4 raw channels individually. Digital beamforming is then applied on the frames for a configurable number of azimuth angles **N**.

The concept of digital beamforming is thoroughly described in radar/signal processing litterature, and allows the forming of focused beams by combining the raw radar channels with adjustments to the phase, amplitude and time depending on the desired steering angle.

You can select a single beam, e.g. `azBeamAngles = {0.0} # degrees` just to get the coherent combination of all the Tx/Rx channels, or you can set up as many beams as you like in the `{-90.0, 90.0}` field-of-view. You can also put the X7F202 module in a vertical orientation to accomplish elevation beamforming.

**NOTE** The X7F202 only has 2 antenna elements with limited directivity, which sets boundaries of beamwidths and beamsteering vectors. Further details and a figure showing a selected set of beam responses in the azimuth direction is found in the [X7F202 azimuth beam responses](#x7f202-azimuth-beam-responses) section below.

The demo provides options to configure the X7 radar chip, the beaforming angles and the visualization, and allows both running live using a Novelda X7F202 radar module, or running playback on recorded data. The visualization gives insight to the range and angular resolutions of the module, and can serve as inspiration for applications either from the simplest ones with a single focused beam, to advanced tracking applications with multiple beams.

### Running the demo
To run the demo you first need to set up the necessary parameters in a preset file. You can find examples of them in the `Presets` folder. A convenient way to work is to make a copy of the preset you want to base your application on, then update it with the relevant local paths and custom parameter changes. The default preset used is Presets/[default_preset.json](./Presets/default_preset.json). When you have your desired preset, you can run:
```
python <path-to-runX7RadarDirectBeamforming.py> <path-to-preset_file.json>
```

### Configuration

The available demo configuration parameters can be found in [default_preset.json](./Presets/default_preset.json). Some general formatting rules apply for specifying parameters in the setup file, which can be seen in the [X7BasebandRaw_Readme/Configuration](../X7BasebandRaw/X7BasebandRaw_Readme.md#configuration).

Please refer to the sections below for the available parameters, and examples on how to set them.

#### GUI parameters

![X7RadarDirectBeamforming example](./Images/RadarDirectBeamformingExample.png)

The GUI panel on the bottom is used to provide information while running the demo and allows configuration of the visualization on the fly.

The user can adjust the axis limits by changing the min/max parameters, which is useful e.g. for inspecting specific parts of the range/angle plots. When editing axis limits, press `Enter` to apply changes.

The sector plot (top) visualizes the beams and their response in range/azimuth. By default, they are interpolated in both range and azimuth through linear interpolation which smoothes the responses in the visualization. This works best when the configured beams are fairly closely spaced. In the case that only a small set of sparsely spaced beams are configured, checking the `Show Beam Sectors` box will give a better visualization by plotting the response for each beam separately in a configurable width. In the sector plot, the dynamic of the color map can be adjusted by using the color map sliders on the right of the sector plot.

Using the `Angles to plot` and `Ranges to plot` buttons, windows will open for configuration of which angles and ranges to visualize:

![Choose plots window example](./Images/PlotsToShow.png)

Use the sliders to find the range/angle you want to plot, then press `Space` or `Add Plot`.

These can also be set as parameters in the preset file:

`RangeSlicesToPlot` specifies the range slices of the beamformed baseband frames to plot.
`AngleSlicesToPlot` specifies the angle slices of the beamformed baseband frames to plot.

In order to make the visualization a bit less cluttered, you can add a threshold by using the `Thresholds` button. This will open a window where you can customize a threshold to limit the sector plot to only visualize power above the thresholds. These parameters are further explained [below](#other-parameters).

![Thresholds window example](./Images/Thresholds.png)

In addition, there are some hotkeys for GUI control:

| Hotkey | Description |
| -------- | -------- |
| LeftArrow | Pause the plotting and step back to the previous plot. |
| RightArrow | Pause the plotting and step forward to the next plot. |
| SpaceBar | Toggle play/pause. |
| MouseWheel | Zoom view in/out. |
| LeftMouseButton (click + hold) | Move view. |
| R | Restore plots to default view. |
| RightMouseButton (click on range/angle plots) | Place surface marker at specific range/angle. |
| RightMouseButton (click outside plot) | Remove surface marker. |
| AD | Move the surface marker in the respective direction. |


#### High level demo parameters

The available high level demo parameters the same as those described in the [X7BasebandRaw readme](../X7BasebandRaw/X7BasebandRaw_Readme.md#high-level-demo-parameters).

#### X7 radar parameters

With the exception of `TxChannelSequence` and `RxMaskSequence` which are fixed for this demo, the available X7 radar parameters are the same as those described in the [X7BasebandRaw readme](../X7BasebandRaw/X7BasebandRaw_Readme.md#x7-radar-parameters).

#### Static removal parameters

| Parameter | Type  | Example | Description |
| -------- |-------| -------- | -------- |
| DCEstimationSmoothCoeff | float | `"0.8"` | Static removal IIR smoothing coefficient. Valid values are in the range of `{0.0, 1.0}`. For details on how to configure this coefficient, please refer to the [Configuring the IIR static removal coefficient](#configuring-the-iir-static-removal-coefficient) section below. |


#### Digital Beamforming parameters
| Parameter | Type  | Example | Description |
| -------- |-------| -------- |-----------------|
| azBeamAngles | float | `"{-45.0, -30.0, -15.0, 0.0, 15.0, 30.0, 45.0}"` | The azimuth angles for digital beamforming. The length of the vector gives the number of beams. Note that azimuth in this context is relative to the sensor orientation and is defined as steering in the X/Y plane as indicated by the unit coordinate system visible on the X7F202 Shield silk screen. This means that orienting the sensor upright, the beemsteering will in fact be in elevation. |

#### Other parameters

```
"RadarDirectBeamPlottingParameters" : 
{
    "MaxBufferedFrames" : "10000",
    "PowerLimVec" : "{-60.0, 40.0}",
    "RangeLimVec" : "{}",
    "AngleLimVec" : "{}",

    "ColorMapRange" : "{-60.0, 30.0}",
    "BeamSectorWidthDeg" : "20.0",

    "RangeSlicesToPlot" : "{2.0}",
    "AngleSlicesToPlot" : "{0.0}",

    "ThresholdAtRanges" : "{0.2, 2.0, 5.0}",
    "ThresholdValues" : "{10.0, 5.0, 5.0}"
}
```

The visualization buffers beamformed baseband frames in memory, allowing stepping backwards/forwards for closer evaluation. `MaxBufferedFrames` specifies the maximum number of frames to hold in memory. The actual value will be different in the backend. If this is set to a negative value, then `MaxBufferedFrames` will be 100k.

To pick the range/angle slices you want to plot, use the `Angles/Ranges to plot` buttons. This will open a new window where you can change plotting parameters, with parameters described above. For specifying axis limits, the following parameters are available:

`PowerLimVec` specifies the initial Z-limits (in dB) in the visualization.
`RangeLimVec` specifies the initial range limits (in meters).
`AngleLimVec` specifies the initial angle limits (in deg).

In addition you can add a custom threshold to limit the range/angle map visualization to only include values above the threshold. The threshold can be set by configuring the `ThresholdAtRanges` and `ThresholdValues` parameters. They need to be equal length, and the `ThresholdValues` specifies a threshold in `dB` for each range specified by `ThresholdAtRanges`. For the range values inbetween those specified, the thresholds are calculated through linear interpolation. For the values outside the range min/max, the thresholds are the same as those specified at min/max.

All of these parameters can be changed interactively while running the demo. If any of these limit vectors are omitted then the default values will be used.

## X7F202 azimuth beam responses

As briefly explained above, the X7F202 antenna module contains only two elements, each with a fairly low directivity. This means that the configured beams will be quite wide, and suffer from strong sidelobes as you steer the beams further out in the azimuth direction. Below is a figure showing the simulated beam responses for a set of azimuth beams as a function of azimuth angle.

![Azimuth beam responses](./Images/AzimuthBeamResponses.png)

From the figure, it's clear that the further out you steer, the stronger the sidelobe on the opposite side will be, which will limit the ability to separate and accurately position multiple targets in the scene. For single target applications, this is less of a problem, since the measured response can be compared to the expected responses and thus resolve the correct position.

## Configuring the IIR static removal coefficient

In order to detect moving targets in an environment cluttered with large static objects (walls, furniture, etc), it's convenient to filter out the still/slow moving reflections. There are a number of techniques to do this, and in this application this is done with a simple one-pole IIR smoothing filter.

The static reflections are estimated by the IIR filter at each range bin, and the resulting vector is then subtracted from each new incoming frame. The result should then only contain power from reflections which have movement outside of the IIR filter stop band.

The IIR filter is configured by a single parameter, the smoothing coefficient (or filter weight) `DCEstimationSmoothCoeff` which determines how much to weight the current state of the filter, against the new incoming frame. The value of the filter weight is limited to the range `{0.0, 1.0}`, where a low value gives a filter with a wider stop band (faster settling time), and a low value gives a more narrow stop band (slower settling time).

In the extremes, a filter weight of `0.0` collapses to a two-tap MTI filter, and a filter weight of `1.0` functions as a passthrough filter.

The figure below shows the filter transfer function magnitude spectrum for a few select filter weights. `FPS` is the number of frames per second as configured in the radar settings.

![IIR filter transfer functions](./Images/StaticRemoval_TransferFunctions.png)

The figure below shows the filter settling time as a function of filter weight. Like above, `FPS` is the number of frames per second as configured in the radar settings.

![IIR filter settling time](./Images/StaticRemoval_SettlingTime.png)

Below is a table of the settling time and filter bandwidths for a set of filter weights. To convert the settling time from num updates to seconds, simply divide with the configured `FPS`. To convert the bandwidth from normalized to absolute frequency, simply multiply by the configured `FPS`.

| Filter weight | Settling time<br>[num updates] | 3 dB bandwidth<br>[f/FPS]| 10 dB bandwidth<br>[f/FPS] |
|:--------:|:--------------------:|:------------------------:|:-------------------------:|
| 0.00 | 2 | 0.2505 | 0.1026 |
| 0.05 | 4 | 0.2346 | 0.0934 |
| 0.10 | 4 | 0.2188 | 0.0849 |
| 0.15 | 5 | 0.2031 | 0.0770 |
| 0.20 | 5 | 0.1877 | 0.0698 |
| 0.25 | 6 | 0.1725 | 0.0630 |
| 0.30 | 7 | 0.1577 | 0.0567 |
| 0.35 | 8 | 0.1433 | 0.0508 |
| 0.40 | 9 | 0.1293 | 0.0453 |
| 0.45 | 10 | 0.1158 | 0.0402 |
| 0.50 | 11 | 0.1028 | 0.0354 |
| 0.55 | 13 | 0.0903 | 0.0309 |
| 0.60 | 15 | 0.0783 | 0.0266 |
| 0.65 | 17 | 0.0668 | 0.0226 |
| 0.70 | 20 | 0.0559 | 0.0189 |
| 0.75 | 25 | 0.0454 | 0.0153 |
| 0.80 | 32 | 0.0355 | 0.0119 |
| 0.85 | 44 | 0.0260 | 0.0088 |
| 0.90 | 67 | 0.0169 | 0.0057 |
| 0.95 | 136 | 0.0083 | 0.0029 |
| 0.99 | 688 | 0.0018 | 0.0007 |
| 1.00 | Inf | N/A | N/A |
