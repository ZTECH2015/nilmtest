# -*- coding: utf-8 -*-
"""
Created on Mon Dec  7 11:14:27 2015

@author: bao18
"""

import pickle
import time
import matplotlib.pyplot as plt
import numpy as np
start = time.time()
data = open('testData_slow_start_PC.pkl', 'rb')
data = pickle.load(data)
print(time.time()-start)
voltage = []
current = []
p = []
q = []
i = []
emi = []
data_all = []
len_uipq = 16

for d in data:
    if len(d) == 8:
        for dd in d:
            if type(dd) is not float:
                voltage.extend(dd[\
                :len_uipq])
                current.extend(dd[len_uipq:len_uipq*2])
                p.extend(dd[len_uipq*2:len_uipq*3])
                q.extend(dd[len_uipq*3:len_uipq*4])
                i.append(dd[-5:])
    else:
        emi.append(d[0])
        
        
i = np.array(i).transpose()
emi = np.array(emi).transpose()
data_all.append(voltage)
data_all.append(current)
data_all.append(p)
data_all.append(q)
#plt.plot(voltage)
#plt.plot(current)
plt.plot(p)
#plt.plot(q)
#plt.plot(emi, alpha = 1)
#plt.plot(i[0,:])
plt.show()
#fig = plt.figure()
#ax = fig.add_subplot(111)
#li, =plt.plot(current[0])
#fig.canvas.draw()
#plt.show()
#
#for d in current:
#    li.set_ydata(d)
#    fig.canvas.draw()
#    time.sleep(0.2)