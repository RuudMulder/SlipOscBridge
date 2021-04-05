#!/usr/bin/env python3
from SlipOscBridgeFunctions import *
import argparse
import time
# 2021-04-05 Ruud Mulder
# Commandline server for bridging Slip to OSC
#
parser = argparse.ArgumentParser()
parser.add_argument('-s', '--serial',    required=True, help='Serial port')
parser.add_argument('-b', '--baudrate',  default=9600,  type=int, help='Baudrate (default=9600)')
parser.add_argument('-i', '--oscin',     required=True, type=int, help='OSC to Serial port number')
parser.add_argument('-a', '--ipaddress', default='',    help='IP address OSC output sends to (default=localhost)')
parser.add_argument('-o', '--oscout',    required=True, type=int, help='port number where OSC output is sent to')
n = vars(parser.parse_args())
try:
    startSerialOscServer(n['serial'], n['baudrate'], n['oscin'], n['ipaddress'], n['oscout'])
    print('Use ctrl-c to stop the server')
    while True:
        time.sleep(10)
except Exception as e:
    print(str(e), file=sys.stderr)
    stopSerialOscServer()
