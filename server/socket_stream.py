import socket
from multiprocessing import Process



def recv():
	HOST = '104.194.113.209'
	PORT = 9999
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s.bind((HOST, PORT))
	s.listen(1)
	conn, addr = s.accept()
	print 'Connected by', addr
	while 1:
	    print(pickle.loads(conn.recv(2**16)))


if __name__ == '__main__':
	recv = Process(target = recv)
	recv.start()
	#conn.close()