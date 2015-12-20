# -*- coding: utf-8 -*-
"""
Created on Sat Dec 19 08:24:53 2015

@author: bao18
"""
from sklearn.cluster import AffinityPropagation
from sklearn import preprocessing
import pandas as pd
import scipy as sp
import pickle, time
from sklearn.decomposition import PCA
import matplotlib.pyplot as plt
from save2Database import *

def data():
    #feature = pickle.load(open('features.pkl', 'rb'))
    feature = readFeature(db)
    #print(feature)
    data_index = ['dp_tr','dp_t','dq_tr','dq_t','du_tr','du_t','di_tr','di_t','dp_s','dq_s','du_s','di_s','dp_dq','first_h','third_h','fifth_h']
    sample = feature.loc[:,data_index]
    sample_norm = (sample-sample.mean()) / (sample.max()-sample.min())
    sample_norm.fillna(0)
    #print(sample_norm)
    return sample_norm
    
def do_pca():
    sample = data()
    n_com = 3
    pca = PCA(n_components=n_com)
    pca_fit = pca.fit(sample)
    X_r = pca_fit.transform(sample)
    #print(X_r)
    pickle.dump(pca_fit, open('pca_fit.pkl', 'wb'))
    print(pca.explained_variance_ratio_)
    #print(X_r)
    return X_r,n_com,pca_fit
    
def ap():
    data_index = ['dp_tr','dp_t','dq_tr','dq_t','du_tr','du_t','di_tr','di_t','dp_s','dq_s','du_s','di_s','dp_dq','first_h','third_h','fifth_h']
    feature = readFeature(db)
    sample, n_com, pca_fit = do_pca()
    sample=pd.DataFrame(sample)
    sample['p_n'] = feature['p_n'].values
    
    sample_up = sample[sample.p_n == 1].iloc[:,0:n_com]
    sample_down = sample[sample.p_n == 0].iloc[:,0:n_com]
    
    
    start = time.time()
    print('start to do training')
    p = -0.5
    af_up = AffinityPropagation(damping=0.5, preference=p).fit(sample_up)
    af_down = AffinityPropagation(damping=0.5, preference=p).fit(sample_down)
    print('Event number of starting appliances:',af_up.predict(sample_up))
    print('Event number of stoping appliances:',af_down.predict(sample_down))
    #feature['labels'] = af.labels_
    saveModel2mdb(db,[af_up, af_down, pca_fit, feature.loc[:,data_index].max(),feature.loc[:,data_index].min(),feature.loc[:,data_index].mean()])
    print('done with training take:', time.time()-start,'seconds')


if __name__ == '__main__':
    ap()
    #do_pca()