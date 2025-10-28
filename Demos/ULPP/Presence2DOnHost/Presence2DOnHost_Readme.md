# ULPP Presence2DOnHost demo

This document describes the X7 Ultra Low Power Presence (ULPP) Presence2DOnHost demo and how to configure it. Please note that the configuration is the same as for the Presence2D demo, so this document only has a high-level description and instructions for running the demo, and refers to the [Presence2D demo](../Presence2D/Presence2D_Readme.md) for all configuration and GUI descriptions.

## Description of the X7 ULPP Presence2DOnHost demo

The X7 ULPP Presence2D demo uses the Novelda X7 RadarDirect radar application for streaming complex baseband frames from the X7 chip which are then processed through the ULPP_Presence2D application algorithm on host, and then visualized in the GUI.

In this demo, the ULPP_Presence2D application runs on the host computer and allows running playback of recorded baseband data through the Presence2D application with custom parameter tuning. This way you can record raw data of the use cases you want to test, then tune the application parameters until you have the performance you want. The parameters can then be deployed in the [Presence2D](../Presence2D/Presence2D_Readme.md) demo for deployment in a prototype product setup.

**NOTE** This demo uses the RadarDirect radar application, so make sure that the `BA22FirmwarePath` parameter points to the RadarDirect FW as opposed to the Presence2D demo which uses the ULPP_Presence2D FW.

For a description of the application output please refer to the description in the Presence2D demo [here](../Presence2D/Presence2D_Readme.md#description-of-the-x7-ulpp-presence2d-demo).

### Running the demo

To run the demo you first need to set up the necessary parameters in a preset file. You can find examples of them in the `Presets` folder. A convenient way to work is to make a copy of the preset you want to base your application on, then update it with the relevant local paths and custom parameter changes. When you have your desired preset, you can run:

```
python <path-to-runX7ULPP_Presence2DOnHostPlot.py> <path-to-preset_file.json>
```

### Configuration

For a description of the available configuration parameters, please refer to the descriptions in the Presence2D demo [here](../Presence2D/Presence2D_Readme.md#configuration).
