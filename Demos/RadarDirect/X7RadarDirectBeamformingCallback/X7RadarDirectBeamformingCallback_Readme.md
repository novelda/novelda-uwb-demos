# X7 RadarDirect Beamforming callback demo

This document describes the X7 RadarDirect Beamforming callback demo and how to configure it.

## Description of the X7 RadarDirect callback demo

The X7 RadarDirect Beamforming callback demo uses the Novelda X7 RadarDirect radar application for streaming complex baseband frames from the X7 chip. In this demo, the X7 is configured in alternating Tx, dual Rx mode. First, the baseband frames go through a static removal process, implemented as a single-pole IIR filter, on each of the 4 raw channels individually. Digital beamforming is then applied on the frames for a configurable number of azimuth angles. The demo shows how to set a callback function in python to receive the beamformed baseband frames, making it easy to do further processing. The demo allows both running live using a Novelda X7F202 radar module, or running playback on recorded data.

The demo provides an example of how to set up a callback function for receiving the beamformed baseband frames, and how to start the radar/playback which will trigger the callback function on every new frame.

### Running the demo

To run the demo you first need to set up the necessary parameters in a preset file. There are no presets in the demo folder itself, but you can find examples of them with all the relevant parameters in `X7RadarDirectBeamforming/Presets`. A convenient way to work is to make a copy of the preset you want to base your application on, then update it with the relevant local paths and custom parameter changes. When you have your desired preset, you can run the example:
```
python <path-to-runX7BeamformingCallback_example.py> <path-to-preset_file.json>
```
You now have the power to implement your own processing on top of the beamformed baseband frames, from a simple 1D application with a single focused beam, or a complex tracking application with multiple beams.

### Callback function arguments

The `RadarDirectBeamCallback` python class handles readout of the data and packs it into a series input arguments to the callback function. The tables below lists the callback function arguments and briefly explains them.

#### Input arguments

| Parameter | Type | Description |
| --------- | ---- | ----------- |
| `rd_beams` | `numpy.ndarray` | 3D numpy array of floating point values, holding beamformed baseband frames for each configured angle. The shape of the received array will be `{numAzimuthAngles, 2, numRangeBins}`, where `numAzimuthAngles` corresponds to the configured beamforming angles `azBeamAngles`, `2` comes from the complex baseband in-phase/quadrature (I/Q) components and `numRangeBins` is the number of range bins per frame. |
| `sequence_num` | `int` | Sequence number - A contigouous sequence number increasing for each received frame. |
| `timestamp` | `int` | POSIX timestamp for the received frame in milliseconds since 01.01.1970. |
| `rd_helper` | `RadarDirectBeamHelper` | Helper object for calculating parameters and vectors necessary for understanding the incoming data. Includes get-methods for e.g. `range_vector` and `azimuth_angles`. For the full `RadarDirectBeamHelper` class definition, see [RadarDirectBeamCallbackRunner.py](./RadarDirectBeamCallbackRunner.py). |

#### Output arguments

| Parameter | Type | Description |
| --------- | ---- | ----------- |
| `Continue` | `bool` | Whether to continue processing - `False` stops the flow, `True` continues. |


### Configuration

The available demo configuration parameters should be in any of the supplied presets in the X7RadarDirectBeamforming demo folder (e.g. [X7RadarDirectBeamforming/Presets/default_preset.json](../X7RadarDirectBeamforming/Presets/default_preset.json)). Some general formatting rules apply for specifying parameters in the setup file, which can be seen in the [X7BasebandRaw_Readme/Configuration](../X7BasebandRaw/X7BasebandRaw_Readme.md#configuration).

#### High level demo parameters

The available high level demo parameters the same as those described in the [X7BasebandRaw readme](../X7BasebandRaw/X7BasebandRaw_Readme.md#high-level-demo-parameters).

#### X7 radar parameters

The available X7 radar parameters are the same as those described in the [X7BasebandRaw readme](../X7BasebandRaw/X7BasebandRaw_Readme.md#x7-radar-parameters).

#### Digital Beamforming parameters
The available digital beamforming parameters are the same as those described in the [X7RadarDirectBeamforming readme](../X7RadarDirectBeamforming/X7RadarDirectBeamforming_Readme.md#digital-beamforming-parameters).
