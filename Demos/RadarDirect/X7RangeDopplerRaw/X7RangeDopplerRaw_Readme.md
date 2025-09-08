# X7 RangeDoppler raw channels demo

This document describes the X7 RangeDoppler raw channels demo and how to configure it. In addition the concept of Range-Doppler processing is briefly explained. To run the demo just run the 'runX7RangeDopplerRaw.py' file with python.

```
python <path-to-runX7RangeDopplerRaw.py>
```

## Description of the X7 RangeDoppler raw channels demo

The X7 RangeDoppler raw channels demo uses the Novelda X7 RadarDirect radar application for streaming complex baseband frames from the X7 chip, and then calculates the Range-Doppler map for each active raw radar channel. The demo provides options to configure the X7 radar chip, the Range-Doppler processing and the visualization, and allows both running live using a Novelda X7F202 radar module, or running playback on recorded data. For a description of the concept of Range-Doppler processing, please see the [Range-Doppler processing](#range-doppler-processing) section.

### Configuration

The available demo configuration parameters can be found in [rd_raw_setup.json](./rd_raw_setup.json). Some general formatting rules apply for specifying parameters in the setup file:
- All algorithm parameters (`RadarSource` and `RangeDopplerRawChannels`) must be written as strings, i.e. encapsulated by `""`.
- Parameters have assigned types, and the provided default settings indicate the type through formatting of the parameter strings. A type mismatch will cause the parameters to not take effect.
- Floating point values are written with a dot, e.g. `"FPS" : "32.0"`
- Signed 32-bit integers are written without any postfix, e.g. `"IterationsPerFrame" : "30"`
- Unsigned 16-bit integers are written with a `u16` postfix, e.g. `"RxMaskSequence" : "{3u16, 3u16}"`
- File path strings must be separated with `\\` or `/` and not a single `\`.
- Parameter names (keys) should not be changed from the provided defaults as they will cease to take effect.

Please refer to the sections below for the available parameters, and examples on how to set them.

#### GUI parameters

![X7RangeDopplerRaw example](./Images/X7RangeDopplerRawExample.png)

The GUI panel (highlighted in red) is used to provide information while running the demo and allows configuration of the visualization on the fly.

The user can adjust the axis limits by changing the min/max parameters, which is useful e.g. for inspecting specific parts of the Range-Doppler map. When editing axis limits, press `Enter` to apply changes.

In addition, there are some hotkeys for GUI control:

| Hotkey | Description |
| -------- | -------- |
| LeftArrow | Pause the plotting and step back to the previous Range-Doppler map. |
| RightArrow | Pause the plotting and step forward to the next Range-Doppler map. |
| SpaceBar | Toggle play/pause. |
| MouseWheel | Zoom view in/out. |
| LeftMouseButton (click + hold) | Rotate view. |
| X | Switch to an orthographic view of the range axis in orthographic mode. |
| Y | Switch to an orthographic view of frequency axis in orthographic mode. |
| Z | Switch to an orthographic top-down view in orthographic mode.
| R | Restore camera to default view. |
| RightMouseButton (click on RD map surface) | Place surface marker at specific Range-Doppler cell. |
| RightMouseButton (click outside RD map surface) | Remove surface marker. |
| WASD | Move the surface marker in the respective direction. |


#### High level demo parameters

Below is an example of the available high level demo parameters, and examples on how to set them.

| Hotkey | Description |
| -------- | -------- |
| IsLive | `true`/`false` - Controls whether to run live with an X7F202 radar module connected, or playback of already recorded data. |
| BA22FirmwarePath | `"<path-to-sdk>/firmware/X7_Application_BA22_*_RadarDirect_*.app"` - Necessary when `IsLive = true` and should point to the RadarDirect application binary provided in the Novelda X7 SDK. |
| PlaybackFile | `"<path-to-RecordingDirectory>/rec_*.sig"` - Necessary when `IsLive = false` and should point to the recorded data file. |
| DoRecording | `true`/`false` - Controls whether to record the radar data to a file when `IsLive = true` |
| RecordingDirectory | `"<path-to-RecordingDirectory>"` - Folder to save recorded data files |
| RecordingPrefix | E.g. `"test_recording_"` - Prefix for the recorded data file. Will be appended by timestamp for when recording started. |

#### X7 radar parameters

Configuration of the low-level X7 radar parameters requires deep understanding of the chip, and it's recommended to use provided configuration tools (e.g. `pyx7configuration`) to help set up the system correctly. For a description of each of the X7 radar parameters, please see the pyx7configuration documentation provided in the Novelda X7 SDK (`<path-to-sdk>/pyx7configuration/Docs`).

The table below shows the available X7 radar parameters, their type and an example on how to set them in the configuration file. Note that these only take effect when running live, and not in playback mode.

| Parameter | Type | Example |
| -------- | -------- | -------- |
| FPS | float | `"32.0"` |
| PulsePeriod | int32 | `"12"` |
| MframesPerPulse | int32 | `"6"` |
| PulsesPerIteration | int32 | `"35"` |
| IterationsPerFrame | int32 | `"30"` |
| TxPower | int32 | `"3"` |
| InterleavedFrames | int32 | `"0"` |
| Ilo5xMode | int32 | `"1"` |
| TxChannelSequence | uint16 | `"{0u16, 1u16}"` |
| RxMaskSequence | uint16 | `"{3u16, 3u16}"` |

#### Range-Doppler parameters

The Range-Doppler processing can be configured with the following available parameters:

| Parameter | Type | Example | Description |
| -------- | -------- | -------- | -------- |
| NumFramesInPD | int32 | `"64"` | Number of radar frames to buffer and process for each Range-Doppler calculation. The observation time can be calculated as `Tobs = NumFramesInPD/FPS`. |
| FramesBetweenPD | int32 | `"32"` | Number of radar frames between each new Range-Doppler update. The time between each Range-Doppler can be calculated as `TimeBetweenPD = FramesBetweenPD/FPS`. |
| FFTSize | int32 | `"64"` | Length of the FFT for Range-Doppler calculation, allowing oversampling in the FFT. `FFTSize` needs to be a power of 2, with 16 being the lowest and 4096 being the highest. In addition `FFTSize` needs to be greater than or equal to `NumFramesInPD`. |
| enableDCRemoval | bool | `"true"` | Enable/disable removal of static objects through a weighted arithmetic mean per range bin of the frame buffer. If `false` all static reflections in the scene will be visible, making detection of moving targets harder. |

#### Other parameters

```
"PlotRangeDopplerRawChannels": {
    "MaxBufferedFrames" : "-1"
}
```

The visualization buffers Range-Doppler maps in memory, allowing stepping backwards/forwards for closer evaluation. `MaxBufferedFrames` specifies the maximum number of frames (Range-Doppler maps) to hold in memory. The actual value will be different in the backend. If this is set to a negative value, then `MaxBufferedFrames` will be 100k. With the default setup of 96 range bins and `FFTSize = 64` each Range-Doppler map is about 95kB.

## Range-Doppler processing

Range-Doppler is a radar signal processing technique that provides a two-dimensional map of target responses, showing both range (distance of the target) and Doppler (radial speed/direction of the target).

When active, the Novelda X7 chip transmits Gaussian shaped radar pulses, and the receiver(s) sample the pulses at different discrete points in time (typically called fast time). Each point in time represents the radial distance from the radar and is typically called a range bin. After downconversion, the resulting vector (typically called a radar frame) holds a complex baseband value for each of the range bins.

The Range-Doppler processing is performed by buffering a number of consecutive radar frames (in slow time), and then performing a fast Fourier transform (FFT) on each range bin, to convert from time domain to the frequency (Doppler/radial speed) domain. This allows targets to be resolved in the frequency (speed) domain, and thus allows them to be separated even if closely spaced in range. In addition, the processing increases the signal-to-noise ratio of the target signal by coherently integrating signal, as long as the target stays within the same range bin during the observation window (number of buffered frames).

Below is an example of a Range-Doppler map for a single radar channel (TX0RX0), where the radar streams 64 frames per second (FPS), and the Range-Doppler is configured to buffer and process 64 frames (i.e. the observation time is 1 second). The figure shows range along one axis, and Doppler frequency along the other.

![Range-Doppler example](./Images/RangeDopplerExample.png)

For more information on Range-Doppler processing (also referred to as Pulse-Doppler), visit e.g. https://en.wikipedia.org/wiki/Pulse-Doppler_signal_processing.
