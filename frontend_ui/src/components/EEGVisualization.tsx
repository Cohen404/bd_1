import React, { useMemo } from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend } from 'recharts';
import Plot from 'react-plotly.js';

// 伪随机数生成器 - 基于种子的线性同余生成器
class SeededRandom {
  private seed: number;

  constructor(seed: number) {
    this.seed = seed % 2147483647;
    if (this.seed <= 0) this.seed += 2147483646;
  }

  // 生成 0-1 之间的伪随机数
  next(): number {
    this.seed = (this.seed * 16807) % 2147483647;
    return (this.seed - 1) / 2147483646;
  }

  // 生成指定范围内的随机数
  range(min: number, max: number): number {
    return min + this.next() * (max - min);
  }

  // 生成指定范围内的随机整数
  rangeInt(min: number, max: number): number {
    return Math.floor(this.range(min, max + 1));
  }
}

// 生成基于dataId和visualizationType的确定性EEG数据
const generateRandomEEGData = (dataId: number, visualizationType: string) => {
  const channels = Array.from({ length: 8 }, (_, i) => `通道${i + 1}`);
  
  // 根据dataId和visualizationType创建种子
  const typeHash = visualizationType.split('').reduce((acc, char) => acc + char.charCodeAt(0), 0);
  const baseSeed = dataId * 1000 + typeHash;
  
  // 为不同的数据类型创建不同的随机数生成器
  const createRng = (offset: number) => new SeededRandom(baseSeed + offset);
  
  // 生成更合理的EEG特征数据，确保每个通道都有明显不同的值
  const generateChannelData = (min: number, max: number, decimals: number, seedOffset: number) => {
    const rng = createRng(seedOffset);
    return channels.map((_, index) => {
      // 为每个通道生成不同的基础值，确保数据有差异
      const baseValue = min + (max - min) * (index / (channels.length - 1)) * 0.7;
      const randomVariation = (rng.next() - 0.5) * (max - min) * 0.15;
      const finalValue = Math.max(min, Math.min(max, baseValue + randomVariation));
      const result = parseFloat(finalValue.toFixed(decimals));
      
      return result;
    });
  };
  
  // 生成整数型通道数据
  const generateIntChannelData = (baseMin: number, baseMax: number, step: number, seedOffset: number) => {
    const rng = createRng(seedOffset);
    return channels.map((_, index) => {
      const base = baseMin + index * step;
      const variation = rng.rangeInt(-5, 5);
      return Math.max(baseMin, base + variation);
    });
  };
  
  const data = {
    channels,
    // 功率特征数据 (μV²) - 更真实的EEG功率范围
    // Theta波段 (4-8Hz): 通常在放松或浅睡眠时较强
    thetaPower: generateChannelData(1.2, 4.8, 2, 100),
    // Alpha波段 (8-13Hz): 清醒放松状态，闭眼时增强
    alphaPower: generateChannelData(2.5, 8.5, 2, 200),
    // Beta波段 (13-30Hz): 清醒活跃思考状态
    betaPower: generateChannelData(0.8, 3.5, 2, 300),
    // Gamma波段 (30-100Hz): 高级认知处理
    gammaPower: generateChannelData(0.3, 1.8, 2, 400),
    
    // 频带特征数据 - 更真实的频带能量分布
    band1: generateChannelData(1.0, 4.5, 2, 500),  // 低频段
    band2: generateChannelData(1.8, 6.2, 2, 600),  // 中低频段
    band3: generateChannelData(2.2, 7.8, 2, 700),  // 中频段
    band4: generateChannelData(1.5, 5.5, 2, 800),  // 中高频段
    band5: generateChannelData(0.8, 3.2, 2, 900),  // 高频段
    
    // 时域特征数据 - 更真实的时域统计特征
    zeroCrossings: generateIntChannelData(25, 85, 8, 1000), // 过零率: 25-85次
    variance: generateChannelData(0.5, 2.5, 3, 1100), // 方差: 0.5-2.5 μV²
    energy: generateIntChannelData(100, 500, 50, 1200), // 能量: 100-500 μV²
    diff: generateChannelData(0.8, 3.5, 2, 1300), // 微分熵: 0.8-3.5
    
    // 血清指标数据 - 更真实的临床指标范围
    serum: ['CRP', 'IL-6', 'TNF-α', 'LDH', 'CK'],
    serumValues: (() => {
      // 为每个血清指标设置不同的真实范围
      const crp = createRng(1400).range(0.5, 15.0);      // CRP: 0.5-15 mg/L
      const il6 = createRng(1401).range(2.0, 50.0);      // IL-6: 2-50 pg/mL
      const tnf = createRng(1402).range(5.0, 80.0);      // TNF-α: 5-80 pg/mL
      const ldh = createRng(1403).range(120.0, 350.0);   // LDH: 120-350 U/L
      const ck = createRng(1404).range(30.0, 250.0);     // CK: 30-250 U/L
      return [
        parseFloat(crp.toFixed(1)),
        parseFloat(il6.toFixed(1)),
        parseFloat(tnf.toFixed(1)),
        parseFloat(ldh.toFixed(0)),
        parseFloat(ck.toFixed(0))
      ];
    })(),

    // 时频图（STFT）模拟数据 - 更真实的时频能量分布
    timeFreq: {
      x: Array.from({ length: 100 }, (_, i) => i * 0.05), // 时间: 0-5秒
      y: Array.from({ length: 50 }, (_, i) => i),   // 频率: 0-50 Hz
      z: (() => {
        const rng = createRng(1500);
        // 模拟更真实的时频能量分布，低频能量较高
        return Array.from({ length: 50 }, (_, freqIdx) => {
          // 频率越高，基础能量越低
          const baseEnergy = 30 - (freqIdx / 50) * 20; // 30降到10
          return Array.from({ length: 100 }, () => {
            const variation = rng.range(-5, 8);
            return Math.max(0, baseEnergy + variation);
          });
        });
      })(),
    },
  };
  
  
  return data;
};

// 辅助函数：创建柱状图
const BarChartComponent = ({ data, title, dataKey, color }: {
  data: any[];
  title: string;
  dataKey: string;
  color: string;
}) => (
  <div className="mb-6">
    <h3 className="text-lg font-semibold text-gray-900 mb-3 text-center">{title}</h3>
    <div className="bg-white p-4 rounded-lg border">
      <BarChart data={data} width={500} height={250}>
        <CartesianGrid strokeDasharray="3 3" />
        <XAxis dataKey="name" />
        <YAxis />
        <Tooltip />
        <Legend />
        <Bar dataKey={dataKey} fill={color} />
      </BarChart>
    </div>
  </div>
);

// 时频图组件（使用 Plotly）
const TimeFreqChart = ({ timeFreq }: { timeFreq: any }) => {
  return (
    <div className="mb-6">
      <h3 className="text-lg font-semibold text-gray-900 mb-3 text-center">时频域特征图</h3>
      <div className="bg-white p-4 rounded-lg border">
        <Plot
          data={[
            {
              z: timeFreq.z,
              x: timeFreq.x,
              y: timeFreq.y,
              type: 'heatmap',
              colorscale: 'Viridis',
              showscale: true,
            },
          ]}
          layout={{
            title: '时频域特征图',
            xaxis: { title: '时间 (s)' },
            yaxis: { title: '频率 (Hz)' },
            width: 500,
            height: 300,
          }}
        />
      </div>
    </div>
  );
};

// 血清指标图
const SerumChart = ({ serumData }: { serumData: any[] }) => (
  <div className="mb-6">
    <h3 className="text-lg font-semibold text-gray-900 mb-3 text-center">血清指标分析</h3>
    <div className="bg-white p-4 rounded-lg border">
      <BarChart data={serumData} width={500} height={250}>
        <CartesianGrid strokeDasharray="3 3" />
        <XAxis dataKey="name" />
        <YAxis />
        <Tooltip />
        <Bar dataKey="value" fill="#FF6B6B" />
      </BarChart>
    </div>
  </div>
);

// 微分熵特征图
const DiffEntropyChart = ({ data }: { data: any[] }) => (
  <div className="mb-6">
    <h3 className="text-lg font-semibold text-gray-900 mb-3 text-center">微分熵特征图</h3>
    <div className="bg-white p-4 rounded-lg border">
      <BarChart data={data} width={500} height={250}>
        <CartesianGrid strokeDasharray="3 3" />
        <XAxis dataKey="name" />
        <YAxis />
        <Tooltip />
        <Bar dataKey="Diff" fill="#4ECDC4" />
      </BarChart>
    </div>
  </div>
);

// 主组件
interface EEGVisualizationProps {
  visualizationType: string;
  dataId?: number;
}

const EEGVisualization: React.FC<EEGVisualizationProps> = ({ visualizationType, dataId }) => {
  // 使用useMemo缓存数据生成，只有当dataId或visualizationType变化时才重新生成
  // 使用dataId和visualizationType作为种子，确保相同的输入产生相同的输出
  const mockData = useMemo(() => generateRandomEEGData(dataId || 1, visualizationType), [dataId, visualizationType]);
  
  const channelData = useMemo(() => {
    const data = mockData.channels.map((channel, index) => ({
      name: channel,
      Theta: mockData.thetaPower[index],
      Alpha: mockData.alphaPower[index],
      Beta: mockData.betaPower[index],
      Gamma: mockData.gammaPower[index],
      Band1: mockData.band1[index],
      Band2: mockData.band2[index],
      Band3: mockData.band3[index],
      Band4: mockData.band4[index],
      Band5: mockData.band5[index],
      Zero: mockData.zeroCrossings[index],
      Variance: mockData.variance[index],
      Energy: mockData.energy[index],
      Diff: mockData.diff[index],
    }));
    
    
    return data;
  }, [mockData, visualizationType]);

  // 生成血清数据
  const serumData = useMemo(() => mockData.serum.map((label, i) => ({ 
    name: label, 
    value: mockData.serumValues[i] 
  })), [mockData]);

  const renderVisualization = () => {
    switch (visualizationType) {
      case 'differential_entropy':
        return <DiffEntropyChart data={channelData} />;
      
      case 'theta':
        return (
          <BarChartComponent
            data={channelData}
            title="Theta功率特征图"
            dataKey="Theta"
            color="#3498db"
          />
        );
      
      case 'alpha':
        return (
          <BarChartComponent
            data={channelData}
            title="Alpha功率特征图"
            dataKey="Alpha"
            color="#2ecc71"
          />
        );
      
      case 'beta':
        return (
          <BarChartComponent
            data={channelData}
            title="Beta功率特征图"
            dataKey="Beta"
            color="#e74c3c"
          />
        );
      
      case 'gamma':
        return (
          <BarChartComponent
            data={channelData}
            title="Gamma功率特征图"
            dataKey="Gamma"
            color="#f39c12"
          />
        );
      
      case 'frequency_band_1':
        return (
          <BarChartComponent
            data={channelData}
            title="均分频带1特征图"
            dataKey="Band1"
            color="#9b59b6"
          />
        );
      
      case 'frequency_band_2':
        return (
          <BarChartComponent
            data={channelData}
            title="均分频带2特征图"
            dataKey="Band2"
            color="#1abc9c"
          />
        );
      
      case 'frequency_band_3':
        return (
          <BarChartComponent
            data={channelData}
            title="均分频带3特征图"
            dataKey="Band3"
            color="#f1c40f"
          />
        );
      
      case 'frequency_band_4':
        return (
          <BarChartComponent
            data={channelData}
            title="均分频带4特征图"
            dataKey="Band4"
            color="#e67e22"
          />
        );
      
      case 'frequency_band_5':
        return (
          <BarChartComponent
            data={channelData}
            title="均分频带5特征图"
            dataKey="Band5"
            color="#34495e"
          />
        );
      
      case 'time_zero_crossing':
        return (
          <BarChartComponent
            data={channelData}
            title="时域特征-过零率"
            dataKey="Zero"
            color="#8e44ad"
          />
        );
      
      case 'time_variance':
        return (
          <BarChartComponent
            data={channelData}
            title="时域特征-方差"
            dataKey="Variance"
            color="#d35400"
          />
        );
      
      case 'time_energy':
        return (
          <BarChartComponent
            data={channelData}
            title="时域特征-能量"
            dataKey="Energy"
            color="#27ae60"
          />
        );
      
      case 'time_difference':
        return (
          <BarChartComponent
            data={channelData}
            title="时域特征-差分"
            dataKey="Diff"
            color="#1a535c"
          />
        );
      
      case 'frequency_wavelet':
        return <TimeFreqChart timeFreq={mockData.timeFreq} />;
      
      case 'serum_analysis':
        return <SerumChart serumData={serumData} />;
      
      default:
        return (
          <div className="text-center py-8">
            <p className="text-gray-500">未知的可视化类型: {visualizationType}</p>
          </div>
        );
    }
  };

  return (
    <div className="w-full">
      <div className="max-h-96 overflow-y-auto">
        {renderVisualization()}
      </div>
    </div>
  );
};

export default EEGVisualization;
