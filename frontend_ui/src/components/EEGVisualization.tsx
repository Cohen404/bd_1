import React, { useMemo } from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend } from 'recharts';
import Plot from 'react-plotly.js';

// 生成随机EEG数据的辅助函数
const generateRandomEEGData = () => {
  const channels = Array.from({ length: 8 }, (_, i) => `通道${i + 1}`);
  
  // 生成更合理的EEG特征数据，确保每个通道都有明显不同的值
  const generateChannelData = (min: number, max: number, decimals: number = 2) => {
    return channels.map((_, index) => {
      // 为每个通道生成不同的基础值，确保数据有差异
      // 使用更简单的算法，确保每个通道都有明显不同的值
      const baseValue = min + (max - min) * (index / (channels.length - 1)) * 0.7;
      const randomVariation = (Math.random() - 0.5) * (max - min) * 0.15;
      const finalValue = Math.max(min, Math.min(max, baseValue + randomVariation));
      const result = parseFloat(finalValue.toFixed(decimals));
      
      return result;
    });
  };
  
  const data = {
    channels,
    // 功率特征数据 (μV²) - 更合理的范围，确保每个通道都有明显差异
    thetaPower: generateChannelData(0.5, 2.5, 2),
    alphaPower: generateChannelData(0.8, 3.2, 2),
    betaPower: generateChannelData(0.3, 1.8, 2),
    gammaPower: generateChannelData(0.1, 1.2, 2),
    
    // 频带特征数据
    band1: generateChannelData(0.4, 2.0, 2),
    band2: generateChannelData(0.6, 2.8, 2),
    band3: generateChannelData(0.8, 3.5, 2),
    band4: generateChannelData(1.0, 4.2, 2),
    band5: generateChannelData(1.2, 5.0, 2),
    
    // 时域特征数据 - 确保每个通道都有明显不同的值
    zeroCrossings: channels.map((_, index) => Math.floor(10 + index * 4 + Math.random() * 10)), // 10-40次，递增趋势
    variance: generateChannelData(0.1, 0.8, 3), // 方差
    energy: channels.map((_, index) => Math.floor(50 + index * 30 + Math.random() * 50)), // 50-300，递增趋势
    diff: generateChannelData(0.2, 1.5, 2), // 微分熵特征
    
    // 血清指标数据
    serum: ['CRP', 'IL-6', 'TNF-α', 'LDH', 'CK'],
    serumValues: generateChannelData(0.5, 5.0, 1).slice(0, 5), // 取前5个值

    // 时频图（STFT）模拟数据
    timeFreq: {
      x: Array.from({ length: 100 }, (_, i) => i * 0.01), // 时间 (秒)
      y: Array.from({ length: 50 }, (_, i) => i * 0.5),   // 频率 (Hz)
      z: Array.from({ length: 50 }, () =>
        Array.from({ length: 100 }, () => Math.random() * 20 + 10)
      ),
    },
  };
  
  
  return data;
};

// 注意：mockData将在组件内部生成，确保每次渲染都有新的随机数据

// 辅助函数：创建柱状图
const BarChartComponent = ({ data, title, key, color }: {
  data: any[];
  title: string;
  key: string;
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
        <Bar dataKey={key} fill={color} />
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
  const mockData = useMemo(() => generateRandomEEGData(), [dataId, visualizationType]);
  
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
            key="Theta"
            color="#3498db"
          />
        );
      
      case 'alpha':
        return (
          <BarChartComponent
            data={channelData}
            title="Alpha功率特征图"
            key="Alpha"
            color="#2ecc71"
          />
        );
      
      case 'beta':
        return (
          <BarChartComponent
            data={channelData}
            title="Beta功率特征图"
            key="Beta"
            color="#e74c3c"
          />
        );
      
      case 'gamma':
        return (
          <BarChartComponent
            data={channelData}
            title="Gamma功率特征图"
            key="Gamma"
            color="#f39c12"
          />
        );
      
      case 'frequency_band_1':
        return (
          <BarChartComponent
            data={channelData}
            title="均分频带1特征图"
            key="Band1"
            color="#9b59b6"
          />
        );
      
      case 'frequency_band_2':
        return (
          <BarChartComponent
            data={channelData}
            title="均分频带2特征图"
            key="Band2"
            color="#1abc9c"
          />
        );
      
      case 'frequency_band_3':
        return (
          <BarChartComponent
            data={channelData}
            title="均分频带3特征图"
            key="Band3"
            color="#f1c40f"
          />
        );
      
      case 'frequency_band_4':
        return (
          <BarChartComponent
            data={channelData}
            title="均分频带4特征图"
            key="Band4"
            color="#e67e22"
          />
        );
      
      case 'frequency_band_5':
        return (
          <BarChartComponent
            data={channelData}
            title="均分频带5特征图"
            key="Band5"
            color="#34495e"
          />
        );
      
      case 'time_zero_crossing':
        return (
          <BarChartComponent
            data={channelData}
            title="时域特征-过零率"
            key="Zero"
            color="#8e44ad"
          />
        );
      
      case 'time_variance':
        return (
          <BarChartComponent
            data={channelData}
            title="时域特征-方差"
            key="Variance"
            color="#d35400"
          />
        );
      
      case 'time_energy':
        return (
          <BarChartComponent
            data={channelData}
            title="时域特征-能量"
            key="Energy"
            color="#27ae60"
          />
        );
      
      case 'time_difference':
        return (
          <BarChartComponent
            data={channelData}
            title="时域特征-差分"
            key="Diff"
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
