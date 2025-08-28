## Installation instructions for the Novelda X7 Python Demos ##

In order to use the demos you need to download an SDK for your OS which can be downloaded from [dev.novelda.com](https://novelda.com/developer/). 
You will need to have a valid user login in order to be able to download. Currently we need to reserve the right to choose which 
customers will get access.

You will also need an X7F202-Devkit. 

Here are the steps for setting up and running the demos, in no specific order.

1. Set up __PATH__  and __PYTHONPATH__ for __PySignalFlow__ and the necessary libraries
2. Install python demo dependencies
3. (Linux) Set up __udev rules__ 

**NOTE** The demos are only designed to work with python 3.10. 

__PySignalFlow__ is a python module that allows the user to configure and receive data from __Novelda__ signalprocessing algorithms from python. We need to tell python where to import it from. We will do this by adding the path to __PYTHONPATH__.

### Windows ###

#### Setting up a virtual environment ####

If you don't care about installing python packages in your global environment this isn't necessary.
````
cd <DemoDirectory>
python -m venv .demos
.\.demos\Scripts\activate
````
This will create a new virtual environment in 'DemoDirectory' named '.demos' and activate it. To deactivate it, just run the command 'deactivate'.

#### Installing dependencies ####

Now you can run
````
pip install -r path/to/requirements.txt
````
The requirements.txt file will be in the demo directory.

#### Setting up PATH and PYTHONPATH ####

For the Windows SDK, __PySignalFlow__ and other libraries are in the SDK_Root/bin directory. Using powershell you can temporarily add them like so
````
$Env:PYTHONPATH += ";path/to/SDK_Root/bin"
$Env:PATH += ";path/to/SDK_Root/bin"
````

Or add them permanently in settings. Just search for "env" in Windows and it will show up as "Edit the system environment variables", then click "Environment Variables". There you can add new variables.

And that's it, now you should be able to run the demos.

### Linux ###

#### Setting up PATH and PYTHONPATH ####
There are several ways to do this. One way is to add the following to your .bashrc/.zshrc file in your <home> directory.

``` 
export PYTHONPATH=<path-to-sdk>/lib:$PYTHONPATH
export PATH=<path-to-sdk>/lib:$PATH
```

For the changes to take effect do:
``` 
> source .bashrc
```

#### Verification ####
Start python3.10 interpreter and you should be able to do:
``` 
>>> import PySignalFlow
```
If this works without errors you have successfully setup the necessary path to be able to run the demos.

#### Drivers ####
When running the X7F202 module from a host computer like Windows or Linux, you need to use the
FTDI interface board. This board contains a chip that allows a computer to send SPI transactions to the 
X7 chip over a USB connection.

No driver installation is necessary as they are part of the SDK. However in order to use the device you need to setup
__udev rules__ for the device.

In a terminal do:

``` 
> sudo nano /etc/udev/rules.d/99-x7f202.rules 
```

Add the following lines to the file:

``` 
# Novelda FTDI USB Serial Device
SUBSYSTEM=="usb",ATTRS{idVendor}=="0403",ATTRS{idProduct}=="601c",MODE="0777",GROUP="dialout",SYMLINK+="x7f202"
```

You now either need to reboot or do the following for the changes to take instant effect:

```
> sudo udevadm control --reload-rules
> sudo udevadm trigger
```

Plug in the x7f202 module to a usb port and you should see it with:

```
> ls -lh /dev
```

If everything worked it should show up as __x7f202__.

**NOTE** If you have tried to use the Novelda HPD studio on Linux and not gotten it to work without using __sudo__, this will
eliminate the need for that.

#### Installation of python dependencies ####
There is a __requirements.txt__ file in this folder which contains a list of all necessary dependencies.

Create a virtual environment with either:
```
python -m venv .demos
source ./.demos/bin/activate
```

or
```
> conda create x7demos
```

then do:
```
> pip install -m requirements.txt
```

That's it! You are now ready for having fun with your X7F202 radar module.