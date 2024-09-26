import numpy as np               # 导入numpy库用于数组和矩阵运算
import mne                      # 导入mne库用于处理神经电生理数据
import scipy.signal             # 导入scipy的signal模块用于信号处理
import pywt                     # 导入pywt库用于小波分析
from statsmodels.tsa.ar_model import AutoReg   # 导入自回归模型
import matplotlib.pyplot as plt # 导入matplotlib的pyplot模块用于绘图
import seaborn as sns           # 导入seaborn库用于数据可视化
import os

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
    plt.figure(figsize=(15, 8))
    titles = ['过零率', '方差', '能量', '差分']
    for idx, title in enumerate(titles, 1):
        plt.subplot(2, 2, idx)
        plt.bar(channel_indices, [feature[title] for feature in features])
        plt.title(title)
        plt.xlabel('通道')
        plt.ylabel(f'{title}值')
    plt.tight_layout()
    save_plot(plt.gcf(), 'time_domain_features.png')
    # plt.show()

def plot_frequency_domain_features(features):
    channel_indices = range(len(features))
    plt.figure(figsize=(15, 10))
    band_names = ["Band 1", "Band 2", "Band 3", "Band 4", "Band 5"]
    for idx, band_name in enumerate(band_names):
        plt.subplot(3, 2, idx+1)
        avg_powers = [feature["均分频带"][idx] for feature in features]
        # ptl todo
        plt.bar(channel_indices, avg_powers)
        plt.title(f'均分频带: {band_name}')
        plt.xlabel('通道')
        plt.ylabel('功率')
    plt.tight_layout()
    save_plot(plt.gcf(), 'frequency_domain_features.png')
    # plt.show()

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
    save_plot(plt.gcf(), 'time_frequency_features.png')
    # plt.show()

def plot_differential_entropy(features):
    channel_indices = range(len(features))
    plt.figure(figsize=(15, 5))
    de_values = [feature["5频带微分熵"] for feature in features]
    plt.bar(channel_indices, de_values)
    plt.title('微分熵')
    plt.xlabel('通道')
    plt.ylabel('微分熵值')
    save_plot(plt.gcf(), 'differential_entropy.png')
    # plt.show()

def plot_theta_alpha_beta_gamma_powers(band_powers):
    bands = ["Theta", "Alpha", "Beta", "Gamma"]
    plt.figure(figsize=(15, 8))
    for idx, band in enumerate(bands):
        plt.subplot(2, 2, idx+1)
        powers = [channel[band] for channel in band_powers]
        plt.bar(range(len(powers)), powers)
        plt.title(f'{band} 功率')
        plt.xlabel('通道')
        plt.ylabel('功率')
    plt.tight_layout()
    save_plot(plt.gcf(), 'theta_alpha_beta_gamma_powers.png')
    # plt.show()
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

    # 打印特征
    print("时域特征:")
    print_time_domain_features(time_domain_features)

    print("\n频域特征:")
    print_frequency_domain_features(frequency_domain_features)

    print("\n时频域特征:")
    print_time_frequency_features(time_frequency_features)

    print("\nTheta/Alpha/Beta/Gamma 功率:")
    print_theta_alpha_beta_gamma_powers(theta_alpha_beta_gamma_powers)

    # 可视化
    plot_time_domain_features(time_domain_features)
    plot_frequency_domain_features(frequency_domain_features)
    plot_time_frequency_features(time_frequency_features)
    plot_differential_entropy(frequency_domain_features)
    plot_theta_alpha_beta_gamma_powers(theta_alpha_beta_gamma_powers)
