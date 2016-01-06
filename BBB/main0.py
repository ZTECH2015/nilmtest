import numpy as np
import time, os
from socket import *
import cPickle as pickle
import Adafruit_BBIO.UART as UART
import beaglebone_pru_adc as adc
import serial
from multiprocessing import Process, Queue
from select import select
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
host_test = "127.0.0.1"
host_iitserver = '104.194.126.108'
host = '104.194.124.231'
host_qb = '10.221.33.195'
port = 9999
#port_emi = 8000



#the number of sample UI
num_ui = 1000

def clean_data(data):
	voltage = []
	current = []
	p = []
	q = []
	h = []
	emi = []
	new_data = []
	len_uipq = 16
	for d in data[:-2]:
		voltage.extend(d[:len_uipq])
		current.extend(d[len_uipq:len_uipq*2])
		p.extend(d[len_uipq*2:len_uipq*3])
		q.extend(d[len_uipq*3:len_uipq*4])
		h.append(d[-5:])
	new_data.append(voltage)
	new_data.append(current)
	new_data.append(p)
	new_data.append(q)
	new_data.append(h)
	new_data.append(data[-2])
	new_data.append(data[-1])
	return new_data
		
def send(q,addr):
	try:
		s = socket(AF_INET, SOCK_STREAM)
		s.connect(addr)
		#counter = 0
		print "open socket"
		while 1:
			start0 = time.time()
			data = clean_data(q.get(True))
			if s.send(pickle.dumps(data, protocol = -1)):
			#if s.sendto(pickle.dumps(data),addr):
				#print('.')
				#counter = counter + 1
				#print("send data consume:", time.time()-start0, "counter is :", counter)
				time.sleep(0.2)
			else:
				print("send fail consume...................", time.time()-start0)
	except:
		pass
	try:
		s.close()
		print "close the socket"
	except:
		pass

def readEMI(q_emi):
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
				q_emi.put(1)
				q_emi.put(data)
				emi_ready = 1
			else:
				print("fail to get emi")
			#print data.shape[0]
			#print "finish writing"
			#send2Server_emi(ser.read(4096))
			#print("send EMI consume:", time.time()-start)

def readUI_u(q,q_emi):
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
				data_s.append(data)
				if len(data_s) == 4:
					while q_emi.get(True) != 1:
						time.sleep(0.1)
					data_s.append(q_emi.get(True))
					data_s.append(time.time())
					q.put(data_s)
					data_s = []
					#print("ui_emi 2 pipe")
			else:
				print("fail to get u......i........")
			#print data.shape[0]
			#print "finish writing"
			#send2Server_emi(ser.read(4096))
			#print("send EMI consume:", time.time()-start)

def socVerify(s):
	readable, writable, exceptional = select([s],[],[], 0)
	print writable
	if readable:
		return 1
	else:
		return 0
def testSoc(s,addr):
	while(1):
		if(s.sendto(pickle.dumps(np.random.random(10)),addr)):
			print "sending data"
		time.sleep(1)

if __name__ == '__main__':
	# Create socket
	#s = socket(AF_INET,SOCK_DGRAM)
	addr = (host, port)
	
	#s = socket(AF_INET, SOCK_STREAM)
	#Process(target = testSoc, args = (s, addr,)).start()
	
	

	while 1:
		while os.system("ping -c 1 " + host) == 0:
			print "connect the server fail"
			os.system("ifdown wlan0")
			time.sleep(10)
			os.system("ifup wlan0")
			
		q = Queue()
		q_emi = Queue()
		p_send = Process(target = send, args = (q, addr,))
		p_ui = Process(target = readUI_u, args = (q, q_emi,))
		p_emi = Process(target = readEMI, args = (q_emi,))
		p_send.start()
		p_ui.start()
		p_emi.start()
		print "connect successfully!!"
		
		p_send.join()

		print "fail to connect server socket! we will try again later!"

		p_ui.terminate()
		p_emi.terminate()
		time.sleep(120)
		
