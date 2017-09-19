#encoding:utf-8
#! /usr/bin/env python

import os
import sys
import tensorflow as tf
import numpy as np
import argparse
from tensorflow.python.lib.io import file_io
import pandas as pd
import data_loader as dl

FLAGS = None
time_step = 6

# Parameters
# ==================================================
parser = argparse.ArgumentParser()
#获得股票代码
parser.add_argument('--innerCode', type=int, default='1',
        help='stock inner code')
#获得checkpoint路径
parser.add_argument('--checkpointDir', type=str, default='model/cloud/runs/1505107245/checkpoints/',
                        help='output model path')
FLAGS, _ = parser.parse_known_args()

eval_file_path, lastTradingDay = dl.get_stock_data(FLAGS.innerCode)

if eval_file_path is None:
    print(-1)
    sys.exit(0)

#ali-oss read mode
with file_io.FileIO(eval_file_path, mode="r") as f:
    df=pd.read_csv(f)     #读入股票数据
    data_x=df.iloc[:,0:3].values   #取前3列
os.remove(eval_file_path)

mean = np.mean(data_x, axis=0)
std = np.std(data_x, axis=0)
normalized_eval_data = (data_x-mean) / std  #标准化
len_data = len(normalized_eval_data)
size = (len_data + time_step - 1) // time_step  #有size个sample
eval_x = []
for i in range(size - 1):
   x = normalized_eval_data[len_data-(i+1)*time_step:len_data-i*time_step]
   eval_x.append(x.tolist())
eval_x = eval_x[::-1]
# Evaluation
# ==================================================

graph = tf.Graph()
with graph.as_default():    
    checkpoint_file = tf.train.latest_checkpoint(FLAGS.checkpointDir)
    with tf.Session() as sess:
#        # Initialize all variables
        sess.run(tf.local_variables_initializer())
        sess.run(tf.global_variables_initializer())
        
        # Load the saved meta graph and restore variables
        saver = tf.train.import_meta_graph("{}.meta".format(checkpoint_file))
        saver.restore(sess, checkpoint_file)

        # Get the placeholders from the graph by name
        input_x = graph.get_operation_by_name("input_x").outputs[0]
        p_result = graph.get_operation_by_name("p_result").outputs[0]
        p_rate = graph.get_operation_by_name("p_rate").outputs[0]
        # Tensors we want to evaluate
        get_result = graph.get_operation_by_name("get_result").outputs[0]
        get_rate = graph.get_operation_by_name("get_rate").outputs[0]

        sess.run([get_result, get_rate], {input_x: eval_x[0:]})
        pred_result, pred_rate = sess.run([p_result, p_rate])
        
        date_str = lastTradingDay.strftime('%Y-%m-%d %H:%M:%S')

        print(str(pred_result) + "," + str(pred_rate[pred_result]) + "," + date_str)
