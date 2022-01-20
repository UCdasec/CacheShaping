import numpy as np
import pandas as pd
import os
import re
import random
from sklearn import preprocessing


def rename():
    path = '/home/erc/PycharmProjects/cache_attack/data/obf_linux_chrome/'
    files = os.listdir(path)
    files.sort()
    # new_path = '/home/erc/PycharmProjects/cache_attack/data/obf_linux_chrome_8mp/'
    for file in files:
        idx = [m.start() for m in re.finditer('_', file)]
        new_name = 'obf_linux_chrome_8mp' + file[idx[3]:]
        os.rename(path+file, path+new_name)


def muti_lines_test():
    path = "/media/erc/Mistake/detection/malicious/txt/"
    files = os.listdir(path)
    for file in files:
        text_file = open(path + file, "r")
        lines = text_file.readlines()
        l = []
        n = 0
        for line in lines:

            data = line.split(',')[:-1]
            data = [float(i) for i in data]

            labeled_d = [1] + data

            l.append(labeled_d)

        df = pd.DataFrame(l)

        df.to_csv(path + file[:-4] + '.csv',index=False)
    print()


def speed_cal():
    path = "/home/erc/Documents/Mastik-0.02-AyeAyeCapn/demo/data/"
    # path = "/home/erc/Documents/omp_test/data/"
    files = os.listdir(path)
    files.sort()
    n = 0
    for file in files:
        text_file = open(path + file, "r")
        lines = text_file.readlines()
        # data = lines[0].split(',')
        data = list(lines[0])
        n += len(data) / 768
    print(n)


def single_test():
    text_file = open("/home/erc/PycharmProjects/cache_attack/data/14.txt", "r")
    lines = text_file.readlines()
    # data = lines[0].split(',')
    data = list(lines[0])
    n = len(data)/768
    df = pd.DataFrame(data)
    df.to_csv('test.csv',header=False)
    print()


def numeric():
    data = pd.read_csv('obf_chrome_test6.csv')
    y = data.iloc[:, 0]
    le = preprocessing.LabelEncoder()
    labels = le.fit_transform(y)
    data.iloc[:, 0] = labels
    data.to_csv('obf_chrome_test_numeric6.csv')


def proc_lists():
    path = '/home/erc/PycharmProjects/cache_attack/open_world_list.csv'
    data = pd.read_csv(path).tolist()
    new_list = []
    for w in data:
        name = w.split('.')
        label = name[0]
        http = 'http://www.' + name
        new_list.append([label, http])
    print()


def group():
    path = '/home/erc/PycharmProjects/cache_attack/data/obf_linux_chrome/'
    files = os.listdir(path)
    files.sort()
    data_in_row = []
    one = []
    for file in files:
        f_name = file
        idx = [m.start() for m in re.finditer('_', f_name)]
        label = f_name[:idx[4]]
        data = pd.read_csv(path + f_name)['0']
        data_in_row = [label] + data.values.tolist()
        one.append(data_in_row)

    df = pd.DataFrame(one)
    df.to_csv('data/random_obf_linux_chrome_mp_25.csv', index=False)


def ow_generator():
    non_sen_path = '/media/erc/Mistake/detection/normal/csv/normal_1000-1999.csv'
    non_data = pd.read_csv(non_sen_path)
    path = '/media/erc/Mistake/detection/test_malicious/csv/'
    files = os.listdir(path)
    for file in files:
        sen_path = path + file

        # non_data['0'] = 'non'
        sen_data = pd.read_csv(sen_path)
        data = pd.concat([non_data, sen_data])
        data.to_csv('detection_test_' + file[:-4] + '.csv', index=False)


def partly_def():
    ori_path = '/media/erc/Mistake/chrome/linux_chrome.csv'
    def_path = '/media/erc/Mistake/chrome/obf_linux_chrome_mp.csv'
    ori_data = pd.read_csv(ori_path)
    def_data = pd.read_csv(def_path)

    for i in [11,13,15]:
        def_range = int(i/0.002)
        partly_def_data = def_data.iloc[:,:def_range]
        partly_ort_data = ori_data.iloc[:,def_range:]
        partly_data = pd.concat([partly_def_data,partly_ort_data],axis=1)
        partly_data.to_csv(str(i)+'_partly_obf_linux_chrome.csv',index=False)


def random_partly_def():
    ori_path = '/media/erc/Mistake/chrome/linux_chrome.csv'
    def_path = '/media/erc/Mistake/chrome/obf_linux_chrome_mp.csv'
    ori_data = pd.read_csv(ori_path)
    def_data = pd.read_csv(def_path)

    random_partly_data = ori_data.iloc[:,0]
    for i in range(1,15001):
        r = random.randint(0, 9)
        if r < 7:
            random_partly_data = pd.concat([random_partly_data,ori_data.iloc[:,i]],axis=1)
        else:
            random_partly_data = pd.concat([random_partly_data, def_data.iloc[:, i]], axis=1)
    random_partly_data.to_csv("random_0.3_obf_linux_chrome.csv", index=False)

if __name__ == '__main__':
    # ow_generator()
    # numeric()
    # muti_lines_test()
    # single_test()
    # speed_cal()
    # rename()
    # group()
    # proc_lists()
    # data1 = pd.read_csv('/home/erc/PycharmProjects/cache_attack/data/obf_linux_tor_seq.csv')
    # data2 = pd.read_csv('/home/erc/PycharmProjects/cache_attack/data/ow_obf_linux_tor_seq.csv')
    # data2['0'] = 'non'
    # frames = [data1,data2]
    #
    # result = pd.concat(frames)
    # result.to_csv('ow_obf_linux_tor_seq_stm.csv',index=False)

    # partly_def()
    random_partly_def()

