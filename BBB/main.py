import numpy as np
import time
from socket import *
import cPickle as pickle
import Adafruit_BBIO.UART as UART
import beaglebone_pru_adc as adc
import serial
from multiprocessing import Process, Pipe
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
port_ui = 9999
port_emi = 8000
buf = 10**4
addr_ui = (host_qb,port_ui)
addr_emi = (host_qb,port_emi)

# Create socket
#UDPSock = socket(AF_INET,SOCK_DGRAM)

s_ui = socket(socket.AF_INET, socket.SOCK_STREAM)
s_ui.connect((host, port_ui))
s_emi = socket(socket.AF_INET, socket.SOCK_STREAM)
s_emi.connect((host, port_emi))
#the number of sample UI
div_ui = 3
num_ui = 400*div_ui

# Send messages
def send2Server_ui(data):
	s_ui.send(pickle.dumps(data))

def send2Server_emi(data):
    s_emi.send(pickle.dumps(data))

def readUI(UI_in):
	capture = adc.Capture()
	capture.start()
	while(1):
		data = np.empty([num_ui+2,1])
		data[num_ui,0] = time.time()
		for i in range(num_ui):
			data[i] = capture.values[:1]
			time.sleep(0.00004)
		#print data, offset, voltage_zoom, data[:,0]
		#data[:,0] = (data[:,0]*v_conv-offset) * voltage_zoom
		#data[:,1] = (data[:,1]*v_conv-offset) * current_zoom/resist
		#print type(data)
		data[num_ui+1,0]=time.time())
		#print data
		UI_in.send(data)
		#print data
		#print(time.time() - start)
def sendUI(UIpipe):
	UI_out, UI_in = UIpipe
	UI_in.close()
	while 1:
		start0 = time.time()
		# start = data[num_ui,0]
		# end = data[num_ui,1]
		# u_data = (data[:num_ui,0].reshape(-1,div_ui).mean(axis = 1)*v_conv-offset) * voltage_zoom
		# i_data = (data[:num_ui,1].reshape(-1,div_ui).mean(axis = 1)*v_conv-offset) * current_zoom
		# data = np.vstack((np.vstack((u_data, i_data)).transpose(),[start,end]))
		#print data
		send2Server_ui(UI_out.recv())
		print("send UI consume:", time.time()-start0)

def read_sendEMI():
	UART.setup("UART1")
	ser = serial.Serial(port = "/dev/ttyO1", baudrate=460800)
	ser.close()
	ser.open()
	if ser.isOpen():
		while(1):
			#print "writing uart"
			start = time.time()

			@timeout(2)
			readUart(ser)
			#ser.write('1')
			#print "finish writing"
			#send2Server_emi(ser.read(4096))
			print("send EMI consume:", time.time()-start)

def readUart(ser):
	ser.write('1')
	send2Server_emi(ser.read(4096))

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

UI_out, UI_in = Pipe()
p_sendui = Process(target = sendUI, args = ((UI_out, UI_in),))
p_sendui.start()
p_readui = Process(target = readUI, args = (UI_in,))
p_readui.start()

#EMI_out, EMI_in = Pipe()
read_sendEMI = Process(target = read_sendEMI)
read_sendEMI.start()
#p_reademi = Process(target = readEMI, args = (EMI_in,))
#p_reademi.start()