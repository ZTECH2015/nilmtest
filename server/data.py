import pickle
import time
import matplotlib.pyplot as plt
start = time.time()
data = open('testData.pkl', 'rb')
data = pickle.load(data)
print(time.time()-start)
voltage = []
current = []
emi = []
for d in data:
    if d.shape[0] == 1001:
        voltage.append(d[:-1,0])
        current.append(d[:-1,1])
    else:
        emi.append(d)

fig = plt.figure()
ax = fig.add_subplot(111)
li, =plt.plot(current[0])
fig.canvas.draw()
plt.show()

for d in current:
    li.set_ydata(d)
    fig.canvas.draw()
    time.sleep(0.2)