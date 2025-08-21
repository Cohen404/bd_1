import numpy as np               # 导入numpy库用于数组和矩阵运算
import mne                      # 导入mne库用于处理神经电生理数据
import scipy.signal             # 导入scipy的signal模块用于信号处理
import pywt                     # 导入pywt库用于小波分析
from statsmodels.tsa.ar_model import AutoReg   # 导入自回归模型
import matplotlib.pyplot as plt # 导入matplotlib的pyplot模块用于绘图
import seaborn as sns           # 导入seaborn库用于数据可视化
import os
import pandas as pd
import logging
import traceback
import matplotlib.font_manager as fm
import urllib.request
import shutil

# 设置绘图风格
sns.set_style("whitegrid")      # 设置seaborn绘图的背景样式

# 设置中文字体
def setup_chinese_font():
    """设置中文字体"""
    import warnings
    import platform
    
    # 根据操作系统选择不同的字体优先级
    system = platform.system()
    if system == "Darwin":  # macOS
        chinese_fonts = ['PingFang SC', 'Heiti SC', 'STHeiti', 'Arial Unicode MS']
    elif system == "Windows":
        chinese_fonts = ['Microsoft YaHei', 'SimHei', 'SimSun', 'STSong']
    else:  # Linux
        chinese_fonts = ['DejaVu Sans', 'WenQuanYi Micro Hei', 'WenQuanYi Zen Hei']
    
    font_prop = None
    
    # 临时禁用matplotlib字体警告
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        
        for font_name in chinese_fonts:
            try:
                # 检查字体是否可用
                font_families = [f.name for f in fm.fontManager.ttflist]
                if font_name in font_families:
                    font_prop = fm.FontProperties(family=font_name)
                    logging.info(f"使用字体: {font_name}")
                    break
                else:
                    # 尝试使用findfont查找类似字体
                    font_path = fm.findfont(fm.FontProperties(family=font_name), fallback_to_default=False)
                    if font_path and os.path.exists(font_path) and 'default' not in font_path.lower():
                        font_prop = fm.FontProperties(family=font_name)
                        logging.info(f"使用字体: {font_name}")
                        break
            except Exception:
                continue
    
    if font_prop is None:
        logging.warning("未找到合适的中文字体，使用默认字体")
        # 设置matplotlib使用默认字体并禁用中文显示警告
        plt.rcParams['font.sans-serif'] = ['DejaVu Sans']
        plt.rcParams['axes.unicode_minus'] = False
        font_prop = fm.FontProperties()
    else:
        # 设置matplotlib全局字体
        plt.rcParams['font.sans-serif'] = [font_prop.get_name()]
        plt.rcParams['axes.unicode_minus'] = False
    
    # 设置全局字体
    plt.rcParams['font.family'] = ['sans-serif']
    
    return font_prop

# 初始化中文字体
chinese_font = setup_chinese_font()

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
    # 检查文件扩展名
    ext = os.path.splitext(filename)[1].lower()
    
    if ext == '.edf':
        data = mne.io.read_raw_edf(filename, preload=True)  # 加载EDF文件
        data.crop(tmin=10)                                  # 裁剪前10秒数据
        return data, data.get_data(picks='eeg')             # 返回预处理后的数据和EEG数据
    elif ext == '.fif':
        # 读取fif文件
        try:
            # 首先尝试作为raw数据读取
            data = mne.io.read_raw_fif(filename, preload=True)
            return data, data.get_data(picks='eeg')
        except:
            try:
                # 如果失败，尝试作为epochs数据读取
                epochs = mne.read_epochs(filename, preload=True)
                # 获取所有trials的平均数据
                data = epochs.average()
                return data, data.data
            except Exception as e:
                print(f"无法读取fif文件: {e}")
                raise

    else:
        raise NotImplementedError(f"不支持的文件格式: {ext}")

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
    return abs(_phi(m+1) - _phi(m))

def sample_entropy(U, m, r):
    """计算样本熵"""
    U = np.asarray(U)
    N = len(U)

    def _phi(m):
        x = np.array([U[i:i+m] for i in range(N - m + 1)])
        count = np.sum(np.abs(x[:, np.newaxis] - x).max(axis=2) <= r, axis=1)
        return np.sum(count) - (N - m + 1)
    
    return -np.log(_phi(m+1) / _phi(m))

def ar_coefficients(U, lags):
    """计算自回归模型系数"""
    try:
        model = AutoReg(U, lags=lags)
        model_fit = model.fit()
        return model_fit.params
    except Exception as e:
        logging.warning(f"AR系数计算失败: {str(e)}")
        return np.zeros(lags + 1)  # 返回零数组作为默认值

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
        plt.title(title, fontproperties=chinese_font)
        plt.xlabel('通道', fontproperties=chinese_font)
        plt.ylabel(f'{title}值', fontproperties=chinese_font)
        save_plot(plt.gcf(), f'time_{title}.png')
        plt.close()

def plot_frequency_domain_features(features):
    channel_indices = range(len(features))
    band_names = ["Band 1", "Band 2", "Band 3", "Band 4", "Band 5"]
    for idx, band_name in enumerate(band_names):
        plt.figure(figsize=(15, 5))
        avg_powers = [feature["均分频带"][idx] for feature in features]
        plt.bar(channel_indices, avg_powers)
        plt.title(f'均分频带: {band_name}', fontproperties=chinese_font)
        plt.xlabel('通道', fontproperties=chinese_font)
        plt.ylabel('功率', fontproperties=chinese_font)
        save_plot(plt.gcf(), f'frequency_band_{idx+1}.png')
        plt.close()

def plot_time_frequency_features(features):
    channel_indices = range(len(features))
    plt.figure(figsize=(15, 10))
    for idx in range(4):
        plt.subplot(2, 2, idx+1)
        energies = [feature[idx] for feature in features]
        plt.bar(channel_indices, energies)
        plt.title(f'小波变换能量: Level {idx+1}', fontproperties=chinese_font)
        plt.xlabel('通道', fontproperties=chinese_font)
        plt.ylabel('能量', fontproperties=chinese_font)
    plt.tight_layout()
    save_plot(plt.gcf(), 'frequency_wavelet.png')
    plt.close()

def plot_differential_entropy(features):
    channel_indices = range(len(features))
    plt.figure(figsize=(15, 5))
    de_values = [feature["5频带微分熵"] for feature in features]
    plt.bar(channel_indices, de_values)
    plt.title('微分熵', fontproperties=chinese_font)
    plt.xlabel('通道', fontproperties=chinese_font)
    plt.ylabel('微分熵值', fontproperties=chinese_font)
    save_plot(plt.gcf(), 'differential_entropy.png')
    plt.close()

def plot_theta_alpha_beta_gamma_powers(band_powers):
    bands = ["Theta", "Alpha", "Beta", "Gamma"]
    for band in bands:
        plt.figure(figsize=(15, 5))
        powers = [channel[band] for channel in band_powers]
        plt.bar(range(len(powers)), powers)
        plt.title(f'{band} 功率', fontproperties=chinese_font)
        plt.xlabel('通道', fontproperties=chinese_font)
        plt.ylabel('功率', fontproperties=chinese_font)
        save_plot(plt.gcf(), f'{band}.png')
        plt.close()

def print_time_domain_features(features):
    """打印时域特征"""
    for idx, feature in enumerate(features):
        print(f"通道 {idx + 1}:")
        for key, value in feature.items():
            print(f"  {key}: {value}")
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
    """
    分析EEG数据并提取特征
    
    参数：
    file_path: EEG数据文件路径
    
    功能：
    - 检查是否已存在fif文件和可视化图片，如果都存在则直接返回True
    - 如果只有fif文件但没有图片，则只生成可视化图像
    - 如果都不存在，则进行特征提取和可视化
    
    返回：
    bool: 处理是否成功
    """
    try:
        # 获取数据目录路径
        data_dir = os.path.dirname(file_path)
        global folder_path
        folder_path = data_dir

        # 检查是否已存在可视化图片
        required_images = [
            'time_过零率.png', 'time_方差.png', 'time_能量.png', 'time_差分.png',
            'frequency_band_1.png', 'frequency_band_2.png', 'frequency_band_3.png',
            'frequency_band_4.png', 'frequency_band_5.png',
            'frequency_wavelet.png', 'differential_entropy.png',
            'Theta.png', 'Alpha.png', 'Beta.png', 'Gamma.png'
        ]
        
        # 先检查当前目录
        all_images_exist = all(os.path.exists(os.path.join(data_dir, img)) for img in required_images)
        
        # 如果当前目录没有图片，检查子目录
        if not all_images_exist:
            for item in os.listdir(data_dir):
                item_path = os.path.join(data_dir, item)
                if os.path.isdir(item_path):
                    sub_images_exist = all(os.path.exists(os.path.join(item_path, img)) for img in required_images)
                    if sub_images_exist:
                        all_images_exist = True
                        # 更新folder_path为子目录
                        folder_path = item_path
                        break
        
        # 检查fif文件路径
        fif_file_path = None
        if file_path.endswith('.fif'):
            fif_file_path = file_path
        else:
            # 在数据目录中查找fif文件
            fif_files = [f for f in os.listdir(data_dir) if f.endswith('.fif')]
            if fif_files:
                fif_file_path = os.path.join(data_dir, fif_files[0])
        
        # 如果是fif文件且所有图片都存在，直接返回
        if fif_file_path and all_images_exist:
            logging.info(f"File {fif_file_path} is already processed with visualizations")
            return True

        # 加载和预处理数据
        # 如果有fif文件，使用fif文件，否则使用传入的文件路径
        actual_file_path = fif_file_path if fif_file_path else file_path
        data1, eeg_data = load_preprocess_data(actual_file_path)

        # 如果数据是3D的（epochs数据），取平均值转换为2D
        if len(eeg_data.shape) == 3:
            eeg_data = np.mean(eeg_data, axis=0)

        # 提取特征
        time_domain_features = [extract_time_domain_features(channel) for channel in eeg_data]
        
        # 获取采样频率
        if isinstance(data1, mne.io.Raw):
            sfreq = data1.info['sfreq']
        else:  # Epochs或Evoked对象
            sfreq = data1.info['sfreq']
            
        frequency_domain_features = [extract_frequency_domain_features(channel, sfreq) for channel in eeg_data]
        time_frequency_features = [extract_time_frequency_features(channel) for channel in eeg_data]
        theta_alpha_beta_gamma_powers = [extract_theta_alpha_beta_gamma_powers(channel, sfreq) for channel in eeg_data]

        # 如果不是fif文件，则保存特征到CSV
        if not actual_file_path.endswith('.fif'):
            # 创建特征DataFrame
            feature_df, feature_names = create_feature_dataframe(
                time_domain_features, 
                frequency_domain_features, 
                time_frequency_features, 
                theta_alpha_beta_gamma_powers
            )

            # 保存DataFrame到CSV文件
            csv_path = os.path.join(folder_path, 'eeg_features.csv')
            feature_df.to_csv(csv_path)
            logging.info(f"特征已保存到: {csv_path}")

            # 保存特征名称到文本文件
            feature_names_path = os.path.join(folder_path, 'feature_names.txt')
            with open(feature_names_path, 'w') as f:
                for name in feature_names:
                    f.write(f"{name}\n")
            logging.info(f"特征名称已保存到: {feature_names_path}")

        # 如果图片不完整，则生成可视化图像
        if not all_images_exist:
            plot_time_domain_features(time_domain_features)
            plot_frequency_domain_features(frequency_domain_features)
            plot_time_frequency_features(time_frequency_features)
            plot_differential_entropy(frequency_domain_features)
            plot_theta_alpha_beta_gamma_powers(theta_alpha_beta_gamma_powers)
        
        if not actual_file_path.endswith('.fif'):
            return feature_df, feature_names
        return True
        
    except Exception as e:
        logging.error(f"分析过程中出现错误: {str(e)}")
        raise

def plot_serum_data(data_path):
    """
    绘制血清数据的可视化图表
    
    参数:
    - data_path: 数据路径
    """
    try:
        # 读取血清数据
        xq_path = os.path.join(data_path, 'xq.csv')
        if not os.path.exists(xq_path):
            logging.warning(f"血清数据文件不存在: {xq_path}")
            return
            
        # 读取数据，第一行为表头
        df = pd.read_csv(xq_path)
        if len(df) < 1:
            logging.warning("血清数据为空")
            return
            
        # 处理数据，将特殊值和字符串转换为数值
        values = []
        for val in df.values.flatten():
            try:
                # 如果是字符串类型且包含"<"，取"<"后面的数值的一半
                if isinstance(val, str) and '<' in val:
                    num_val = float(val.replace('<', '')) / 2
                    values.append(num_val)
                else:
                    values.append(float(val))
            except (ValueError, TypeError):
                # 如果无法转换为数值，使用0
                values.append(0)
                logging.warning(f"无法转换的值: {val}，使用0代替")
        
        # 创建柱状图
        plt.figure(figsize=(15, 8))
        bars = plt.bar(range(len(values)), values)
        # 使用自定义的指标名称
        custom_labels = [
            "HCY", "E", "DA", "NE", "孕酮", "17-羟孕酮", "孕烯醇酮", "皮质醇",
            "17-羟孕烯醇酮", "21-脱氧皮质醇", "可的松", "18-羟皮质醇", "18-氧皮质醇", "11-脱氧皮质醇"
        ]
        # 根据数据长度自适应标签
        data_length = len(values)
        labels = []
        for i in range(data_length):
            label_index = i % len(custom_labels)
            if i >= len(custom_labels):
                labels.append(f"{custom_labels[label_index]}_{i//len(custom_labels)+1}")
            else:
                labels.append(custom_labels[label_index])
        plt.xticks(range(len(values)), labels, rotation=45, ha='right', fontproperties=chinese_font)
        plt.title('血清指标分析', fontproperties=chinese_font)
        plt.xlabel('指标名称', fontproperties=chinese_font)
        plt.ylabel('指标值', fontproperties=chinese_font)
        
        # 在柱子上添加数值标签
        for bar, val, orig_val in zip(bars, values, df.iloc[0].values):
            if isinstance(orig_val, str) and '<' in orig_val:
                # 对于小于某值的情况，显示原始字符串
                plt.text(bar.get_x() + bar.get_width()/2, bar.get_height(),
                        orig_val, ha='center', va='bottom', fontproperties=chinese_font)
            else:
                # 对于普通数值，显示数值
                plt.text(bar.get_x() + bar.get_width()/2, bar.get_height(),
                        f'{val:.1f}', ha='center', va='bottom', fontproperties=chinese_font)
        
        plt.tight_layout()
        
        # 保存图片
        save_plot(plt.gcf(), 'serum_analysis.png')
        plt.close()
        
    except Exception as e:
        logging.error(f"绘制血清数据图表时发生错误: {str(e)}")
        logging.error(traceback.format_exc())

def plot_scale_data(data_path):
    """
    绘制量表数据的可视化图表
    
    参数:
    - data_path: 数据路径
    """
    try:
        # 读取量表数据
        lb_path = os.path.join(data_path, 'lb.csv')
        if not os.path.exists(lb_path):
            logging.warning(f"量表数据文件不存在: {lb_path}")
            return
            
        # 读取数据，没有表头
        df = pd.read_csv(lb_path, header=None)
        if len(df) < 1:
            logging.warning("量表数据为空")
            return
            
        # 创建柱状图
        plt.figure(figsize=(15, 8))
        
        # 创建x轴位置
        x = np.arange(40)
        
        # 绘制柱状图，前20题为焦虑量表（蓝色），后20题为抑郁量表（橙色）
        bars1 = plt.bar(x[:20], df.iloc[0, :20], color='#4B9CD3', label='焦虑量表')
        bars2 = plt.bar(x[20:], df.iloc[0, 20:], color='#F4A460', label='抑郁量表')
        
        # 添加分隔线
        plt.axvline(x=19.5, color='r', linestyle='--', alpha=0.3)
        
        # 设置标题和标签
        plt.title('量表得分分析', fontproperties=chinese_font)
        plt.xlabel('题目序号', fontproperties=chinese_font)
        plt.ylabel('得分', fontproperties=chinese_font)
        plt.legend(prop=chinese_font)
        
        # 设置x轴刻度
        plt.xticks(x, [str(i+1) for i in x], rotation=45)
        
        # 设置y轴范围（量表得分范围为1-5）
        plt.ylim(0, 5.5)
        
        # 在柱子上添加数值标签
        for bars in [bars1, bars2]:
            for bar in bars:
                height = bar.get_height()
                plt.text(bar.get_x() + bar.get_width()/2., height,
                        f'{height:.0f}', ha='center', va='bottom', fontproperties=chinese_font)
        
        # 添加网格线
        plt.grid(True, axis='y', linestyle='--', alpha=0.3)
        
        plt.tight_layout()
        
        # 保存图片
        save_plot(plt.gcf(), 'scale_analysis.png')
        plt.close()
        
    except Exception as e:
        logging.error(f"绘制量表数据图表时发生错误: {str(e)}")
        logging.error(traceback.format_exc()) 