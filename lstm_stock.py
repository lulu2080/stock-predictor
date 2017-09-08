#encoding:utf-8
'''
A Recurrent Neural Network (LSTM) implementation example using TensorFlow..
Next word prediction after n_input words learned from text file.
A story is automatically generated if the predicted word is fed back as input.

Author: Rowel Atienza
Project: https://github.com/roatienza/Deep-Learning-Experiments
'''

from __future__ import print_function
import argparse
import os
import tensorflow as tf
from tensorflow.contrib import rnn
import random
import datetime
import time
import data_helper

FLAGS = None

start_time = time.time()
def elapsed(sec):
    if sec<60:
        return str(sec) + " sec"
    elif sec<(60*60):
        return str(sec/60) + " min"
    else:
        return str(sec/(60*60)) + " hr"


parser = argparse.ArgumentParser()
#获得buckets路径
parser.add_argument('--buckets', type=str, default='d:/ai/stock-predictor/',
        help='input data path')
#获得checkpoint路径
parser.add_argument('--checkpointDir', type=str, default='d:/ai/stock-predictor/model/',
                        help='output model path')
FLAGS, _ = parser.parse_known_args()

# Parameters
#batch_size = 1000
#time_step = 22
#learning_rate = 0.001
#num_epochs = 10
#evaluate_every = 10000000
#display_step = 10000
#n_input = 3
#num_classes = 3
#checkpoint_every = 10000
#num_checkpoints = 20
#train_begin = 0
#train_end = 98000
#
## number of units in RNN cell
#n_hidden = 400

# Parameters
batch_size = 100
time_step = 6
learning_rate = 1e-4
num_epochs = 100000
evaluate_every = 1000000
display_step = 1000000
n_input = 3
num_classes = 3
checkpoint_every = 1000000
num_checkpoints = 20
train_begin = 0
train_end = 6000

# number of units in RNN cell
n_hidden = 300

print("Loaded data...")
batch_index, train_x, train_y = data_helper.get_train_data(batch_size, time_step, train_begin, train_end)
_, _, test_x, test_y = data_helper.get_test_data(time_step, train_end)
#print("batch_index")
#print(batch_index)
#print("train_x")
#print(train_x)
#print("train_y")
#print(train_y)
#print("test_x")
#print(test_x)
#print("test_y")
#print(test_y)

# tf Graph input
x = tf.placeholder("float", [None, time_step, n_input], name="input_x")
y = tf.placeholder("float", [None, time_step, num_classes])

# RNN output node weights and biases
weights = {
#    'in': tf.Variable(tf.random_normal([n_input, n_hidden])), 
    'out': tf.Variable(tf.random_normal([n_hidden, num_classes]))
}
biases = {
#    'in': tf.Variable(tf.random_normal([n_hidden])), 
    'out': tf.Variable(tf.random_normal([num_classes]))
}

def RNN(x, weights, biases):

    # reshape to [1, n_input]
    x = tf.reshape(x, [-1, n_input])

    x = tf.split(x, n_input, 1)


    # 2-layer LSTM, each layer has n_hidden units.
    # Average Accuracy= 95.20% at 50k iter
    rnn_cell = rnn.MultiRNNCell([rnn.BasicLSTMCell(n_hidden), rnn.BasicLSTMCell(n_hidden)])
    rnn_cell.zero_state(batch_size, dtype = tf.float32)

    # 1-layer LSTM with n_hidden units but with lower accuracy.
    # Average Accuracy= 90.60% 50k iter
    # Uncomment line below to test but comment out the 2-layer rnn.MultiRNNCell above
    # rnn_cell = rnn.BasicLSTMCell(n_hidden)

    # generate prediction
    outputs, states = rnn.static_rnn(rnn_cell, x, dtype=tf.float32)

    # there are n_input outputs but
    # we only want the last output
    return tf.nn.softmax(tf.matmul(outputs[-1], weights['out']) + biases['out'])

#def RNN(x, weights, biases):
#    cell = tf.nn.rnn_cell.BasicLSTMCell(n_hidden)
#    init_state = cell.zero_state(batch_size, dtype = tf.float32)
#    output_rnn, final_states = tf.nn.dynamic_rnn(cell, x, initial_state=init_state, dtype=tf.float32)  #output_rnn是记录lstm每个输出节点的结果，final_states是最后一个cell的结果
#    output = tf.reshape(output_rnn, [-1, n_hidden]) #作为输出层的输入
#
#    # there are n_input outputs but
#    # we only want the last output
#    return tf.matmul(output, weights['out']) + biases['out']

#input_rnn = tf.matmul(tf.reshape(x, [-1, n_input]), weights['in']) + biases['in']
#input_rnn = tf.reshape(input_rnn, [-1, time_step, n_hidden])

pred = RNN(x, weights, biases)

global_step = tf.Variable(0, name="global_step", trainable=False)

y_ = tf.reshape(y, [-1,num_classes])
# Loss and optimizer
cost = tf.reduce_mean(tf.nn.softmax_cross_entropy_with_logits(logits=pred, labels=y_))
#optimizer = tf.train.RMSPropOptimizer(learning_rate=learning_rate).minimize(cost)
train_op = tf.train.AdamOptimizer(learning_rate=learning_rate).minimize(cost)

#optimizer = tf.train.AdamOptimizer(learning_rate)
#grads_and_vars = optimizer.compute_gradients(cost)
#train_op = optimizer.apply_gradients(grads_and_vars, global_step=global_step)

# Model evaluation
correct_pred = tf.equal(tf.argmax(pred,1), tf.argmax(y_,1))
accuracy = tf.reduce_mean(tf.cast(correct_pred, tf.float32))
predictions = tf.argmax(pred, 1, name="predictions")

p_result = tf.Variable(0, name="p_result")
p_rate = tf.Variable(tf.ones(shape=[3], dtype=tf.float32), name="p_rate")
get_result = tf.assign(p_result, tf.cast(predictions[-1], tf.int32), name="get_result")
get_rate = tf.assign(p_rate, pred[-1], name="get_rate")
#grads_and_vars = optimizer.compute_gradients(cost)

# Initializing the variables
init = tf.global_variables_initializer()

# Launch the graph
with tf.Session() as session:
    session.run(init)
    offset = random.randint(0, n_input + 1)
    end_offset = n_input + 1
    acc_total = 0
    loss_total = 0
    current_step = 0

#    # Keep track of gradient values and sparsity (optional)
#    grad_summaries = []
#    for g, v in grads_and_vars:
#        if g is not None:
#            grad_hist_summary = tf.summary.histogram("{}/grad/hist".format(v.name), g)
#            sparsity_summary = tf.summary.scalar("{}/grad/sparsity".format(v.name), tf.nn.zero_fraction(g))
#            grad_summaries.append(grad_hist_summary)
#            grad_summaries.append(sparsity_summary)
#    grad_summaries_merged = tf.summary.merge(grad_summaries)
#
    # Output directory for models and summaries
    timestamp = str(int(time.time()))
    out_dir = os.path.join(FLAGS.checkpointDir, "runs", timestamp)
    print("Writing to {}\n".format(out_dir))
#
#    # Summaries for loss and accuracy
#    loss_summary = tf.summary.scalar("loss", cost)
#    acc_summary = tf.summary.scalar("accuracy", accuracy)
#
#    # Train Summaries
#    train_summary_op = tf.summary.merge([loss_summary, acc_summary, grad_summaries_merged])
#    train_summary_dir = os.path.join(out_dir, "summaries", "train")
#    if not os.path.exists(train_summary_dir):
#        os.makedirs(train_summary_dir)            
#    train_summary_writer = tf.summary.FileWriter(train_summary_dir, session.graph)
#
#    # Dev summaries
#    dev_summary_op = tf.summary.merge([loss_summary, acc_summary])
#    dev_summary_dir = os.path.join(out_dir, "summaries", "dev")
#    if not os.path.exists(dev_summary_dir):
#        os.makedirs(dev_summary_dir)
#    dev_summary_writer = tf.summary.FileWriter(dev_summary_dir, session.graph)

    # Checkpoint directory. Tensorflow assumes this directory already exists so we need to create it
    checkpoint_dir = os.path.join(out_dir, "checkpoints")
    checkpoint_prefix = os.path.join(checkpoint_dir, "model")
    if not os.path.exists(checkpoint_dir):
        os.makedirs(checkpoint_dir)
    saver = tf.train.Saver(tf.global_variables(), max_to_keep=num_checkpoints)

    def train_step(x_batch, y_batch):
#        print("x_batch:")
#        print(x_batch)
#        print("y_batch:")
#        print(y_batch)
        """
        A single training step
        """
        feed_dict = {
          x: x_batch,
          y: y_batch,
        }
        _, step, acc, loss, pred_result = session.run(
            [train_op, global_step, accuracy, cost, pred],
            feed_dict)
        time_str = datetime.datetime.now().isoformat()
        print("{}: step {}, loss {:g}, acc {:g}".format(time_str, current_step+1, loss, acc))
#        train_summary_writer.add_summary(summaries, step)

        return step, acc, loss, pred_result    

    def dev_step(x_batch, y_batch, writer=None):
#        print("x_test_batch:")
#        print(x_batch)
#        print("y_test_batch:")
#        print(y_batch)
        """
        Evaluates model on a dev set
        """
        
        feed_dict = {
          x: x_batch,
          y: y_batch,
        }
        _, step, acc, loss, pred_result = session.run(
            [train_op, global_step, accuracy, cost, pred],
            feed_dict)
        time_str = datetime.datetime.now().isoformat()
        print("{}: step {}, loss {:g}, acc {:g}".format(time_str, current_step+1, loss, acc))
#        if writer:
#            writer.add_summary(summaries, step)


    for i in range(num_epochs):
        for di in range(len(batch_index) - 1):
            x_batch = train_x[batch_index[di]:batch_index[di + 1]]
            y_batch = train_y[batch_index[di]:batch_index[di + 1]]
    
            step, acc, loss, pred_result = train_step(x_batch, y_batch)
    #        current_step = tf.train.global_step(session, global_step)
#            print(pred_result)
    
            loss_total += loss
            acc_total += acc
    
            if (current_step + 1) % checkpoint_every == 0:
                path = saver.save(session, checkpoint_prefix, global_step=current_step+1)
                print("Saved model checkpoint to {}\n".format(path))
    
            if (current_step + 1) % display_step == 0:
                print("Iter= " + str(current_step+1) + ", Average Loss= " + \
                      "{:.6f}".format(loss_total/display_step) + ", Average Accuracy= " + \
                      "{:.2f}%".format(100*acc_total/display_step))
                pred_r = tf.argmax(pred_result, 1).eval()
                print("pred_result:")
                print(pred_r)
                acc_total = 0
                loss_total = 0
                
            if (current_step + 1) % evaluate_every == 0:
                print("\nEvaluation:")
                dev_step(test_x[0:-1], test_y[0:-1])
                print("")

            current_step += 1

    print("Optimization Finished!")
    print("Elapsed time: ", elapsed(time.time() - start_time))