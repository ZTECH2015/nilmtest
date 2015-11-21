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
offset = 5*4.7*2/51.7
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
num_ui = 1200


def readUI(q):
	capture = adc.Capture()
	capture.start()
	while(1):
		data = np.empty([num_ui+1,2])
		data[num_ui,0] = time.time()
		for i in range(num_ui):
			data[i] = capture.values[:2]
			time.sleep(0.00002)
		#print data, offset, voltage_zoom, data[:,0]
		#data[:,0] = (data[:,0]*v_conv-offset) * voltage_zoom
		#data[:,1] = (data[:,1]*v_conv-offset) * current_zoom/resist
		#print type(data)
		data[num_ui,1]=time.time())
		#print data
		q.put(data)
		#print data
		#print(time.time() - start)
def send(q,s):
	while 1:
		start0 = time.time()
		# start = data[num_ui,0]
		# end = data[num_ui,1]
		# u_data = (data[:num_ui,0].reshape(-1,div_ui).mean(axis = 1)*v_conv-offset) * voltage_zoom
		# i_data = (data[:num_ui,1].reshape(-1,div_ui).mean(axis = 1)*v_conv-offset) * current_zoom
		# data = np.vstack((np.vstack((u_data, i_data)).transpose(),[start,end]))
		#print data
		s.send(pickle.dumps(q.get(True)))
		print("send UI consume:", time.time()-start0)

def readEMI(q):
	UART.setup("UART1")
	ser = serial.Serial(port = "/dev/ttyO1", baudrate=460800)
	ser.close()
	ser.open()
	if ser.isOpen():
		while(1):
			#print "writing uart"
			#start = time.time()
			readUart(ser)
			#ser.write('1')
			#print "finish writing"
			#send2Server_emi(ser.read(4096))
			#print("send EMI consume:", time.time()-start)

@timeout(1)
def readUart(ser):
	ser.write('1')
	#q.put(ser.read(4096))
	q.put(np.fromstring(ser.read(4096), dtype = np.float32))

def sendEMI(EMIpipe):
	EMI_out, EMI_in = EMIpipe
	EMI_in.close()
	while 1:
		start = time.time()
		data = EMI_out.recv()
		#data = np.fromstring(data, dtype = np.float32)
		#print data
		send2Server_emi(data)
		print("send EMI consume:", time.time()-start)

if __name__ = '__main__':
	# Create socket
	#UDPSock = socket(AF_INET,SOCK_DGRAM)
	s = socket(socket.AF_INET, socket.SOCK_STREAM)
	s.connect((host, port))
	q = Queue()
	Process(target = readUI, args = (q,)).start()
	Process(target = readEMI, args = (q,)).start()
	Process(target = send, args = (q,s,)).start()
	#EMI_out, EMI_in = Pipe()
	#read_sendEMI = Process(target = read_sendEMI)
	#read_sendEMI.start()
	#p_reademi = Process(target = readEMI, args = (EMI_in,))
	#p_reademi.start()