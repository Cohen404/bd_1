import scipy.io as scio
import numpy as np
import matplotlib.pyplot as plt
from numpy.fft import fft
from scipy.interpolate import make_interp_spline
from scipy.ndimage import gaussian_filter1d
from sklearn import preprocessing

# import librosa

path = '../data/32_1800_8.mat'


# 快速傅里叶变换(健康评估页面、结果查看页面专用)
def pressure_curve(path):
    # 一秒65536个数据，即频率是65536
    Fs = 1000  # 采样频率
    Ts = 1 / Fs  # 采样区间
    x = np.arange(0, 1, Ts)  # 时间向量，65536个

    data = scio.loadmat(path)
    channel = data['Channel_2_Data']
    channel_last = []
    for i in channel[0:1000]:
        channel_last.append(i[0])
    channel_last = np.array(channel_last)
    y = channel_last
    # y = channel

    N = 1000
    frq = np.arange(N)  # 频率数65536个数
    half_x = frq[range(int(N / 2))]  # 取一半区间

    fft_y = np.fft.fft(y)

    abs_y = np.abs(fft_y)  # 取复数的绝对值，即复数的模(双边频谱)
    angle_y = 180 * np.angle(fft_y) / np.pi  # 取复数的弧度,并换算成角度

    # gui_y = abs_y/N     #归一化处理（双边频谱），不在0~1之间
    # 归一化到0~1之间
    list = abs_y.reshape(-1, 1)
    scaler = preprocessing.MinMaxScaler()
    gui_y = scaler.fit_transform(list)

    # gui_half_y = gui_y[range(int(N / 2))]  # 由于对称性，只取一半区间（单边频谱）

    plt.plot(frq, gui_y, 'g')
    f = plt.gcf()  # 获取当前图像
    plt.savefig('../img/' + 'pressure.png')
    # plt.show()
    f.clear()  # 释放内存

#
# # 快速傅里叶变换(数据查看页面专用)
# def pressure_curve1(path):
#     # 一秒65536个数据，即频率是65536
#     Fs = 10000  # 采样频率
#     Ts = 1 / Fs  # 采样区间
#     x = np.arange(0, 1, Ts)  # 时间向量，65536个
#
#     data = scio.loadmat(path)
#     channel = data['Channel_2_Data']
#     channel_last = []
#     for i in channel[:10000]:
#         channel_last.append(i[0])
#     channel_last = np.array(channel_last)
#     y = channel_last
#     # y = channel
#
#     N = 10000
#     frq = np.arange(N)  # 频率数65536个数
#     half_x = frq[range(int(N / 2))]  # 取一半区间
#
#     fft_y = np.fft.fft(y)
#
#     abs_y = np.abs(fft_y)  # 取复数的绝对值，即复数的模(双边频谱)
#     angle_y = 180 * np.angle(fft_y) / np.pi  # 取复数的弧度,并换算成角度
#
#     # gui_y = abs_y/N     #归一化处理（双边频谱），不在0~1之间
#     # 归一化到0~1之间
#     list = abs_y.reshape(-1, 1)
#     scaler = preprocessing.MinMaxScaler()
#     gui_y = scaler.fit_transform(list)
#
#     # gui_half_y = gui_y[range(int(N / 2))]  # 由于对称性，只取一半区间（单边频谱）
#
#     plt.plot(frq, gui_y, 'g')
#     f = plt.gcf()  # 获取当前图像
#     plt.savefig('../img/' + 'pressure.png')
#     # plt.show()
#     f.clear()  # 释放内存

# pressure_curve(path)
#
#
channel = 'Channel_1_Data'


# 快速傅里叶变换
def any_pressure_curve(path, channel):
    # 一秒65536个数据，即频率是65536
    Fs = 10000  # 采样频率
    Ts = 1 / Fs  # 采样区间
    x = np.arange(0, 1, Ts)  # 时间向量，65536个

    data = scio.loadmat(path)
    channel = data[channel]
    channel_last = []
    for i in channel[:10000]:
        channel_last.append(i[0])
    channel_last = np.array(channel_last)
    y = channel_last

    N = len(y)
    frq = np.arange(N)  # 频率数65536个数
    half_x = frq[range(int(N / 2))]  # 取一半区间

    fft_y = np.fft.fft(y)

    abs_y = np.abs(fft_y)  # 取复数的绝对值，即复数的模(双边频谱)
    angle_y = 180 * np.angle(fft_y) / np.pi  # 取复数的弧度,并换算成角度

    # gui_y = abs_y / N  # 归一化处理（双边频谱）
    # 归一化到0~1之间
    list = abs_y.reshape(-1, 1)
    scaler = preprocessing.MinMaxScaler()
    gui_y = scaler.fit_transform(list)

    gui_half_y = gui_y[range(int(N / 2))]  # 由于对称性，只取一半区间（单边频谱）

    plt.plot(frq, gui_y, 'g')
    f = plt.gcf()  # 获取当前图像
    plt.savefig('../img/' + 'pressure.png')
    # plt.show()
    f.clear()  # 释放内存


#
any_pressure_curve(path, channel)


# # 压力曲线图     结果查看、健康评估两个页面调用
# def pressure_curve(path):
#     data = scio.loadmat(path)
#     channel = data['Channel_2_Data']
#     # print(channel)
#     channel_last = []
#     # 65536、32768
#
#     for i in channel[-2048:]:
#         # print(i[0])
#         channel_last.append(i[0])
#     channel_last = np.array(channel_last)
#
#     # channel_last = fft(channel_last)    # 快速傅里叶变化
#     # print(channel_last)
#     # 数据归一化
#     list = channel_last.reshape(-1, 1)
#     # print('Original List:',list)
#     scaler = preprocessing.MinMaxScaler()
#     normalizedlist = scaler.fit_transform(list)
#
#
#     plt.plot(range(len(normalizedlist)), normalizedlist, color="b")
#     f = plt.gcf()  # 获取当前图像
#     plt.savefig('../img/' + 'pressure.png')
#     plt.show()
#     f.clear()  # 释放内存

# pressure_curve(path)

# # 健康状态
# def status(path):
#
#
# # 评估寿命


# channel = 'Channel_2_Data'


# # 任意压力曲线图       数据查看页面调用
# def any_pressure_curve(path, channel):
#     data = scio.loadmat(path)
#     channel_data = data[channel]
#     # print(channel)
#     channel_last = []
#     # 65586、32768
#     for i in channel_data[-2048:]:
#         # print(i[0])
#         channel_last.append(i[0])
#     channel_last = np.array(channel_last)
#     # print(channel_last)
#     # 数据归一化
#     list = channel_last.reshape(-1, 1)
#     # print('Original List:',list)
#     scaler = preprocessing.MinMaxScaler()
#     normalizedlist = scaler.fit_transform(list)
#
#
#     plt.plot(range(len(normalizedlist)), normalizedlist, color="b")
#     f = plt.gcf()  # 获取当前图像
#     plt.savefig('../img/' + 'pressure.png')
#     plt.show()
#     f.clear()  # 释放内存

# any_pressure_curve(path,channel)


# data1 = [2895,2895,2895,2895,2895,2222,2220.345,1889.367,1234.567,1224.32,1219.9,456.3,121.0,0,0,0,0]
def life_curve(data1):
    Y = np.array(data1)
    X = np.linspace(1, len(data1), len(data1))  # X轴坐标数据
    # plt.figure(figsize=(8, 6))  # 定义图的大小
    plt.xlabel("frequency")  # X轴标签
    plt.ylabel("time(hour)")  # Y轴坐标标签
    plt.plot(X, Y)
    plt.scatter(X, Y, marker='o')  # 绘制散点图
    f = plt.gcf()  # 获取当前图像
    plt.savefig('../img/' + 'life.png')
    # plt.show()
    f.clear()  # 释放内存


# life_curve(data1)


# data2 = [0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,1,1,1,2,2]
def status_curve(data2):
    Y = np.array(data2)
    X_table = []  # X轴坐标数据
    # print(X)
    # X = np.linspace(1, len(data2), len(data2))  # X轴坐标数据
    plt.xlabel("frequency")  # X轴标签 当前评估index
    plt.ylabel("status")  # Y轴坐标标签
    color = []
    for i in range(len(Y)):
        X_table.append('eval' + str(i + 1))
        if Y[i] == 0:
            color.append('green')
            Y[i] += 3
            # plt.bar(X[i], Y[i]+2, 1, color="green")
        elif Y[i] == 1:
            color.append('yellow')
            Y[i] += 1
            # plt.bar(X[i], Y[i]+1, 1, color="yellow")
        elif Y[i] == 2:
            color.append('red')
            Y[i] -= 1
            # plt.bar(X[i], Y[i], 1, color="red")

    plt.bar(X_table, Y, color=color)
    plt.xticks(rotation='vertical')
    plt.subplots_adjust(bottom=0.2)

    ax = plt.gca()
    ax.axes.yaxis.set_ticklabels([])

    f = plt.gcf()  # 获取当前图像
    plt.savefig('../img/' + 'status.png')
    # plt.show()
    f.clear()  # 释放内存

# status_curve(data2)
