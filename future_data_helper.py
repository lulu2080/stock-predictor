#encoding:utf-8

import os
import numpy as np
import pandas as pd
from tensorflow.python.lib.io import file_io

#local read mode
#f=open('future_data.csv')
#df=pd.read_csv(f)     #读入期货数据
#data_x=df.iloc[:,0:3].values   #取前3列
#data_y=df.iloc[:,3].values     #取第4列
#y_onehot = np.zeros([len(data_y), 3], dtype=float)
#y_onehot[np.arange(data_y.shape[0]), data_y] = 1.0
#f.close()

#ali-oss read mode
data_file_path = os.path.join('oss://myaitest001/stock-predictor/', 'future_data.csv')
with file_io.FileIO(data_file_path, mode="r") as f:
    df=pd.read_csv(f)     #读入期货数据
    data_x=df.iloc[:,0:3].values   #取前3列
    data_y=df.iloc[:,3].values     #取第4列
    y_onehot = np.zeros([len(data_y), 3], dtype=float)
    y_onehot[np.arange(data_y.shape[0]), data_y] = 1.0

#——————————获取训练集——————————
#def get_train_data(batch_size=60, time_step=20, train_begin=0, train_end=6000):
#    batch_index = []
#    data_train  = data_x[train_begin:train_end]
#    label_train = y_onehot[train_begin:train_end]
#    normalized_train_data = (data_train-np.mean(data_train,axis=0)) / np.std(data_train,axis=0)  #标准化
##    normalized_train_data = (data_train - np.min(data_train,axis=0)) / (np.max(data_train,axis=0) - np.min(data_train,axis=0))  #标准化
#    train_x, train_y = [], []   #训练集x和y初定义
#    for i in range(len(normalized_train_data) - time_step):
#       if i % batch_size==0:
#           batch_index.append(i)
#       x = normalized_train_data[i:i+time_step]
#       y = label_train[i:i+time_step]
#       train_x.append(x.tolist())
#       train_y.append(y.tolist())
#    batch_index.append((len(normalized_train_data)-time_step))
#    return batch_index, train_x, train_y

def get_train_data(batch_size=60, time_step=20, train_begin=0, train_end=6000):
    batch_index = []
    data_train  = data_x[train_begin:train_end]
    label_train = y_onehot[train_begin:train_end]
    normalized_train_data = (data_train-np.mean(data_train,axis=0)) / np.std(data_train,axis=0)  #标准化
#    normalized_train_data = (data_train - np.min(data_train,axis=0)) / (np.max(data_train,axis=0) - np.min(data_train,axis=0))  #标准化
    len_data = len(normalized_train_data)
    train_x, train_y = [], []   #训练集x和y初定义
    for i in range(len_data - time_step):
       if i % batch_size==0:
           batch_index.append(i)
       x = normalized_train_data[len_data-time_step-i:len_data-i]
       y = label_train[len_data-time_step-i:len_data-i]
       train_x.append(x.tolist())
       train_y.append(y.tolist())
#    batch_index.append((len(normalized_train_data)-time_step))
    return batch_index[::-1], train_x, train_y

#——————————获取测试集——————————
def get_test_data(batch_size=60, time_step=20, test_begin=6000):
    data_test  = data_x[test_begin:test_begin+2000]
    label_test = y_onehot[test_begin:test_begin+2000]
    mean = np.mean(data_test, axis=0)
    std = np.std(data_test, axis=0)
    normalized_test_data = (data_test-mean) / std  #标准化
    len_data = len(normalized_test_data)
#    size = (len_data + time_step - 1) // time_step  #有size个sample
    batch_index = []
    test_x,test_y = [],[]
#    for i in range(size - 1):
#       x = normalized_test_data[len_data-(i+1)*time_step:len_data-i*time_step]
#       y = label_test[len_data-(i+1)*time_step:len_data-i*time_step]
#       test_x.append(x.tolist())
#       test_y.append(y.tolist())
#    test_x = test_x[::-1]
#    test_y = test_y[::-1]
    for i in range(len_data - time_step + 1):
        #构建一个batch
        if i % batch_size == 0:
            batch_index.append(i)
        #构建一个序列(time_step)
        x = normalized_test_data[len_data-time_step-i:len_data-i]
        y = label_test[len_data-time_step-i:len_data-i]
        test_x.append(x.tolist())
        test_y.append(y.tolist())
    
    return batch_index[::-1], test_x, test_y