import Adafruit_BBIO.UART as UART
import serial
import numpy as np
import struct

UART.setup("UART1")
 
ser = serial.Serial(port = "/dev/ttyO1", baudrate=460800)
ser.close()
ser.open()
count = 0
while(1):
	if ser.isOpen():
		data = ser.read(4096)
	data = np.fromstring(data, dtype = np.float32)
#	print 'the lenght of data is', len(data)
#	print ' '.join(format(ord(x), 'b') for x in data)
#	print data
#	data = struct.unpack('ff',data[:8])
#	print data
	count = count + 1
	print count
#print ' '.join(format(ord(x), 'b') for x in data)
#print data.decode('utf-8')
