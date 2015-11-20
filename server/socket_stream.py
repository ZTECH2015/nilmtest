import socket
from multiprocessing import Process

HOST = '104.194.113.209'
#PORT = 9999

def recv(PORT):
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s.bind((HOST, PORT))
	s.listen(1)
	conn, addr = s.accept()
	print 'Connected by', addr
	while 1:
	    data = conn.recv(4096)

recv_ui = Process(target = recv, args = ((9999),))
recv_ui.start()
recv_emi = Process(target = recv, args = ((8000),))
recv_emi.start()
#conn.close()