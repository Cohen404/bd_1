# 文件功能：EEG数据预处理
# 该脚本用于读取EDF格式的脑电图数据，进行预处理，包括删除非EEG通道、设置电极位置、
# 插值坏道、降采样、滤波、ICA分析、重新参考等步骤，最后保存处理后的数据。

from mne.io import concatenate_raws, read_raw_edf
import matplotlib.pyplot as plt
import mne
import os
import numpy as np

def treat(data_dir):
    """
    对指定目录中的EDF文件进行预处理
    
    参数:
    data_dir (str): 包含EDF文件的目录路径

    功能:
    1. 读取EDF文件
    2. 删除非EEG通道
    3. 设置电极位置
    4. 创建事件
    5. 插值坏道
    6. 降采样
    7. 滤波处理
    8. 独立成分分析（ICA）
    9. 重新参考
    10. 创建Epochs对象
    11. 保存处理后的数据
    """
    # 文件路径
    #     data_dir = 'E:/brain_data/焦虑'
    edf_files = [f for f in os.listdir(data_dir) if f.endswith('.edf')]

    # 读取EDF文件
    for edf_file in edf_files:
        edf_path = os.path.join(data_dir, edf_file)
        raw = read_raw_edf(edf_path)
        print(f"Loaded data from {edf_path}")

    # 获取采样频率和采样总数
    freq = raw.info['sfreq']
    n_samples = raw.n_times / freq

    # 删除非EEG通道
    non_eeg_channel = ['ECG', 'HEOR', 'HEOL', 'VEOU', 'VEOL', 'Status']
    # raw.drop_channels(non_eeg_channel)

    # 检查是否存在非EEG通道，如果存在则删除
    exisiting_non_eeg_channels = [ch for ch in non_eeg_channel if ch in raw.ch_names]
    if not exisiting_non_eeg_channels:
        print("数据已经预处理过，跳过后续处理")
        return
    else:
        print(f"删除非EEG通道: {exisiting_non_eeg_channels}")
        raw.drop_channels(exisiting_non_eeg_channels)

    # 设置电极位置
    # 使用标准的10-05系统设置电极位置
    montage = mne.channels.make_standard_montage("standard_1005")
    raw.set_montage(montage)
    # raw.plot_sensors(show_names=True)

    # 创建事件
    # 从原始数据的注释中创建事件
    events, event_id = mne.events_from_annotations(raw)
    event_id = 1  # 事件ID
    duration = 1  # 事件持续时间/秒
    # 创建固定长度的事件
    events = mne.make_fixed_length_events(raw, event_id, start=0, duration=duration, overlap=0)

    # 插值坏道
    print(raw.info['bads'])
    raw.load_data()
    raw.interpolate_bads()

    #raw.plot(title="after")

    # 降采样到500Hz
    target_sfreq = 500
    raw_resampled = raw.copy().resample(sfreq=target_sfreq)
    # raw_resampled.plot()

    # 滤波处理，设置1-100Hz频段
    raw_filtered = raw_resampled.copy().filter(l_freq=1, h_freq=100)
    # raw_filtered.plot()
    # raw_filtered.plot_psd(fmax=250)

    # 独立成分分析（ICA）
    # ICA用于去除眼动和肌电等伪迹
    raw_ica = raw_filtered.copy()
    ica = mne.preprocessing.ICA(n_components=20)
    ica.fit(raw_ica)
    raw_ica.load_data()
    # ica.plot_sources(raw_ica)
    # ica.plot_components()

    # 基于平均通道重新参考
    raw_ref = raw_filtered.copy()
    raw_ref.load_data()
    raw_ref.set_eeg_reference(ref_channels="average", projection=False)

    # 创建Epochs对象
    t_min = -1.0  # 事件前1秒
    t_max = 1.0 - 1 / target_sfreq  # 事件后1秒
    reject_criteria = dict(eeg=100e-6)  # 设置EEG拒绝标准

    epochs = mne.Epochs(raw_ref, events=events, event_id=event_id, tmin=t_min, tmax=t_max, reject=reject_criteria, baseline=None, preload=True)

    # 调整epochs形状
    epochs_data = epochs.get_data()
    if epochs_data.shape[2] == 1001:
        epochs_data = epochs_data[:, :, :-1]

    # 只取最后108个epochs
    data = epochs_data[-108::, :, :]
    print(data.shape)

    # 绘制数据
    # raw_ref.plot()
    # epochs.plot()
    # raw_ref.plot_psd()

    # 保存处理后的数据
    save_dir = os.path.join(data_dir, 'fif.fif')
    epochs.save(save_dir, overwrite=True)

# 注释：
# 1. 该脚本首先读取指定目录中的所有EDF文件
# 2. 删除非EEG通道，如ECG、HEOR等
# 3. 设置标准的电极位置
# 4. 创建固定长度的事件
# 5. 插值处理坏道
# 6. 将采样率降至500Hz
# 7. 应用1-100Hz的带通滤波器
# 8. 进行独立成分分析（ICA）
# 9. 使用平均通道重新参考
# 10. 创建Epochs对象，设置拒绝标准
# 11. 调整Epochs数据形状，只保留最后108个epochs
# 12. 最后将处理后的数据保存为fif格式