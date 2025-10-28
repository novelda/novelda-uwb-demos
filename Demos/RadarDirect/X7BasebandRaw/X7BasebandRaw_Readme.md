# X7 Baseband raw channels demo

This document describes the X7 Baseband raw channels demo and how to configure it.

## Description of the X7 Baseband raw channels demo

The X7 Baseband raw channels demo uses the Novelda X7 RadarDirect radar application for streaming complex baseband frames from the X7 chip, and then visualizes the amplitude of the frames from each of the raw radar channels. The demo provides options to configure the X7 radar chip and the visualization, whether to do static removal, and allows both running live using a Novelda X7F202 radar module, or running playback on recorded data.

### Running the demo

To run the demo you first need to set up the necessary parameters in a preset file. You can find examples of them in the `Presets` folder. A convenient way to work is to make a copy of the preset you want to base your application on, then update it with the relevant local paths and custom parameter changes. When you have your desired preset, you can run:
```
python <path-to-runX7BasebandRawPlot.py> <path-to-preset_file.json>
```

### Configuration

The available demo configuration parameters can be found in the `Presets` folder. Some general formatting rules apply for specifying parameters in the setup file:
- All algorithm parameters (`RadarSource`) must be written as strings, i.e. encapsulated by `""`.
- Parameters have assigned types, and the provided default settings indicate the type through formatting of the parameter strings. A type mismatch will cause the parameters to not take effect.
- Floating point values are written with a dot, e.g. `"FPS" : "100.0"`
- Signed 32-bit integers are written without any postfix, e.g. `"IterationsPerFrame" : "6"`
- Unsigned 16-bit integers are written with a `u16` postfix, e.g. `"RxMaskSequence" : "{3u16, 3u16}"`
- File path strings must be separated with `\\` or `/` and not a single `\`.
- Parameter names (keys) should not be changed from the provided defaults as they will cease to take effect.

Please refer to the sections below for the available parameters, and examples on how to set them.

#### GUI parameters

![X7BasebandRaw example](./Images/basebandPlotExampleImg.png)

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
| A | Move marker to the left by one rangebin |
| D | Move marker to the right by one rangebin |

#### High level demo parameters

Below is an example of the available high level demo parameters, and examples on how to set them.

| Parameter | Description |
| -------- | -------- |
| IsLive | `true`/`false` - Controls whether to run live with an X7F202 radar module connected, or playback of already recorded data. |
| BA22FirmwarePath | `"<path-to-sdk>/firmware/X7_Application_BA22_*_RadarDirect_*.app"` - Necessary when `IsLive = true` and should point to the RadarDirect application binary provided in the Novelda X7 SDK. |
| PlaybackFile | `"<path-to-RecordingDirectory>/rec_*.sig"` - Necessary when `IsLive = false` and should point to the recorded data file. When recording, a preset file with this already filled out is automatically generated alongside the recording. |
| DoRecording | `true`/`false` - Controls whether to record the radar data to a file when `IsLive = true` |
| RecordingDirectory | `"<path-to-RecordingDirectory>"` - Folder to save recorded data files |
| RecordingPrefix | E.g. `"test_recording_"` - Prefix for the recorded data file. Will be appended by timestamp for when recording started. |
| DCRemoval | `true`/`false` - Enables/disables DC removal, i.e. removal of static objects. Enabling this makes it easier to detect moving targets. |

If `DoRecording = true` the JSON preset file will be copied and filled out with `IsLive=false` and `PlaybackFile=<path-to-rec>` so that you can use it when doing playback.

#### X7 radar parameters

Configuration of the low-level X7 radar parameters requires deep understanding of the chip, and it's recommended to use provided configuration tools (e.g. `pyx7configuration`) to help set up the system correctly. For a description of each of the X7 radar parameters, please see the pyx7configuration documentation provided on the [Novelda X7 developer website](https://dev.novelda.com/X7/_examples/x7_fundamentals/pyx7configuration_0.6.html) (requires access).

The table below shows the available X7 radar parameters, their type and an example on how to set them in the configuration file. Note that these only take effect when running live, and not in playback mode.

| Parameter | Type | Example |
| -------- | -------- | -------- |
| FPS | float | `"100.0"` |
| PulsePeriod | int32 | `"12"` |
| MframesPerPulse | int32 | `"6"` |
| PulsesPerIteration | int32 | `"35"` |
| IterationsPerFrame | int32 | `"6"` |
| TxPower | int32 | `"3"` |
| InterleavedFrames | int32 | `"5"` |
| TxChannelSequence | uint16 | `"{0u16, 1u16}"` |
| RxMaskSequence | uint16 | `"{3u16, 3u16}"` |

#### Other parameters

```
"BBPlottingParameters": 
{
    "MaxBufferedFrames" : "-1",
    "YLimVec" : "{-60.0, 60.0}",
    "XLimVec" : "{0.4, 6.0}"
}
```

The visualization buffers Baseband data in memory, allowing stepping backwards/forwards for closer evaluation. `MaxBufferedFrames` specifies the maximum number of frames to hold in memory. The actual value will be different in the backend. If this is set to a negative value, then `MaxBufferedFrames` will be 100k.

`XLimVec` specifies the initial range limits (in meters)
`YLimVec` specifies the initial Power limits (in dB)

All of these can be changed interactively while running the demo. If any of these limit vectors are omitted then the default values will be used.
