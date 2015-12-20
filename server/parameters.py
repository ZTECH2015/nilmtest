# -*- coding: utf-8 -*-
"""
Created on Sun Nov  1 20:36:49 2015

@author: sbadvance
"""

import pandas as pd
import scipy as sp

outputfre=60
std=3
Nd=int(outputfre*0.5) #event detect window size
Nm=int(outputfre*1) #event detector mean value window size
Ns=int(outputfre*1)  #window size for extract stationary feature
Ne=int(outputfre/5) #event end point detect window size
Nb=int(outputfre*4) #data before event remained for feature extracting

h=(15-std)*Nd #event threshold
stft=outputfre #steady feature window size
detectorsize=int(2*outputfre) #length of eventdetection window


def ev_detect(data,databuffer,q1):
    index1=data[6]+sp.linspace(0,63/60,64)
    data=pd.DataFrame({'u' : pd.Series(data[0],index=index1),
                         'i' : pd.Series(data[1],index=index1),
                         'p' : pd.Series(data[2],index=index1),
                         'q' : pd.Series(data[3],index=index1),
                         'harmony' : pd.Series(data[4],index=data[6]+sp.linspace(0,48/60,4)),
                         'emi' : pd.Series([data[5]],index=[data[6]])})
    databuffer=pd.concat([databuffer,data]) 
    #print(len(databuffer['p']),Ns+Nd+Nm+Nb)
    if len(databuffer['p'])>(Ns+Nd+Nm+Nb):
        k=Nb
        p=databuffer['p'] # use active power for event detect
        N=len(p)
        eventstartp=[]
        eventstartn=[]
        eventendp=[]
        eventendn=[]
        indx1=N-Nd-Ns-Nm+1
        #print(p.iloc[k-Nm:k].std())
        while k < indx1:
            mu=p.iloc[k-Nm:k].mean()
            sigma=p.iloc[k-Nm:k].std() # ?????
            kcusum=0
            dp=0
            dn=0
            gp=0
            gn=0
            findevent=0
            while kcusum<Nd:
                #gp=max(0,gp+p.iloc[k+kcusum]-mu)
                #gn=max(0,gn-p.iloc[k+kcusum]+mu)
                gp=max(0,gp+p.iloc[k+kcusum]-mu-sigma)
                gn=max(0,gn-p.iloc[k+kcusum]+mu-sigma)
                if gp>0:
                    if gp>h:
                        eventstartp=k+kcusum-dp-2  #????
                        findevent=1
                        k=eventstartp
                        indx2=k
                        while indx2<k+Ns:
                            stdp=p.iloc[indx2:indx2+Ne].std()
                            if stdp<sigma:
                                break
                            indx2+=Ne
                        eventendp=indx2  
                        #print("something is up")
                        dp_tr=databuffer['p'].iloc[eventstartp:eventendp].max()-databuffer['p'].iloc[eventstartp-Nm:eventstartp].mean()# 1.dp_tr: transient delta p
                        #dp_tr=max(p[eventstartp:eventendp])-sp.mean(p[eventstartp-Nm:eventstartp])
                        dp_t=databuffer['p'].iloc[eventstartp:eventendp].argmax()-databuffer['p'].index[eventstartp]# 2.dp_t: transient delta t for p
                        dq_tr=databuffer['q'].iloc[eventstartp:eventendp].max()-databuffer['q'].iloc[eventstartp-Nm:eventstartp].mean()# 3.dq_tr: transient delta q
                        dq_t=databuffer['q'].iloc[eventstartp:eventendp].argmax()-databuffer['q'].index[eventstartp]# 4.dq_t: transient delta t for q
                        du_tr=databuffer['u'].iloc[eventstartp:eventendp].max()-databuffer['u'].iloc[eventstartp-Nm:eventstartp].mean()# 5.du_tr: transient delta u
                        du_t=databuffer['u'].iloc[eventstartp:eventendp].argmax()-databuffer['u'].index[eventstartp]# 6.du_t: transient delta t for u
                        di_tr=databuffer['i'].iloc[eventstartp:eventendp].max()-databuffer['i'].iloc[eventstartp-Nm:eventstartp].mean()# 7.di_tr: transient delta i
                        di_t=databuffer['i'].iloc[eventstartp:eventendp].argmax()-databuffer['i'].index[eventstartp]# 8.di_t: transient delta t for i
                        dp_s=databuffer['p'].iloc[eventendp:eventendp+Nm].mean()-databuffer['p'].iloc[eventstartp-Nm:eventstartp].mean()# 9.dp_s: stable delta p
                        dq_s=databuffer['q'].iloc[eventendp:eventendp+Nm].mean()-databuffer['q'].iloc[eventstartp-Nm:eventstartp].mean()# 10.dq_s: stable delta q
                        du_s=databuffer['u'].iloc[eventendp:eventendp+Nm].mean()-databuffer['u'].iloc[eventstartp-Nm:eventstartp].mean()# 11.du_s: stable delta u
                        di_s=databuffer['i'].iloc[eventendp:eventendp+Nm].mean()-databuffer['i'].iloc[eventstartp-Nm:eventstartp].mean()# 12.di_s: stable delta i
                        dp_dq=dp_s/dq_s# 13.dp_dq: delta p over delta q
                        #temp = databuffer['harmony'].iloc[eventendp+1:eventendp+17].iloc[sp.where(databuffer['harmony'].iloc[eventendp+1:eventendp+17].notnull())[0]].iloc[0]-databuffer['harmony'].iloc[eventstartp-33:eventstartp-1].iloc[sp.where(databuffer['harmony'].iloc[eventstartp-33:eventstartp-1].notnull())[0]].iloc[-2]
                        #print(type(list(temp)))
                        [first_h,s_h,third_h,fr_h,fifth_h]=databuffer['harmony'].iloc[eventendp+1:eventendp+17].iloc[sp.where(databuffer['harmony'].iloc[eventendp+1:eventendp+17].notnull())[0]].iloc[0]-databuffer['harmony'].iloc[eventstartp-33:eventstartp-1].iloc[sp.where(databuffer['harmony'].iloc[eventstartp-33:eventstartp-1].notnull())[0]].iloc[-2]
                        # 14.first_h: first harmonic
                        # 15.third_h: third harmonic
                        # 16.fifth_h: fifth harmonic
                        demi=databuffer['emi'].iloc[eventendp+1:eventendp+65].iloc[sp.where(databuffer['emi'].iloc[eventendp+1:eventendp+65].notnull())[0]].iloc[0]-databuffer['emi'].iloc[eventstartp-129:eventstartp-1].iloc[sp.where(databuffer['emi'].iloc[eventstartp-129:eventstartp-1].notnull())[0]].iloc[-2]
                        # 18.demi: delta emi
                        time_stamp=databuffer.index[eventstartp-1]
                        feature=pd.DataFrame({'dp_tr' : dp_tr, 'dp_t' : dp_t,
                                              'dq_tr' : dq_tr, 'dq_t' : dq_t,
                                              'du_tr' : du_tr, 'du_t' : du_t,
                                              'di_tr' : di_tr, 'di_t' : di_t,
                                              'dp_s' : dp_s, 'dq_s' : dq_s,
                                              'du_s' : du_s, 'di_s' : di_s,
                                              'dp_dq' : dp_dq, 
                                              'first_h' : first_h, 'third_h' : third_h,
                                              'fifth_h' : fifth_h, 'demi' : [demi],
                                              'time_stamp' : time_stamp, 'p_n': 1})
                        #save_feature(conn, dp_tr, dp_t, dq_tr, dq_t, du_tr, du_t, di_tr, di_t, dp_s, dq_s, du_s, di_s, dp_dq, first_h, third_h, fifth_h, demi, time_stamp, 1)
                        q1.put(feature)
                        k=eventendp+Nm
                        break
                    else:
                        dp=dp+1
                else:dp=0
                
                
                if gn>0:
                    if gn>h:
                        eventstartn=k+kcusum-dn-2
                        findevent=1
                        k=eventstartn
                        indx2=k
                        while indx2<k+Ns:
                            stdp=p.iloc[indx2:indx2+Ne].std()
                            if stdp<std:
                                break
                            indx2+=Ne
                        eventendn=indx2   
                        #print("something is down")
                        dp_tr=-(databuffer['p'].iloc[eventstartn:eventendn].max()-databuffer['p'].iloc[eventendn:eventendn+Nm].mean())# 1.dp_tr: transient delta p      it was eventstartn-Nm:eventstartn    modified by zb                             
                        dp_t=databuffer['p'].index[eventendn]-databuffer['p'].iloc[eventstartn:eventendn].argmax()# 2.dp_t: transient delta t for p                                               
                        dq_tr=-(databuffer['q'].iloc[eventstartn:eventendn].max()-databuffer['q'].iloc[eventendn:eventendn+Nm].mean())# 3.dq_tr: transient delta q
                        dq_t=databuffer['q'].index[eventendn]-databuffer['q'].iloc[eventstartn:eventendn].argmax()# 4.dq_t: transient delta t for q
                        du_tr=-(databuffer['u'].iloc[eventstartn:eventendn].max()-databuffer['u'].iloc[eventendn:eventendn+Nm].mean())# 5.du_tr: transient delta u
                        du_t=databuffer['u'].index[eventendn]-databuffer['u'].iloc[eventstartn:eventendn].argmax()# 6.du_t: transient delta t for u
                        di_tr=-(databuffer['i'].iloc[eventstartn:eventendn].max()-databuffer['i'].iloc[eventendn:eventendn+Nm].mean())# 7.di_tr: transient delta i
                        di_t=databuffer['i'].index[eventendn]-databuffer['i'].iloc[eventstartn:eventendn].argmax()# 8.di_t: transient delta t for i
                        dp_s=databuffer['p'].iloc[eventendn:eventendn+Nm].mean()-databuffer['p'].iloc[eventstartn-Nm:eventstartn].mean()# 9.dp_s: stable delta p
                        dq_s=databuffer['q'].iloc[eventendn:eventendn+Nm].mean()-databuffer['q'].iloc[eventstartn-Nm:eventstartn].mean()# 10.dq_s: stable delta q
                        du_s=databuffer['u'].iloc[eventendn:eventendn+Nm].mean()-databuffer['u'].iloc[eventstartn-Nm:eventstartn].mean()# 11.du_s: stable delta u
                        di_s=databuffer['i'].iloc[eventendn:eventendn+Nm].mean()-databuffer['i'].iloc[eventstartn-Nm:eventstartn].mean()# 12.di_s: stable delta i
                        dp_dq=dp_s/dq_s# 13.dp_dq: delta p over delta q 
                        [first_h,s_h,third_h,fr_h,fifth_h]=databuffer['harmony'].iloc[eventendn+1:eventendn+17].iloc[sp.where(databuffer['harmony'].iloc[eventendn+1:eventendn+17].notnull())[0]].iloc[0]-databuffer['harmony'].iloc[eventstartn-33:eventstartn-1].iloc[sp.where(databuffer['harmony'].iloc[eventstartn-33:eventstartn-1].notnull())[0]].iloc[-2]
#                        # 14.first_h: first harmonic
#                        # 15.third_h: third harmonic
#                        # 16.fifth_h: fifth harmonic
                        demi=databuffer['emi'].iloc[eventendn+1:eventendn+65].iloc[sp.where(databuffer['emi'].iloc[eventendn+1:eventendn+65].notnull())[0]].iloc[0]-databuffer['emi'].iloc[eventstartn-129:eventstartn-1].iloc[sp.where(databuffer['emi'].iloc[eventstartn-129:eventstartn-1].notnull())[0]].iloc[-2]
#                        # 18.demi: delta emi
                        time_stamp=databuffer.index[eventstartn-1]
                        feature=pd.DataFrame({'dp_tr' : 0, 'dp_t' : 0,
                                              'dq_tr' : 0, 'dq_t' : 0,
                                              'du_tr' : 0, 'du_t' : 0,
                                              'di_tr' : 0, 'di_t' : 0,
                                              'dp_s' : dp_s, 'dq_s' : dq_s,
                                              'du_s' : du_s, 'di_s' : di_s,
                                              'dp_dq' : dp_dq, 
                                              'first_h' : first_h, 'third_h' : third_h,
                                              'fifth_h' : fifth_h, 'demi' : [demi],
                                              'time_stamp' : time_stamp, 'p_n': 0})
                        #save_feature(conn, dp_tr, dp_t, dq_tr, dq_t, du_tr, du_t, di_tr, di_t, dp_s, dq_s, du_s, di_s, dp_dq, first_h, third_h, fifth_h, demi, time_stamp, 0)
                        
                        q1.put(feature)
                        k=eventendn+Nm
                        break
                    else:
                        dn=dn+1
                else:
                    dn=0
                kcusum=kcusum+1
                
            if findevent==0:
                
                k=k+Nd+1-max(dp,dn) 
        databuffer = databuffer.drop(databuffer.index[:k-Nb])
        #print("I am done!!")
    return databuffer