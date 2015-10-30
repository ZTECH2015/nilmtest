import Adafruit_BBIO.ADC as ADC
import time

ADC.setup()

y = []
t = []
delta_time = []
start_time = time.time()

while delta_time < 5:
	y.append(ADC.read("P9_40"))
	t.append(delta_time)
	time.sleep(1)
	delta_time = time.time() - start_time()

print len(y)