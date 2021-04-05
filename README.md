### SlipOSCBridge/SlipOSCBridgeServer

This is an application to make a bridge from Slip to UDP sockets. It is intended for OSC (Open Sound Control). There are two versions:
- SlipOSCBridge
  A Gui that is probably easier for an end-user than the command line version.
- SlipOSCBridgeServer
  A command line version.

It can be used for any UDP-Slip connection

A complete application for OS X can be downloaded from: [SerialMidiBridge.app.zip](https://mega.nz/file/k5skCQqL#Gu-krXfbGkKWxxRzex5TsaKGbu9fc9izKQyb72-ZagA).

It also works on Linux (at least on Lubuntu19). A complete application for Linux can be downloaded from:
[SlipOscBridge.zip](https://mega.nz/file/Ug9h1QTB#_gvN7DPf7y9jejG2K-4btN61jieIyUxwtCvAK9iOorQ)

Windows users will have to generate an application by themselves or start it from the command line as described below.

### Usage

After starting you will be able to choose the serial port, baudrate, ip address and port. The Scan button will re-scan for available serial ports. Your selection is remembered for next usage. After starting the server no changes can be made until the server is stopped.

### Starting from the command line

It can also be started in the Terminal after downloading the python script as follows:

```
python3 SlipOscBridge.py
```

This requires some python extra packages. You can install them as follows:

```
pip install pyserial pysimplegui
```

### Adapting/building

If you want to make changes or build your own application you can use pyinstaller:

```
pyinstaller --onefile --windowed SlipOscBridge.py
```

N.B. pyinstaller can be installed as follows:

```
pip install pyinstaller
```

You are free to modify it as long as it's not for commercial purposes.

### Notes

Due to the use of [PySimpleGui](https://pypi.org/project/PySimpleGUI/) there are some cosmetic 'features':

- There is extra space after all texts because the width in characters is set for a non-proportional font.
- When the previously used serial port is not available at startup its name might still be in the selection box.
