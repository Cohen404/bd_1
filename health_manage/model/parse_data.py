import scipy.io as scio
import os
import re
import numpy as np
import torch


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

# 传数据路径,测试用
def process_data(fpath):
    Channel_2 = []
    ys = []
    fps = 1024
    types = []
    leng = 0
    # for f in norm_files:
    #     fpath = os.path.join(data_path, f)
    data = scio.loadmat(fpath)
    # for key in data.keys():
    # f = '1_1800_4.mat'
    # type_key = int(f.split('_')[0])
    # if re.match('Channel_2_Data', key):
    d = data['Channel_2_Data']
    leng += d.shape[0]
    d = d.reshape(-1)
    sample_num = int(d.shape[0] / fps)
    for i in range(sample_num):
        Channel_2.append(list(d[i * fps:(i + 1) * fps]))
        # ys.append(type_key)
        # types.append(type_key)
    # ys = classifier(ys)
    # DEdata = {'X': np.array(Channel_2), 'y': np.array(ys), 'types': types}
    DEdata = {'X': np.array(Channel_2)}
    return DEdata

# 单通道数据
def process_data1(fpath):
    fps = 1024
    data = scio.loadmat(fpath)
    # for key in data.keys():
    #     print(key)
    channel_data = data['Channel_2_Data']
    new_data = []
    sample_num = int(channel_data.shape[0] / fps)
    for i in range(sample_num):
        new_data.append(list(channel_data[i * fps:(i + 1) * fps]))

    new_data = np.array(new_data)
    # print(new_data.shape)
    return new_data
# path = '../data/1_1200_4.mat'
# process_data1(path)

# 四通道数据
def process_data4(fpath):
    new_data = []
    fps = 1024
    data = scio.loadmat(fpath)
    channel_data_1 = data['Channel_1_Data']
    new_data_1 = []
    sample_num_1 = int(channel_data_1.shape[0] / fps)
    for i in range(sample_num_1):
        new_data_1.append(list(channel_data_1[i * fps:(i + 1) * fps]))

    channel_data_2 = data['Channel_2_Data']
    new_data_2 = []
    sample_num_2 = int(channel_data_2.shape[0] / fps)
    for i in range(sample_num_2):
        new_data_2.append(list(channel_data_2[i * fps:(i + 1) * fps]))

    channel_data_3 = data['Channel_3_Data']
    new_data_3 = []
    sample_num_3 = int(channel_data_3.shape[0] / fps)
    for i in range(sample_num_3):
        new_data_3.append(list(channel_data_3[i * fps:(i + 1) * fps]))

    channel_data_4 = data['Channel_4_Data']
    new_data_4 = []
    sample_num_4 = int(channel_data_4.shape[0] / fps)
    for i in range(sample_num_4):
        new_data_4.append(list(channel_data_4[i * fps:(i + 1) * fps]))

    new_data.append([new_data_1, new_data_2, new_data_3, new_data_4])

    new_data = np.array(new_data)

    new_data = np.squeeze(new_data)
    new_data = new_data.swapaxes(0, 1)
    new_data = new_data.swapaxes(1, 2)

    # print(new_data.shape)
    return new_data

# process_data()
# path = '../data/32_1800_0.mat'
# process_data4(path)
# process_data('D:\\BaiduNetdiskDownload\\Test_data_classification\\test_data')
