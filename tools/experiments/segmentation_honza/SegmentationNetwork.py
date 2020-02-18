import numpy as np
import tensorflow as tf
import tensorflow.keras as keras
import copy
import time
import random
import json
import importlib
import segmenteddataset


DIM=35+3+1 #35+max(shifts)+1








#precission if we want recall at least r percent.
def precission_at_recall(recall, predictions_true, predictions_false):
    predictions_true=sorted(predictions_true, key=lambda x: -x)
    true_positives=int(  recall*len(predictions_true)  +0.4999)
    if(len(predictions_true)==0):
        minimal_activation=min(predictions_false)-1
    else:
        minimal_activation=predictions_true[true_positives-1]

    false_positives=0
    for x in predictions_false:
        if(x>=minimal_activation):
            false_positives+=1

    return true_positives/(false_positives+true_positives),minimal_activation




class DataPreprocessor:
    #additional_shift:
    #      we may need to shift the labels, so that they correspond more with the way how CNN works.
    #      Let's imagine the word "přijít". We want a convolutional filter to decide, that "při"
    #      is a prefix in the moment it covers (při). But our labels (depending on padding and filter sizes)
    #      may ask it for verdict in the moment when it covers (řij), which cannot result in reasonable results.
    #      This issue may get more complex (or disappear?) with multiple layers of convolutions.

    alphabet="^$qwertyuiopasdfghjklzxcvbnmméěřťžúůíóášďýčň"
    def __init__(self, additional_shift):
        self.additional_shift=additional_shift
        self.alphabet2={}
        i=0
        while i<len(self.alphabet):
            self.alphabet2[self.alphabet[i]]=i+1
            i+=1

    @staticmethod
    def find_separation_indices(word):
        word=word.strip()
        found_spaces=[]
        for i,c in enumerate(word):
            if(c==" " or c=="|"):
                found_spaces.append(i-len(found_spaces))
        return found_spaces

    #undo the additional shift.
    def postprocess_labels(self, labels):
        labels_out=np.zeros(shape=labels.shape, dtype=labels.dtype)
        for i in range(labels.shape[0]):
            for j in range(labels.shape[1]):
                labels_out[i][j]=labels[i][j-1-self.additional_shift]
        return labels_out


    def preprocess_data(self,data):
        maxlen=-1
        for x in data:
            maxlen=max(maxlen,len(x[0]))
        maxlen=maxlen+2+1 #+2 because of ^ and $, +1 because of padding of zeros and ones.
        maxlen=max([maxlen,35,DIM])
        data2_samples=np.zeros(shape=[len(data), maxlen], dtype=np.int32)
        data2_labels=np.zeros(shape=[len(data), maxlen], dtype=np.int32)
        data2_masks=np.zeros(shape=[len(data), maxlen], dtype=np.int32)

        i=0
        for lemma_, segmented in data:
            lemma="^"+lemma_.lower().strip()+"$"
            #now convert the lemma to numbers.
            skip=False
            for c in lemma:
                if(not c in self.alphabet):
                    skip=True
                    break
            if(skip):
                print("skipping "+str(lemma))
                continue
            for j,c in enumerate(lemma):
                data2_samples[i][j]=self.alphabet2[c]
                if(c!="^" and c!="$"):
                    data2_masks[i][j+self.additional_shift]=1
            for j in DataPreprocessor.find_separation_indices(segmented):
                data2_labels[i][j+1+self.additional_shift]=1 #(+1 because of the initial ^ ), +1 because we would rather predict it after we see the letter behind the cut.
            i+=1
        data2_samples=data2_samples[:i]
        data2_labels=data2_labels[:i]
        data2_masks=data2_masks[:i]
        return data2_samples, data2_labels,data2_masks




class NetworkBuilder:
    def __init__(self, session, graph, params):
        params=copy.deepcopy(params)
        self.layers=[]
        self.session=session
        self.graph=graph
        for layer_fn, args in params:
            if(layer_fn==tf.keras.layers.GRU):
                process_output_sequence=args["process_output_sequence"] #1 for sequence outputs, 1 for final state.
                del(args["process_output_sequence"])
                gru=layer_fn(**args)
                self.layers.append(lambda x: gru(x)[1-process_output_sequence])
            else:
                self.layers.append(layer_fn(**args))

    def __call__(self, input, mask=None):
        with self.session.as_default(), self.graph.as_default():
            for layer in self.layers:
                input=layer(input)
        print(input.shape)
        return input

#create the network
class Segmentation_Network:

    def __init__(self, params, name=""):
        self.global_step=0
        self.graph = tf.Graph()
        self.session = tf.compat.v1.Session(graph=self.graph,config=tf.compat.v1.ConfigProto(allow_soft_placement=True,log_device_placement=False))

        self.build(params)
        self.experiment_name="learning_segmentation_from_1k_dataset-"+str(time.time())+name
        self.summary_writer = tf.summary.create_file_writer("outputs\\exp3\\tf_summaries\\cnnXcnnXdense\\"+self.experiment_name)
        with self.summary_writer.as_default():
            tf.summary.text("ModelParams",str(params),step=0)
        self.prepare_summaries()


    #todo: mask also the $ and ^
    def build(self, params):
        self.params=params
        with self.session.as_default(), self.graph.as_default():
            self.net=NetworkBuilder(self.session, self.graph, self.params["net_description"])


            self.character_embeddings=keras.layers.Embedding(len(DataPreprocessor.alphabet)+1, 10, mask_zero=True,name="Embeddings");
            self.samples =tf.keras.backend.placeholder(shape=[None,DIM], dtype=tf.float32,name="Samples")
            self.labels =tf.keras.backend.placeholder(shape=[None,DIM], dtype=tf.int32,name="Labels")
            self.masks =tf.keras.backend.placeholder(shape=[None,DIM], dtype=tf.float32,name="Masks")
            self.class_ballance =tf.keras.backend.placeholder(shape=(), dtype=tf.float32,name="ClassBallance")

            self.labels2=tf.reshape(self.labels,shape=np.array([-1,DIM,1]))
            labels3=tf.cast(self.labels2,dtype=tf.float32)

            #self.mask = self.samples>2 #If character is padding, ^ or $, we do not care about the output.  #self.character_embeddings.compute_mask(self.samples)
            self.masks2=tf.reshape(self.masks, shape=np.array([-1,DIM, 1]))
            self.outputs = self.net(self.character_embeddings(self.samples ))*self.masks2
            #self.outputs = self.outputs*tf.cast(self.mask2,dtype=tf.float32) #false means zero. which means that there will be no gradients going through the masked outputs.
            self.outputs_out=tf.reshape(self.outputs, shape=[-1, DIM]) #tf.squeeze(self.outputs) #tf.nn.softmax(self.outputs, axis=-1)

            partial_loss=(self.outputs-labels3)**2
            self.loss=tf.reduce_mean(labels3*partial_loss+(1-labels3)*self.class_ballance*partial_loss) #tf.reduce_mean(tf.nn.softmax_cross_entropy_with_logits(labels=self.labels, logits=self.outputs))

            #todo: summaries and tensorboard
            self.optimizer=tf.compat.v1.train.AdamOptimizer(learning_rate=0.001)
            self.training=self.optimizer.minimize(self.loss) #, var_list=tf.compat.v1.trainable_variables())
            init = tf.compat.v1.global_variables_initializer()
            self.session.run(init)
            self.saver = tf.compat.v1.train.Saver(tf.compat.v1.trainable_variables())

    def prepare_summaries(self):
        with self.session.as_default(), self.graph.as_default():
            self.summaries_training=[
                            ("StandardTraining/loss", self.loss,tf.summary.scalar),
            ]

        self.summaries_ops_training=list(map(lambda x: x[1], self.summaries_training))
        self.summaries_eval=[
                        ("StandardDevelopment/loss", self.loss,tf.summary.scalar, "average"),
        ]
        self.summaries_ops_eval=list(map(lambda x: x[1], self.summaries_eval))


    def save(self, fname):
        with self.session.as_default(), self.graph.as_default():
            self.saver.save(self.session,fname, global_step=self.global_step)

    def load(self, fname):
        with self.session.as_default(), self.graph.as_default():
            self.saver.restore(self.session,fname)



    def train(self, data,labels,masks, summaries=False):
        #class_balance is count of ones divided by the number of zeros. We then compute "loss for label zero" with this number and we are done
        counts=[0,0]
        for i in range(0, data.shape[0]):
            for j in range(0, data.shape[1]):
                if(masks[i][j]!=0): #if not masked.
                    counts[labels[i][j]]+=1
        num_zeros=counts[0]
        num_ones=counts[1]
        #print("Class counts:"+str(counts))
        class_ballance=num_ones/num_zeros
        ops=[self.training,self.loss]
        if(summaries):
            ops+=self.summaries_ops_training
        outputs=self.session.run(ops, feed_dict={self.samples:data,self.labels:labels,self.masks:masks, self.class_ballance:class_ballance})
        #write summaries
        shift=len(outputs)-len(self.summaries_training)
        if(summaries):
            with self.summary_writer.as_default():
                tf.summary.scalar("StandardTraining/class_ballance", class_ballance, step=self.global_step)
                tf.summary.scalar("StandardTraining/percentage_of_ones", num_ones/(num_ones+num_zeros), step=self.global_step)
                for i,(name, _, summary_type) in enumerate(self.summaries_training):
                    summary_type(name, outputs[shift+i], step=self.global_step)
                #network.summary_writer.flush()
        self.global_step+=1
        return outputs

    def compute_predictions(self, data, masks):
        return self.session.run([self.outputs_out], feed_dict={self.samples:data, self.masks:masks})



    def evaluate(self, data,labels,masks, name_prefix=""):
        #loss,outputs,mask=self.session.run([self.loss,self.outputs_out,self.mask2], feed_dict={self.samples:data,
        #                                                             self.labels:labels,self.class_ballance:1})
        counts=[0,0]
        for i in range(0, data.shape[0]):
            for j in range(0, data.shape[1]):
                if(masks[i][j]!=0): #if not masked.
                    counts[labels[i][j]]+=1
        num_zeros=counts[0]
        num_ones=counts[1]

        class_ballance=num_ones/num_zeros
        with self.summary_writer.as_default():
            tf.summary.scalar(name_prefix+"Evaluation/class_ballance", class_ballance, step=self.global_step)
            tf.summary.scalar(name_prefix+"Evaluation/percentage_of_ones", num_ones/(num_ones+num_zeros), step=self.global_step, description="Percentage of ones among the nonmasked labels.")


        outputs=[]
        for i,(name, tensor, summary_type, combination_type) in enumerate(self.summaries_eval):
            if(combination_type=="average"):
                outputs.append(0.0)
            elif(combination_type=="append"):
                outputs.append([])
            else:
                outputs.append(None)
                raise NotImplementedError("unknown evaluation summary reduction operation")

        batch_size=256
        k=0
        maxk=len(data)
        masks_out=[]
        predictions=[]
        while k<maxk:
            cnt=min(maxk-k,batch_size)

            #Preprocess data
            data2  =data[k:k+batch_size]
            labels2=labels[k:k+batch_size]
            masks2=masks[k:k+batch_size]

            #Computing outputs for one batch
            out=self.session.run([self.masks2,self.outputs_out]+self.summaries_ops_eval, feed_dict={self.samples:data2,self.masks:masks2,
                                                                                  self.labels:labels2, self.class_ballance:1})
            #print(out[0])
            masks_, predictions_=out[:2]
            masks_out.append(masks_)
            predictions.append(predictions_)
            out=out[2:]

            #Intermediate aggregation
            for i,summary_data in enumerate(out):
                combination_type=self.summaries_eval[i][3]
                if(combination_type=="average"):
                    outputs[i]+=summary_data*cnt
                elif(combination_type=="append"):
                    outputs[i].append(summary_data)
                else:
                    outputs.append(None)
                    raise NotImplementedError("unknown evaluation summary reduction operation")
            k+=batch_size

        predictions=np.concatenate(predictions,axis=0)
        masks=np.concatenate(masks_out,axis=0)

        predictions_true=[]
        predictions_false=[]
        for i in range(labels.shape[0]):
            for j in range(labels.shape[1]): #TODO: are we counting also ^ and $?
                if(masks[i][j]):
                    if(labels[i][j]==0):
                        predictions_false.append(predictions[i][j])
                    elif(labels[i][j]==1):
                        predictions_true.append(predictions[i][j])
                    else:
                        raise Exception("should never happen")


        prec_at_rec={}
        with self.summary_writer.as_default():
            tf.summary.histogram(name=name_prefix+"Evaluation/PredictionsTrue", data=predictions_true,  step=self.global_step, description="How big likelihood of segmentation line does the network assign to a place where it should draw a segmentation boundary.")
            tf.summary.histogram(name=name_prefix+"Evaluation/PredictionsFalse",data=predictions_false, step=self.global_step, description="How big likelihood of segmentation line does the network assign to a place where it should NOT draw a segmentation boundary.")

            for recall in [0.1,0.25,0.5,0.75,0.9,0.95]:
                precission,minimal_activation=precission_at_recall(recall, predictions_true, predictions_false)
                prec_at_rec[recall]=(precission,minimal_activation)
                tf.summary.scalar(name=name_prefix+"Evaluation/PrecissionAt"+str(int(recall*100))+"PercentRecall",data=precission, step=self.global_step, description="Precission for k% recall. If we want k% recall, we will have this good a precission.")
                tf.summary.scalar(name=name_prefix+"Evaluation-DecissionBoundaries/PrecissionAt"+str(int(recall*100))+"PercentRecall_decission_boundary",data=minimal_activation, step=self.global_step, description="If this threshold is exceeded, there is a segment.")

        #Final aggregation
        for i in range(len(outputs)):
            combination_type=self.summaries_eval[i][3]
            if(combination_type=="average"):
                outputs[i]/=maxk
            elif(combination_type=="append"):
                outputs[i]=np.concatenate(outputs[i], axis=0)
            else:
                outputs.append(None)
                raise NotImplementedError("unknown evaluation summary reduction operation")

        #Write summaries
        with self.summary_writer.as_default():
            for i,(name, tensor, summary_type, reduction_type) in enumerate(self.summaries_eval):
                summary_type(name_prefix+"Evaluation/"+name, outputs[i], step=self.global_step)
            #network.summary_writer.flush()


        return outputs,prec_at_rec





class NetworkSegmentationPredictor:
    def __init__(self, params, shift, decission_boundary, fname):
        self.params=params
        self.shift=shift
        self.network=Segmentation_Network(params, name="networkPredictor"+str(time.time()))
        self.network.load(fname)
        self.preprocessor=DataPreprocessor(shift)
        self.decission_boundary=decission_boundary

    def predict_likelihoods(self,words):
        if(type(words[0])==str):
            words2=[]
            for w in words:
                words2.append((w,w))
            words=words2
        samples, extracted_labels, masks=self.preprocessor.preprocess_data(words)
        predictions=self.network.compute_predictions(samples, masks)[0]
        predictions=self.preprocessor.postprocess_labels(predictions)
        predictions2=[]
        for i in range(predictions.shape[0]):
            predictions2.append([])
            for j in range(predictions.shape[1]):
                if(masks[i][j]==1):
                    predictions2[-1].append(predictions[i][j])
        return predictions2

    def predict_segments_with_likelihoods(self,words):
        segments=[]
        predictions=self.predict_likelihoods(words)
        for i in range(len(predictions)):
            segments.append([])
            for j in range(len(predictions[i])):
                segments[-1].append((j, predictions[i][j]))
        return segments

    def predict_segments(self,words):
        segments=[]
        predictions=self.predict_likelihoods(words)
        for i in range(len(predictions)):
            segments.append(set())
            for j in range(len(predictions[i])):
                if(predictions[i][j]>=self.decission_boundary):
                    segments[-1].add(j)
        return segments

















architecture=[
    (tf.keras.layers.Conv1D, {"filters":200, "kernel_size":4, "strides":1, "activation":tf.nn.relu, "use_bias":True, "padding":"same"}),
    (tf.keras.layers.Conv1D, {"filters":200,   "kernel_size":4, "strides":1, "activation":tf.nn.relu, "use_bias":True, "padding":"same"}),
    (tf.keras.layers.Dense, {"units":1, "activation":tf.math.sigmoid, "use_bias":True})
]
Predictor1=None
try:
    Predictor1=NetworkSegmentationPredictor(params={"net_description":architecture}, shift=-1, decission_boundary=0.9792, fname="segmentation-cnnXcnnXdense-f200-ks4-acR-160")
except Exception as e:
    print("Error while constructiong predictor "+str(e))

#ok oversegmentation undersegmentation
#440 18 443