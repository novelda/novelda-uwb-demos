## Windows Installation instructions for the Novelda X7 Python Demos ##

Here are the steps for setting up and running the demos, in no specific order.

1. Set up __PATH__  and __PYTHONPATH__ for __PySignalFlow__ and the necessary libraries
2. Install python demo dependencies

**NOTE** The demos are only designed to work with python 3.10. 

__PySignalFlow__ is a python module that allows the user to configure and receive data from __Novelda__ signalprocessing algorithms from python. We need to tell python where to import it from. We will do this by adding the path to __PYTHONPATH__.

### Setting up PATH and PYTHONPATH ###

For the Windows SDK, __PySignalFlow__ and other libraries are in the <Novelda_SDK_Root>/bin directory. Using powershell you can temporarily add them like so.

````
$Env:PYTHONPATH += ";<path-to-sdk>/bin"
$Env:PYTHONPATH += ";<path-to-novelda-uwb-demos-repo>/Nodes/Python/Novelda"
$Env:PATH += ";<path-to-sdk>/bin"
````

Or add them permanently in settings. Just search for "env" in Windows and it will show up as "Edit the system environment variables", then click "Environment Variables". There you can add new variables.

### Installation of python dependencies ###

If you don't care about installing python packages in your global environment this isn't necessary.
````
cd <DemoDirectory>
python -m venv .demos
.\.demos\Scripts\activate
````
This will create a new virtual environment in 'DemoDirectory' named '.demos' and activate it. To deactivate it, just run the command 'deactivate'.

Now you can run
````
pip install -r path/to/requirements.txt
````
The __requirements.txt__ file will be in the demo directory.

#### Verification ####
Start python3.10 interpreter and you should be able to do:
``` 
>>> import PySignalFlow
```
If this works without errors you have successfully setup the necessary path to be able to run the demos.

And that's it, now you should be able to run the demos.

