#results of random prediction:
#if I have 2/3 of zeros class and 1/3 of ones, then I will observe class ballance of 0.5 and for recall of r%, I'll have to pick samples with likelihood of r%, which will result in precission r% * ones / (r%* zeros + r% * ones) = ones% recall

#results: cnnXdense <=50%, cnnxcnn1xcnn ~ 60%, gru <= 38%


#TODO: compute F1 score
#TODO: use additional information for training (e.g. class of word)

####
#Load data
import numpy as np
import tensorflow as tf
import tensorflow.keras as keras
import copy
import time
import random
import json
import importlib
import segmenteddataset
importlib.reload(segmenteddataset)

train=segmenteddataset.train
devel=segmenteddataset.devel
test =segmenteddataset.test

####
#Preprocess data
import SegmentationNetwork
importlib.reload(SegmentationNetwork)

train2={}
devel2={}
test2={}
shifts=[-1,0,1,2,3]
preprocessors={}
for shift in shifts:
    dp=SegmentationNetwork.DataPreprocessor(shift)
    preprocessors[shift]=dp
    train2[shift]=dp.preprocess_data(train)
    devel2[shift]=dp.preprocess_data(devel)
    test2[shift]=dp.preprocess_data(test)


###### Test various architectures
##
architectures=[]

for recurrent_dropout  in [0,0.5]:
    for filters in [30,50,100,200,400]:
        for units in [10,20,30,50,80,100,200]:
                name="cnnXgruXdense-f%s-u%s-rd%s"%(filters, units, recurrent_dropout)
                arch=[(tf.keras.layers.Conv1D, {"filters":filters, "kernel_size":3, "strides":1, "activation":tf.nn.sigmoid, "use_bias":True, "padding":"same"}),
                    (tf.keras.layers.GRU, {"units":units, "return_sequences":True, "return_state":False, "process_output_sequence":1, "recurrent_dropout":recurrent_dropout}),
                    (tf.keras.layers.Dense, {"units":1, "activation":tf.math.sigmoid, "use_bias":True})]
                architectures.append((name,arch))

for filters in [10,20,30,50,80,100,200,400,1000]:
    for kernel_size in [3,4,5]:
        for activation,ac_name in [(tf.math.sigmoid,"S"), (tf.math.tanh, "T"), (tf.nn.relu, "R")]:
            name="cnnXdense-f%s-ks%s-ac%s"%(filters, kernel_size,ac_name)
            arch=[(tf.keras.layers.Conv1D, {"filters":filters, "kernel_size":kernel_size, "strides":1, "activation":activation, "use_bias":True, "padding":"same"}),
                  (tf.keras.layers.Dense, {"units":1, "activation":tf.math.sigmoid, "use_bias":True})]
            architectures.append((name,arch))


for units in [10,20,30,50,80,100,200,400,1000]:
            name="gruXdense-u%s"%(units,)
            arch=[(tf.keras.layers.GRU, {"units":units, "return_sequences":True, "return_state":False, "process_output_sequence":1}),
                  (tf.keras.layers.Dense, {"units":1, "activation":tf.math.sigmoid, "use_bias":True})]
            architectures.append((name,arch))




for filters in [30,50,80,100,200,400,1000]:
    for bottleneck in [30,50,100,200]:
        for dummy_bottleneck in [0, 1]:
            if(bottleneck>filters):
                continue
            for kernel_size in [3,4,5]:
                for activation,ac_name in [(tf.math.sigmoid,"S"), (tf.math.tanh, "T"), (tf.nn.relu, "R")]:
                    name="cnnXcnn1x1XcnnXdense-f%s-b%s-dum%s-ks%s-ac%s"%(filters,bottleneck,dummy_bottleneck, kernel_size,ac_name)
                    if(dummy_bottleneck==1):
                        bottleneck_activation=None
                        bottleneck_bias=False
                    else:
                        bottleneck_activation=activation
                        bottleneck_bias=True
                    arch=[(tf.keras.layers.Conv1D, {"filters":filters, "kernel_size":kernel_size, "strides":1, "activation":activation, "use_bias":True, "padding":"same"}),
                        (tf.keras.layers.Conv1D, {"filters":bottleneck,"kernel_size":1, "strides":1, "activation":bottleneck_activation, "use_bias":bottleneck_bias, "padding":"same"}),
                        (tf.keras.layers.Conv1D, {"filters":filters,   "kernel_size":kernel_size, "strides":1, "activation":activation, "use_bias":True, "padding":"same"}),
                        (tf.keras.layers.Dense, {"units":1, "activation":tf.math.sigmoid, "use_bias":True})]
                    architectures.append((name,arch))


for filters in [30,50,80,100,200,400,1000]:
    for kernel_size in [3,4,5]:
        for activation,ac_name in [(tf.math.sigmoid,"S"), (tf.math.tanh, "T"), (tf.nn.relu, "R")]:
            name="cnnXcnnXdense-f%s-ks%s-ac%s"%(filters, kernel_size,ac_name)
            arch=[(tf.keras.layers.Conv1D, {"filters":filters, "kernel_size":kernel_size, "strides":1, "activation":activation, "use_bias":True, "padding":"same"}),
                (tf.keras.layers.Conv1D, {"filters":filters,   "kernel_size":kernel_size, "strides":1, "activation":activation, "use_bias":True, "padding":"same"}),
                (tf.keras.layers.Dense, {"units":1, "activation":tf.math.sigmoid, "use_bias":True})]
            architectures.append((name,arch))

architectures=[]

print(len(architectures))
random.seed(42)
random.shuffle(architectures)



#TODO: different losses? e.g two outputs and cross entropy.
#TODO: different size of embedding? Didn't seem to change anything

#TODO: try to feed GRU with information whether it created a new segment within the last step?



fout=open("outputs\\exp3\\experiment_log4.txt","a", 1024**2)
i=0
for arch_name,architecture in architectures:
    i+=1
    params={"net_description":architecture}
    print("Training %s (%s/%s)"%(arch_name, i,len(architectures)))
    start_arch=time.time()
    for shift in shifts:
        for cv in range(2):
            name2="%s_sft%s_cv%s"%(arch_name,shift, cv+1)
            network=SegmentationNetwork.Segmentation_Network(params, name=name2)
            max_=160
            start=time.time()
            for x in range(max_):
                network.train(train2[shift][0],train2[shift][1],train2[shift][2], summaries=(x%3==0 or x==max_-1))

                if(x%3==0 or x==max_-1):
                    outputs_tr,prec_at_rec_tr=network.evaluate(train2[shift][0],train2[shift][1],train2[shift][2],"TrainingSet")
                    outputs_dev,prec_at_rec_dev=network.evaluate(devel2[shift][0],devel2[shift][1],devel2[shift][2], "DevelSet")
                if(x%20==0 or x==max_-1):
                    fout.write(str([name2,prec_at_rec_tr,prec_at_rec_dev, params, shift, cv])+"\n")
            print("still training %s (%s/%s)"%(arch_name, i,len(architectures)))
            print(time.time()-start)
    print(time.time()-start_arch)
fout.close()



###


shift=-1 #!!!

filters=200
kernel_size=4
activation,ac_name=(tf.nn.relu, "R")
arch_name="cnnXcnnXdense-f%s-ks%s-ac%s"%(filters, kernel_size,ac_name)
architecture=[(tf.keras.layers.Conv1D, {"filters":filters, "kernel_size":kernel_size, "strides":1, "activation":activation, "use_bias":True, "padding":"same"}),
    (tf.keras.layers.Conv1D, {"filters":filters,   "kernel_size":kernel_size, "strides":1, "activation":activation, "use_bias":True, "padding":"same"}),
    (tf.keras.layers.Dense, {"units":1, "activation":tf.math.sigmoid, "use_bias":True})]

params={'net_description':architecture}


name2="%s_sft%s"%(arch_name,shift)
network=SegmentationNetwork.Segmentation_Network(params, name=name2)

def load_network(network,fname="segmentation-cnnXcnnXdense-f200-ks4-acR-160"):
    network.load(fname)



def train_network(train2,devel2, network, arch_name):
    max_=160
    for x in range(max_):
        network.train(train2[shift][0],train2[shift][1],train2[shift][2], summaries=(x%3==0 or x==max_-1))
        if(x%3==0 or x==max_-1):
            outputs_tr,prec_at_rec_tr=network.evaluate(train2[shift][0],train2[shift][1],train2[shift][2],"TrainingSet")
            outputs_dev,prec_at_rec_dev=network.evaluate(devel2[shift][0],devel2[shift][1],devel2[shift][2], "DevelSet")


    network.save("segmentation-"+arch_name)


train_network(train2,devel2, network, arch_name)