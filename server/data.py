import pickle
import time
start = time.time()
data = open('testData.pkl', 'rb')
data = pickle.load(data)
print(time.time()-start)