# novelda-uwb-demos

Welcome to a repo dedicated to demos showcasing the capabilities of the Novelda X7 UWB chip.


If you want to use, modify and share the demos go ahead and clone the repo to 
your machine.

This repo uses [Git LFS](https://git-lfs.com/) for binary and image files. You must first install Git LFS and then set it up with
 ```
 git lfs install
 ```
If you have already cloned the repository before installing and setting up Git LFS, do
 ```
 git lfs install
 git lfs pull
 ```

 Our aim is to keep adding new demo contents to this site so stay updated.

In order to use the demos you will need to download the SDK for the Novelda UWB module. This can be
downloaded at [dev.novelda.com](https://novelda.com/developer). For X7 locate the button with the caption
"X7 documentation and software". You will need a valid login to access it. Anyone is free to
register, just note that for now unfortunately we can only provide access to a select list of customers.
This is due to a limited stock of X7 devkits but we are working hard for this to change.

So let us go ahead and get those demos up and running.

## Installation ##

Currently the demos are supported on the following OS'es:

 OS                    | Since SDK version | Status |
|-----------------------|---------|--------|
| Windows 64-bit x86_64 | 0.6     | Coming |
| Linux 64-bit x86_64   | 0.6     | Coming |
| Mac osx 64-bit x86_64 | N/A     | Coming |
| Mac osx 64-bit arm64  | N/A     | Coming |

Click the link for the installation description on [Windows](./InstallationDescription_Windows.md) 
or [Linux](./InstallationDescription_Linux.md) necessary to run the demos. 

## X7 Demos ##

The demos can be used starting with the official 0.6 SDK release. 

Here is the list of demos currently supported with python 3.10:

| Demo               | Description                                         | Status |
|--------------------|-----------------------------------------------------|--------|
| X7RangeDopplerRaw  | RangeDoppler visualization of the Tx/Rx rawchannels | Coming |
| X7BasebandRecorder | Baseband recorder for the X7-devkit                 | Coming |
| X7BasebandPlotter  | Live/Playback plotting of x7 baseband data          | Coming |
| ULPP_Presence1D    | Live/Playback plotting of x7 presence1d data        | Coming |
| ULPP_Presence2D    | Live/Playback plotting of x7 presence2d data        | Coming |

