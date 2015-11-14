# -*- coding: utf-8 -*-
"""
Created on Fri Nov 13 20:42:42 2015

@author: ZHEN
"""

from scipy.fftpack import fft
import matplotlib.pyplot as plt
from scipy import signal
import numpy as np
# Number of samplepoints
N = 600
# sample spacing
T = 1.0 / 800.0
x = np.linspace(0.0, N*T, N)
trend = np.hstack((np.zeros((N/2)),(x[:300])))
y = np.sin(1 * 2.0*np.pi*x) + np.sin(50.0 * 2.0*np.pi*x) + 0.5*np.sin(80.0 * 2.0*np.pi*x)#+trend
yf = fft(y)
yf0 = signal.detrend(y)
xf = np.linspace(0.0, 1.0/(2.0*T), N/2)

plt.plot(xf, 2.0/N * np.abs(yf[0:N/2]))
plt.grid()
plt.show()