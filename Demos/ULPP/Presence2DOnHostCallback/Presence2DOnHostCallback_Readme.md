# ULPP Presence2DOnHost callback demo

This document describes the X7 Ultra Low Power Presence (ULPP) Presence2DOnHost demo and how to configure it. Please note that the configuration is the same as for the Presence2D demo, so this document only has a high-level description and instructions for running the demo, and refers to the [Presence2D demo](../Presence2D/Presence2D_Readme.md) for all configuration and GUI descriptions.

## Description of the X7 ULPP Presence2DOnHost callback demo

The X7 ULPP Presence2DOnHost callback demo uses the Novelda X7 RadarDirect radar application for streaming complex baseband frames from the X7 chip which are then processed through the ULPP_Presence2D application algorithm on host, and shows how to set a callback function in python to receive the application output, making it easy to build an application on top of the Presence2D application.

Just like in the Presence2DOnHost demo, in this demo, the ULPP_Presence2D application runs on the host computer and allows running playback of recorded baseband data through the Presence2D application with custom parameter tuning. This way you can record raw data of the use cases you want to test, then tune the application parameters until you have the performance you want. The parameters can then be deployed in the [Presence2D](../Presence2D/Presence2D_Readme.md) demo for deployment in a prototype product setup.

The demo provides an example of how to set up a callback function for receiving Presence2D application output, and how to start the radar/playback which will trigger the callback function on every new output.

**NOTE** This demo uses the RadarDirect radar application, so make sure that the `BA22FirmwarePath` parameter points to the RadarDirect FW as opposed to the Presence2D demo which uses the ULPP_Presence2D FW.

For a description of the application output please refer to the description in the Presence2D demo [here](../Presence2D/Presence2D_Readme.md#description-of-the-x7-ulpp-presence2d-demo).

### Running the demo

To run the demo you first need to set up the necessary parameters in a preset file. There are no presets in the demo folder itself, but you can find examples of them in the `Presence2DOnHost/Presets` folder. A convenient way to work is to make a copy of the preset you want to base your application on, then update it with the relevant local paths and custom parameter changes. When you have your desired preset, you can run the example:

```
python <path-to-runX7ULPP_Presence2DOnHostCallback_example.py> <path-to-preset_file.json>
```

The provided example should print the following information for every received HumanPresence2D message:
```
Seq.Num:  59
Timestamp:  1761641895153
Time since start:  3.631
Presence State:  True
X, Y Position:  0.22 ,  -0.44
Confidence:  37
```

You now have the power to easily put your application code on top the Presence2D application output. Create your own callback function and get on with product prototyping!

### Callback function arguments

The `Presence2DOnHostCallback()` python class handles readout of the data and packs it into a series input arguments to the callback function. The tables below lists the callback function arguments and briefly explains them.

#### Input arguments

| Parameter | Type | Description |
| --------- | ---- | ----------- |
| `presence2DHelper` | `Presence2DHelper` | Helper object for extracting the incoming application data. Includes get-methods for all fields in the HumanPresence2D data, plus other convenience methods. For the full `Presence2DHelper` class definition, see [Presence2DHelper.py](../../../Nodes/Python/Novelda/Presence2DPlotter/Presence2DHelper.py). |

#### Output arguments

| Parameter | Type | Description |
| --------- | ---- | ----------- |
| `Continue` | `bool` | Whether to continue processing - `False` stops the flow, `True` continues. |

### Configuration

For a description of the available demo configuration parameters, please refer to the descriptions in the Presence2D demo [here](../Presence2D/Presence2D_Readme.md#configuration).
