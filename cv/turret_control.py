import serial
import random

class TurretRotator(object):
    def __init__(self, portName = "/dev/ttyACM0", cap = 10, baud = 9600): #default port arg is for my raspi, default speed cap 10
        self.portName = portName
        self.cap = cap
        self.baud = baud
        print "Initializing Serial connection at " + self.portName
        self.port = serial.Serial(self.portName, self.baud)
        self.port.flushInput()
        

    def setRotation(self, spd): #set rotation speed, values capped
        spd = max(min(spd, self.cap), -1*self.cap)
        if (self.port != None):
            self.port.write(chr(222)) #signal byte for Arduino, indicating a command byte is following
            self.port.write(chr(spd + 90)) #Arduino takes a value ranging from 0 to 180, 90 is stopped
            #self.port.write(chr(spd + 90)) #write multiple times to fill up buffer...so arduino doesn't read 255 lol
            #self.port.write(chr(spd + 90))
