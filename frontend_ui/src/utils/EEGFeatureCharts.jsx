import React from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend } from 'recharts';
import Plot from 'react-plotly.js';

// 模拟数据
const mockData = {
  channels: Array.from({ length: 8 }, (_, i) => `通道${i + 1}`),
  thetaPower: [0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9],
  alphaPower: [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8],
  betaPower: [0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0],
  gammaPower: [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8],
  band1: [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8],
  band2: [0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9],
  band3: [0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0],
  band4: [0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0, 1.1],
  band5: [0.5, 0.6, 0.7, 0.8, 0.9, 1.0, 1.1, 1.2],
  zeroCrossings: [15, 18, 20, 22, 25, 28, 30, 32],
  variance: [0.01, 0.02, 0.03, 0.04, 0.05, 0.06, 0.07, 0.08],
  energy: [100, 120, 140, 160, 180, 200, 220, 240],
  diff: [0.05, 0.06, 0.07, 0.08, 0.09, 0.10, 0.11, 0.12],
  serum: ['CRP', 'IL-6', 'TNF-α', 'LDH', 'CK'],
  serumValues: [2.1, 3.4, 1.8, 4.2, 2.9],

  // 时频图（STFT）模拟数据
  timeFreq: {
    x: Array.from({ length: 100 }, (_, i) => i * 0.01), // 时间 (秒)
    y: Array.from({ length: 50 }, (_, i) => i * 0.5),   // 频率 (Hz)
    z: Array.from({ length: 50 }, (_, i) =>
      Array.from({ length: 100 }, (_, j) => Math.random() * 20 + 10)
    ),
  },
};

// 辅助函数：创建柱状图
const BarChartComponent = ({ data, title, key, color }) => (
  <div style={{ margin: '20px 0' }}>
    <h3>{title}</h3>
    <BarChart data={data} width={600} height={300}>
      <CartesianGrid strokeDasharray="3 3" />
      <XAxis dataKey="name" />
      <YAxis />
      <Tooltip />
      <Legend />
      <Bar dataKey={key} fill={color} />
    </BarChart>
  </div>
);

// 时频图组件（使用 Plotly）
const TimeFreqChart = () => {
  const { timeFreq } = mockData;
  return (
    <div style={{ margin: '20px 0' }}>
      <h3>时频域特征图</h3>
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
          width: 600,
          height: 400,
        }}
      />
    </div>
  );
};

// 微分熵特征图
const DiffEntropyChart = () => (
  <div style={{ margin: '20px 0' }}>
    <h3>微分熵特征图</h3>
    <BarChart data={mockData.channels.map((ch, i) => ({ name: ch, entropy: mockData.diff[i] }))} width={600} height={300}>
      <CartesianGrid strokeDasharray="3 3" />
      <XAxis dataKey="name" />
      <YAxis />
      <Tooltip />
      <Bar dataKey="entropy" fill="#4ECDC4" />
    </BarChart>
  </div>
);

// 主组件
const EEGFeatureCharts = () => {
  const channelData = mockData.channels.map((channel, index) => ({
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

  return (
    <div style={{ padding: '20px', fontFamily: 'Arial, sans-serif' }}>
      {/* 功率特征图 */}
      <BarChartComponent
        data={channelData}
        title="Theta功率特征图"
        key="Theta"
        color="#3498db"
      />
      <BarChartComponent
        data={channelData}
        title="Alpha功率特征图"
        key="Alpha"
        color="#2ecc71"
      />
      <BarChartComponent
        data={channelData}
        title="Beta功率特征图"
        key="Beta"
        color="#e74c3c"
      />
      <BarChartComponent
        data={channelData}
        title="Gamma功率特征图"
        key="Gamma"
        color="#f39c12"
      />

      {/* 均分频带 */}
      <BarChartComponent
        data={channelData}
        title="均分频带1特征图"
        key="Band1"
        color="#9b59b6"
      />
      <BarChartComponent
        data={channelData}
        title="均分频带2特征图"
        key="Band2"
        color="#1abc9c"
      />
      <BarChartComponent
        data={channelData}
        title="均分频带3特征图"
        key="Band3"
        color="#f1c40f"
      />
      <BarChartComponent
        data={channelData}
        title="均分频带4特征图"
        key="Band4"
        color="#e67e22"
      />
      <BarChartComponent
        data={channelData}
        title="均分频带5特征图"
        key="Band5"
        color="#34495e"
      />

      {/* 时域特征 */}
      <BarChartComponent
        data={channelData}
        title="时域特征-过零率"
        key="Zero"
        color="#8e44ad"
      />
      <BarChartComponent
        data={channelData}
        title="时域特征-方差"
        key="Variance"
        color="#d35400"
      />
      <BarChartComponent
        data={channelData}
        title="时域特征-能量"
        key="Energy"
        color="#27ae60"
      />
      <BarChartComponent
        data={channelData}
        title="时域特征-差分"
        key="Diff"
        color="#1a535c"
      />

      {/* 时频图 */}
      <TimeFreqChart />

      {/* 微分熵 */}
      <DiffEntropyChart />
    </div>
  );
};

export default EEGFeatureCharts;