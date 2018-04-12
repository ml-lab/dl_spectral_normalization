# Using the filter sizes found here: 
# https://github.com/rharish101/DLGeneralization/blob/master/Mini%20Inception/cifar10_tf_inception.py

import tensorflow as tf
import numpy as np
from .. import sn

def incept(input_x, input_filters, ch1_filters, ch3_filters, spectral_norm=True, scope_name='incept'):
    """Inception module"""
    
    if spectral_norm:
        bn = False
    else:
        bn = True
        
    with tf.variable_scope(scope_name):
        ch1_output = tf.nn.relu(sn.conv2d(input_x, [1, 1, input_filters, ch1_filters],
                                          scope_name='conv_ch1', spectral_norm=spectral_norm,
                                          xavier=True, bn=bn))
        ch3_output = tf.nn.relu(sn.conv2d(input_x, [3, 3, input_filters, ch3_filters],
                                          scope_name='conv_ch3', spectral_norm=spectral_norm,
                                          xavier=True, bn=bn))
        return tf.concat([ch1_output, ch3_output], axis=-1)


def downsample(input_x, input_filters, ch3_filters, spectral_norm=True, scope_name='downsamp'):
    """Downsample module"""
    
    if spectral_norm:
        bn = False
    else:
        bn = True
        
    with tf.variable_scope(scope_name):
        ch3_output = tf.nn.relu(sn.conv2d(input_x, [3, 3, input_filters, ch3_filters],
                                          scope_name='conv_ch3', spectral_norm=spectral_norm,
                                          xavier=True, bn=bn, stride=2))
        pool_output = tf.nn.max_pool(input_x, ksize=[1, 3, 3, 1], strides=[1, 2, 2, 1],
                                     padding='SAME', name='pool')
        return tf.concat([ch3_output, pool_output], axis=-1)


def inception(NUM_CLASSES, wd=0):
    """Mini-inception architecture (note that we do batch norm in absence of spectral norm)"""

    input_data = tf.placeholder(tf.float32, shape=[None, 28, 28, 3], name='in_data')
    input_labels = tf.placeholder(tf.int64, shape=[None], name='in_labels')
    
    layer1 = tf.nn.relu(sn.conv2d(input_data, [3, 3, 3, 96], scope_name='conv1', spectral_norm=False))
    layer2 = incept(layer1, 96, 32, 32, scope_name='incept2', spectral_norm=False)
    layer3 = incept(layer2, 32+32, 32, 48, scope_name='incept3', spectral_norm=False)
    layer4 = downsample(layer3, 32+48, 80, scope_name='downsamp4', spectral_norm=False)
    layer5 = incept(layer4, 80+32+48, 112, 48, scope_name='incept5', spectral_norm=False)
    layer6 = incept(layer5, 112+48, 96, 64, scope_name='incept6', spectral_norm=False)
    layer7 = incept(layer6, 96+64, 80, 80, scope_name='incept7', spectral_norm=False)
    layer8 = incept(layer7, 80+80, 48, 96, scope_name='incept8', spectral_norm=False)
    layer9 = downsample(layer8, 48+96, 96, scope_name='downsamp9', spectral_norm=False)
    layer10 = incept(layer9, 96+48+96, 176, 160, scope_name='incept10', spectral_norm=False)
    layer11 = incept(layer10, 176+160, 176, 160, scope_name='incept11', spectral_norm=False)
    layer12 = tf.nn.pool(layer11, window_shape=[7, 7], pooling_type='AVG', 
                         padding='SAME', strides=[1, 1], name='mean_pool12')
    
    fc = sn.linear(layer12, NUM_CLASSES, scope_name='fc', spectral_norm=False, xavier=True)
        
    return input_data, input_labels, fc


def inception_sn(NUM_CLASSES, wd=0):
    """Mini-inception architecture with spectral normalization on all layers"""

    input_data = tf.placeholder(tf.float32, shape=[None, 28, 28, 3], name='in_data')
    input_labels = tf.placeholder(tf.int64, shape=[None], name='in_labels')
    
    layer1 = tf.nn.relu(sn.conv2d(input_data, [3, 3, 3, 96], scope_name='conv1'))
    layer2 = incept(layer1, 96, 32, 32, scope_name='incept2')
    layer3 = incept(layer2, 32+32, 32, 48, scope_name='incept3')
    layer4 = downsample(layer3, 32+48, 80, scope_name='downsamp4')
    layer5 = incept(layer4, 80+32+48, 112, 48, scope_name='incept5')
    layer6 = incept(layer5, 112+48, 96, 64, scope_name='incept6')
    layer7 = incept(layer6, 96+64, 80, 80, scope_name='incept7')
    layer8 = incept(layer7, 80+80, 48, 96, scope_name='incept8')
    layer9 = downsample(layer8, 48+96, 96, scope_name='downsamp9')
    layer10 = incept(layer9, 96+48+96, 176, 160, scope_name='incept10')
    layer11 = incept(layer10, 176+160, 176, 160, scope_name='incept11')
    layer12 = tf.nn.pool(layer11, window_shape=[7, 7], pooling_type='AVG', 
                         padding='SAME', strides=[1, 1], name='mean_pool12')
    
    fc = sn.linear(layer12, NUM_CLASSES, scope_name='fc', xavier=True)
        
    return input_data, input_labels, fc


def inception_sar(NUM_CLASSES, wd=0):
    """Mini-inception architecture with spectral adversarial regularization"""

    input_data = tf.placeholder(tf.float32, shape=[None, 28, 28, 3], name='in_data')
    input_labels = tf.placeholder(tf.int64, shape=[None], name='in_labels')
    
    layer1 = tf.nn.relu(sn.conv2d(input_data, [3, 3, 3, 96], scope_name='conv1'))
    layer2 = incept(layer1, 96, 32, 32, scope_name='incept2')
    layer3 = incept(layer2, 32+32, 32, 48, scope_name='incept3')
    layer4 = downsample(layer3, 32+48, 80, scope_name='downsamp4')
    layer5 = incept(layer4, 80+32+48, 112, 48, scope_name='incept5')
    layer6 = incept(layer5, 112+48, 96, 64, scope_name='incept6')
    layer7 = incept(layer6, 96+64, 80, 80, scope_name='incept7')
    layer8 = incept(layer7, 80+80, 48, 96, scope_name='incept8')
    layer9 = downsample(layer8, 48+96, 96, scope_name='downsamp9')
    layer10 = incept(layer9, 96+48+96, 176, 160, scope_name='incept10')
    layer11 = incept(layer10, 176+160, 176, 160, scope_name='incept11')
    layer12 = tf.nn.pool(layer11, window_shape=[7, 7], pooling_type='AVG', 
                         padding='SAME', strides=[1, 1], name='mean_pool12')
    
    fc = sn.linear(layer12, NUM_CLASSES, scope_name='fc', spectral_norm=False,
                   xavier=True, wd=wd, l2_norm=True)
        
    return input_data, input_labels, fc