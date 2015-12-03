import beaglebone_pru_adc as adc
import time
from multiprocessing import Process

 # how many samples to capture


def ain(n):
	numsamples = 65536
	capture = adc.Capture()
	capture.cap_delay=100
	capture.oscilloscope_init(adc.OFF_VALUES+n, numsamples) # captures AIN0 - the first elt in AIN array
	#capture.oscilloscope_init(adc.OFF_VALUES+4, numsamples) # captures AIN1 - the third elt in AIN array
	capture.start()

	start = time.time()
	for _ in range(10):
    		if capture.oscilloscope_is_complete():
        		break
    		print '.'
    		time.sleep(0.1)
	print "conversion consume time:", time.time()-start
	capture.stop()

	#print 'Saving oscilloscope values to "data.csv"'

   	#for x in capture.oscilloscope_data(numsamples):
		#print x

	#print 'done'

	capture.close()

if __name__ == "__main__":
	while 1:
		Process(target = ain, args = (0,)).start()
