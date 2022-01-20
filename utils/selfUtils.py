import csv
import re
import traceback
import pandas as pd
from sklearn import preprocessing
from sklearn.model_selection import train_test_split, KFold, StratifiedKFold
from keras.utils import np_utils
import numpy as np
import random

def sort_by_second(elem):
    return int(elem[1])


def sort_by_third(elem):
    return int(elem[2])


def sort_by_fourth(elem):
    return int(elem[3])


def sort_by_fifth(elem):
    return int(elem[4])


def sort_by_sixth(elem):
    return int(elem[5])


def sort_by_name(elem):
    return elem[0]


def sort_by_last(elem):
    return elem[-1]


def csv_numpy(packet_path):
    """
    Take the csv files, convert it to "list" structure or "ndarray" structure. Use either of the two
    structure for the future data analysis.
    :param packet_path: path of the csv file
    :return: return the traffic data in a data structure of "list" or "ndarray"
    """
    # df = pd.read_csv(packet_path)
    reader = csv.reader(open(packet_path, "r"), delimiter=",")
    query_in_list = list(reader)
    # query_in_list = df.values.tolist()

    try:
        float(query_in_list[0][1])
    except ValueError:
        query_in_list.pop(0)
    except IndexError:
        print("empty csv")

    N = []
    for p in query_in_list:
        new_list = []

        for m in p:
            try:
                new_list = new_list + [float(m)]
            except ValueError:
                new_list = new_list + [m]
                pass
        N.append(new_list)

    return N


def cal_d(i):
    for j in range(10000):
        if i % pow(2, j) == 0 and i % pow(2, j + 1) != 0:
            d = pow(2, j)
            return int(d)


def cal_g(i):
    if i == 1:
        g = 0
    else:
        d = cal_d(i)
        if i == d and d >= 2:
            g = i / 2
        elif i > d:
            g = i - d
    return int(g)


def same_name(string1, string2):
    name1 = 0
    name2 = 0

    for a, x in enumerate(string1):
        # if x.isdigit():
        if x == '?' and string1[a - 1] == '_':
            name1 = string1[0:a - 1]
            break
        else:
            continue
    for b, y in enumerate(string2):
        # if x.isdigit():
        if y == '?' and string2[b - 1] == '_':
            name2 = string2[0:b - 1]
            break
        else:
            continue

    return name1 == name2


def extract_name(string):
    for a, x in enumerate(string):
        # if x.isdigit():
        if x == '?' and string[a - 1] == '_':
            name = string[0:a - 1]
            break
        else:
            continue
    return name


def just_class(file_path, output_path):
    data = pd.read_csv(file_path)
    labels_raw = data['0']
    labels = []
    for l in labels_raw:
        try:
            match = re.search("\\?", l)
            class_name = l[:match.start()]
            labels.append(class_name)
        except AttributeError:
            print(l)
            print(traceback.print_exc())
    data['0'] = labels
    data.to_csv(output_path, index=False)


def load_split_data(path, sel_col):
    raw_data = pd.read_csv(path)
    print(raw_data.shape)
    y_raw = raw_data.iloc[:, 0]
    le = preprocessing.LabelEncoder()
    labels = le.fit_transform(y_raw)
    num_classes = len(le.classes_)
    # labels = np_utils.to_categorical(labels, num_classes=num_classes)

    X = raw_data.iloc[:, 1:sel_col + 1]
    print(X.shape)
    X_train, X_test, y_train, y_test = train_test_split(X, labels, test_size=0.2, random_state=42)
    return X_train, y_train, X_test, y_test, num_classes
    # retrun X, labels


def load_data(path, sel_col):
    raw_data = pd.read_csv(path).sample(frac=1)

    print(raw_data.shape)
    y_raw = raw_data.iloc[:, 0]
    num_classes = len(np.unique(y_raw))

    X = raw_data.iloc[:, 1:sel_col + 1]
    print(X.shape)
    X = np.array(X)
    y_raw = np.array(y_raw)
    return X, y_raw, num_classes


def load_sel_data(path, sel_col):
    raw_data = pd.read_csv(path).iloc[:, 1:]
    print(raw_data.shape)
    y_raw = raw_data.iloc[:, 0]
    le = preprocessing.LabelEncoder()
    labels = le.fit_transform(y_raw)
    num_classes = len(le.classes_)
    labels = np_utils.to_categorical(labels, num_classes=num_classes)

    X = raw_data.iloc[:, sel_col]
    X_train, X_test, y_train, y_test = train_test_split(X, labels, test_size=0.2, random_state=42)
    return X_train, y_train, X_test, y_test, num_classes
    # retrun X, labels


def shuffle_and_load(path, sel_col):
    raw_data = pd.read_csv(path)
    y_raw = raw_data.iloc[:, 0]
    le = preprocessing.LabelEncoder()
    labels = le.fit_transform(y_raw)
    num_classes = len(le.classes_)
    labels = np_utils.to_categorical(labels, num_classes=num_classes)

    X = raw_data.iloc[:, sel_col]
    X = X.sample(frac=1, axis=1)
    X_train, X_test, y_train, y_test = train_test_split(X, labels, test_size=0.2, random_state=42)
    return X_train, y_train, X_test, y_test, num_classes
