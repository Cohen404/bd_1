import matplotlib
import mne
import numpy as np
# LOAD RAW:
matplotlib.use('Qt5Agg')
exp_f_list = []
exp_f_list2 = []
num_of_data = 108
set_path = "E:/brain_data/焦虑/20230829205108_1-new_experienment.edf"
raw = mne.io.read_raw_edf(set_path)
set_path2 ="E:\EEG_literature\LOSO\dataset\EXP\second time\close eyes-2/resting-state-2001-2.edat3_204232_epoch_reref_reject_100uV_15_step7.edf"
raw2 = mne.io.read_raw_edf(set_path2)
set_path3 = "E:/EEG_literature/LOSO/dataset/EXP/first time/preprocessing-yiyu-1.fif"
raw3 = mne.read_epochs(set_path3)
set_path4 = "E:/EEG_literature/LOSO/dataset/EXP/first time/preprocessing-jiaolv-1.fif"
raw4 = mne.read_epochs(set_path4)
    # 上一行遇到问题了，记一下
#raw.load_data()
raw2.load_data()
raw3.load_data()
raw4.load_data()

#exp_data = raw.get_data()
exp_data = raw2.get_data()
exp_data3 = raw3.get_data()
exp_data4 = raw4.get_data()
#exp_data = raw.get_data()
# 如果时间点数为1001而非1000，进行裁剪
if exp_data4.shape[2] == 1001:
    epochs_data = exp_data4[:, :, :-1]
data = epochs_data[-(num_of_data)::, ::, ::]

segment_length = int(500 * 2)
# 获取数据的形状
num_channels, num_samples = exp_data.shape
#num_channels2, num_samples2 = exp_data2.shape
# 分段数据
segments = []
segments2 = []
for start in range(0, num_samples, segment_length):
    end = start + segment_length
    if end <= num_samples:
        segment = exp_data[:, start:end]
        segments.append(segment)
# 将seqments转换为NumPy数组
data_epochs = np.array(segments)

# 取最后n条数据，修改数据条数n请到最上方改全局变量
data = data_epochs[-(num_of_data)::, ::, ::]
exp_f_list.append(data)

exp_f_data = np.concatenate(exp_f_list, axis=0)

