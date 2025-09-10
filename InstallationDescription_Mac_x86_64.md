## Mac Installation instructions for the Novelda X7 Python Demos ##

Here are the steps for setting up and running the demos for Intel-based Macs.

**NOTE** The demos are only designed to work with python 3.10. 

__PySignalFlow__ is a python module that allows the user to configure and receive data from __Novelda__ signalprocessing algorithms from python. We need to tell python where to import it from. We will do this by adding the path to __PYTHONPATH__.


1. Remove Mac security quarantine on SDK
2. Set up __PATH__  and __PYTHONPATH__ for __PySignalFlow__ and the necessary libraries
3. Install python demo dependencies

### Remove MAC OSX security quarantine on SDK
When downloading the SDK, the OSX will automatically enforce quarantine extended 
file attributes on the whole SDK. To remove it you need to do:

``` 
> xattr -rc <path-to-sdk>
```


### Setting up PATH and PYTHONPATH ###
There are several ways to do this. One way is to add the following to your .bashrc/.zshrc file in your <home> directory.

``` 
export PYTHONPATH=<path-to-sdk>/lib:$PYTHONPATH
export PYTHONPATH=<path-to-novelda-uwb-demos-repo>/Nodes/Python/Novelda:$PYTHONPATH
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


### Installation of python dependencies ###
There is a __requirements.txt__ file in the 'Demos' folder which contains a list of all necessary dependencies.

Create a virtual environment with either: (you may name the virtual environment whatever you like)
```
python -m venv .demos
source ./.demos/bin/activate
```

or
```
> conda create x7demos
> conda activate x7demos
```

then do:
```
> pip install -r requirements.txt
```

#### Pip install error with requirements.txt ####
We have experienced issues when doing pip install step on the requirements.txt. Specfically it fails
on the **PyOpenGL-accelerate** package.
What did work for us if you find yourself in the same predicament, is to manually pip install every package in the 
**requirements.txt**. There is also a suggestion found on the internet to install **numpy** before the 
**PyOpenGL-accelerate** package.


That's it! You are now ready for having fun with your X7F202 radar module.