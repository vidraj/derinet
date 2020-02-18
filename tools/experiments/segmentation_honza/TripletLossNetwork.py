#lets train a simple neural network - rnn or maybe cnn + triplet loss
#TODO: Evaluation should be done via the nearest neighbors search.
#      (find k closest neighbors among all the words, and see, on which position there actually are the other related lemmas)
#We would like to use this net for segmentation via the following strategy:
#  1] train the net to recognize derivations
#  2] compute the representation of the word which we want to separate -> rnn(word)
#  3] remove a part of the word (e.g first letter or two), and compute -> rnn(word[1:])
#  4] measure the distance between rnn(word) and rnn(word[1:]). If it is small (smaller than "margin"?),
#     then we can draw a line between the first and other letters of the word, since there probably is a border
#TODO: For this mechanism to work we need a GOOD method of sampling of negative samples, so that the network does
#      not converge to something as simple as just computing the edit distance.
#      Also, measurements show that after quite a short time, most samples are sufficiently far appart and therefore are not part of the loss function. Only around 1% remains. But training on this one percent further improves the results.
#
#TODO: Maybe we can use a different approach: using also children which are further appart (watch out for trees with thousands of words!)
#      as positive samples during the training. This could lead the network to focus more on the prefixes and suffixes, etc.

import time
import hashlib
import importlib
import tensorflow as tf
import tensorflow.keras as keras
import numpy as np
from TripletLossDataPreparation import *


class TripletLoss_RNN_Network:
    #gets standard words as inputs. Returns a numpy array with zero padding on the right side.
    def preprocess_data(self,data):
        maxlen=-1
        for x in data:
            maxlen=max(maxlen,len(x))
        maxlen=max(35,maxlen)
        data2=np.zeros(shape=[len(data), maxlen], dtype=np.int32)
        for i,x in enumerate(data):
            for j,y in enumerate(x):
                data2[i][j]=self.alphabet2[y]+1 #+1 so that 0 remains only on the masked positions
        return data2

    def __init__(self, name,params={"margin":0.5-0.4, "representation_net":"cnn2", "representation_net_params":None, "learning_rate_decay_by":0.5**0.25, "learning_rate_decay_every":5-5 }):
        self.epoch=0
        self.params=params
        if(params["representation_net"]=="cnn1"):
            params["representation_net"]=self.cnn1
        elif(params["representation_net"]=="cnn2"):
            params["representation_net"]=self.cnn2
        elif(params["representation_net"]=="gru"):
            params["representation_net"]=self.gru
        else:
            raise NotImplementedError("Unknown net")


        self.global_step=1
        self.alphabet="^$qwertyuiopasdfghjklzxcvbnmméěřťžúůíóášďýčň"
        self.alphabet2={}

        i=0
        while i<len(self.alphabet):
            self.alphabet2[self.alphabet[i]]=i
            i+=1



        self.graph = tf.Graph()
        self.session = tf.compat.v1.Session(graph=self.graph,config=tf.compat.v1.ConfigProto(allow_soft_placement=True,log_device_placement=False))
        self.build_net(params)

        MODEL_DESCRIPTION="""
                Stamdard tripplet loss model. Uses purely random selection of tripplets (no e.g. adversarial sampling).
                We select all pairs and for each pick a random tripplet. The two positive samples are parrent and child in the derivation tree.
                Then after 10 epochs we start selecting random word pairs (not necessarily related) from each of the big trees (>10 nodes) and train on this data.
                Each epoch has it's own set of randomly generated samples.
            """
        hash=hashlib.sha1(bytes(MODEL_DESCRIPTION, "utf-8")).hexdigest()[:4]

        self.experiment_name=name+"_"+str(time.time())+"_"+hash
        self.summary_writer = tf.summary.create_file_writer("tf_summaries4\\"+self.experiment_name)
        with self.summary_writer.as_default():
            tf.summary.text("ModelParams",str(params),step=0)
            tf.summary.text("ModelDescription",hash+"\n"+MODEL_DESCRIPTION,step=0)

        self.prepare_summaries()


        with self.session.as_default(), self.graph.as_default():
            init = tf.compat.v1.global_variables_initializer()
            self.session.run(init)
            self.saver = tf.compat.v1.train.Saver(tf.compat.v1.trainable_variables())

    gru_=None
    def gru(self, input_tensor, params, mask=None):
        if(params==None):
            params={"state_size":200}
        if(self.gru_==None):
            with self.session.as_default(), self.graph.as_default():
                self.gru_=tf.keras.layers.GRU(params["state_size"], return_sequences=False, return_state=True, name="GRU1")
        states, final_state=self.gru_(input_tensor)
        return final_state

    cnn2_=None
    def cnn2(self, input_tensor, params,mask=None): #what about a simple one layer cnn? then reducemax on activations of each filter on different positions
        if(self.cnn2_==None):
            self.cnn2_=[tf.keras.layers.Conv1D(filters=200,kernel_size=4,strides=1,activation=tf.math.tanh, use_bias=True),
                        tf.keras.layers.Dense(200,use_bias=True, activation=tf.math.tanh),
                        lambda x: tf.reduce_max(x,axis=-2)
                        ]

        input=input_tensor
        for layer in self.cnn2_:
            input=layer(input)
        return input

    cnn1_=None
    def cnn1(self, input_tensor, params,mask=None): #what about a simple one layer cnn? then reducemax on activations of each filter on different positions
        if(self.cnn1_==None):
            self.cnn1_=[tf.keras.layers.Conv1D(filters=200,kernel_size=4,strides=1,activation=tf.math.tanh, use_bias=True),
                        lambda x: tf.reduce_max(x,axis=-2),
                        tf.keras.layers.Dense(100,use_bias=True, activation=tf.math.tanh)]

        input=input_tensor
        for layer in self.cnn1_:
            input=layer(input)
        return input

    def build_net(self, PARAMS):
        with self.session.as_default(), self.graph.as_default():
            net=lambda x,mask: PARAMS["representation_net"](x, params=PARAMS["representation_net_params"],mask=mask)
            self.learning_rate=tf.Variable(0.001, dtype=np.float32, trainable=False, name="LearningRate")
            self.distance_threshold=tf.Variable(PARAMS["margin"], dtype=np.float32, trainable=False, name="DistanceThreshold")
            self.character_embeddings=keras.layers.Embedding(len(self.alphabet)+1, 10, mask_zero=True,name="Embeddings");


            #Placeholders
            self.central_samples =tf.keras.backend.placeholder(shape=[None,35], dtype=tf.float32,name="CentralSamples")
            self.positive_samples=tf.keras.backend.placeholder(shape=[None,35], dtype=tf.float32,name="PositiveSamples")
            self.negative_samples=tf.keras.backend.placeholder(shape=[None,35], dtype=tf.float32,name="NegativeSamples")

            #Compute representations
            mask_central = self.character_embeddings.compute_mask(self.central_samples)
            self.representation_central =net(self.character_embeddings(self.central_samples ), mask=mask_central)

            mask_positive = self.character_embeddings.compute_mask(self.positive_samples)
            self.representation_positive=net(self.character_embeddings(self.positive_samples), mask=mask_positive)

            mask_negative = self.character_embeddings.compute_mask(self.negative_samples)
            self.representation_negative=net(self.character_embeddings(self.negative_samples), mask=mask_negative)

            #Compute distances in pairs.
            self.positive_distance=tf.reduce_mean((self.representation_central-self.representation_positive)**2, axis=-1)
            self.negative_distance=tf.reduce_mean((self.representation_central-self.representation_negative)**2, axis=-1)


            #Compute loss and prepair training.
            self.loss=tf.reduce_mean(tf.maximum(self.positive_distance-self.negative_distance+self.distance_threshold,0))
            self.optimizer=tf.compat.v1.train.AdamOptimizer(learning_rate=self.learning_rate)
            self.training=self.optimizer.minimize(self.loss) #, var_list=tf.compat.v1.trainable_variables())


    def prepare_summaries(self):
        with self.session.as_default(), self.graph.as_default():
            self.positive_distance_eval=tf.reduce_mean(self.positive_distance)
            self.negative_distance_eval=tf.reduce_mean(self.negative_distance)

            self.percentage_closer=tf.reduce_mean(tf.cast(self.positive_distance<self.negative_distance, dtype=tf.float32))
            self.percentage_trainable=tf.reduce_mean(tf.cast(self.positive_distance-self.negative_distance>0, dtype=tf.float32))

            self.summaries_training=[
                            ("StandardTraining/loss", self.loss,tf.summary.scalar),
                            ("StandardTraining/positive_distance", self.positive_distance,tf.summary.histogram),
                            ("StandardTraining/negative_distance", self.negative_distance,tf.summary.histogram),
                            ("StandardTraining/positive_distance_mean", self.positive_distance_eval,tf.summary.scalar),
                            ("StandardTraining/negative_distance_mean", self.negative_distance_eval, tf.summary.scalar),
                            ("StandardTraining/learning_rate", self.learning_rate, tf.summary.scalar),
                            ("StandardTraining/PercentageCloser",
                                self.percentage_closer,
                                lambda name,data,step:tf.summary.scalar(name,data,step,"How big percentage of central samples is closer to their positive sample than to the negative. 1 is best."),
                            ),
                            ("StandardTraining/PercentageTrainable",
                                self.percentage_trainable,
                                lambda name,data,step:tf.summary.scalar(name,data,step,"Tripplets, which are sufficiently far appart are not part of the loss function. This is percentage of those that remain."),
                            ),
            ]
            self.summaries_ops_training=list(map(lambda x: x[1], self.summaries_training))


            self.summaries_eval=[
                            ("StandardDevelopment/loss", self.loss,tf.summary.scalar, "average"),
                            ("StandardDevelopment/positive_distance", self.positive_distance,tf.summary.histogram,"append"),
                            ("StandardDevelopment/negative_distance", self.negative_distance,tf.summary.histogram,"append"),
                            ("StandardDevelopment/positive_distance_mean", self.positive_distance_eval,tf.summary.scalar, "average"),
                            ("StandardDevelopment/negative_distance_mean", self.negative_distance_eval, tf.summary.scalar,"average"),
                            ("StandardDevelopment/PercentageCloser",
                                self.percentage_closer,
                                lambda name,data,step:tf.summary.scalar(name,data,step,"How big percentage of central samples is closer to their positive sample than to the negative. 1 is best."),
                                "average"
                            ),
            ]
            self.summaries_ops_eval=list(map(lambda x: x[1], self.summaries_eval))


    def train_batch(self, data, summaries=False):
        (pos,neg,cen)=data
        data=self.session.run([self.training,self.loss]+self.summaries_ops_training, feed_dict={self.positive_samples:pos,
                                                        self.negative_samples:neg,self.central_samples:cen})
        shift=len(data)-len(self.summaries_training)

        with self.summary_writer.as_default():
            for i,(name, _, summary_type) in enumerate(self.summaries_training):
                summary_type(name, data[shift+i], step=self.global_step)
            self.global_step+=1
            self.summary_writer.flush()
        return data


    def end_of_epoch(self):
        if(self.params["learning_rate_decay_every"]!=None and self.params["learning_rate_decay_every"]!=0 and self.epoch!=0 and self.epoch%self.params["learning_rate_decay_every"]==0):
            with self.session.as_default(), self.graph.as_default():
                self.session.run([self.learning_rate.assign(self.learning_rate*self.params["learning_rate_decay_by"])])
        self.epoch+=1

    def compute_representations(self, data):
        return self.session.run([self.representation_positive], feed_dict={self.positive_samples:data})[0]


    def save(self, fname):
        with self.session.as_default(), self.graph.as_default():
            self.saver.save(self.session,fname, global_step=self.global_step)

    def load(self, fname):
        with self.session.as_default(), self.graph.as_default():
            self.saver.restore(self.session,fname)

    #!!! THIS TAKES RAW DATA!!!
    def evaluate(self, all_raw_data, summary_name_prefix):
        (pos,neg,cen)=all_raw_data

        #Set initial values for aggregated variables
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
        maxk=len(pos)
        while k<maxk:

            cnt=min(maxk-k,batch_size)

            #Preprocess data
            pos2=self.preprocess_data(pos[k:k+batch_size])
            neg2=self.preprocess_data(neg[k:k+batch_size])
            cen2=self.preprocess_data(cen[k:k+batch_size])


            #Computing outputs for one batch
            data=self.session.run(self.summaries_ops_eval, feed_dict={self.positive_samples:pos2,
                                                                      self.negative_samples:neg2,
                                                                      self.central_samples:cen2})

            #Intermediate aggregation
            for i,summary_data in enumerate(data):
                combination_type=self.summaries_eval[i][3]
                if(combination_type=="average"):
                    outputs[i]+=summary_data*cnt
                elif(combination_type=="append"):
                    outputs[i].append(summary_data)
                else:
                    outputs.append(None)
                    raise NotImplementedError("unknown evaluation summary reduction operation")
            k+=batch_size

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
                summary_type(summary_name_prefix+name, outputs[i], step=self.global_step)
            self.summary_writer.flush()
        return data



        return outputs




















def train_epoch(network, data):
    pos,neg,cen=data
    i=0
    maxi=len(neg)
    batch_size=512
    while i<maxi:
        i1=i
        i2=i+batch_size
        out=network.train_batch(
                (
                    network.preprocess_data(pos[i1:i2]),
                    network.preprocess_data(neg [i1:i2]),
                    network.preprocess_data(cen[i1:i2])
                )
            )
        loss=out[1]
        if(i%4096==0):
            print(loss)
        i+=batch_size
    network.end_of_epoch()




def train_hard_batch(network, selected_train_words,skip_number=5):
    #prepare positive and central samples
    pos=[]
    cen=[]
    pos_tree_id=[]

    i=0
    while i<512*8:
        tree_id=random.randint(0,len(selected_train_words)-1) #TODO: Maybe we want to systematically go through samples of thys type
        idx_p=random.randint(0,len(selected_train_words[tree_id])-1)
        idx_c=random.randint(0,len(selected_train_words[tree_id])-2)
        if(idx_p==idx_c):
            idx_c=len(selected_train_words[tree_id])-1
        p=selected_train_words[tree_id][idx_p]
        c=selected_train_words[tree_id][idx_c]
        pos.append("^"+p+"$")
        cen.append("^"+c+"$")
        pos_tree_id.append(tree_id)
        i+=1


    cen_representations=network.compute_representations(network.preprocess_data(cen))


    #negative samples from which we will pick
    neg=getter.get_next(10**4 *2)
    neg2=list(map(lambda x: x[0],neg))
    neg_representations=network.compute_representations(network.preprocess_data(neg2))

    #compute and argsort distances
    c=cen_representations
    n=neg_representations

    ab=-2 * ( np.matmul( n,c.transpose() ) )

    a=(n**2).sum(axis=1).reshape((-1,1))

    b=(c**2).sum(axis=1)
    b=b.reshape((1,-1))

    distances=a+ab+b
    distances=distances.transpose()
    distances=np.argsort(distances, axis=1)
    print(distances)

    neg_selected=[]
    for i,word in enumerate(pos):
        #we skip 5 hardest samples to avoid really weird samples.
        #Well, after some time of adversarial training it can happen, that even 5 is not always enough,
        #because of somewhat related words in different trees. So we may start skipping more.
        #e.g. (^zesumírovatelnost$', '^vysumírovaný$', '^sesumírovávání$'), or
        #     ('^nahoditelný$', '^povyhazovat$', '^předhazovaný$'), ('^štěrkařsky$', '^štěrkařka$', '^stěrkovost$')
        for index_of_closest_neighbor in distances[i][skip_number:]:
            if(neg[index_of_closest_neighbor][1]!=pos_tree_id[i]): #they are not from the same tree
                break
        neg_selected.append(neg[index_of_closest_neighbor][0])

    samples=[]
    for i in range(len(pos)):
        samples.append((pos[i],cen[i],neg_selected[i]))
    print(samples[:10])
    out=network.train_batch(
            (
                network.preprocess_data(pos),
                network.preprocess_data(neg_selected),
                network.preprocess_data(cen)
            )
        )








def evaluate(network, data, summary_name_prefix=""):
    pos,neg,cen=data
    out=network.evaluate((pos,neg,cen),summary_name_prefix)
    return out




#  train on hard samples
#We've chosen this way because it is way faster than all the other ways
class Getter:
    def __init__(self, dataset):
        self.all_words=[]
        for word,tree_id in dataset:
            if(word[0]!="^"):
                word="^"+word
            if(word[-1]!="$"):
                word=word+"$"
            self.all_words.append((word,tree_id))
        self.last=0
        self.len=len(dataset)

    def get_next(self,n=10000):
        if(self.last+n>self.len):
            random.shuffle(self.all_words)
            self.last=0
        out=self.all_words[self.last:self.last+n]
        self.last+=n
        return out



def do_the_training(network, train_words, devel_words,devel_all_pairs ):
    all_words_with_classes=[]
    for tree_id,tree_words in enumerate(train_words):
        for word in tree_words:
            all_words_with_classes.append((word,tree_id))

    getter=Getter(all_words_with_classes)


    selected_train_words=[]
    for x in train_words:
        if(len(x)>=5):
            selected_train_words.append(x)




    #TODO: evaluovat tak, že se ptám, zda ten kořen netrefím aspoň napodruhé
    #TODO: měřit vzdálenost kořene od průměru reprezentací slov v daném stromě.

    total_iterations=-1
    for x in range(-10, 100+30+127): #puvodni rozsah byl (-10, 130). Ten skončil v global stepu 2.481k. Po global stepu 4.751k to už nikam neroste
        total_iterations+=1
        if(0<=x<10):
            with network.summary_writer.as_default():
                tf.scalar.summary("StandardTraining/SampleType", 1, step=total_iterations)
                tf.scalar.summary("StandardTraining/SampleType2", 1, step=network.global_step)
            print("preparing data for next epoch")
            #pos,neg,cen=generate_standard_triplets_from_all_pairs(train_all_pairs)
            pos,neg,cen=generate_standard_triplets_from_whole_trees(train_words) #generate_standard_triplets(train_pairs)
            print("running epoch "+str(x))
            train_epoch(network,(pos,neg,cen))

        elif(x<40):
            with network.summary_writer.as_default():
                tf.summary.scalar("StandardTraining/SampleType", 2, step=total_iterations)
                tf.summary.scalar("StandardTraining/SampleType2", 2, step=network.global_step)
            #adding this significantly improves results on development set for equally generated data.
            #(SampleFromBigTrees-StandardDevelopment/PercentageCloser improves by 2 percentage points)
            print("preparing data for next epoch (samples from big trees, which are often further appart)")
            pos,neg,cen=generate_standard_triplets_from_whole_big_trees(train_words)
            print("running epoch "+str(x))
            train_epoch(network, (pos,neg,cen))
        elif(x<70):
            with network.summary_writer.as_default():
                tf.summary.scalar("StandardTraining/SampleType", 3, step=total_iterations)
                tf.summary.scalar("StandardTraining/SampleType2", 3, step=network.global_step)
            for i in range(10):
                train_hard_batch(network, selected_train_words)
        else:
            with network.summary_writer.as_default():
                tf.summary.scalar("StandardTraining/SampleType", 4, step=total_iterations)
                tf.summary.scalar("StandardTraining/SampleType2", 4, step=network.global_step)
            for i in range(10):
                train_hard_batch(network, selected_train_words,10) #PERCENTAGE TRAINABLE DROPPED FROM 5% to 2.7%!!
        if(x<10 or x>=40 or abs(x)%3==0):
            print("evaluating")
            #training on all_pairs is able to optimize all the losses.
            pos,neg,cen=generate_standard_triplets_from_all_pairs(devel_all_pairs) #generate_standard_triplets(devel)
            outputs=evaluate(network, (pos,neg,cen), "SampleFromAllPairs-")

            pos,neg,cen=generate_standard_triplets(devel_pairs)
            outputs=evaluate(network, (pos,neg,cen), "OnePairPerTree-")

            pos,neg,cen=generate_standard_triplets_from_whole_trees(devel_words)
            outputs=evaluate(network, (pos,neg,cen), "SampleFromTrees-")

            pos,neg,cen=generate_standard_triplets_from_whole_big_trees(devel_words)
            outputs=evaluate(network, (pos,neg,cen), "SampleFromBigTrees-")
            print(outputs)
            eval_detect_root2(network)


        #todo: regularly run also the nearest neighbor evaluation, and the segmentation evaluation
        print("running knn_evaluation")
    model_fname="tfsaves\\tf_tripletloss_model_"+str(time.time())
    network.save(model_fname)
    return model_name
