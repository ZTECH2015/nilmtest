# -*- coding: utf-8 -*-
"""
Created on Sun Dec  6 17:54:14 2015

@author: bao18
"""

import pickle
import time
import numpy as np
start = time.time()
data = open('testData.pkl', 'rb')
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


window_len = 65
evdetc_tol = 20      #the threshold is from experiment

event_num = 0
event_flag = 0
for index, d in enumerate(data):
    ## save data to buff
    if len(d) == 4:
        for dd in d:
            if np.shape(dd)[0] == 69:
                voltage.extend(dd[:len_uipq])
                current.extend(dd[len_uipq:len_uipq*2]*50)
                p.extend(dd[len_uipq*2:len_uipq*3])
                q.extend(dd[len_uipq*3:len_uipq*4])
                i.append(dd[-5:])
    else:
        emi.append(d)
        
    ## do event detection
    if len(p) >= window_len:
        p = np.array(p)
        condition = np.abs(p[1:]-p[:-1]).max() > evdetc_tol
        if condition:
            event_num += 1
            event_flag = 1
            print("something happen", (index+1)*4, event_num)
        print(p[60-window_len:])
        p = list(p[60-window_len:])
            