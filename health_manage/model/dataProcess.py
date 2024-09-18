import scipy.io as scio
import os
import re
import numpy as np


def classifier(list):
    final_list = []
    for data in list:
        if data >= 1 and data < 32:
            data = 0
            final_list.append(data)
        elif data >= 32 and data <= 39:
            data = 1
            final_list.append(data)
        else:
            data = 2
            final_list.append(data)
    return final_list


def process_data(data_path):
    norm_dir = os.listdir(data_path)
    norm_files = []
    for file in norm_dir:
        if re.search('(.)+_1800+.*', file):
            norm_files.append(file)
    Channel_2 = []
    ys = []
    fps = 1024
    types = []
    leng = 0
    for f in norm_files:
        fpath = os.path.join(data_path, f)
        data = scio.loadmat(fpath)
        for key in data.keys():
            type_key = int(f.split('_')[0])
            if re.match('Channel_2_Data', key):
                d = data[key]
                leng += d.shape[0]
                d = d.reshape(-1)
                sample_num = int(d.shape[0] / fps)
                for i in range(sample_num):
                    Channel_2.append(list(d[i * fps:(i + 1) * fps]))
                    ys.append(type_key)
                    types.append(type_key)
    ys = classifier(ys)
    DEdata = {'X': np.array(Channel_2), 'y': np.array(ys), 'types': types}
    return DEdata


# process_data('D:\BaiduNetdiskDownload\Test_data_classification\programs')
# process_data('D:\\BaiduNetdiskDownload\\Test_data_classification\\test_data')
