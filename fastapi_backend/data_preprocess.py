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
import logging


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
    8. ICA分析
    9. 重新参考
    10. 创建Epochs对象
    11. 保存处理后的数据
    
    优化点：
    1. 使用内存映射加载大文件
    2. 优化ICA计算
    3. 并行处理某些步骤
    4. 减少不必要的数据复制
    5. 使用更高效的数据结构
    """
    try:
        # 检查是否已有处理好的FIF文件
        fif_files = [f for f in os.listdir(data_dir) if f.endswith('.fif')]
        if fif_files:
            print("发现已预处理的FIF文件，验证数据有效性")
            fif_path = os.path.join(data_dir, fif_files[0])
            try:
                # 尝试读取并验证数据
                epochs = mne.read_epochs(fif_path, preload=True)
                if epochs.get_data().size == 0:
                    print("FIF文件数据无效，重新进行预处理")
                    # 删除无效的FIF文件
                    os.remove(fif_path)
                else:
                    print("FIF文件数据有效，直接进行保存")
                    save_dir = os.path.join(data_dir, 'fif.fif')
                    epochs.save(save_dir, overwrite=True)
                    return True
            except Exception as e:
                print(f"FIF文件验证失败: {str(e)}")
                # 删除无效的FIF文件
                os.remove(fif_path)

        print("开始预处理流程...")
        
        # 按优先级查找不同格式的脑电数据文件
        edf_files = [f for f in os.listdir(data_dir) if f.endswith('.edf')]
        set_files = [f for f in os.listdir(data_dir) if f.endswith('.set')]

        raw = None
        
        # 尝试按优先级读取不同格式的文件
        if edf_files:
            print("找到EDF文件，开始处理...")
            edf_path = os.path.join(data_dir, edf_files[0])
            raw = read_raw_edf(edf_path, preload=True)  # 直接加载到内存
            print(f"已加载EDF文件: {edf_path}")
        elif set_files:
            print("找到SET/FDT文件，开始处理...")
            set_path = os.path.join(data_dir, set_files[0])
            
            # 尝试不同方式读取SET文件
            try:
                print("尝试默认参数读取SET文件...")
                raw = read_raw_eeglab(set_path, preload=True)  # 直接加载到内存
                print("成功读取SET文件作为原始数据")
            except (TypeError, ValueError, RuntimeError) as e1:
                print(f"默认参数读取失败: {str(e1)}")
                try:
                    print("尝试使用ascii编码读取SET文件...")
                    raw = read_raw_eeglab(set_path, preload=True, uint16_codec='latin1')
                    print("使用ascii编码成功读取SET文件")
                except (TypeError, ValueError, RuntimeError) as e2:
                    print(f"ascii编码读取失败: {str(e2)}")
                    try:
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
                        try:
                            print("尝试使用ascii编码读取epochs数据...")
                            epochs = mne.io.read_epochs_eeglab(set_path, uint16_codec='latin1')
                            print("使用ascii编码成功读取epochs数据")
                            
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
            raw.set_montage(montage, match_case=False)
        except ValueError as e:
            print(f"设置电极位置时出错: {str(e)}")
            print("尝试使用其他montage模板...")
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
        events, event_id = mne.events_from_annotations(raw)
        event_id = 1
        duration = 1
        events = mne.make_fixed_length_events(raw, event_id, start=0, duration=duration, overlap=0)

        # 插值坏道
        print(raw.info['bads'])
        raw.interpolate_bads()

        # 降采样到500Hz
        target_sfreq = 500
        raw_resampled = raw.copy().resample(sfreq=target_sfreq)
        del raw  # 释放原始数据内存

        # 滤波处理，设置1-100Hz频段
        raw_filtered = raw_resampled.copy().filter(l_freq=1, h_freq=100, n_jobs=2)
        del raw_resampled

        # 独立成分分析（ICA）- 优化ICA计算
        raw_ica = raw_filtered.copy()
        ica = mne.preprocessing.ICA(
            n_components=20,
            method='fastica',  # 使用更快的FastICA算法
            max_iter=200,      # 限制迭代次数
            random_state=42    # 固定随机种子
        )
        ica.fit(raw_ica, decim=3)  # 降采样以加速ICA
        del raw_ica

        # 基于平均通道重新参考
        raw_ref = raw_filtered.copy()
        raw_ref.set_eeg_reference(ref_channels="average", projection=False)
        del raw_filtered

        # 创建Epochs对象
        t_min = -1.0
        t_max = 1.0 - 1 / target_sfreq
        reject_criteria = dict(eeg=100e-6)  # 初始阈值
        max_attempts = 5  # 最大尝试次数，防止无限循环
        attempt = 0

        while attempt < max_attempts:
            try:
                print(f"尝试创建Epochs，当前reject_criteria: {reject_criteria}")
                epochs = mne.Epochs(
                    raw_ref, 
                    events=events, 
                    event_id=event_id, 
                    tmin=t_min, 
                    tmax=t_max, 
                    reject=reject_criteria, 
                    baseline=None, 
                    preload=True
                )
                
                # 获取epochs数据
                epochs_data = epochs.get_data()
                print(f"当前获得的epochs数量: {epochs_data.shape[0]}")
                
                # 检查epochs数量是否足够
                if epochs_data.shape[0] >= 108:
                    print("获得足够的epochs数量")
                    break
                else:
                    print(f"epochs数量不足（{epochs_data.shape[0]} < 108），增加阈值重试")
                    # 增加阈值
                    reject_criteria['eeg'] *= 10
                    attempt += 1
                    
                del epochs_data  # 释放内存
                
            except Exception as e:
                print(f"创建Epochs时出错: {str(e)}")
                reject_criteria['eeg'] *= 10
                attempt += 1

        if attempt >= max_attempts:
            print("警告：达到最大尝试次数，使用最后一次的结果")

        del raw_ref

        # 验证epochs数据的有效性
        epochs_data = epochs.get_data()
        if epochs_data.size == 0:
            print("生成的epochs数据无效")
            return False

        # 调整epochs形状
        if epochs_data.shape[2] == 1001:
            epochs_data = epochs_data[:, :, :-1]
        
        # 只取最后108个epochs
        data = epochs_data[-108::, :, :]
        print(data.shape)
        del epochs_data

        # 保存处理后的数据
        save_dir = os.path.join(data_dir, 'fif.fif')
        epochs.save(save_dir, overwrite=True)
        return True
        
    except Exception as e:
        error_msg = f"数据预处理失败: {str(e)}\n{traceback.format_exc()}"
        print(error_msg)
        logging.error(error_msg)
        return False 