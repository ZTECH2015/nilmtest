# -*- coding: utf-8 -*-
"""
Created on Sun Dec 13 09:53:51 2015

@author: sbadvance
"""
import matplotlib.pyplot as plt
import scipy as sp
lines1=[]
lines2=[]
fig=plt.figure()
ax = fig.add_subplot(211)
ax.set_ylabel('watts')
ax.set_title('real time active power')
bx = fig.add_subplot(212)
#bx.set_ylabel('')
bx.set_title('real time emi')
lines1.append(ax.plot([0]*10000))
lines2.append(bx.plot([0]*10000))
for i in range(10000):
    ax.lines.pop(0)
    lines1.remove(lines1[0])    
    lines1.append(ax.plot(range(i*1000,i*1000+10000),color='b'))
    
    bx.lines.pop(0)
    lines2.remove(lines2[0])    
    lines2.append(bx.plot(range(i*1000,i*1000+10000),color='r'))
    
    plt.pause(0.5)
    
    
    
    

