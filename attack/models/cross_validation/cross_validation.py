from keras.layers import Dense, Conv1D, MaxPooling1D, Dropout, GlobalAveragePooling1D, Flatten, BatchNormalization
from keras.models import Sequential
from keras.initializers import glorot_normal
from keras.callbacks import Callback, ModelCheckpoint, LearningRateScheduler, TensorBoard, EarlyStopping
import keras.backend as K
from keras.utils import np_utils
from sklearn.model_selection import StratifiedKFold
from sklearn import preprocessing
import sys
import json
import tensorflow as tf
sys.path.append('/home/haipeng/Documents/dl_attack')
import selfUtils as su
import pandas as pd
import logging
import numpy as np

LOG = logging.getLogger('cnn_cache')


def best_params(browser):
    with open(browser + ".cfg", "r") as f:
        cfg = json.loads(f.read())

    params = cfg['parameters']
    return params


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


def train(model, params, X_train, y_train, X_test, y_test):
    print('Generating Model...')

    es = EarlyStopping(monitor='val_acc', mode='max', patience=10)

    def schedule(epoch):
        if epoch % 20 == 0 and epoch != 0:
            lr = K.get_value(model.optimizer.lr)
            K.set_value(model.optimizer.lr, lr * params['decay'])
            print("lr changed to {}".format(lr * params['decay']))
        return K.get_value(model.optimizer.lr)

    lrs = LearningRateScheduler(schedule)
    print('Traning Model...')
    checkpointer = ModelCheckpoint(filepath='/home/haipeng/Documents/models/cnn_wf.hdf5',
                                   monitor='val_acc', verbose=1, save_best_only=True, mode='max')
    history = model.fit(X_train, y_train, batch_size=params['batch_size'],
                        epochs=50, validation_split=0.2, callbacks=[es, lrs])

    print('Training Finished!!')
    print('Testing...')
    score, acc = model.evaluate(X_test, y_test, batch_size=100)
    print('Test score:', score)
    print('Test accuracy:', acc)
    return score, acc


def main(browser):

    PARAMS = best_params(browser)
    # X_train, y_train, X_test, y_test, num_classes = su.load_slit_data('/home/haipeng/Documents/dataset/cache_dataset/obf_linux_ff_2mp.csv', PARAMS['data_dim'])
    X, y, num_classes = su.load_data('/home/haipeng/Documents/dataset/cache_dataset/'+ browser +'.csv', PARAMS['data_dim'])
    print('num_classes is ' + str(num_classes))
    skf = StratifiedKFold(n_splits=5,random_state=42)
    acc_result = []
    for train_index, test_index in skf.split(X, y):
        X_train, X_test = X[train_index], X[test_index]
        y_train, y_test = y[train_index], y[test_index]
        print(len(np.unique(y_train)),len(np.unique(y_test)))
        le = preprocessing.LabelEncoder()
        y_train = le.fit_transform(y_train)
        y_test = le.fit_transform(y_test)

        y_train = np_utils.to_categorical(y_train, num_classes)
        y_test = np_utils.to_categorical(y_test, num_classes)
        X_train = np.expand_dims(X_train, axis=2)
        X_test = np.expand_dims(X_test, axis=2)
        model = built_and_compile(PARAMS, num_classes)
        score, acc = train(model, PARAMS, X_train, y_train, X_test, y_test)
        acc_result.append([score,acc])

    df = pd.DataFrame(acc_result)
    df.to_csv('/home/haipeng/Documents/results/' + browser + '.csv', header=None)


if __name__ == '__main__':
    browser = sys.argv[1]
    print(tf.test.is_built_with_cuda())
    print(tf.test.is_gpu_available())
    main(browser)
