import numpy as np
import time
from socket import *
import cPickle as pickle
import Adafruit_BBIO.UART as UART
import beaglebone_pru_adc as adc
import serial
from multiprocessing import Process, Queue
from timeout import timeout

# Set up zooming coefficient
offset = 5*9.1/(9.1+47)
v_conv = 1.8/4096
voltage_zoom = 56150/float(150)
current_zoom = 100/0.033/28

#print "offset", offset
#print "voltage_zoom", voltage_zoom
#print "current_zoom", current_zoom

# Set the socket parameters
host = '104.194.113.209'
host_qb = '10.221.33.195'
port = 9999



#the number of sample UI
num_ui = 1000


def readUI(q):
	capture = adc.Capture()
	capture.start()
	while(1):
		data = np.empty([num_ui+1,2])
		data[num_ui,0] = time.time()
		for i in range(num_ui):
			data[i] = capture.values[:2]
			time.sleep(0.00001)
		print data
		#data[:,0] = (data[:,0]*v_conv-offset) * voltage_zoom
		#data[:,1] = (data[:,1]*v_conv-offset) * current_zoom/resist
		#print type(data)
		data[num_ui,1]=time.time()
		#print data
		q.put(data)
		#print data
		#print(time.time() - start)
def send(q,s,addr):
	while 1:
		start0 = time.time()
		# start = data[num_ui,0]
		# end = data[num_ui,1]
		# u_data = (data[:num_ui,0].reshape(-1,div_ui).mean(axis = 1)*v_conv-offset) * voltage_zoom
		# i_data = (data[:num_ui,1].reshape(-1,div_ui).mean(axis = 1)*v_conv-offset) * current_zoom
		# data = np.vstack((np.vstack((u_data, i_data)).transpose(),[start,end]))
		#print data
		s.sendto(pickle.dumps(q.get(True)),addr)
		print("send data consume:", time.time()-start0)

def readEMI(q):
	UART.setup("UART1")
	ser = serial.Serial(port = "/dev/ttyO1", baudrate=460800, timeout = 1)
	ser.close()
	ser.open()
	if ser.isOpen():
		while(1):
			#print "writing uart"
			#start = time.time()
			ser.write('1')
			#q.put(ser.read(4096))
			q.put(np.fromstring(ser.read(4096), dtype = np.float32))
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
	Process(target = readUI, args = (q,)).start()
	#Process(target = readEMI, args = (q,)).start()
	Process(target = send, args = (q,s,addr,)).start()