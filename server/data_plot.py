import pickle
import time
import matplotlib.pyplot as plt
import numpy as np
from matplotlib import pyplot
import os

import pylab
from pylab import *

#from parameters import *
start = time.time()
data_raw = pickle.load(open('testData.pkl', 'rb'))
#fig_len = 600
#p_buf = []
#p_buf = [0 for x in range(fig_len)]
#
#
#fig = plt.figure()
#ax = fig.add_subplot(111)
#ax.set_title("Realtime a Power Plot")
#ax.set_xlabel("Time")
#ax.set_ylabel("Amplitude")
#ax.axis([0,fig_len,-100,100])
#li, =ax.plot(np.arange(fig_len), p_buf)
#
#
#fig.canvas.draw()
#plt.show()


def realtime():
    lines1=[]
    lines2=[]
    fig = plt.figure()
    fig1 = fig.add_subplot(211)
    fig1.set_ylabel('watts')
    fig1.set_title('real time active power')
    fig2 = fig.add_subplot(212)
    #fig2.set_ylabel('')
    fig2.set_title('real time emi')
    p=[0]*600
    emi=[0]*1024
    lines1.append(fig1.plot(p))
    lines2.append(fig2.plot(emi))
    for data in data_raw:
        p.extend(data[2])
        p[0:len(data[2])]=[]
        emi=data[5]
        
        fig1.lines.pop(0)
        lines1.append(fig1.plot(p,color='b'))
        lines1.remove(lines1[0])
        
        fig2.lines.pop(0)
        lines2.append(fig2.plot(emi,color='r'))
        lines2.remove(lines2[0])
        
        plt.pause(0.5)

        
        
#for data in data_raw:
#    try:
#        p_buf.extend(data[2])
#        p_buf = p_buf[len(data[2]):]
#        li.set_ydata(p_buf)
#        ax.axis([0,fig_len,0,1.2*np.max(p_buf)])
#        fig.canvas.draw()
#        time.sleep(0.5)
#        #emi_buf.extend(data[5])
#    except KeyboardInterrupt:
#        break
realtime()
print(time.time()-start)


#voltage = []
#current = []
#p = []
#q = []
#i = []
#emi = []
#data_all = []
#time_stamp = []
#len_uipq = 16
#
#for d in data:
#    if len(d) == 6:
#        for dd in d:
#            if type(dd) is not float:
#                if len(dd) == 69:
#                    voltage.extend(dd[:len_uipq])
#                    current.extend(dd[len_uipq:len_uipq*2])
#                    p.extend(dd[len_uipq*2:len_uipq*3])
#                    q.extend(dd[len_uipq*3:len_uipq*4])
#                    i.append(dd[-5:])
#                elif len(dd) == 1024:
#                    emi.append(dd)
#            else:
#                time_stamp.append(dd)
#               
#i = np.array(i)
#emi = np.array(emi).transpose()

#plt.plot(voltage)
#plt.plot(current)
#plt.plot(p)
#plt.plot(q)
#plt.plot(emi[:,:100], alpha = 0.01)
#plt.plot(i[:,0])
#plt.show()
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