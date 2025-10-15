# X7 RangeDoppler Beamforming demo

This document describes the X7 RangeDoppler Beamforming demo and how to configure it.

## Description of the X7 RangeDoppler Beamforming demo

The X7 RangeDoppler Beamforming demo uses the Novelda X7 RadarDirect radar application for streaming complex baseband frames from the X7 chip. In this demo, the X7 is configured in alternating Tx, dual Rx mode. Digital beamforming is then applied on the incoming complex baseband frames from all 4 raw channels for a configurable number of azimuth angles **N**.

The concept of digital beamforming is thoroughly described in radar/signal processing litterature, and allows the forming of focused beams by combining the raw radar channels with adjustments to the phase, amplitude and time depending on the desired steering angle.

After beamforming the **N** complex digital beamformed frames are fed into Range-Doppler processing for each individual beam, producing **N** Range-Doppler maps, one for each of the provided azimuth angles. You can select a single beam, e.g. `azBeamAngles = {0.0} # degrees` just to get the coherent combination of all the Tx/Rx channels, or you can set up as many beams as you like in the `{-90.0, 90.0}` field-of-view. You can also put the X7F202 module in a vertical orientation to accomplish elevation beamforming.

**NOTE** The X7F202 only has 2 antenna elements which sets boundaries of beamwidths and beamsteering vectors.

The demo provides options to configure the X7 radar chip, the beaforming angles, the Range-Doppler processing and the visualization, and allows both running live using a Novelda X7F202 radar module, or running playback on recorded data. For a description of the concept of Range-Doppler processing, please see the [Range-Doppler readme](../X7RangeDopplerRaw/X7RangeDopplerRaw_Readme.md#range-doppler-processing).

Some last words of inspiration; this demo should be regarded as a tool for evaluation, inspiration and development. It could be the starting point for making really high-end products whether it be respiration applications, multi-target positioning, or using the micro-Doppler preset for advanced target classification like drones, human/animal, fall detection or anything with specific movement pattern characteristics. Applying machine learning to this output should be the dream of a data scientist.

### Running the demo
To run the demo you first need to set up the necessary parameters in a preset file. You can find examples of them in the `Presets` folder. A convenient way to work is to make a copy of the preset you want to base your application on, then update it with the relevant local paths and custom parameter changes. The default preset used is Presets/[default_preset.json](./Presets/default_preset.json). When you have your desired preset, you can run:
```
python <path-to-runX7RangeDopplerBeamforming.py> <path-to-preset_file.json>
```

### Configuration

The available demo configuration parameters can be found in [default_preset.json](./Presets/default_preset.json). Some general formatting rules apply for specifying parameters in the setup file, which can be seen in the [X7RangeDopplerRaw_Readme/Configuration](../X7RangeDopplerRaw/X7RangeDopplerRaw_Readme.md#configuration).

Please refer to the sections below for the available parameters, and examples on how to set them.

#### GUI parameters

![X7RangeDopplerBeamforming example](./Images/X7RangeDoppBeamExample.png)

The GUI panel (highlighted in red) is used to provide information while running the demo and allows configuration of the visualization on the fly.

The user can adjust the axis limits by changing the min/max parameters, which is useful e.g. for inspecting specific parts of the Range-Doppler map. When editing axis limits, press `Enter` to apply changes.

The demo allows visualization of the beamformed Range-Doppler maps in different ways, depending on what is selected in the `Axes` drop-down menu. The available options are:
- `Range-Doppler` - Plots Range-Doppler maps for selected beamforming angles.
- `Range-Angle` - Plots Range-Angle maps for selected Doppler values.
- `Angle-Doppler` - Plots Angle-Doppler maps for selected range values.

Using the `Choose Plots` button opens a window to configure which angles/ranges/Doppler frequencies to visualize the different maps:

![Choose plots window example](./Images/AddPlotWindow.png)

`RangeSlicesToPlot` specifies the slices of the Range-Doppler matrix to plot if the chosen axes don't include range values.  
`DopplerSlicesToPlot` specifies the slices of the Range-Doppler matrix to plot if the chosen axes don't include Doppler values.  
`AngleSlicesToPlot` specifies the slices of the Range-Doppler matrix to plot if the chosen axes don't include angle values.  
`GridColsPerRow` defines the grid that holds the plots, how many plots in a single row.  

The examples below shows all the three different map types for a target sitting at `2.0 meters` range, `0.0 degrees` azimuth, and breathing at `~0.28 Hz = 16.8 respirations/minute`.

![RangeDoppler@0deg](./Images/RangeDoppler0deg.png)
![RangeAngle@0.28Hz](./Images/RangeAngle0.28Hz.png)
![AngleDoppler@2.0m](./Images/AngleDoppler2.0m.png)

In addition, there are some hotkeys for GUI control:

| Hotkey | Description |
| -------- | -------- |
| LeftArrow | Pause the plotting and step back to the previous Range-Doppler map. |
| RightArrow | Pause the plotting and step forward to the next Range-Doppler map. |
| SpaceBar | Toggle play/pause. |
| MouseWheel | Zoom view in/out. |
| LeftMouseButton (click + hold) | Rotate view. |
| X | Switch to an orthographic view of the X axis in orthographic mode (range/Doppler/azimuth, depending on setup). |
| Y | Switch to an orthographic view of the Y axis in orthographic mode (range/Doppler/azimuth, depending on setup). |
| Z | Switch to an orthographic top-down view in orthographic mode.
| R | Restore camera to default view. |
| RightMouseButton (click on RD map surface) | Place surface marker at specific Range-Doppler cell. |
| RightMouseButton (click outside RD map surface) | Remove surface marker. |
| WASD | Move the surface marker in the respective direction. |


#### High level demo parameters

The available high level demo parameters the same as those described in the [X7RangeDopplerRaw readme](../X7RangeDopplerRaw/X7RangeDopplerRaw_Readme.md#high-level-demo-parameters).

#### X7 radar parameters

The available X7 radar parameters are the same as those described in the [X7RangeDopplerRaw readme](../X7RangeDopplerRaw/X7RangeDopplerRaw_Readme.md#x7-radar-parameters).

#### Digital Beamforming parameters
| Parameter | Type  | Example | Description                                                                                                                |
| -------- |-------| -------- |----------------------------------------------------------------------------------------------------------------------------|
| azBeamAngles | float | `"{-45.0, -30.0, -15.0, 0.0, 15.0, 30.0, 45.0}"` | The azimuth angles for digital beamforming. The length of the vector gives the number of Range-Doppler maps. Note that azimuth in this context is relative to the sensor orientation and is defined as steering in the X/Y plane as indicated by the unit coordinate system visible on the X7F202 Shield silk screen. This means that orienting the sensor upright, the beemsteering will in fact be in elevation. |


#### Range-Doppler parameters

The available Range-Doppler parameters are the same as those described in the [X7RangeDopplerRaw readme](../X7RangeDopplerRaw/X7RangeDopplerRaw_Readme.md#range-doppler-parameters).


#### Other parameters

```
"MultiRDPlottingParameters" : 
{
    "MaxBufferedFrames" : "2000",
    "PowerLimVec" : "{-60.0, 20.0}",
    "RangeLimVec" : "{}",
    "DopplerLimVec" : "{}",
    "AngleLimVec" : "{-90.0, 90.0}",

    "RangeSlicesToPlot" : "{0.4, 1.5, 4.0}",
    "DopplerSlicesToPlot" : "{-30.0, 0.0, 30.0}",
    "AngleSlicesToPlot" : "{-30.0, 0.0, 30.0}",

    "GridColsPerRow" : "2"
}
```

The visualization buffers beamformed Range-Doppler maps in memory, allowing stepping backwards/forwards for closer evaluation. `MaxBufferedFrames` specifies the maximum number of frames (in this case beamformed Range-Doppler maps) to hold in memory. The actual value will be different in the backend. If this is set to a negative value, then `MaxBufferedFrames` will be 100k. Since the power data coming in is represented in 3 dimensions (angle, range, doppler) you can specify which axes to show in the dropdown box labeled `Axes`. The Z-axis will always show power and can't be changed. To pick the slices of the missing dimension, click the `Choose Plots` button. This will open a new window where you can change plotting parameters, with parameters described above. For specifying axis limits, the following parameters are available:

`PowerLimVec` specifies the initial Z-limits (in dB) in the visualization.  
`RangeLimVec` specifies the initial range limits (in meters).  
`DopplerLimVec` specifies the initial Doppler limits (in hertz).  
`AngleLimVec` specifies the initial angle limits (in deg).  

All of these can be changed interactively while running the demo. If any of these limit vectors are omitted then the default values will be used.

You can also save these plotting parameters to a JSON and load them later.
