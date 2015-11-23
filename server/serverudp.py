# Server program

from socket import *
import pickle
import numpy as np
from multiprocessing import Process, Queue

def recv(q):
	# Set the socket parameters
	host = '104.194.113.209'
	port = 9999
	buf = 2**16
	addr = (host,port)

	# Create socket and bind to address
	UDPSock = socket(AF_INET,SOCK_DGRAM)
	UDPSock.bind(addr)

	# Receive messages
	for i in range(1000):
	    data,addr = UDPSock.recvfrom(buf)
	    if data:
		    L = pickle.loads(data, encoding="bytes")
		    #print(repr(L))
		    q.put(L)
	# Close socket
	UDPSock.close()

def save(q):
	offset = 5*9.1/(9.1+47)
	v_conv = 1.8/4096
	voltage_zoom = 510/20*(120/9)
	current_zoom = 100/0.05/18
	testData = []
	for i in range(1000):
		data = q.get(True)
		if np.shape(data)[0] == 1024:
			testData.append(data)
		else:
			data[:-1,0] = (data*v_conv-offset)*voltage_zoom
			data[:-1,1] = (data*v_conv-offset)*current_zoom
			testData.append(data)
	output = open('testData.pkl', 'wb')
	pickle.dump(testData, output)
	output.close


if "__name__" == "__main__":
	q = Queue()
	Process(target = recv, args = (q,)).start()
	Process(target = save, args = (q,)).start()