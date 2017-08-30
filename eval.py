#encoding:utf-8
#! /usr/bin/env python

import tensorflow as tf
import numpy as np
import os
import argparse
from tensorflow.python.lib.io import file_io
import pandas as pd
import csv

FLAGS = None

time_step=3

# Parameters
# ==================================================
parser = argparse.ArgumentParser()
#获得buckets路径
parser.add_argument('--buckets', type=str, default='D:/ai/stock-predictor/',
        help='input data path')
#获得checkpoint路径
parser.add_argument('--checkpointDir', type=str, default='D:/ai/stock-predictor/model/model/runs/1504015093/checkpoints/',
                        help='output model path')
FLAGS, _ = parser.parse_known_args()

print("Loaded data...")

#ali-oss read mode
eval_file_path = os.path.join(FLAGS.buckets, 'eval_stock.csv')
with file_io.FileIO(eval_file_path, mode="r") as f:
    df=pd.read_csv(f)     #读入股票数据
    data_x=df.iloc[:,0:3].values   #取前3列
mean = np.mean(data_x, axis=0)
std = np.std(data_x, axis=0)
normalized_eval_data = (data_x-mean) / std  #标准化
size = (len(normalized_eval_data) + time_step - 1) // time_step  #有size个sample
eval_x = []
ii = 0
for i in range(size - 1):
   x = normalized_eval_data[i*time_step:(i+1)*time_step]
   eval_x.append(x.tolist())
   ii = i
eval_x.append((normalized_eval_data[(ii+1)*time_step:]).tolist())

print("\nEvaluating...\n")

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
        # Tensors we want to evaluate
        predictions = graph.get_operation_by_name("predictions").outputs[0]

        pred_results = sess.run(predictions, {input_x: eval_x[0:-1]})
        
        print("pred_results:")
        print(pred_results)

# Save the evaluation to a csv
out_path = os.path.join(FLAGS.buckets, "output/", "prediction.csv")
print("Saving evaluation to {0}".format(out_path))
with file_io.FileIO(out_path, mode="w") as f:
    csv.writer(f).writerow([pred_results[-1]])