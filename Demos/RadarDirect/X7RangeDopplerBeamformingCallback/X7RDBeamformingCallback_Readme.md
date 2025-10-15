# X7 Range-Doppler Beamforming callback demo

This document describes the X7 Range-Doppler Beamforming callback demo and how to configure it.

## Description of the X7 RadarDirect callback demo

The X7 Range-Doppler Beamforming callback demo uses the Novelda X7 RadarDirect radar application for streaming complex baseband frames from the X7 chip, then the frames go through digital beamforming for a configurable number of angles before being processed through Range-Doppler per beam. The demo shows how to set a callback function in python to receive the beamformed Range-Doppler maps, making it easy to do further processing. The demo allows both running live using a Novelda X7F202 radar module, or running playback on recorded data.

For more information about the underlying signal processing, refer to the [Range-Doppler demo readme](../X7RangeDopplerRaw/X7RangeDopplerRaw_Readme.md#range-doppler-processing), and the [beamforming demo readme](../X7RangeDopplerBeamforming/X7RangeDopplerBeamforming_Readme.md#description-of-the-x7-rangedoppler-beamforming-demo).

The demo provides an example of how to set up a callback function for receiving the beamformed Range-Doppler maps, and how to start the radar/playback which will trigger the callback function on every new frame.

### Running the demo

To run the demo you first need to set up the necessary parameters in a preset file. There are no presets in the demo folder itself, but you can find examples of them with all the relevant parameters in `X7RangeDopplerBeamforming/Presets`. A convenient way to work is to make a copy of the preset you want to base your application on, then update it with the relevant local paths and custom parameter changes. When you have your desired preset, you can run the example:
```
python <path-to-runX7RDBeamformingCallback_example.py> <path-to-preset_file.json>
```
You now have the power to implement your own processing on top of the beamformed Range-Doppler maps. Maybe you want to do target classification or multi-target positioning?

### Callback function arguments

The `RDBeamformingCallback` python class handles readout of the data and packs it into a series input arguments to the callback function. The tables below lists the callback function arguments and briefly explains them.

#### Input arguments

| Parameter | Type | Description |
| --------- | ---- | ----------- |
| `rd_beams` | `numpy.ndarray` | 3D numpy array of floating point values, holding beamformed Range-Doppler maps for each configured angle. The shape of the received array will be: <ul><li>If `"Convert2Pwr": "true"`:<br>`{numAzimuthAngles, numRangeBins, numDopplerBins}`, where `numAzimuthAngles` corresponds to the configured beamforming angles `azBeamAngles`, `numRangeBins` is the number of range bins per frame, and `numDopplerBins = FFTSize`. Each sample holds a power value for the given cell.</li><li>If `"Convert2Pwr": "false"`:<br>`{numAzimuthAngles, numRangeBins, 2*numDopplerBins}`, where in the Doppler dimension, the even numbered indices hold the real part, and the odd numbered indices hold the imaginary part of the complex FFT values in the Doppler dimension.</li></ul> |
| `sequence_num` | `int` | Sequence number - A contigouous sequence number increasing for each received frame. |
| `timestamp` | `int` | POSIX timestamp for the received frame in milliseconds since 01.01.1970. |
| `rd_helper` | `RangeDopplerBeamHelper` | Helper object for calculating parameters and vectors necessary for understanding the incoming data. Includes get-methods for e.g. `range_vector`, `doppler_vector` and `azimuth_angles`. For the full `RangeDopplerBeamHelper` class definition, see [RDBeamCallbackRunner.py](./RDBeamCallbackRunner.py). |

#### Output arguments

| Parameter | Type | Description |
| --------- | ---- | ----------- |
| `Continue` | `bool` | Whether to continue processing - `False` stops the flow, `True` continues. |


### Configuration

The available demo configuration parameters should be in any of the supplied presets in the X7RangeDopplerBeamforming demo folder (e.g. [X7RangeDopplerBeamforming/Presets/default_preset.json](../X7RangeDopplerBeamforming/Presets/default_preset.json)). Some general formatting rules apply for specifying parameters in the setup file, which can be seen in the [X7RangeDopplerRaw_Readme/Configuration](../X7RangeDopplerRaw/X7RangeDopplerRaw_Readme.md#configuration).

#### High level demo parameters

The available high level demo parameters the same as those described in the [X7RangeDopplerRaw readme](../X7RangeDopplerRaw/X7RangeDopplerRaw_Readme.md#high-level-demo-parameters).

#### X7 radar parameters

The available X7 radar parameters are the same as those described in the [X7RangeDopplerRaw readme](../X7RangeDopplerRaw/X7RangeDopplerRaw_Readme.md#x7-radar-parameters).

#### Digital Beamforming parameters
The available digital beamforming parameters are the same as those described in the [X7RangeDopplerBeamforming readme](../X7RangeDopplerBeamforming/X7RangeDopplerBeamforming_Readme.md#digital-beamforming-parameters).

#### Range-Doppler parameters

The available Range-Doppler parameters are the same as those described in the [X7RangeDopplerRaw readme](../X7RangeDopplerRaw/X7RangeDopplerRaw_Readme.md#range-doppler-parameters).
