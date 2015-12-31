
import numpy as np
import time, os
from socket import *
import cPickle as pickle
import Adafruit_BBIO.UART as UART
import beaglebone_pru_adc as adc
import serial
from multiprocessing import Process, Queue
from select import select

UART.setup("UART4")
ser = serial.Serial(port = "/dev/ttyO4", baudrate=460800, timeout = 1)
ser.close()
ser.open()
data_s = []
if ser.isOpen():
	while(1):
		ser.write('1')
		data = ser.read(276)
		if len(data) == 276:
			data = np.fromstring(data, dtype = np.float32)
		else:
			print("fail to get u......i........")
		print data
		#print "finish writing"
		#send2Server_emi(ser.read(4096))
		#print("send EMI consume:", time.time()-start)