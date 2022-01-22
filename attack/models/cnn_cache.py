from keras.layers import Dense, Conv1D, MaxPooling1D, Dropout, GlobalAveragePooling1D, Flatten, BatchNormalization
from keras.models import Sequential, load_model
from keras.initializers import glorot_normal
from keras.callbacks import Callback, ModelCheckpoint, LearningRateScheduler, TensorBoard, EarlyStopping
import keras.backend as K
from keras.utils import np_utils
from sklearn.model_selection import StratifiedKFold
from sklearn import preprocessing
import pandas as pd
import sys

import tensorflow as tf
import selfUtils as su
import argparse
import time
import random
import pandas as pd
import logging
import numpy as np
import nni
from datetime import datetime

LOG = logging.getLogger('cnn_cache')


def default_params():
    return {
        'optimizer': 'Adam',
        'learning_rate': 0.001,
        'activation1': 'relu',
        'activation2': 'relu',
        'activation3': 'relu',
        'drop_rate1': 0.5,
        'drop_rate2': 0.5,
        'drop_rate3': 0.5,
        'decay': 0.1,
        'batch_size': 32,
        'epochs': 50,
        'data_dim': 15000,
        'conv1': 32,
        'conv2': 64,
        'conv3': 32,
        'pool1': 5,
        'pool2': 3,
        'pool3': 3,
        'kernel_size1': 10,
        'kernel_size2': 10,
        'kernel_size3': 5,
        'dense1': 150,
        'dese1_act': 'relu',
    }


def built_and_compile(params, num_classes):
    layers = [Conv1D(params['conv1'], kernel_size=params['kernel_size1'], activation=params['activation1'],
                     input_shape=(params['data_dim'], 1), use_bias=False, kernel_initializer=glorot_normal(seed=7)),
              MaxPooling1D(params['pool1']),
              Dropout(rate=params['drop_rate1']),

              Conv1D(params['conv2'], kernel_size=params['kernel_size2'], activation=params['activation2'],
                     use_bias=False, kernel_initializer=glorot_normal(seed=7)),
              MaxPooling1D(params['pool2']),
              Dropout(rate=params['drop_rate2']),

              Conv1D(params['conv3'], kernel_size=params['kernel_size3'], activation=params['activation3'],
                     use_bias=False, kernel_initializer=glorot_normal(seed=7)),
              MaxPooling1D(params['pool3']),
              Dropout(rate=params['drop_rate3']),
              Flatten(),
              Dense(params['dense1'], activation=params['dense1_act'], use_bias=False,
                    kernel_initializer=glorot_normal(seed=7)),
              Dense(num_classes, activation='softmax', kernel_initializer=glorot_normal(seed=7))]

    model = Sequential(layers)
    model.compile(loss='categorical_crossentropy',
                  optimizer=params['optimizer'], metrics=['accuracy'])

    return model


class nniRep(Callback):
    def accRep(self, logs={}):
        LOG.debug(logs)
        nni.report_intermediate_result(logs['val_acc'])


def train(model, params, X_train, y_train, X_test, y_test, out_path):
    print('Generating Model...')

    # modelDir = 'modelDir'
    # modelPath = os.path.join(modelDir, 'cnn_weights.hdf5')
    # if not os.path.isdir(modelDir):
    #     os.makedirs(modelDir)
    # checkpointer = ModelCheckpoint(filepath=modelPath, monitor='val_acc', verbose=1, save_best_only=True, mode='max')

    tensorboard = TensorBoard(log_dir="logs/{}".format(time.time()))
    es = EarlyStopping(monitor='val_acc', mode='max', patience=10)

    def schedule(epoch):
        if epoch % 20 == 0 and epoch != 0:
            lr = K.get_value(model.optimizer.lr)
            K.set_value(model.optimizer.lr, lr * params['decay'])
            print("lr changed to {}".format(lr * params['decay']))
        return K.get_value(model.optimizer.lr)

    lrs = LearningRateScheduler(schedule)
    print('Traning Model...')
    checkpointer = ModelCheckpoint(filepath=out_path,
                                   monitor='val_acc', verbose=1, save_best_only=True, mode='max')
    history = model.fit(X_train, y_train, batch_size=params['batch_size'],
                        epochs=params['epochs'], validation_split=0.2, callbacks=[nniRep(), es, lrs])

    print('Training Finished!!')
    t = str(datetime.now())
    # modelname = 'cnn_wf_' + t + '.h5'
    # model.save('/home/haipeng/Documents/models/wf/' + modelname)
    return model


def test(params, model, X_test, y_test, NUM_CLASS):
    print('Predicting results with best model...')
    # model = built_and_compile(params, NUM_CLASS)
    # model = load_model(out_path)
    score, acc = model.evaluate(X_test, y_test, batch_size=100)

    nni.report_final_result(acc)
    modelname = 'obf_linux_chrome_' + str(acc) + '.h5'
    #model.save('/home/usr/Documents/models/cache/' + modelname)
    print('Test score:', score)
    print('Test accuracy:', acc)
    return score, acc


def main(data_path, out_path):
    try:
        # get parameters from tuner
        RECEIVED_PARAMS = nni.get_next_parameter()
        LOG.debug(RECEIVED_PARAMS)
        PARAMS = default_params()
        PARAMS.update(RECEIVED_PARAMS)
        LOG.debug(PARAMS)
        X_train, y_train, X_test, y_test, num_classes = su.load_split_data(data_path, PARAMS['data_dim'])
        print('num_classes is ' + str(num_classes))

        X_train = np.expand_dims(X_train, axis=2)
        X_test = np.expand_dims(X_test, axis=2)
        model = built_and_compile(PARAMS, num_classes)
        m = train(model, PARAMS, X_train, y_train, X_test, y_test, out_path)
        score, acc = test(PARAMS, m, X_test, y_test, num_classes, out_path)
    except Exception as exception:
        LOG.exception(exception)
        raise

if __name__ == '__main__':
    # opts = parseOpts(sys.argv)
    data_path = sys.argv[1]
    out_path = sys.argv[2]
    print(tf.test.is_built_with_cuda())
    print(tf.test.is_gpu_available())
    main(data_path, out_path)
