import queue
import socket
import serial
import serial.tools.list_ports
import threading
import sys
import struct
import re
# 2021-04-05 Ruud Mulder
# Functions for bridging Slip to OSC
#
bridgeActive = False # set to True when bridge is active
# communication between Serial and OSC part
osc2SerialQueue = queue.Queue()
serial2OscQueue = queue.Queue()
# global communication channels for Serial and OSC
serialPort   = None
oscAddress   = None # will be (ip,port)
oscInSocket  = None
oscOutSocket = None

def oscInHandler():
    global bridgeActive, oscInSocket, osc2SerialQueue
    oscInSocket.settimeout(2) # wait maximum of 2 seconds before checking bridgeActive
    while bridgeActive:
        try:
            message = oscInSocket.recvfrom(1024) # maximum message size
        except socket.timeout:
            continue
        # N.B. address of sender is lost, return messages are sent to oscAddress
        # here we have a message, or the server is stopped
        if bridgeActive:
            osc2SerialQueue.put(message[0]) # only message, address is lost
    try:
        oscInSocket.shutdown() # close osc input socket completely after stopping
        oscInSocket.close()
    except:
        pass # ignore close error

def oscOutHandler():
    global bridgeActive, oscAddress, oscOutSocket, serial2OscQueue
    while bridgeActive:
        try:
            message = serial2OscQueue.get(timeout = 2) # wait maximum of 2 seconds before checking bridgeActive
        except queue.Empty:
            continue
        try:
            oscOutSocket.sendto(message, oscAddress) # only reached on message received
        except Exception as err: # will probably never occur
            raise Exception("Error opening OSC to Serial port:\n"+str(err))
            continue

# Special Slip bytes for serial handlers
END     = b'\xc0'
ESC     = b'\xdb'
ESC_END = b'\xdc'
ESC_ESC = b'\xdd'
def serialInHandler():
    global bridgeActive, serial2OscQueue, serialPort
    message = b''
    data    = b''
    running_status = 0
    while bridgeActive:
        # add data, because a partial message may remain after a complete message
        data = serialPort.read()
        if len(data) > 0:
            # this seems the way to get the elements as bytes, not ints
            for elem in struct.unpack(str(len(data))+'c', data):
                if ((len(message) == 0) and (elem == END)) or (len(message) > 0):
                    message += elem # receiving message
                    data = data[1:] # remove processed element
                    if elem == END:
                        if len(message) == 2:
                            # empty message, so the first was the start of an incomplete one
                            message = END # start of possible new message
                        elif len(message) > 1: # skip message with only first END byte
                            # complete message received
                            # print('Serial in message:')
                            # print(message)
                            msg = message[1:len(message)-1]
                            # remove beginning and trailing END characters
                            if not (
                                msg.endswith(ESC)
                                or re.search(
                                    ESC + b'[^' + ESC_END + ESC_ESC + b']',
                                    msg)):
                                __Serial2OscQueue.put(
                                    msg.replace(ESC + ESC_END, END
                                               ).replace(ESC + ESC_ESC, ESC))
                            message = b''  # next message
    # close SerialPort after stopping
    del serialPort

def serialOutHandler():
    global bridgeActive, osc2SerialQueue, serialPort
    while bridgeActive:
        try:
            msg = osc2SerialQueue.get(timeout=0.4) # timeout to force checking bridgeActive
        except queue.Empty:
            continue
        if bridgeActive: # just to be safe, server may have been stopped and port deleted by serialInHandler
            msgout = END + msg.replace(ESC, ESC + ESC_ESC).replace(END, ESC + ESC_END) + END
            # print('Serial out message:')
            # print(msgout)
            serialPort.write(msgout)

oscInThread     = None
oscOutThread    = None
serialInThread  = None
serialOutThread = None
def startSerialOscServer(serial_port_name, serial_baud, portIn, ipOut, portOut):
    global serialPort, oscInSocket, oscAddress, oscOutSocket, bridgeActive
    global oscInThread, oscOutThread, serialInThread, serialOutThread
    ok = True
    bridgeActive = True
    try:
        serialPort  = serial.Serial(serial_port_name,serial_baud)
        # create sockets
        try:
            if portIn == portOut:
                raise ValueError('The two port numbers must be different')
            oscInSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            oscInSocket.bind(("", portIn)) # accept UDP dgrams from any sender on port
            oscOutSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            oscAddress   = (ipOut, portOut)  # portnumber or (hostname,port)
            # N.B. there is no test on validity of the sockets
        except Exception as err: # will probably never occur
            raise Exception("Error opening OSC to Serial port:\n"+str(err))
            ok = False
    except serial.serialutil.SerialException as err:
        raise Exception("Serial port opening error:\n"+str(err))
        ok = False

    if ok:
        serialPort.timeout = 0.4
        # The names do not need to be kept. Thread finishes stopSerialOscServer,
        # By default the program waits for threads to finish before exiting.
        oscInThread     = threading.Thread(target = oscInHandler)
        oscOutThread    = threading.Thread(target = oscOutHandler)
        serialInThread  = threading.Thread(target = serialInHandler)
        serialOutThread = threading.Thread(target = serialOutHandler)
        oscInThread.start()
        oscOutThread.start()
        serialInThread.start()
        serialOutThread.start()
    return ok

def stopSerialOscServer():
    global bridgeActive
    bridgeActive = False
    threadsStopped = False
    while threadsStopped:
        for t in [oscInThread, oscOutThread, SerialInThread, serialOutThread]:
            threadsStopped = True
            if t.is_alive():
                threadsStopped = False
