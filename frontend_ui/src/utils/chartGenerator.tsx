// utils/chartGenerator.ts
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, Radar } from 'recharts';
import { createRoot } from 'react-dom/client';
import React from 'react';
import html2canvas from 'html2canvas';
import { ResultItem } from './localStorage';

// 生成EEG数据的辅助函数（与EEGVisualization.tsx一致）
const generateRandomEEGData = () => {
  const channels = Array.from({ length: 8 }, (_, i) => `通道${i + 1}`);
  
  const generateChannelData = (min: number, max: number, decimals: number = 2) => {
    return channels.map((_, index) => {
      const baseValue = min + (max - min) * (index / (channels.length - 1)) * 0.7;
      const randomVariation = (Math.random() - 0.5) * (max - min) * 0.15;
      const finalValue = Math.max(min, Math.min(max, baseValue + randomVariation));
      return parseFloat(finalValue.toFixed(decimals));
    });
  };
  
  return {
    channels,
    thetaPower: generateChannelData(0.5, 2.5, 2),
    alphaPower: generateChannelData(0.8, 3.2, 2),
    betaPower: generateChannelData(0.3, 1.8, 2),
    gammaPower: generateChannelData(0.1, 1.2, 2),
    band1: generateChannelData(0.4, 2.0, 2),
    band2: generateChannelData(0.6, 2.8, 2),
    band3: generateChannelData(0.8, 3.5, 2),
    band4: generateChannelData(1.0, 4.2, 2),
    band5: generateChannelData(1.2, 5.0, 2),
    zeroCrossings: channels.map((_, index) => Math.floor(10 + index * 4 + Math.random() * 10)),
    variance: generateChannelData(0.1, 0.8, 3),
    energy: channels.map((_, index) => Math.floor(50 + index * 30 + Math.random() * 50)),
    diff: generateChannelData(0.2, 1.5, 2),
    // 时频图（STFT）模拟数据
    timeFreq: {
      x: Array.from({ length: 100 }, (_, i) => i * 0.01), // 时间 (秒)
      y: Array.from({ length: 50 }, (_, i) => i * 0.5),   // 频率 (Hz)
      z: Array.from({ length: 50 }, () =>
        Array.from({ length: 100 }, () => Math.random() * 20 + 10)
      ),
    },
  };
};

export class ChartGenerator {
  // 生成雷达图
  static async generateRadarChart(result: ResultItem): Promise<string> {
    const data = [
      {
        subject: '应激',
        A: result.stress_score,
        fullMark: 100
      },
      {
        subject: '抑郁',
        A: result.depression_score,
        fullMark: 100
      },
      {
        subject: '焦虑',
        A: result.anxiety_score,
        fullMark: 100
      },
      {
        subject: '社交孤立',
        A: result.social_isolation_score,
        fullMark: 100
      }
    ];
    
    const RadarChartComponent = () => (
      <RadarChart width={500} height={350} data={data}>
        <PolarGrid stroke="#e0e0e0" />
        <PolarAngleAxis dataKey="subject" tick={{ fill: '#333', fontSize: 14 }} />
        <PolarRadiusAxis angle={90} domain={[0, 100]} tick={{ fill: '#666' }} />
        <Radar name="评分" dataKey="A" stroke="#3498db" fill="#3498db" fillOpacity={0.6} strokeWidth={2} />
        <Legend />
      </RadarChart>
    );
    
    return await this.renderChartToBase64(RadarChartComponent);
  }
  
  // 生成综合脑电功率图
  static async generateEEGChart(_result: ResultItem): Promise<string> {
    const eegData = generateRandomEEGData();
    const chartData = eegData.channels.map((channel, index) => ({
      name: channel,
      Theta: eegData.thetaPower[index],
      Alpha: eegData.alphaPower[index],
      Beta: eegData.betaPower[index],
      Gamma: eegData.gammaPower[index],
    }));
    
    const EEGChartComponent = () => (
      <BarChart width={700} height={350} data={chartData}>
        <CartesianGrid strokeDasharray="3 3" stroke="#e0e0e0" />
        <XAxis dataKey="name" tick={{ fill: '#333', fontSize: 12 }} />
        <YAxis tick={{ fill: '#666' }} label={{ value: '功率 (μV²)', angle: -90, position: 'insideLeft', style: { fill: '#333' } }} />
        <Tooltip 
          contentStyle={{ backgroundColor: '#fff', border: '1px solid #ccc', borderRadius: '4px' }}
          labelStyle={{ color: '#333', fontWeight: 'bold' }}
        />
        <Legend wrapperStyle={{ paddingTop: '10px' }} />
        <Bar dataKey="Theta" fill="#3498db" name="Theta波" />
        <Bar dataKey="Alpha" fill="#2ecc71" name="Alpha波" />
        <Bar dataKey="Beta" fill="#e74c3c" name="Beta波" />
        <Bar dataKey="Gamma" fill="#f39c12" name="Gamma波" />
      </BarChart>
    );
    
    return await this.renderChartToBase64(EEGChartComponent, 750, 400);
  }
  
  // 生成时域特征图（新增）
  static async generateTimeDomainChart(_result: ResultItem): Promise<string> {
    const eegData = generateRandomEEGData();
    const chartData = eegData.channels.map((channel, index) => ({
      name: channel,
      过零率: eegData.zeroCrossings[index],
      方差: eegData.variance[index] * 50, // 缩放以便显示
      能量: eegData.energy[index] / 10, // 缩放以便显示
      差分: eegData.diff[index] * 30, // 缩放以便显示
    }));
    
    const TimeDomainComponent = () => (
      <BarChart width={700} height={350} data={chartData}>
        <CartesianGrid strokeDasharray="3 3" stroke="#e0e0e0" />
        <XAxis dataKey="name" tick={{ fill: '#333', fontSize: 12 }} />
        <YAxis tick={{ fill: '#666' }} />
        <Tooltip 
          contentStyle={{ backgroundColor: '#fff', border: '1px solid #ccc', borderRadius: '4px' }}
        />
        <Legend wrapperStyle={{ paddingTop: '10px' }} />
        <Bar dataKey="过零率" fill="#8e44ad" name="过零率" />
        <Bar dataKey="方差" fill="#d35400" name="方差(×50)" />
        <Bar dataKey="能量" fill="#27ae60" name="能量(÷10)" />
        <Bar dataKey="差分" fill="#1a535c" name="差分(×30)" />
      </BarChart>
    );
    
    return await this.renderChartToBase64(TimeDomainComponent, 750, 400);
  }
  
  // 生成频带特征图（新增）
  static async generateFrequencyBandChart(_result: ResultItem): Promise<string> {
    const eegData = generateRandomEEGData();
    const chartData = eegData.channels.map((channel, index) => ({
      name: channel,
      Band1: eegData.band1[index],
      Band2: eegData.band2[index],
      Band3: eegData.band3[index],
      Band4: eegData.band4[index],
      Band5: eegData.band5[index],
    }));
    
    const FrequencyBandComponent = () => (
      <BarChart width={700} height={350} data={chartData}>
        <CartesianGrid strokeDasharray="3 3" stroke="#e0e0e0" />
        <XAxis dataKey="name" tick={{ fill: '#333', fontSize: 12 }} />
        <YAxis tick={{ fill: '#666' }} label={{ value: '功率', angle: -90, position: 'insideLeft', style: { fill: '#333' } }} />
        <Tooltip 
          contentStyle={{ backgroundColor: '#fff', border: '1px solid #ccc', borderRadius: '4px' }}
        />
        <Legend wrapperStyle={{ paddingTop: '10px' }} />
        <Bar dataKey="Band1" fill="#9b59b6" name="频带1" />
        <Bar dataKey="Band2" fill="#1abc9c" name="频带2" />
        <Bar dataKey="Band3" fill="#f1c40f" name="频带3" />
        <Bar dataKey="Band4" fill="#e67e22" name="频带4" />
        <Bar dataKey="Band5" fill="#34495e" name="频带5" />
      </BarChart>
    );
    
    return await this.renderChartToBase64(FrequencyBandComponent, 750, 400);
  }
  
  // 生成微分熵特征图（新增）
  static async generateDiffEntropyChart(_result: ResultItem): Promise<string> {
    const eegData = generateRandomEEGData();
    const chartData = eegData.channels.map((channel, index) => ({
      name: channel,
      微分熵: eegData.diff[index],
    }));
    
    const DiffEntropyComponent = () => (
      <BarChart width={700} height={350} data={chartData}>
        <CartesianGrid strokeDasharray="3 3" stroke="#e0e0e0" />
        <XAxis dataKey="name" tick={{ fill: '#333', fontSize: 12 }} />
        <YAxis tick={{ fill: '#666' }} label={{ value: '微分熵值', angle: -90, position: 'insideLeft', style: { fill: '#333' } }} />
        <Tooltip 
          contentStyle={{ backgroundColor: '#fff', border: '1px solid #ccc', borderRadius: '4px' }}
        />
        <Legend wrapperStyle={{ paddingTop: '10px' }} />
        <Bar dataKey="微分熵" fill="#4ECDC4" name="微分熵特征" />
      </BarChart>
    );
    
    return await this.renderChartToBase64(DiffEntropyComponent, 750, 400);
  }
  
  // 生成血清图
  static async generateSerumChart(_result: ResultItem): Promise<string> {
    const serumData = [
      { name: 'CRP', value: 2.1 + Math.random() * 2, unit: 'mg/L' },
      { name: 'IL-6', value: 3.4 + Math.random() * 2, unit: 'pg/mL' },
      { name: 'TNF-α', value: 1.8 + Math.random() * 2, unit: 'pg/mL' },
      { name: 'LDH', value: 4.2 + Math.random() * 2, unit: 'U/L' },
      { name: 'CK', value: 2.9 + Math.random() * 2, unit: 'U/L' }
    ];
    
    const SerumChartComponent = () => (
      <BarChart width={700} height={350} data={serumData}>
        <CartesianGrid strokeDasharray="3 3" stroke="#e0e0e0" />
        <XAxis dataKey="name" tick={{ fill: '#333', fontSize: 12 }} />
        <YAxis tick={{ fill: '#666' }} label={{ value: '浓度', angle: -90, position: 'insideLeft', style: { fill: '#333' } }} />
        <Tooltip 
          contentStyle={{ backgroundColor: '#fff', border: '1px solid #ccc', borderRadius: '4px' }}
        />
        <Legend wrapperStyle={{ paddingTop: '10px' }} />
        <Bar dataKey="value" fill="#FF6B6B" name="血清指标" />
      </BarChart>
    );
    
    return await this.renderChartToBase64(SerumChartComponent, 750, 400);
  }
  
  // 生成时频域特征图（新增）
  static async generateTimeFreqChart(_result: ResultItem): Promise<string> {
    const eegData = generateRandomEEGData();
    
    // 创建一个Canvas来绘制时频域热图
    const TimeFreqComponent = () => {
      const canvasRef = React.useRef<HTMLCanvasElement>(null);
      
      React.useEffect(() => {
        if (canvasRef.current) {
          const canvas = canvasRef.current;
          const ctx = canvas.getContext('2d');
          if (!ctx) return;
          
          const width = 700;
          const height = 350;
          const padding = 60;
          const plotWidth = width - 2 * padding;
          const plotHeight = height - 2 * padding;
          
          // 清空画布
          ctx.fillStyle = 'white';
          ctx.fillRect(0, 0, width, height);
          
          // 绘制时频域热图数据
          const timeSteps = eegData.timeFreq.x.length;
          const freqSteps = eegData.timeFreq.y.length;
          const cellWidth = plotWidth / timeSteps;
          const cellHeight = plotHeight / freqSteps;
          
          // 找到最大最小值用于归一化
          const allValues = eegData.timeFreq.z.flat();
          const minVal = Math.min(...allValues);
          const maxVal = Math.max(...allValues);
          
          // 绘制热图
          for (let i = 0; i < freqSteps; i++) {
            for (let j = 0; j < timeSteps; j++) {
              const value = eegData.timeFreq.z[i][j];
              const normalized = (value - minVal) / (maxVal - minVal);
              
              // 使用Viridis色系
              const r = Math.floor(255 * (0.267 + 0.004 * normalized));
              const g = Math.floor(255 * (0.004 + 0.5 * normalized));
              const b = Math.floor(255 * (0.329 + 0.6 * normalized));
              
              ctx.fillStyle = `rgb(${r}, ${g}, ${b})`;
              ctx.fillRect(
                padding + j * cellWidth,
                padding + (freqSteps - i - 1) * cellHeight,
                cellWidth + 1,
                cellHeight + 1
              );
            }
          }
          
          // 绘制边框
          ctx.strokeStyle = '#333';
          ctx.lineWidth = 2;
          ctx.strokeRect(padding, padding, plotWidth, plotHeight);
          
          // 绘制坐标轴标签
          ctx.fillStyle = '#333';
          ctx.font = 'bold 14px Arial';
          ctx.textAlign = 'center';
          ctx.fillText('时频域特征图', width / 2, 30);
          
          ctx.font = '12px Arial';
          ctx.fillText('时间 (s)', width / 2, height - 10);
          
          ctx.save();
          ctx.translate(20, height / 2);
          ctx.rotate(-Math.PI / 2);
          ctx.fillText('频率 (Hz)', 0, 0);
          ctx.restore();
          
          // 绘制刻度
          ctx.font = '10px Arial';
          ctx.fillStyle = '#666';
          
          // X轴刻度
          const xTicks = 5;
          for (let i = 0; i <= xTicks; i++) {
            const x = padding + (plotWidth * i) / xTicks;
            const time = ((eegData.timeFreq.x[timeSteps - 1] * i) / xTicks).toFixed(2);
            ctx.textAlign = 'center';
            ctx.fillText(time, x, height - 30);
          }
          
          // Y轴刻度
          const yTicks = 5;
          for (let i = 0; i <= yTicks; i++) {
            const y = padding + (plotHeight * i) / yTicks;
            const freq = ((eegData.timeFreq.y[freqSteps - 1] * (yTicks - i)) / yTicks).toFixed(0);
            ctx.textAlign = 'right';
            ctx.fillText(freq, padding - 10, y + 4);
          }
          
          // 绘制色标
          const legendWidth = 20;
          const legendHeight = plotHeight;
          const legendX = width - 40;
          const legendY = padding;
          
          for (let i = 0; i < legendHeight; i++) {
            const normalized = i / legendHeight;
            const r = Math.floor(255 * (0.267 + 0.004 * normalized));
            const g = Math.floor(255 * (0.004 + 0.5 * normalized));
            const b = Math.floor(255 * (0.329 + 0.6 * normalized));
            
            ctx.fillStyle = `rgb(${r}, ${g}, ${b})`;
            ctx.fillRect(legendX, legendY + legendHeight - i, legendWidth, 2);
          }
          
          ctx.strokeStyle = '#333';
          ctx.lineWidth = 1;
          ctx.strokeRect(legendX, legendY, legendWidth, legendHeight);
          
          // 色标标签
          ctx.fillStyle = '#666';
          ctx.font = '10px Arial';
          ctx.textAlign = 'left';
          ctx.fillText(maxVal.toFixed(0), legendX + legendWidth + 5, legendY + 10);
          ctx.fillText(minVal.toFixed(0), legendX + legendWidth + 5, legendY + legendHeight);
        }
      }, []);
      
      return (
        <div style={{ background: 'white', padding: '20px', display: 'inline-block' }}>
          <canvas ref={canvasRef} width={700} height={350} />
        </div>
      );
    };
    
    return await this.renderChartToBase64(TimeFreqComponent, 750, 400);
  }

  // 生成量表图
  static async generateScaleChart(_result: ResultItem): Promise<string> {
    const scaleData = Array.from({ length: 40 }, (_, i) => ({
      name: `题${i + 1}`,
      score: Math.floor(Math.random() * 5) + 1
    }));
    
    const ScaleChartComponent = () => (
      <BarChart width={700} height={350} data={scaleData}>
        <CartesianGrid strokeDasharray="3 3" stroke="#e0e0e0" />
        <XAxis 
          dataKey="name" 
          tick={{ fill: '#333', fontSize: 10 }} 
          interval={4}
        />
        <YAxis domain={[0, 5]} tick={{ fill: '#666' }} label={{ value: '分数', angle: -90, position: 'insideLeft', style: { fill: '#333' } }} />
        <Tooltip 
          contentStyle={{ backgroundColor: '#fff', border: '1px solid #ccc', borderRadius: '4px' }}
        />
        <Legend wrapperStyle={{ paddingTop: '10px' }} />
        <Bar dataKey="score" fill="#4ECDC4" name="量表得分" />
      </BarChart>
    );
    
    return await this.renderChartToBase64(ScaleChartComponent, 750, 400);
  }
  
  // 将React组件渲染为base64图片
  private static async renderChartToBase64(
    Component: React.ComponentType, 
    width: number = 600, 
    height: number = 400
  ): Promise<string> {
    return new Promise((resolve) => {
      const tempDiv = document.createElement('div');
      tempDiv.style.width = `${width}px`;
      tempDiv.style.height = `${height}px`;
      tempDiv.style.position = 'absolute';
      tempDiv.style.left = '-9999px';
      tempDiv.style.backgroundColor = '#ffffff';
      tempDiv.style.padding = '10px';
      document.body.appendChild(tempDiv);
      
      const root = createRoot(tempDiv);
      root.render(React.createElement(Component));
      
      setTimeout(async () => {
        const canvas = await html2canvas(tempDiv, {
          scale: 2,
          useCORS: true,
          backgroundColor: '#ffffff'
        });
        
        const base64 = canvas.toDataURL('image/png');
        document.body.removeChild(tempDiv);
        resolve(base64);
      }, 1000);
    });
  }
}