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
	testData = []
	while 1:
		data = q.get(True)
		testData.append(data)
		print(data)
		if len(testData) > 30:
			output = open('testData.pkl', 'wb')
			pickle.dump(testData, output)
			output.close
			testData = []
			print('write to the file done!!!!!')


if __name__ == "__main__":
	q = Queue()
	Process(target = recv, args = (q,)).start()
	Process(target = save, args = (q,)).start()