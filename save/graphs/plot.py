import numpy as np
import matplotlib.pyplot as plt
batch_size =150

def get_len(data):
    return len(data)

avg = np.load('reward_data_avg.npy')
avg = avg[avg!=0]
min_ = np.load('reward_data_min.npy')
min_ = min_[min_!=0]
max_ =np.load('reward_data_max.npy')
max_ = max_[max_!=0]
plt.plot(np.arange(get_len(avg))*batch_size,avg[:get_len(avg)],label='avg')
plt.plot(np.arange(get_len(avg))*batch_size,min_[:get_len(avg)],label='min')
plt.plot(np.arange(get_len(avg))*batch_size,max_[:get_len(avg)],label='max')
plt.legend(loc='lower right')
plt.show()
