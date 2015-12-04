import numpy as np
import time
from socket import *
import cPickle as pickle
import Adafruit_BBIO.UART as UART
import beaglebone_pru_adc as adc
import serial
from multiprocessing import Process, Queue
#from timeout import timeout

# Set up zooming coefficient
#offset = 5*9.1/(9.1+47)
#v_conv = 1.8/4096
#voltage_zoom = 56150/float(150)
#current_zoom = 100/0.033/28

#print "offset", offset
#print "voltage_zoom", voltage_zoom
#print "current_zoom", current_zoom

# Set the socket parameters
host = '104.194.113.209'
#host = '104.194.113.208'
host_qb = '10.221.33.195'
port = 9999



#the number of sample UI
num_ui = 1000


def readUI(q):
	capture = adc.Capture()
	capture.cap_delay = 10000
	capture.start()
	while(1):
		data = np.empty([num_ui+1,2])
		data[num_ui,0] = time.time()
		for i in range(num_ui):
			data[i] = capture.values[:2]
			#print capture.timer
			time.sleep(0.00002)
		data[num_ui,1]=time.time()
		print data[num_ui,1]- data[num_ui,0]
		q.put(data)

def send(q,s,addr):
	while 1:
		start0 = time.time()
		data = q.get(True)
		s.sendto(pickle.dumps(data),addr)
		#s.send(pickle.dumps(data, protocol = -1))
		#s.settimeout(0.2)
		#print(data)
		#time.sleep(0.18)
		print("send data consume:", time.time()-start0)
		

def readEMI(q):
	UART.setup("UART1")
	ser = serial.Serial(port = "/dev/ttyO1", baudrate=460800, timeout = 1)
	ser.close()
	ser.open()
	if ser.isOpen():
		while(1):
			ser.write('1')
			#data = ser.read(4096)
			data = ser.read(4096)
			if len(data) == 4096:
				data = 20*np.log10(1000*np.fromstring(data, dtype = np.float32)/2048)
				q.put(data)
				print("emi 2 pipe")
			#print data.shape[0]
			#print "finish writing"
			#send2Server_emi(ser.read(4096))
			#print("send EMI consume:", time.time()-start)

def readUI_u(q):
	UART.setup("UART4")
	ser = serial.Serial(port = "/dev/ttyO4", baudrate=460800, timeout = 1)
	ser.close()
	ser.open()
	iter = 0
	data_s = []
	if ser.isOpen():
		while(1):
			iter = iter+1
			ser.write('1')
			data = ser.read(276)
			if len(data) == 276:
				data = np.fromstring(data, dtype = np.float32)
				data_s.append(data)
			#print(len(data))
			#print(data)
				if iter == 4:
					q.put(data_s)
					data_s = []
					iter = 0
					print("ui 2 pipe")
			#print data.shape[0]
			#print "finish writing"
			#send2Server_emi(ser.read(4096))
			#print("send EMI consume:", time.time()-start)


def testSoc(s,addr):
	while(1):
		if(s.sendto(pickle.dumps(np.random.random(10)),addr)):
			print "sending data"
		time.sleep(1)

if __name__ == '__main__':
	# Create socket
	s = socket(AF_INET,SOCK_DGRAM)
	addr = (host, port)
	#s = socket(AF_INET, SOCK_STREAM)
	#s.connect((host, port))
	#Process(target = testSoc, args = (s, addr,)).start()
	q = Queue()
	Process(target = readUI_u, args = (q,)).start()
	Process(target = readEMI, args = (q,)).start()
	Process(target = send, args = (q,s,addr,)).start()