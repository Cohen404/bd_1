import numpy as np               # 导入numpy库用于数组和矩阵运算
import mne                      # 导入mne库用于处理神经电生理数据
import scipy.signal             # 导入scipy的signal模块用于信号处理
import pywt                     # 导入pywt库用于小波分析
from statsmodels.tsa.ar_model import AutoReg   # 导入自回归模型
import matplotlib.pyplot as plt # 导入matplotlib的pyplot模块用于绘图
import seaborn as sns           # 导入seaborn库用于数据可视化
import os
import pandas as pd

# 设置绘图风格
sns.set_style("whitegrid")      # 设置seaborn绘图的背景样式
plt.rcParams['font.sans-serif'] = ['SimHei']  # 设置中文显示
plt.rcParams['axes.unicode_minus'] = False    # 用于正常显示负号

# 全局变量
folder_path = ''

# 功能函数定义区
def zero_crossing_rate(signal):
    """计算信号的过零率。"""
    return ((signal[:-1] * signal[1:]) < 0).sum()

def energy(signal):
    """计算信号的能量。"""
    return np.sum(signal ** 2)

def difference(signal):
    """计算信号的差分值。"""
    return np.sum(np.diff(signal) ** 2)

def extract_band_power(frequencies, psd, band_range):
    """从给定的功率谱密度中提取特定频带的功率。"""
    mask = (frequencies >= band_range[0]) & (frequencies <= band_range[1])
    return np.sum(psd[mask])

def extract_theta_alpha_beta_gamma_powers(channel_data, sfreq):
    """提取Theta, Alpha, Beta 和 Gamma波段的功率。"""
    f, Pxx = compute_power_spectral_density(channel_data, sfreq)
    return {
        "Theta": extract_band_power(f, Pxx, (4, 8)),
        "Alpha": extract_band_power(f, Pxx, (8, 13)),
        "Beta": extract_band_power(f, Pxx, (13, 30)),
        "Gamma": extract_band_power(f, Pxx, (30, 40))
    }

def compute_power_spectral_density(signal, sfreq):
    """计算信号的功率谱密度。"""
    f, Pxx = scipy.signal.welch(signal, fs=sfreq, nperseg=sfreq * 2, noverlap=sfreq, scaling='density')
    return f, Pxx

def differential_entropy(psd):
    """计算功率谱密度的微分熵。"""
    psd_norm = psd / np.sum(psd)
    de = -np.sum(psd_norm * np.log2(psd_norm))
    return de

def compute_wavelet_energy(data):
    """计算小波系数的能量。"""
    coeffs = pywt.wavedec(data, 'db4', level=4)
    return [np.sum(np.square(coeff)) for coeff in coeffs]

# 数据加载和预处理函数
def load_preprocess_data(filename):
    """加载和预处理数据。"""
    data = mne.io.read_raw_edf(filename, preload=True)  # 加载EDF文件
    data.crop(tmin=10)                                  # 裁剪前10秒数据
    return data, data.get_data(picks='eeg')             # 返回预处理后的数据和EEG数据

# 特征提取函数
def extract_time_domain_features(channel_data):
    """提取时域特征。"""
    m = 2
    r = 0.2 * np.std(channel_data)  # 这是一个示例值，您可能需要根据实际数据进行调整
    lags = 4
    return {
         "过零率": zero_crossing_rate(channel_data),
         "方差": np.var(channel_data),
         "能量": energy(channel_data),
         "差分": difference(channel_data),
        # "近似熵": approximate_entropy(channel_data, m, r),
         #"样本熵": sample_entropy(channel_data, m, r),
         "AR": ar_coefficients(channel_data, lags)
    }


def extract_frequency_domain_features(channel_data, sfreq):
    """提取频域特征。"""
    f, Pxx = compute_power_spectral_density(channel_data, sfreq)
    freq_bands = np.array_split(Pxx, 5)  # 将频率范围分为5个等间隔的频带
    avg_power = [np.mean(band) for band in freq_bands]
    return {
        "均分频带": avg_power,
        "5频带微分熵": differential_entropy(Pxx)
    }
def approximate_entropy(U, m, r):
    """计算近似熵"""
    def _maxdist(x_i, x_j):
        return max([abs(ua - va) for ua, va in zip(x_i, x_j)])

    def _phi(m):
        x = [[U[j] for j in range(i, i + m - 1 + 1)] for i in range(N - m + 1)]
        C = [len([1 for x_j in x if _maxdist(x_i, x_j) <= r]) / (N - m + 1.0) for x_i in x]
        return (N - m + 1.0)**-1 * sum(np.log(C))

    N = len(U)
    print(4)
    return abs(_phi(m+1) - _phi(m))

def sample_entropy(U, m, r):
    """计算样本熵"""
    U = np.asarray(U)
    N = len(U)

    def _phi(m):
        x = np.array([U[i:i+m] for i in range(N - m + 1)])
        count = np.sum(np.abs(x[:, np.newaxis] - x).max(axis=2) <= r, axis=1)
        return np.sum(count) - (N - m + 1)
    print(1)
    return -np.log(_phi(m+1) / _phi(m))

def ar_coefficients(U, lags):
    """计算自回归模型系数"""
    model = AutoReg(U, lags=lags)
    model_fit = model.fit()
    print(4)
    return model_fit.params

def extract_time_frequency_features(channel_data):
    """提取时频域特征。"""
    return compute_wavelet_energy(channel_data)
def save_plot(fig, plot_name):
    """保存绘图到指定的文件夹"""
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
    file_path = os.path.join(folder_path, plot_name)
    fig.savefig(file_path)

def plot_time_domain_features(features):
    channel_indices = range(len(features))
    titles = ['过零率', '方差', '能量', '差分']
    for title in titles:
        plt.figure(figsize=(15, 5))
        plt.bar(channel_indices, [feature[title] for feature in features])
        plt.title(title)
        plt.xlabel('通道')
        plt.ylabel(f'{title}值')
        save_plot(plt.gcf(), f'time_{title}.png')
        plt.close()

def plot_frequency_domain_features(features):
    channel_indices = range(len(features))
    band_names = ["Band 1", "Band 2", "Band 3", "Band 4", "Band 5"]
    for idx, band_name in enumerate(band_names):
        plt.figure(figsize=(15, 5))
        avg_powers = [feature["均分频带"][idx] for feature in features]
        plt.bar(channel_indices, avg_powers)
        plt.title(f'均分频带: {band_name}')
        plt.xlabel('通道')
        plt.ylabel('功率')
        save_plot(plt.gcf(), f'frequency_band_{idx+1}.png')
        plt.close()

def plot_time_frequency_features(features):
    channel_indices = range(len(features))
    plt.figure(figsize=(15, 10))
    for idx in range(4):
        plt.subplot(2, 2, idx+1)
        energies = [feature[idx] for feature in features]
        plt.bar(channel_indices, energies)
        plt.title(f'小波变换能量: Level {idx+1}')
        plt.xlabel('通道')
        plt.ylabel('能量')
    plt.tight_layout()
    save_plot(plt.gcf(), 'frequency_wavelet.png')
    plt.close()

def plot_differential_entropy(features):
    channel_indices = range(len(features))
    plt.figure(figsize=(15, 5))
    de_values = [feature["5频带微分熵"] for feature in features]
    plt.bar(channel_indices, de_values)
    plt.title('微分熵')
    plt.xlabel('通道')
    plt.ylabel('微分熵值')
    save_plot(plt.gcf(), 'differential_entropy.png')
    plt.close()

def plot_theta_alpha_beta_gamma_powers(band_powers):
    bands = ["Theta", "Alpha", "Beta", "Gamma"]
    for band in bands:
        plt.figure(figsize=(15, 5))
        powers = [channel[band] for channel in band_powers]
        plt.bar(range(len(powers)), powers)
        plt.title(f'{band} 功率')
        plt.xlabel('通道')
        plt.ylabel('功率')
        save_plot(plt.gcf(), f'{band}.png')
        plt.close()

def print_time_domain_features(features):#打印时域特征
    for idx, feature in enumerate(features):
        print(f"通道 {idx + 1}:")#通道数
        for key, value in feature.items():#遍历字典
            print(f"  {key}: {value}")#打印键值对
        print("----------")

def print_frequency_domain_features(features):
    for idx, feature in enumerate(features):
        print(f"通道 {idx + 1}:")
        print("  均分频带:")
        for band, power in enumerate(feature["均分频带"]):
            print(f"    Band {band + 1}: {power}")
        print(f"  5频带微分熵: {feature['5频带微分熵']}")
        print("----------")

def print_time_frequency_features(features):
    for idx, feature in enumerate(features):
        print(f"通道 {idx + 1}: 小波变换能量 {feature}")
        print("----------")

def print_theta_alpha_beta_gamma_powers(powers):
    for idx, power in enumerate(powers):
        print(f"通道 {idx + 1}:")
        for band, value in power.items():
            print(f"  {band}: {value}")
        print("----------")

def create_feature_dataframe(time_domain_features, frequency_domain_features, time_frequency_features, theta_alpha_beta_gamma_powers):
    """
    创建一个包含所有特征的DataFrame
    """
    all_features = []
    feature_names = []

    for channel in range(len(time_domain_features)):
        channel_features = {}
        
        # 时域特征
        for key, value in time_domain_features[channel].items():
            if key == 'AR':
                for i, coef in enumerate(value):
                    channel_features[f'AR_coef_{i}'] = coef
                    if channel == 0:
                        feature_names.append(f'AR_coef_{i}')
            else:
                channel_features[key] = value
                if channel == 0:
                    feature_names.append(key)
        
        # 频域特征
        for i, power in enumerate(frequency_domain_features[channel]['均分频带']):
            channel_features[f'Band_{i+1}_power'] = power
            if channel == 0:
                feature_names.append(f'Band_{i+1}_power')
        channel_features['微分熵'] = frequency_domain_features[channel]['5频带微分熵']
        if channel == 0:
            feature_names.append('微分熵')
        
        # 时频域特征
        for i, energy in enumerate(time_frequency_features[channel]):
            channel_features[f'Wavelet_energy_{i+1}'] = energy
            if channel == 0:
                feature_names.append(f'Wavelet_energy_{i+1}')
        
        # Theta/Alpha/Beta/Gamma 功率
        for band, power in theta_alpha_beta_gamma_powers[channel].items():
            channel_features[f'{band}_power'] = power
            if channel == 0:
                feature_names.append(f'{band}_power')
        
        all_features.append(channel_features)
    
    df = pd.DataFrame(all_features)
    df.index.name = 'Channel'
    return df, feature_names

def analyze_eeg_data(file_path):
    # 加载和预处理数据
    data1, eeg_data = load_preprocess_data(file_path)
    global folder_path  # 声明要修改全局变量
    folder_path = os.path.dirname(file_path)

    # 提取特征
    time_domain_features = [extract_time_domain_features(channel) for channel in eeg_data]
    frequency_domain_features = [extract_frequency_domain_features(channel, data1.info['sfreq']) for channel in eeg_data]
    time_frequency_features = [extract_time_frequency_features(channel) for channel in eeg_data]
    theta_alpha_beta_gamma_powers = [extract_theta_alpha_beta_gamma_powers(channel, data1.info['sfreq']) for channel in eeg_data]

    # 创建特征DataFrame
    feature_df, feature_names = create_feature_dataframe(time_domain_features, frequency_domain_features, time_frequency_features, theta_alpha_beta_gamma_powers)

    # 保存DataFrame到CSV文件
    csv_path = os.path.join(folder_path, 'eeg_features.csv')
    feature_df.to_csv(csv_path)
    print(f"特征已保存到: {csv_path}")

    # 保存特征名称到文本文件
    feature_names_path = os.path.join(folder_path, 'feature_names.txt')
    with open(feature_names_path, 'w') as f:
        for name in feature_names:
            f.write(f"{name}\n")
    print(f"特征名称已保存到: {feature_names_path}")

    # 可视化
    plot_time_domain_features(time_domain_features)
    plot_frequency_domain_features(frequency_domain_features)
    plot_time_frequency_features(time_frequency_features)
    plot_differential_entropy(frequency_domain_features)
    plot_theta_alpha_beta_gamma_powers(theta_alpha_beta_gamma_powers)
    return feature_df, feature_names

# 如果需要，您可以在这里调用 analyze_eeg_data 函数
# feature_df, feature_names = analyze_eeg_data('your_eeg_file.edf')