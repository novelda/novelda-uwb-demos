# ULPP Presence2D demo

This document describes the X7 Ultra Low Power Presence (ULPP) Presence2D demo and how to configure it.

## Description of the X7 ULPP Presence2D demo

The X7 ULPP Presence2D demo uses the Novelda X7 ULPP_Presence2D radar application for streaming Presence2D and detection data from the X7 chip which is then visualized in the GUI. In this demo, the ULPP_Presence2D application runs on the Novelda X7 built-in MCU and only application output is sent to the host.

**NOTE** This demo uses the ULPP_Presence2D radar application, so make sure that the `BA22FirmwarePath` parameter points to the ULPP_Presence2D FW as opposed to the Presence2DOnHost demo which uses the RadarDirect FW.

In the case that you want to record raw baseband data, and process back the recording through the Presence2D application while tuning application parameters, please use the [Presence2DOnHost](../Presence2DOnHost/Presence2DOnHost_Readme.md) demo to first do a recording, and then do a playback of the recording. The application parameters you find can then be deployed in this demo for prototype product testing.

**NOTE** The X7 radar parameters (FPS, chip integration, etc) are currently not configurable in this demo, but we are planning to add more configurability in upcoming versions of the SDK.

The HumanPresence2D output is a vector with dimension (1 x 4) where the content is:

``` HumanPresence2D = [PresenceState, X-coord, Y-coord, Confidence] ```

The data is formatted as 16-bit signed integers where:

* PresenceState = 0/1 indicating NoPresence or Presence
* X-coord: X coordinate of detection in centimeters
* Y-coord: Y coordinate of detection in centimeters
* Confidence: Measure of certainty of Presence from 0-100 where 100 is the strongest indication of certainty.

In addition, the demo extracts the power vector which is the basis for detection and calculates the position (range/angle) of the closest detection and the associated signal-to-noise ratio (SNR).

**NOTE** The HumanDetection2D detection list data is currently not supported in the output.

### Running the demo

To run the demo you first need to set up the necessary parameters in a preset file. You can find examples of them in the `Presets` folder. A convenient way to work is to make a copy of the preset you want to base your application on, then update it with the relevant local paths and custom parameter changes. When you have your desired preset, you can run:

```
python <path-to-runX7ULPP_Presence2DPlot.py> <path-to-preset_file.json>
```

### Configuration

The available demo configuration parameters can be found in the `Presets` folder. Some general formatting rules apply for specifying parameters in the setup file:
- All application parameters (`public`) must be written as strings, i.e. encapsulated by `""`.
- Parameters have assigned types, and the provided default settings indicate the type through formatting of the parameter strings. 
A type mismatch will cause the parameters to not take effect.
- Floating point values are written with a dot, e.g. `"ThresholdLevelAdjustment_Linear" : "1.0"`
- Signed 32-bit integers are written without any postfix, e.g. `"ConfidenceValues" : "{30, 80, 75, 25}"`
- File path strings must be separated with `\\` or `/` and not a single `\`.
- Parameter names (keys) should not be changed from the provided defaults as they will cease to take effect.

Please refer to the sections below for the available parameters, and examples on how to set them.

#### GUI parameters

![Presence2D example](./Images/ULPP_Presence2D_example.png)

The GUI panel (highlighted in red) is used to provide information while running the demo and allows configuration of the visualization on the fly.

The user can adjust the axis limits by changing the min/max parameters. When editing axis limits, press `Enter` to apply changes.

In addition, there are some hotkeys for GUI control:

| Hotkey | Description |
| -------- | -------- |
| LeftArrow | Pause the plotting and step back to the previous plot. |
| RightArrow | Pause the plotting and step forward to the next plot. |
| SpaceBar | Toggle play/pause. |
| MouseWheel | Zoom view in/out. |
| LeftMouseButton (click + hold) | Move plot |
| LeftMouseButton (click) | Place a marker on a plotted line |
| A | Move marker to the left by one range bin |
| D | Move marker to the right by one range bin |

#### High level demo parameters

Below is an example of the available high level demo parameters, and examples on how to set them.

| Parameter | Description |
| -------- |------------------|
| IsLive | `true`/`false` - Controls whether to run live with an X7F202 radar module connected, or playback of already recorded data. |
| BA22FirmwarePath | `"<path-to-sdk>/firmware/X7_Application_BA22_*_ULPP_Presence2D_*.app"` - This path must point to the ULPP_Presence2D application binary provided in the Novelda X7 SDK. |
| PlaybackFile | `"<path-to-RecordingDirectory>/rec_pres2d_*.sig"` - Necessary when `IsLive = false` and should point to the recorded data file. When recording, a preset file with this already filled out is automatically generated alongside the recording. Note that the Presence2D demo only supports playback of ULPP_Presence2D FW recordings and not baseband data from the RadarDirect FW. For that, refer to the Presence2DOnHost demo. |
| RecordingDirectory | `"<path-to-RecordingDirectory>"` - Folder to save recorded data files |
| RecordingPrefix | E.g. `"rec_pres2d_"` - Prefix for the recorded data file. Will be appended by timestamp for when recording started. |

#### ULPP Presence2D public parameters

The table below shows the available ULPP Presence2D application public parameters, their type and an example on how to set them in the configuration file. This section also briefly describes the parameters.

**NOTE** When doing playback of recorded Presence2D application output, changing these parameters will not have an effect other than changing the visualized detection zone and thresholds. If you want to do playback of recorded data and tune application parameters, use the [Presence2DOnHost](../Presence2DOnHost/Presence2DOnHost_Readme.md) demo.

| Parameter | Type   | Example |
| -------- | -------- |-------- |
| DetectionZoneXYPoints | float | `"{0.0, 0.5}, {1.0, 0.5}, {1.0, -0.5}, {0.0, -0.5}"` |
| ConfidenceValues | int32 | `"{30, 80, 75, 25}"` |
| ThresholdLevelAdjustment_Linear | float | `"1.0"` |
| MaxNumDetections | int32 | `"1"` |

##### Parameter descriptions

- `DetectionZoneXYPoints` - Vector of `{X, Y}` points specifying vertices to form an arbitrarily shaped 2D detection zone. The length can be up to a maximum of 20 `{X, Y}` tuples. A set of detection zone presets with examples can be found in `Presence2D/Presets/DetectionZonePresets`. These can be copied into the relevant demo preset, or used as examples on how to set up different shaped detection zones.
- `ConfidenceValues` - Configures the confidence weights and thresholds for transitions between presence/no presence state. This is key for balancing response time vs detection robustness. For a detailed description on how to tune the confidence values parameter, please refer to the [Tuning Confidence values](#tuning-confidence-values) section below.
- `ThresholdAdjustment_Linear` - Linear scale multiplication factor of the thresholds. Used to adjust the thresholds up from the baseline to reduce the probability of false detections, but also making the system less sensitive. In the case that you experience false detections, this parameter can be used to mitigate that. The threshold increase in `dB` can be calculated as `ThresholdAdjustment_dB = 5*log10(ThresholdAdjustment_Linear)`, where the `5` comes from how the four raw channels are combined in the application.
- `MaxNumDetections` - The number of detections processed internally in the ULPP_Presence2D application. Detections are processed with increasing range, meaning if `MaxNumDetections = 1`, only the closest detection will be found. This means that if the detection zone is offset from the origin, or the zone is rectangular with the longest dimension in the X direction, you run the risk of not detecting a target inside the detection zone. If that is the case, you can increase `MaxNumDetections` to a higher number (maximum 10), however note that this also increases the risk of false detections inside the detection zone.

**NOTE** The public parameter `MaxNumHumanDetection2DOutputs` is not listed here, since that output is not processed and visualized in the demo.

#### Other parameters

```
    "Presence2DPlottingParameters": {
      "ShowFOVLines": "true",
      "ShowXYCoordinates": "true",
      "InvertedTopView": "false",

      "TrailBackwardSeconds": "1.0",
      "TrailForwardSeconds": "1.0",
      
      "MaxHistoryTimeplotsInS" : "300",

      "RangeLimVec": "{}",
      "PowerLimVec": "{-80.0, 20.0}",

      "DefaultMiddlePlot": "Range",
      "MaxBufferedFrames": "-1"
    }
```

The visualization buffers HumanPresence2D data in memory, allowing stepping backwards/forwards for closer evaluation. `MaxBufferedFrames` specifies the maximum number of frames to hold in memory. The actual value will be different in the backend. If this is set to a negative value, then `MaxBufferedFrames` will be 100k.

The table below describes the available plotting parameters configurable in the preset file:

| Parameter | Description |
| -------- |------------------|
| ShowFOVLines | `true`/`false` - Enable/disable the FoV lines in the sector plot. |
| ShowXYCoordinates | `true`/`false` - Enable/disable the FoV lines in the sector plot. |
| InvertedTopView | `true`/`false` - Enable/disable top/down inversion of the sector plot. |
| TrailBackwardSeconds | Floating point value specifying the fade-out time in seconds of the backwards trail (red) of detections in the sector plot. |
| TrailForwardSeconds | Floating point value specifying the fade-out time in seconds of the forwards trail (blue) of detections in the sector plot (only visible when stepping back in time in the plot). |
| MaxHistoryTimeplotsInS | Value adjusting the time (X) axis limits of the time series plots. |
| PowerLimVec | Specifies the initial power limits (in dB) in the power visualization. |
| RangeLimVec | Specifies the initial range limits (in meters) in the power visualization. |
| DefaultMiddlePlot | `"Range"`, `"SNR"` or `"Angle"` - Specifies the initial middle time series plot. |

All of the parameters in the table above can be changed interactively while running the demo through the GUI panel. If any of these limit vectors are omitted in the preset file, the default values will be used.

You can also save these plotting parameters to a JSON and load them later.

## Tuning Confidence values ##

Understanding the __ConfidenceValues__ is the key to tuning the Presence2D algorithm to fit
 your application. In this chapter we will discuss how to configure the different 
values to emphasize different behaviour of the application and what are the **pros** and **cons** 
of changing the values in a certain direction.

Typically we want to emphasize on one or more of the following key parameters:

* Response time
* Robustness of detection

__ConfidenceValues__ consist of these four values:

``` ConfidenceValues = [WeightPresence, WeightNoPresence, ConfidenceThresholdPresence, ConfidenceThresholdNoPresence] ```

We need to separate the thought process when tuning going from __NoPresence__ to __Presence__ state 
and from __Presence__ to __NoPresence__ state.

#### ConfidenceThreshold ####
The __ConfidenceThresholdPresence__ is the value the Confidence value need to exceed or equal before we switch 
the output __PresenceState__ from __NoPresence__ to __Presence__. 

That means if you set __ConfidenceThresholdPresence__ = 60, the confidence value need to be >=60 before the 
__PresenceState__ changes to __Presence__.

Adversely the __ConfidenceThresholdNoPresence__ is the value the Confidence value need to fall below before we switch 
the output __PresenceState__ from __Presence__ to __NoPresence__

That means if you set __ConfidenceThresholdNoPresence__ = 10, the confidence value need to be <10 before the 
__PresenceState__ changes to __NoPresence__.

#### Weights ####
The weights are maybe the hardest to understand. However, they are a very easy and powerful way 
to accomplish your goal for the application.

The weight can be in the interval [0, 100]. The new confidence value is calculated from the 
existing confidence value and the new detection update. The update rate is 8 fps. This means every 125ms the 
confidence value is updated with the new detection information. 

A high value of the weight means you put high trust in the current confidence value and a lower trust on the new detection information.
 A low weight means you put little trust in the existing confidence value and high trust 
in the new detection information.

If we take it to the extreme.
Weight = 100 means you only trust your existing confidence and have no trust in the new detection. That means the confidence 
will forever be the same value. Since the confidence starts at 0 it would forever be 0 if you would choose WeightPresence=100.

Adversely if you would choose __WeightNoPresence__=100 and __WeightPresence__<100, once you got to __PresenceState__ = __Presence__ 
you would stay there forever.

Weight = 0 means you only trust your new detection update to set the new confidence value. 
That means if you were to have alternating detection updates of Presence, NoPresence, Presence, NoPresence ... 
and your confidence value would alternate between 100, 0, 100, 0, ...

Below we show how the confidence grows differently when in __NoPresence__ state for 4 different values 
of __WeightPresence__ [10, 30, 60, 90]. We assume we get a set of positive detections starting at time>0.5 seconds.

![confidence](./Images/confidence_vs_weights.png)

If we zoom in on the 3 lowest weights we can see it in a bit more detail.

![confidence-zoom](./Images/confidence_vs_weights_zoom.png)

__WeightPresence__=10 only requires one detection (125ms) to get us into __Presence__.
__WeightPresence__=30 requires two detections (250ms) to get us into __Presence__.
__WeightPresence__=60 requires three detections (375ms) to get us into __Presence__.
__WeightPresence__=90 requires fourteen detections (1750ms) to get us into __Presence__.

**NOTE** The assumption here is we got positive detection on every update and with fixed 
__ConfidenceThresholds__ of 75 and 25.

#### Response time vs Robustness ####
If you need a fast response time to __Presence__ you choose a low weight. The low weight will make the confidence value grow 
fast since you put little trust in the existing value of it and high trust in the new incoming detections.

The problem however with a low weight is you get more susceptible to false detections causing the confidence value 
to exceed the __ConfidenceThresholdPresence__ giving you unwanted output of 
__PresenceState__ = __Presence__. 

Adversely a high weight value means you get a much more robust trustworthy system but you will 
sacrifice on the response time. This is the system level decision you have to make to fine tune the 
application to your need.

When in __Presence__, the target-of-interest might be very still, i.e. little body movement and it is harder for the application to get
 consistent detections. In this case you might want a high value of __WeightNoPresence__ to maintain the confidence value above 
the __ConfidenceThresholdNoPresence__ to keep __Presence__ for the duration of the time the 
target-of-interest remains in the detection zone. 
A combination of high __WeightNoPresence__ and lowering the __ConfidenceThresholdNoPresence__ might be the way to go.

Hopefully with this tool you can experiment and find the correct combination of __ConfidenceValues__ for your application.

#### Response time tables for different weight and thresholds ####

Here is a table of the response time in seconds going from confidence=0 to __Presence__ for different __WeightPresence__ values (column 1) and
for different __ConfidenceThresholdPresence__ (CTP) in columns 2 to 6. We assume positive detection on every update.


|   WeightPresence |   CTP=50 |   CTP=60 |   CTP=70 |   CTP=80 |   CTP=90 |
|------------------|----------|----------|----------|----------|----------|
|               10 |    0.125 |    0.125 |    0.125 |    0.125 |    0.125 |
|               15 |    0.125 |    0.125 |    0.125 |    0.125 |    0.25  |
|               20 |    0.125 |    0.125 |    0.125 |    0.125 |    0.25  |
|               25 |    0.125 |    0.125 |    0.125 |    0.25  |    0.25  |
|               30 |    0.125 |    0.125 |    0.125 |    0.25  |    0.25  |
|               35 |    0.125 |    0.125 |    0.25  |    0.25  |    0.375 |
|               40 |    0.125 |    0.125 |    0.25  |    0.25  |    0.375 |
|               45 |    0.125 |    0.25  |    0.25  |    0.375 |    0.375 |
|               50 |    0.125 |    0.25  |    0.25  |    0.375 |    0.5   |
|               55 |    0.25  |    0.25  |    0.375 |    0.375 |    0.5   |
|               60 |    0.25  |    0.25  |    0.375 |    0.5   |    0.625 |
|               65 |    0.25  |    0.375 |    0.375 |    0.5   |    0.75  |
|               70 |    0.25  |    0.375 |    0.5   |    0.625 |    0.875 |
|               75 |    0.375 |    0.5   |    0.625 |    0.75  |    1.125 |
|               80 |    0.5   |    0.625 |    0.75  |    1     |    1.375 |
|               82 |    0.5   |    0.625 |    0.875 |    1.125 |    1.5   |
|               84 |    0.5   |    0.75  |    0.875 |    1.25  |    1.75  |
|               86 |    0.625 |    0.875 |    1     |    1.375 |    2     |
|               88 |    0.75  |    1     |    1.25  |    1.625 |    2.375 |
|               90 |    0.875 |    1.125 |    1.5   |    2     |    2.75  |
|               92 |    1.125 |    1.375 |    1.875 |    2.5   |    3.5   |
|               94 |    1.5   |    1.875 |    2.5   |    3.375 |    4.75  |
|               96 |    2.125 |    2.875 |    3.75  |    5     |    7.125 |
|               98 |    4.375 |    5.75  |    7.5   |   10     |   14.25  |


Here is a table of the response time in seconds going from confidence=100 to __NoPresence__ for different __WeightNoPresence__ values (column 1) and
for different __ConfidenceThresholdNoPresence__ (CTNP) in columns 2 to 6. We assume no detection on every update.

|   WeightNoPresence |   CTNP=50 |   CTNP=40 |   CTNP=30 |   CTNP=20 |   CTNP=10 |
|--------------------|-----------|-----------|-----------|-----------|-----------|
|                 10 |     0.125 |     0.125 |     0.125 |     0.125 |     0.25  |
|                 15 |     0.125 |     0.125 |     0.125 |     0.125 |     0.25  |
|                 20 |     0.125 |     0.125 |     0.125 |     0.25  |     0.25  |
|                 25 |     0.125 |     0.125 |     0.125 |     0.25  |     0.25  |
|                 30 |     0.125 |     0.125 |     0.25  |     0.25  |     0.25  |
|                 35 |     0.125 |     0.125 |     0.25  |     0.25  |     0.375 |
|                 40 |     0.125 |     0.25  |     0.25  |     0.25  |     0.375 |
|                 45 |     0.125 |     0.25  |     0.25  |     0.375 |     0.375 |
|                 50 |     0.25  |     0.25  |     0.25  |     0.375 |     0.5   |
|                 55 |     0.25  |     0.25  |     0.375 |     0.375 |     0.5   |
|                 60 |     0.25  |     0.25  |     0.375 |     0.5   |     0.625 |
|                 65 |     0.25  |     0.375 |     0.375 |     0.5   |     0.75  |
|                 70 |     0.25  |     0.375 |     0.5   |     0.625 |     0.875 |
|                 75 |     0.375 |     0.5   |     0.625 |     0.75  |     1.125 |
|                 80 |     0.5   |     0.625 |     0.75  |     1     |     1.375 |
|                 82 |     0.5   |     0.625 |     0.875 |     1.125 |     1.5   |
|                 84 |     0.5   |     0.75  |     0.875 |     1.25  |     1.75  |
|                 86 |     0.625 |     0.875 |     1     |     1.375 |     2     |
|                 88 |     0.75  |     1     |     1.25  |     1.625 |     2.375 |
|                 90 |     0.875 |     1.125 |     1.5   |     2     |     2.75  |
|                 92 |     1.125 |     1.375 |     1.875 |     2.5   |     3.5   |
|                 94 |     1.5   |     1.875 |     2.5   |     3.375 |     4.75  |
|                 96 |     2.125 |     2.875 |     3.75  |     5     |     7.125 |
|                 98 |     4.375 |     5.75  |     7.5   |    10     |    14.25  |
