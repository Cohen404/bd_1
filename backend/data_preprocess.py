# 文件功能：EEG数据预处理
# 该脚本用于读取多种格式的脑电图数据，进行预处理，包括删除非EEG通道、设置电极位置、
# 插值坏道、降采样、滤波、ICA分析、重新参考等步骤，最后保存处理后的数据。

from mne.io import concatenate_raws, read_raw_edf, read_raw_eeglab
import matplotlib.pyplot as plt
import mne
import os
import numpy as np
import scipy.io as sio
import traceback


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
        
        # 尝试不同方式读取SET文件
        try:
            # 1. 首先尝试默认参数读取
            print("尝试默认参数读取SET文件...")
            raw = read_raw_eeglab(set_path, preload=False)
            print("成功读取SET文件作为原始数据")
        except (TypeError, ValueError, RuntimeError) as e1:
            print(f"默认参数读取失败: {str(e1)}")
            try:
                # 2. 尝试使用ascii编码读取
                print("尝试使用ascii编码读取SET文件...")
                raw = read_raw_eeglab(set_path, preload=False, uint16_codec='latin1')
                print("使用ascii编码成功读取SET文件")
            except (TypeError, ValueError, RuntimeError) as e2:
                print(f"ascii编码读取失败: {str(e2)}")
                try:
                    # 3. 尝试作为epochs数据读取
                    print("尝试作为epochs数据读取...")
                    epochs = mne.io.read_epochs_eeglab(set_path)
                    print("成功读取SET文件作为epochs数据")
                    
                    # 将epochs数据转换为连续数据
                    data = epochs.get_data()
                    info = mne.create_info(
                        ch_names=epochs.ch_names,
                        sfreq=epochs.info['sfreq'],
                        ch_types='eeg'
                    )
                    # 重塑数据形状 (trials x channels x time) -> (channels x time)
                    data_reshaped = np.concatenate(data, axis=1)
                    raw = mne.io.RawArray(data_reshaped, info)
                    print(f"已将epochs数据转换为连续数据，形状: {data_reshaped.shape}")
                except Exception as e3:
                    # 4. 最后尝试使用ascii编码读取epochs
                    try:
                        print("尝试使用ascii编码读取epochs数据...")
                        epochs = mne.io.read_epochs_eeglab(set_path, uint16_codec='latin1')
                        print("使用ascii编码成功读取epochs数据")
                        
                        # 将epochs数据转换为连续数据
                        data = epochs.get_data()
                        info = mne.create_info(
                            ch_names=epochs.ch_names,
                            sfreq=epochs.info['sfreq'],
                            ch_types='eeg'
                        )
                        data_reshaped = np.concatenate(data, axis=1)
                        raw = mne.io.RawArray(data_reshaped, info)
                        print(f"已将epochs数据转换为连续数据，形状: {data_reshaped.shape}")
                    except Exception as e4:
                        print("所有读取方式都失败了")
                        print(f"最后尝试失败: {str(e4)}")
                        return False

        if raw is None:
            print("SET文件读取失败")
            return False

    if raw is None:
        print("未找到支持的脑电数据文件（.edf, .set/.fdt, .mat）")
        return False

    print("开始进行预处理...")
    
    # 获取采样频率和采样总数
    freq = raw.info['sfreq']
    n_samples = raw.n_times / freq

    # 定义要保留的59个通道
    channels_to_keep = ['Fpz', 'Fp1', 'Fp2', 'AF3', 'AF4', 'AF7', 'AF8', 'Fz', 'F1', 'F2', 
                       'F3', 'F4', 'F5', 'F6', 'F7', 'F8', 'FCz', 'FC1', 'FC2', 'FC3', 'FC4', 
                       'FC5', 'FC6', 'FT7', 'FT8', 'Cz', 'C1', 'C2', 'C3', 'C4', 'C5', 'C6', 
                       'T7', 'T8', 'CP1', 'CP2', 'CP3', 'CP4', 'CP5', 'CP6', 'TP7', 'TP8', 
                       'Pz', 'P3', 'P4', 'P5', 'P6', 'P7', 'P8', 'POz', 'PO3', 'PO4', 'PO5', 
                       'PO6', 'PO7', 'PO8', 'Oz', 'O1', 'O2']

    # 检查当前数据中的通道
    current_channels = raw.ch_names
    print(f"原始通道 ({len(current_channels)}个): {current_channels}")

    # 找出需要删除的通道
    channels_to_drop = [ch for ch in current_channels if ch not in channels_to_keep]
    
    # 删除不需要的通道
    if channels_to_drop:
        print(f"删除的通道: {channels_to_drop}")
        raw.drop_channels(channels_to_drop)
    
    # 输出保留的通道
    remaining_channels = raw.ch_names
    print(f"保留的通道 ({len(remaining_channels)}个): {remaining_channels}")

    # 设置电极位置
    try:
        montage = mne.channels.make_standard_montage("standard_1005")
        raw.set_montage(montage, match_case=False)  # 添加match_case=False以忽略大小写
    except ValueError as e:
        print(f"设置电极位置时出错: {str(e)}")
        print("尝试使用其他montage模板...")
        # 尝试其他常用的montage模板
        montage_names = ["standard_1020", "standard_1010", "biosemi64"]
        for name in montage_names:
            try:
                montage = mne.channels.make_standard_montage(name)
                raw.set_montage(montage, match_case=False)
                print(f"成功使用 {name} montage")
                break
            except ValueError:
                continue

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