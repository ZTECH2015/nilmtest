import numpy as np
import time
from socket import *
import pickle
import Adafruit_BBIO.GPIO as GPIO
import beaglebone_pru_adc as adc

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

def read():
	capture = adc.Capture()
	capture.start()
	while(1):
		data = np.empty([5001,2])
		start = time.time()
		for i in range(5000):
			data[i] = capture.values[:2]
		data[:,0] = (data*1.8-offset) * voltage_zoom
		data[:,1] = (data*1.8-offset) * current_zoom/resist
		data[5001]=(start, time.time())
		print data

if __name__ == "__main__":
	read()
	send2Server(a)
	print a
