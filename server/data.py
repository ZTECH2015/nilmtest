import pickle
#from save2Database import  *
import time
import matplotlib.pyplot as plt
import numpy as np
start = time.time()
data_raw = open('testData.pkl', 'rb')
data_raw = pickle.load(data_raw)
#print(time.time()-start)
#
p = []
q = []
u = []
for data in data_raw:
    p.extend(data[2])
    q.extend(data[3])
    u.extend(data[0])
#    save_raw(conn, data[0], data[1], data[2], 
#             data[3], data[4], data[5], data[6])
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