#!/usr/bin/env python3
from SlipOscBridgeFunctions import *
import PySimpleGUI as sg
# 2021-04-05 Ruud Mulder
# Gui for bridging Slip to OSC
#
def popupError(s):
    sg.popup_error(s, font=myfont)

myfont = 'Any 12'
spStrings   = []
spPortnames = []
# set serial portnames and 'port - desc' for Combo
def setSerialPortnames():
    global spStrings, spPortnames
    spStrings   = []
    spPortnames = []
    for n, (portname, desc, hwid) in enumerate(sorted(serial.tools.list_ports.comports())):
        spStrings.append(u'{} - {}'.format(portname, desc))
        spPortnames.append(portname)

bdValues = []
def setBaudrates():
    global bdValues
    bdValues = serial.Serial.BAUDRATES

setSerialPortnames()
setBaudrates()
# make components for Gui
scbString = 'ScanPorts'
stbString = 'Start'
exbString = 'Exit'
wb = len(max([scbString, stbString, exbString],key=len)) # length of longest button string.
spText  = 'Serial port' # text of labels
bdText  = 'baudrate'
o2sText = 'OSC to Serial port'
oscText = 'Serial to OSC IP address'
s2oText = 'Serial to OSC port'
lb = len(max([spText,bdText,o2sText,oscText,s2oText],key=len)) # length of longest label.
csize = (32,1) # can be resized
bsize = (wb,1)
tsize = (lb,1)
spSettings  = 'SerialPortName' # names for UserSettings
bdSettings  = 'Baudrate'
o2sSettings = 'Osc2SerialPort'
oscSettings = 'OscIPaddress'
s2oSettings = 'Serial2OscPort'
msgServerStopped = 'Server stopped'
o2sKey   = '-O2S-'
s2oKey   = '-S2O-'
spDef    = sg.UserSettings().get(spSettings,'')
spCombo  = sg.Combo(spStrings,  size=csize, default_value=spDef)
bdCombo  = sg.Combo(bdValues,   size=csize, default_value=sg.UserSettings().get(bdSettings,''))
o2sInput = sg.Input(default_text=sg.UserSettings().get(o2sSettings,''), size=csize, change_submits=True, key=o2sKey)
oscInput = sg.Input(default_text=sg.UserSettings().get(oscSettings,''), size=csize)
s2oInput = sg.Input(default_text=sg.UserSettings().get(s2oSettings,''), size=csize, change_submits=True, key=s2oKey)
msgArea  = sg.Multiline(default_text=msgServerStopped, size=(32,1), no_scrollbar=True, background_color='lightgrey')
scKey = '-SCAN-'
stKey = '-START-'
exKey = '-EXIT-'
scButton = sg.Button(scbString, size=bsize, key=scKey, tooltip='Scan for Serial ports')
stButton = sg.Button(stbString, size=bsize, key=stKey, tooltip='Start/stop the Slip-OSC bridging')
exButton = sg.Button(exbString, size=bsize, key=exKey)
# scan serial ports and try to set the one already selected
def scanports():
    setSerialPortnames()
    sel = spCombo.get()
    spCombo.Update(values=spStrings, value=sel, size=(None, len(spStrings))) # set size to show all values

layout = [[sg.Text(spText,  size=tsize), sg.Text(':'), spCombo],
          [sg.Text(bdText,  size=tsize), sg.Text(':'), bdCombo],
          [sg.Text(o2sText, size=tsize), sg.Text(':'), o2sInput],
          [sg.Text(oscText, size=tsize), sg.Text(':'), oscInput],
          [sg.Text(s2oText, size=tsize), sg.Text(':'), s2oInput],
          [scButton, stButton, exButton],
          [msgArea]
         ]
enabled = False
window  = sg.Window('Slip-OSC bridge', layout, resizable=True, font=myfont)
window.finalize()
# Only expand in x, do not enlarge distance between rows
for a in [spCombo, bdCombo, o2sInput, oscInput, s2oInput]:
    a.expand(expand_x=True, expand_y=False, expand_row=False)

def guiStopSerialOscServer():
    msgArea.update(value = 'Server stopping')
    stopSerialOscServer()
    msgArea.update(value = msgServerStopped)

def SetGuiDisabledState(state = True): # disable/enable Gui elements on server start/stop
    for elem in [scButton, spCombo, bdCombo, o2sInput, oscInput, s2oInput]:
        elem.update(disabled = state)
    if state: # experimenting got me these colors; not sure if they work with other themes
        c = sg.theme_element_background_color()
    else:
        c = sg.theme_input_text_color()
    #print(str(state)+' '+str(c))
    for elem in [o2sInput, oscInput, s2oInput]:
        elem.update(text_color = c)

msgArea.update(disabled=True)
msgArea.expand(expand_x=True, expand_y=True, expand_row=False)
# Main event loop
while True:
    event, values = window.read()
    if event == sg.WIN_CLOSED or event == exKey:
        if bridgeActive:
            stopSerialOscServer()
        break
    elif event == o2sKey: # only allow numbers for osc ports
        o2sInput.Update(re.sub("[^0-9]", "", values[event]))
    elif event == s2oKey:
        s2oInput.Update(re.sub("[^0-9]", "", values[event]))
    elif event == scKey:
        scanports()
    elif event == stKey:
        if enabled:
            stButton.update(text='Start')
            enabled = False
            SetGuiDisabledState(state = False)
            guiStopSerialOscServer()
        else:
            try:
                # check if all values are chosen correctly (oscInput may be ''=localhost)
                try:
                    spi  = spStrings.index(spCombo.get())
                except ValueError:
                    raise ValueError('No valid Serial port selected')
                try:
                    bdi  = bdValues.index(bdCombo.get())
                except ValueError:
                    raise ValueError('No valid baudrate selected')
                o2sNum = 0
                try:
                    o2sNum = int(o2sInput.get())
                except ValueError:
                    raise ValueError('Must specify valid number for OSC to Serial port')
                s2oNum = 0
                try:
                    s2oNum = int(s2oInput.get())
                except ValueError:
                    raise ValueError('Must specify valid number for OSC to Serial port')
                # all values chosen, now start server
                msgArea.update(value = 'Server active')
                ok = startSerialOscServer(spPortnames[spi], bdValues[bdi], o2sNum, oscInput.get(), s2oNum)
                if ok:
                    stButton.update(text='Stop')
                    enabled = True
                    SetGuiDisabledState(state = True)
            except Exception as e:
                popupError(str(e)) # startSerialOscServer exceptions are also catched here

# Save selected values for next time
sg.user_settings_set_entry(spSettings,  spCombo.get())
sg.user_settings_set_entry(bdSettings,  bdCombo.get())
sg.user_settings_set_entry(o2sSettings, o2sInput.get())
sg.user_settings_set_entry(oscSettings, oscInput.get())
sg.user_settings_set_entry(s2oSettings, s2oInput.get())
window.close()
