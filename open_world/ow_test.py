from sklearn.metrics import roc_curve
from sklearn.metrics import auc
from sklearn.metrics import classification_report
import pandas as pd
import sys
from sklearn.model_selection import train_test_split
import tensorflow as tf
import selfUtils as su
import pandas as pd
import logging
import numpy as np
from sklearn import preprocessing

def calculatePrecAndRecAndTPRAndFPR(result_Mon, result_Unmon, y_test_mon, maxLabel, threshold_val):
    TP, FP, TN, FN = 0, 0, 0, 0
    monitored_label = list(set(y_test_mon))
    unmonitored_label = [maxLabel]

    # ==============================================================
    # Test with Monitored testing instances
    # evaluation
    for i in range(len(result_Mon)):
        sm_vector = result_Mon[i]
        predicted_class = np.argmax(sm_vector)
        max_prob = max(sm_vector)

        if predicted_class in monitored_label: # predicted as Monitored
            if max_prob >= threshold_val: # predicted as Monitored and actual site is Monitored
                TP = TP + 1
            else: # predicted as Unmonitored and actual site is Monitored
                FN = FN + 1
        elif predicted_class in unmonitored_label: # predicted as Unmonitored and actual site is Monitored
            FN = FN + 1

    # ==============================================================
    # Test with Unmonitored testing instances
    # evaluation
    for i in range(len(result_Unmon)):
        sm_vector = result_Unmon[i]
        predicted_class = np.argmax(sm_vector)
        max_prob = max(sm_vector)

        if predicted_class in monitored_label: # predicted as Monitored
            if max_prob >= threshold_val: # predicted as Monitored and actual site is Unmonitored
                FP = FP + 1
            else: # predicted as Unmonitored and actual site is Unmonitored
                TN = TN + 1
        elif predicted_class in unmonitored_label: # predicted as Unmonitored and actual site is Unmonitored
            TN = TN + 1

    print("TP : ", TP, "\tFP : ", FP, "\tTN : ", TN, "\tFN : ", FN)
    print("Total  : ", TP + FP + TN + FN)
    try:
        TPR = float(TP) / (TP + FN)
    except:
        TPR = 0
    try:
        FPR = float(FP) / (FP + TN)
    except:
        FPR = 0
    print("TPR : ", TPR, "\tFPR : ",  FPR)
    try:
        Precision = TP / (TP + FP)
        Recall = TP / (TP + FN)
    except:
        Precision = Recall = 0
    print("Precision : ", Precision, "\tRecall : ", Recall)
    return Precision, Recall, TPR, FPR


def predict(model, X_test):
    X_test = np.expand_dims(X_test, axis=2)
    print("predicting...")
    y_pred = model.predict(X_test)
    # d = pd.DataFrame(y_test)
    # d.to_csv('y_test.csv')
    # dd = pd.DataFrame(y_pred)
    # dd.to_csv('y_pred.csv')
    return y_pred
    # calculatePrecAndRecAndTPRAndFPR(y_pred)
    # print(y_pred.shape)
    # print(y_test.shape)
    # print(classification_report(y_test.argmax(axis=-1), y_pred.argmax(axis=-1)))
    # fpr, tpr, thresholds = roc_curve(y_test.argmax(axis=-1), y_pred.argmax(axis=-1))
    # auc_area = auc(fpr, tpr)
    # results = [[fpr], [tpr], [thresholds], [auc_area]]
    # df = pd.DataFrame(results)

    # df.to_csv('ow_results_linux_chrome.csv')


def split_Mon_UnNon(data):
    # data = data[data[:, 0].argsort()]
    unmon_data = data[:5000,:]
    mon_data = data[5000:,:]

    # X_mon = mon_data[:, 1:]
    # y_mon = mon_data[:, 0]
    mon_data = pd.DataFrame(mon_data).sample(frac=1).to_numpy()

    unmon_data = pd.DataFrame(unmon_data).sample(frac=1).to_numpy()

    mon_x_test = mon_data[:2000, 1:]
    mon_y_test = mon_data[:2000, 0]
    unmon_y_test = unmon_data[:1000, 0]
    unmon_x_test = unmon_data[:1000, 1:]
    # data = mon_data = unmon_data = None
    # df = pd.DataFrame(mon_x_test)
    # df.to_csv('mon_x_test.csv', index=False)
    #
    # df = pd.DataFrame(mon_y_test)
    # df.to_csv('mon_y_test.csv', index=False)
    #
    # df = pd.DataFrame(unmon_x_test)
    # df.to_csv('unmon_x_test.csv', index=False)
    #
    # df = pd.DataFrame(unmon_y_test)
    # df.to_csv('unmon_y_test.csv', index=False)

    return mon_x_test, mon_y_test, unmon_x_test, unmon_y_test


def numeric_lable(data):
    y_raw = data.iloc[:, 0]
    X = data.iloc[:, 1:]
    le = preprocessing.LabelEncoder()
    labels = le.fit_transform(y_raw)
    labels = np.reshape(labels, (-1, 1))
    numeric_data = np.append(labels, X, axis=1)
    return numeric_data


def main(data_path, model_path):
    model = tf.keras.models.load_model(model_path)
    # X_train, y_train, X_test, y_test, num_classes = su.load_split_data('/home/lhp/PycharmProjects/ow/data/ow_obf_linux_ff_stm.csv', 15000)
    # y_test = np.reshape(y_test, (-1,1))
    # test_data = np.append(y_test, X_test, axis=1)
    data = pd.read_csv(data_path)
    data = numeric_lable(data)
    # split_Mon_UnNon(data)
    mon_x_test, mon_y_test, unmon_x_test, unmon_y_test = split_Mon_UnNon(data)
    #
    unmon_y_pred = predict(model, unmon_x_test)
    mon_y_pred = predict(model, mon_x_test)
    # d = pd.DataFrame(unmon_y_pred)
    # d.to_csv('unmon_y_pred.csv')
    # dd = pd.DataFrame(mon_y_pred)
    # dd.to_csv('mon_y_pred.csv')
    #
    thresholds = [0.1, 0.2,  0.3,  0.4,  0.5,  0.6,  0.7,  0.8,  0.9]
    # thresholds = 0.4 - 1 / np.logspace(0.4, 2, num=25, endpoint=True)
    # thresholds = 1.0 - 1 / np.logspace(0.05, 2, num=15, base=10, endpoint=True)
    results = []
    for thr in thresholds:
        Precision, Recall, TPR, FPR = calculatePrecAndRecAndTPRAndFPR(mon_y_pred, unmon_y_pred, mon_y_test, 100, thr)
        results.append([thr, Precision, Recall, TPR, FPR])

    df = pd.DataFrame(results, columns=["threshold", "Precision", "Recall", "TPR", "FPR"])
    df.to_csv("lstm_ow_obf_linux_chrome_results.csv")



if __name__ == '__main__':
    # opts = parseOpts(sys.argv)
    data_path = sys.argv[1]
    model_path = sys.argv[2]
    main(data_path, model_path)
