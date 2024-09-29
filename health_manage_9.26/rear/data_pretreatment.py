from mne.io import concatenate_raws, read_raw_edf
import matplotlib.pyplot as plt
import mne
import os
import numpy as np

def treat(data_dir):
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

    exisiting_non_eeg_channels = [ch for ch in non_eeg_channel if ch in raw.ch_names]
    if not exisiting_non_eeg_channels:
        print("数据已经预处理过，跳过后续处理")
        return
    else:
        print(f"删除非EEG通道: {exisiting_non_eeg_channels}")
        raw.drop_channels(exisiting_non_eeg_channels)

    # 设置电极位置
    montage = mne.channels.make_standard_montage("standard_1005")
    raw.set_montage(montage)
    # raw.plot_sensors(show_names=True)

    # 创建事件
    events, event_id = mne.events_from_annotations(raw)
    event_id = 1  # 事件ID
    duration = 1  # 事件持续时间/秒
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
