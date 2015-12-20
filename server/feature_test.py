# -*- coding: utf-8 -*-
"""
Created on Thu Dec 17 22:20:59 2015

@author: ZHEN
"""

import pickle
import time
import matplotlib.pyplot as plt
import numpy as np
import os
from multiprocessing import Process, Queue


feature = open('features.pkl', 'rb')
feature = pickle.load(feature)