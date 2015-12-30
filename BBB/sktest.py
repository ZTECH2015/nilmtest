import socket
import cPickle as pickle
import numpy as np

host = "127.0.0.1"
port_ui = 9999
port_emi = 8000

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((host, port_emi))
s.listen(10)
conn, addr = s.accept()
while 1:
	data = conn.recv(2**16)
	try:
		data_test = pickle.loads(data, encoding = "bytes")
		print(len(data))
	except:
		print("error")