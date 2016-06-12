import Classify_helpers as ch
import json
import os
import random
import sys
import re
import numpy as np
from functools import partial

from keras.models import Sequential
from keras.layers import Dense, Activation
from keras.optimizers import SGD
from keras.layers.convolutional import Convolution2D, MaxPooling2D
from keras.layers.core import Dense, Dropout, Activation, Flatten
from keras.utils import np_utils, generic_utils

if len(sys.argv) < 2:
    print "ERROR: provide suffix for model file"
    exit(1)
MODEL_SUFFIX = sys.argv[1]


def split_data(data, split_ratio=0.2):

    split_index = int(len(data) * split_ratio)
    training_data = data[split_index:]
    test_data = data[:split_index]

    return (training_data, test_data)
    

def load_training_data(geometry):
    filepaths = [ str(ch.DATADIR + f + ".json") for f in geometry ]

    all_data = []

    for index in xrange(len(geometry)):

        filename = filepaths[index]
        geo = geometry[index]

        label = [0] * len(geometry)
        label[index] = 1

        with open(filename) as fp:
            data = json.load(fp)
            for datum in data:
                datum.update({'geometry':geo, 'label':label})

        
        all_data.extend(data)

    random.shuffle(all_data)

    return all_data


def save_model_to_file(model, MODEL_SUFFIX):

    json_string = model.to_json()
    open(ch.MODELDIR + 'model_architecture__' + MODEL_SUFFIX + '.json', 'w').write(json_string)
    model.save_weights(ch.MODELDIR + 'model_weights__' + MODEL_SUFFIX + '.h5')



def makeCNN():
    model = Sequential()

    model.add(Convolution2D(32, 3, 3, border_mode='same', input_shape=(3, helpers.IMAGE_HEIGHT, helpers.IMAGE_WIDTH)))
    model.add(Activation('relu'))

    model.add(Convolution2D(32, 3, 3, border_mode='same'))
    model.add(Activation('relu'))

    model.add(MaxPooling2D(pool_size=(2, 2)))
    model.add(Dropout(0.25))
     
    model.add(Convolution2D(64, 3, 3, border_mode='same', input_shape=(3, helpers.IMAGE_HEIGHT, helpers.IMAGE_WIDTH)))
    model.add(Activation('relu'))

    model.add(MaxPooling2D(pool_size=(2, 2)))
    model.add(Dropout(0.25))
     
    model.add(Flatten())
    model.add(Dense(input_dim = (64*8*8), output_dim = 512))
    model.add(Activation('relu'))
    model.add(Dropout(0.5))
     
    model.add(Dense(input_dim=512, output_dim=2))
    model.add(Activation('softmax'))

    model = makeCNN()
    return model


def makeNormal():
    model = Sequential()
    
    model.add(Dense(500, input_shape=(1000,), init='uniform'))
    model.add(Activation("tanh"))
    model.add(Dropout(0.25))

    model.add(Dense(500, init='uniform'))
    model.add(Activation("tanh"))
    model.add(Dropout(0.25))

    model.add(Dense(50, init = 'uniform'))
    model.add(Activation("tanh"))

    model.add(Dense(len(geometry)))
    model.add(Activation("softmax"))
    return model

#####################
#####################

if __name__ == '__main__':

    geometry = ["box", "tetrahedra", "cone"]

    all_data = load_training_data(geometry)

    (training_data, test_data) = split_data(all_data, 0.2)

    training_data_np = np.array(map(lambda x: x['data'], training_data))
    training_labels_np = np.array(map(lambda x: x['label'], training_data))

    test_data_np = np.array(map(lambda x: x['data'], test_data))
    test_labels_np = np.array(map(lambda x: x['label'], test_data))

    model = makeNormal()

    sgd = SGD(lr=0.1, decay=1e-6, momentum=0.9, nesterov=True)

    #model.compile(loss='mse', optimizer=sgd, metrics=['accuracy'])
    #model.compile(loss='mse', optimizer='sgd', metrics=['accuracy'])
    #model.compile(loss='categorical_crossentropy', optimizer=sgd, metrics=['accuracy'])
    model.compile(loss='categorical_crossentropy', optimizer='rmsprop', metrics=['accuracy'])

    print("begin to train")

    history = model.fit(training_data_np, training_labels_np,
            nb_epoch = 10, 
            batch_size= 16, 
            verbose= 2, 
            validation_split=0.2,
            shuffle=True)

    score = model.evaluate(test_data_np, test_labels_np)
   
    print('Test score:', score[0])
    print('Test accuracy:', score[1])

    ####### SAVING

    print ("saving model to file..")

    save_model_to_file(model, MODEL_SUFFIX)


