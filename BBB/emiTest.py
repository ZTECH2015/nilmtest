import numpy as np
import time, os
from socket import *
import cPickle as pickle
import Adafruit_BBIO.UART as UART
import beaglebone_pru_adc as adc
import serial
from multiprocessing import Process, Queue
from select import select

def readEMI():
	UART.setup("UART1")
	ser = serial.Serial(port = "/dev/ttyO1", baudrate=460800, timeout = 1)
	ser.close()
	ser.open()
	
	if ser.isOpen():
		while(1):
			ser.write('1')
			data = ser.read(4096)
			if len(data) == 4096:
				data = 20*np.log10(1000*np.fromstring(data, dtype = np.float32)/2048)
				print data
			else:
				print("fail to get emi")
			#print data.shape[0]
			#print "finish writing"
			#send2Server_emi(ser.read(4096))
			#print("send EMI consume:", time.time()-start)

if __name__ == '__main__':
	readEMI()