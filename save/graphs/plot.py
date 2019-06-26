import numpy as np
import matplotlib.pyplot as plt
batch_size =60

def get_len(data):
    cnt =0
    for i in data:
        if i==0 and cnt>(3000/60):
            break
        cnt+=1
    return cnt

avg = np.load('reward_data_avg.npy')
min_ = np.load('reward_data_min.npy')
max_ = np.load('reward_data_max.npy')

plt.plot(np.arange(get_len(avg))*batch_size,avg[:get_len(avg)],label='avg')
plt.plot(np.arange(get_len(avg))*batch_size,min_[:get_len(avg)],label='min')
plt.plot(np.arange(get_len(avg))*batch_size,max_[:get_len(avg)],label='max')
plt.legend(loc='lower right')
plt.show()
