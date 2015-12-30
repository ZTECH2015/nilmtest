import socket
from multiprocessing import Process, Queue
import numpy as np
import time, pickle
from save2Database import *
import os
import matplotlib.pyplot as plt
from parameters import *

def recv(s, q1, q2):
      # Set the socket parameters
      conn, addr = s.accept()
      data_buf = bytes()
      #exec(open('parameters.py').read())
      # Receive message
      ui_len = 8230
      while 1:
          start = time.time()
          #print(len(data))
          if len(data_buf) >= ui_len:
                  data = data_buf[:ui_len]
                  data = pickle.loads(data, encoding="bytes")
            
                  q2.put([data[2], data[5]])  # put p and emi to real time ploting processing  
                  #save_raw(cursor, data[0], data[1], data[2], data[3], data[4], data[5], data[6])
                  
                  databuffer = ev_detect(data,databuffer)
          else:
              data_buf = data_buf + conn.recv(2**16)
                  #print("fail to get the data at :", time.time())
      s.close()

def realtime(q2):
    lines1=[]
    lines2=[]
    fig=plt.figure()
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
    while 1:
        data=q2.get(True)
        p.extend(data[0])
        p[0:len(data[0])]=[]
        emi=data[1]
        
        fig1.lines.pop(0)
        lines1.append(fig1.plot(p,color='b'))
        lines1.remove(lines1[0])
        
        fig2.lines.pop(0)
        lines2.append(fig2.plot(emi,color='r'))
        lines2.remove(lines2[0])
        
        plt.pause(0.3)
        
        
def classifier(q1):
    if os.path.exists(r'features.pkl'):
        feature = open('features.pkl', 'rb')
        feature = pickle.load(feature)
    else:
        feature=pd.DataFrame([], columns=['dp_tr','dp_t','dq_tr','dq_t','du_tr','du_t','di_tr','di_t','dp_s','dq_s','du_s','di_s','dp_dq','first_h','third_h','fifth_h','demi','time_stamp','p_n'])
        
    while 1:  
        try:
            data=q1.get(True)
            feature=pd.concat([feature,data])  
            
        except KeyboardInterrupt:
            output = open('features.pkl', 'wb')
            pickle.dump(feature, output)
            output.close
            print('write to the file done!!!!!')
            break
        
            
        


if __name__ == '__main__':
      q1 = Queue()
      q2 = Queue()
      host = '104.194.126.108'
      port = 9999

      # Create socket and bind to address
      s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
      s.bind((host, port))
      s.listen(10)
      Process(target = recv, args = (s, q1, q2, )).start()
      Process(target = realtime, args = (q2, )).start()
      #Process(target = classifier, args = (q1, )).start()
 