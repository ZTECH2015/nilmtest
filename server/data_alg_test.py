import pickle
import time
import matplotlib.pyplot as plt
import numpy as np
import os
from multiprocessing import Process, Queue
from sklearn.decomposition import PCA
from save2Database import *


#from parameters import *
exec(open('parameters.py').read())
def read(q1):
    start = time.time()
    data_raw = pickle.load(open('testData.pkl', 'rb'))
    databuffer=pd.DataFrame(columns=['u','i','p','q','harmony','emi'])
    p = []
    for data in data_raw:
        saveRaw2mdb(db,data)
        databuffer = ev_detect(data,databuffer, q1)
        p.extend(data[2])
    
    
#    print(time.time()-start)

def classifier(q1):
#    if os.path.exists(r'features.pkl'):
#        feature = pickle.load(open('features.pkl', 'rb'))
#    else:
#        feature=pd.DataFrame([], columns=['dp_tr','dp_t','dq_tr','dq_t','du_tr','du_t','di_tr','di_t','dp_s','dq_s','du_s','di_s','dp_dq','first_h','third_h','fifth_h','demi','time_stamp','p_n'])
    while 1:
        data=q1.get(True)
        saveFeature2mdb(db,data)
        if data.p_n[0] == 1:
            print('I know something was started up, let me guess what it is!')
        elif data.p_n[0] == 0:
            print('I know something was shut down, let me guess what it is!')
        #feature=pd.concat([feature,data]) 
        try:
            cluster_ap = readModel(db)
            
            cl_up = cluster_ap[0]
            cl_down = cluster_ap[1]
            pca = cluster_ap[2]
            data_max = cluster_ap[3]
            data_min = cluster_ap[4]
            data_mean = cluster_ap[5]                
            data_index = ['dp_tr','dp_t','dq_tr','dq_t','du_tr','du_t','di_tr','di_t','dp_s','dq_s','du_s','di_s','dp_dq','first_h','third_h','fifth_h']
            sample = data.loc[:,data_index]
            sample = (sample-data_mean) / (data_max-data_min)
            sample = sample.fillna(0)
            sample_norm = pca.transform(sample)
            
            if data.p_n[0] == 1:
                print('The event number of starting applicances is:  1',cl_up.predict(sample_norm)[0], '+++++++, at time:', time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(data.time_stamp)))
            elif data.p_n[0] == 0:
                print('The event number of stoping applicances is:   0',cl_down.predict(sample_norm)[0], '-------, at time:', time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(data.time_stamp)))
        except:
            pass
        
        
if __name__ == '__main__':
      q1 = Queue()
      Process(target = read, args = (q1, )).start()
      Process(target = classifier, args = (q1, )).start()