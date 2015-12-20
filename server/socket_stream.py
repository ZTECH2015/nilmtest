import socket
from multiprocessing import Process, Queue
import numpy as np
import time, pickle
from save2Database import *


def recv(s, q, name, port):
	# Set the socket parameters
	conn, addr = s.accept()
	data_buf = bytes()
	#s.listen(1)
	#conn, addr = s.accept()
	#print('Connected by', addr)
	# Receive message
	ui_len = 8230
	while 1:
		start = time.time()
		#print(len(data))
		if len(data_buf) >= ui_len:
			q.put(data_buf[:ui_len])
			data_buf = data_buf[ui_len:]
			#print(len(data_buf))
			print("consume time:", time.time()-start, "in process :", name)
		else:
			data_buf = data_buf + conn.recv(2**16)
			#print("fail to get the data at :", time.time())
	# Close socket
	s.close()

def save(q):
	testData = []
	v = []
	c = []
	p = []
	q_ = []
	h = []
	emi = []
	while 1:
		try:
			data = q.get(True)
			data = pickle.loads(data, encoding="bytes")
			save_raw(cursor, data[0], data[1], data[2], data[3], data[4], data[5], data[6])
			testData.append(data)
			#print(data)
			print(len(testData))
		except KeyboardInterrupt:
			output = open('testData.pkl', 'wb')
			pickle.dump(testData, output)
			output.close
			print('write to the file done!!!!!')
			break

if __name__ == '__main__':
	q = Queue()
	host = '104.194.126.108'
	port = 9999

	# Create socket and bind to address
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s.bind((host, port))
	s.listen(10)
	Process(target = recv, args = (s, q, 1, port, )).start()
	Process(target = save, args = (q,)).start()