# Server program

from socket import *
import pickle
import numpy as np
from multiprocessing import Process, Queue

def recv(q):
	# Set the socket parameters
	#host = '104.194.113.209'
	host = '104.194.113.208'
	port = 9999
	buf = 2**16
	addr = (host,port)

	# Create socket and bind to address
	s = socket(AF_INET,SOCK_DGRAM)
	s.bind(addr)
	#s.listen(1)
	#conn, addr = s.accept()
	#print('Connected by', addr)
	# Receive message
	while 1:
	    data,addr = s.recvfrom(buf)
	    if data:
		    L = pickle.loads(data, encoding="bytes")
		    q.put(L)
		    #print(repr(L))
		# data = conn.recv(buf)
		# print(len(data), type(data))
		#L = pickle.loads(data, encoding="bytes")
	# Close socket
	s.close()

def save(q):
	offset = 5*9.1/(9.1+47)
	v_conv = 1.8/4096
	tol_voltage = 0.057
	tol_current = 0.057
	voltage_zoom = 510/20*(110/8.88)
	current_zoom = 100/0.05/18
	testData = []
	while 1:
		data = q.get(True)
		if type(data) is bytes:
			data = 20*np.log(1000*np.fromstring(data,dtype = np.float32))
			testData.append(data)
		else:
			data[:-1,0] = (data[:-1,0]*v_conv-offset-tol_voltage)*voltage_zoom
			data[:-1,1] = (data[:-1,1]*v_conv-offset-tol_current)*current_zoom
			testData.append(data)
		print(testData)
		if len(testData) > 200:
			output = open('testData.pkl', 'wb')
			pickle.dump(testData, output)
			output.close
			testData = []
			print('write to the file done!!!!!')


if __name__ == "__main__":
	q = Queue()
	Process(target = recv, args = (q,)).start()
	Process(target = save, args = (q,)).start()