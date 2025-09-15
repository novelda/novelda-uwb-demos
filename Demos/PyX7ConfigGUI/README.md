# PyX7Configuration GUI tool

## Documentation for pyx7configuration ##

The underlying pyx7configuration python package is documented [here](https://dev.novelda.com/X7/_examples/x7_fundamentals/pyx7configuration_0.6)

## Usage

This tool imports the python module pyx7configuration and provides a GUI for it. The only requirement, besides pyx7configuration, is PySide6, so if you have installed the requirements.txt file from Demos/requirements.txt then you're good to go. Also make sure that pyx7configuration was installed as 
described in:

```
<path/to/sdk>/pyx7configuration/Docs/README.md
```

If you are also using the novelda uwb demos it might be smart to install it in
 the same virtual environment you use for those. If you are not using virtual environment 
you can disregard this message.


To run it, simply do
```
python Demos/PyX7ConfigGUI/PyX7ConfigGUI.py
```


## Presets ##
There is a 'Presets' folder in the same directory with json files that can be used to populate all the fields. You may create and save new ones.

## Generate X7ChipConfiguration
By pressing the button "Calculate Chip Config" the generated X7ChipConfiguration 
will be displayed in the dialog box.  

You can export that to a custom json file by clicking the button "Export Chip Config".

## Pulse Period and FPS ##
As mentioned in the documentation for the pyx7configuration it is important 
to select a good combination of pulse period and fps. The requirement is:

```
pulse_period >= mframes_per_pulse
```

If you want to use a pulse_period>mframes_per_pulse, you can find good fps candidates 
by inputting a value for pulse_period in the upper right corner and click the 
button "Find FPS". A list of good fps candidates for that pulse_period will be 
shown in the dialog box below.