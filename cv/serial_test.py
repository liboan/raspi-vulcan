import serial
import random

portName = "/dev/ttyACM0"

port = serial.Serial(portName, 9600)
port.flushInput()

while True:
    port.write(chr(89))
