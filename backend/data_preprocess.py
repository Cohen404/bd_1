# 文件功能：EEG数据预处理
# 该脚本用于读取多种格式的脑电图数据，进行预处理，包括删除非EEG通道、设置电极位置、
# 插值坏道、降采样、滤波、ICA分析、重新参考等步骤，最后保存处理后的数据。

from mne.io import concatenate_raws, read_raw_edf, read_raw_eeglab
import matplotlib.pyplot as plt
import mne
import os
import numpy as np
import scipy.io as sio

def read_eeglab_mat(file_path):
    """
    读取EEGLAB生成的.mat格式文件
    
    参数:
    file_path (str): .mat文件的路径
    
    返回:
    mne.io.Raw: MNE Raw对象
    """
    # 读取.mat文件
    mat_data = sio.loadmat(file_path)
    
    # 获取EEG数据和相关信息
    if 'EEG' in mat_data:
        eeg = mat_data['EEG']
        data = eeg['data'][0][0].T  # 转置以匹配MNE格式
        sfreq = float(eeg['srate'][0][0][0][0])
        ch_names = [str(name[0]) for name in eeg['chanlocs'][0][0]['labels'][0]]
        
        # 创建MNE Info对象
        info = mne.create_info(ch_names=ch_names, sfreq=sfreq, ch_types='eeg')
        
        # 创建Raw对象
        raw = mne.io.RawArray(data.T, info)
        return raw
    else:
        raise ValueError("无法从.mat文件中读取EEG数据")

def treat(data_dir):
    """
    对指定目录中的脑电数据文件进行预处理
    
    参数:
    data_dir (str): 包含脑电数据文件的目录路径

    功能:
    1. 读取多种格式的脑电数据文件（.fif, .edf, .set/.fdt, .mat）
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
    # 检查是否已有处理好的FIF文件
    fif_files = [f for f in os.listdir(data_dir) if f.endswith('.fif')]
    if fif_files:
        print("发现已预处理的FIF文件，直接进行保存")
        for fif_file in fif_files:
            fif_path = os.path.join(data_dir, fif_file)
            epochs = mne.read_epochs(fif_path)
            save_dir = os.path.join(data_dir, 'fif.fif')
            epochs.save(save_dir, overwrite=True)
        return True

    print("未发现FIF文件，开始预处理流程...")
    
    # 按优先级查找不同格式的脑电数据文件
    edf_files = [f for f in os.listdir(data_dir) if f.endswith('.edf')]
    set_files = [f for f in os.listdir(data_dir) if f.endswith('.set')]
    mat_files = [f for f in os.listdir(data_dir) if f.endswith('.mat')]

    raw = None
    
    # 尝试按优先级读取不同格式的文件
    if edf_files:
        print("找到EDF文件，开始处理...")
        edf_path = os.path.join(data_dir, edf_files[0])
        raw = read_raw_edf(edf_path)
        print(f"已加载EDF文件: {edf_path}")
    elif set_files:
        print("找到SET/FDT文件，开始处理...")
        set_path = os.path.join(data_dir, set_files[0])
        try:
            # 首先尝试作为原始数据读取
            raw = read_raw_eeglab(set_path)
            print(f"已加载SET文件作为原始数据: {set_path}")
        except TypeError as e:
            if "number of trials" in str(e):
                # 如果是epochs数据，直接读取为epochs
                print("检测到SET文件包含epochs数据，改用epochs读取方式")
                epochs = mne.io.read_epochs_eeglab(set_path)
                # 将epochs数据转换为连续数据
                data = epochs.get_data()
                # 创建info对象
                info = mne.create_info(
                    ch_names=epochs.ch_names,
                    sfreq=epochs.info['sfreq'],
                    ch_types='eeg'
                )
                # 重塑数据形状 (trials x channels x time) -> (channels x time)
                # 首先将所有trials连接在时间维度上
                data_reshaped = np.concatenate(data, axis=1)  # 现在形状是 (channels x (trials*time))
                # 创建Raw对象
                raw = mne.io.RawArray(data_reshaped, info)
                print(f"已将epochs数据转换为连续数据，形状: {data_reshaped.shape}")
            else:
                raise
        except Exception as e:
            print(f"读取SET文件失败: {str(e)}")
            return False
    elif mat_files:
        print("找到EEGLAB MAT文件，开始处理...")
        mat_path = os.path.join(data_dir, mat_files[0])
        try:
            raw = read_eeglab_mat(mat_path)
            print(f"已加载MAT文件: {mat_path}")
        except Exception as e:
            print(f"读取MAT文件失败: {str(e)}")
            return False

    if raw is None:
        print("未找到支持的脑电数据文件（.edf, .set/.fdt, .mat）")
        return False

    print("开始进行预处理...")
    
    # 获取采样频率和采样总数
    freq = raw.info['sfreq']
    n_samples = raw.n_times / freq

    # 删除非EEG通道
    non_eeg_channel = ['ECG', 'HEOR', 'HEOL', 'VEOU', 'VEOL', 'Status']
    exisiting_non_eeg_channels = [ch for ch in non_eeg_channel if ch in raw.ch_names]
    # if exisiting_non_eeg_channels:
    #     print(f"删除非EEG通道: {exisiting_non_eeg_channels}")
    #     raw.drop_channels(exisiting_non_eeg_channels)

    # 设置电极位置
    # 使用标准的10-05系统设置电极位置
    montage = mne.channels.make_standard_montage("standard_1005")
    raw.set_montage(montage)

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

    # 降采样到500Hz
    target_sfreq = 500
    raw_resampled = raw.copy().resample(sfreq=target_sfreq)

    # 滤波处理，设置1-100Hz频段
    raw_filtered = raw_resampled.copy().filter(l_freq=1, h_freq=100)

    # 独立成分分析（ICA）
    raw_ica = raw_filtered.copy()
    ica = mne.preprocessing.ICA(n_components=20)
    ica.fit(raw_ica)
    raw_ica.load_data()

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

    # 保存处理后的数据
    save_dir = os.path.join(data_dir, 'fif.fif')
    epochs.save(save_dir, overwrite=True)
    return True

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