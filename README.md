# Pi Remote

A gRPC-based keyboard & mouse gadget
for [remotecontrol-app](https://github.com/falleng0d/remotecontrol-app) on Pi Zero W

## Features

Basically this allows you to use a tablet or phone of your choice that has 
[remotecontrol-app](https://github.com/falleng0d/remotecontrol-app) installed to 
control another device (.e.g. a PC) as if the inputs are coming from a real 
keyboard and mouse. 

This is possible because the app sends the inputs to the **Rapsberry Pi Zero W**
, which then forwards them to the target device via an usb connection.
