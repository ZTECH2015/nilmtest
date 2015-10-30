from socket import *
import cpickle as pickle
import time
import numpy as np

# Set the socket parameters
host = '104.194.113.209'
port = 9999
buf = 10**4
addr = (host,port)

# Create socket
UDPSock = socket(AF_INET,SOCK_DGRAM)

def_msg = "===Enter message to send to server===";
print ("\n",def_msg)
#a = array('i',[1,3,2])
# Send messages
while 1:
    if(UDPSock.sendto(pickle.dumps(np.random.random(2**10)),addr)):
        print ("Sending message")
    time.sleep(1)

# Close socket
UDPSock.close()