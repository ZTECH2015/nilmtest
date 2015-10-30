import Adafruit_BBIO.ADC as ADC
import numpy as np
import time
from socket import *
import pickle
from Adafruit_BBIO.SPI import SPI
import Adafruit_BBIO.GPIO as GPIO

# Set up zooming coefficient
offset = 5*4.7*2/51.7
voltage_zoom = 56150/float(150)
current_zoom = 100/0.033
resist = float(28)

#print "offset", offset
#print "voltage_zoom", voltage_zoom
#print "current_zoom", current_zoom

# Set the socket parameters
host = '104.194.113.209'
port = 9999
buf = 10**4
addr = (host,port)

# Create socket
UDPSock = socket(AF_INET,SOCK_DGRAM)

# Send messages
def send2Server(data):
    if(UDPSock.sendto(pickle.dumps(data),addr)):
        print "Sending message"
        # Close socket
		#UDPSock.close()


def readUI():
	voltage = (ADC.read("P9_40")*1.8 - offset) * voltage_zoom
	#voltage = ADC.read("P9_40")
	current = (ADC.read("P9_39")*1.8 - offset) * current_zoom/resist
	#current = ADC.read("P9_39")
	return np.append(voltage, current)

def readUIc(num):
	count = 0
	data = [readUI()]
	while count<num:
		data = np.concatenate((data,[readUI()]),axis=0)
		count = count + 1
	return data

if __name__ == "__main__":
	print ("starting to read Voltage and Current")
	start = time.time()
	ADC.setup()
	a = readUIc(1024)
	print time.time()-start
	send2Server(a)
	print a
